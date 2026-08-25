#!/usr/bin/env python3
"""Free long-form builder: HF Flux images + edge-tts Hindi + ffmpeg. 16:9. $0."""
import os, sys, json, time, subprocess, tempfile, urllib.request

HERE=os.path.dirname(os.path.abspath(__file__))
CFG=json.load(open(sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,"ashwatthama.json")))
HF=open(os.path.expanduser("~/.config/hf/.env")).read().split("=",1)[1].strip()
W,H,FPS,TAIL=1920,1080,30,0.35
ASSETS=os.path.join(HERE,CFG["title"]+"_assets"); os.makedirs(ASSETS,exist_ok=True)
OUT=os.path.join(HERE,CFG["title"]+"_final.mp4")
IMG_URL="https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],capture_output=True,text=True).stdout.strip())

def flux(prompt, out):
    if os.path.exists(out): return True
    body=json.dumps({"inputs":prompt,"parameters":{"width":1280,"height":720}}).encode()
    for attempt in range(5):
        try:
            req=urllib.request.Request(IMG_URL,data=body,headers={"Authorization":f"Bearer {HF}","Content-Type":"application/json"})
            d=urllib.request.urlopen(req,timeout=180).read()
            if d[:3]==b'\xff\xd8\xff' or d[:8]==b'\x89PNG\r\n\x1a\n':
                open(out,"wb").write(d); return True
            time.sleep(8)
        except urllib.error.HTTPError as e:
            if e.code in (429,503): time.sleep(15)
            else: time.sleep(8)
        except Exception: time.sleep(8)
    return False

def main():
    tmp=tempfile.mkdtemp(prefix="lf_")
    style=CFG.get("style",""); hero=CFG.get("hero","")
    clips=[];auds=[];last_img=None
    segs=CFG["segments"]
    for i,s in enumerate(segs):
        # voice (edge-tts CLI, fast rate)
        txt=os.path.join(tmp,f"t{i}.txt"); open(txt,"w").write(s["hi"])
        mp3=os.path.join(ASSETS,f"v{i}.mp3")
        if not os.path.exists(mp3):
            run(["edge-tts","--voice",CFG["voice"],f"--rate={CFG['rate']}","--file",txt,"--write-media",mp3])
        wav=os.path.join(tmp,f"v{i}.wav"); run(["ffmpeg","-y","-i",mp3,"-ar","44100","-ac","1",wav])
        d=dur(wav); clen=d+TAIL
        # image
        img=os.path.join(ASSETS,f"img{i}.png")
        prompt=s["img"].replace("$HERO",hero)+style
        if not flux(prompt,img):
            img=last_img or img
        if os.path.exists(img): last_img=img
        # clip (scale->cover 16:9, slow zoom via simple scale, static fallback)
        clip=os.path.join(tmp,f"c{i}.mp4")
        vf=f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS},format=yuv420p"
        run(["ffmpeg","-y","-loop","1","-t",f"{clen:.2f}","-i",img,"-vf",vf,"-c:v","libx264","-pix_fmt","yuv420p","-r",str(FPS),clip])
        clips.append(clip)
        apad=os.path.join(tmp,f"a{i}.wav"); run(["ffmpeg","-y","-i",wav,"-af",f"apad=pad_dur={TAIL}","-t",f"{clen:.2f}",apad]); auds.append(apad)
        print(f"[{i+1}/{len(segs)}] {d:.1f}s  img={'ok' if os.path.exists(img) else 'fallback'}",flush=True)
    vl=os.path.join(tmp,"v.txt"); open(vl,"w").write("".join(f"file '{c}'\n" for c in clips))
    al=os.path.join(tmp,"a.txt"); open(al,"w").write("".join(f"file '{a}'\n" for a in auds))
    vid=os.path.join(tmp,"vid.mp4"); aud=os.path.join(tmp,"aud.wav")
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",vl,"-c","copy",vid])
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",al,"-c","copy",aud])
    run(["ffmpeg","-y","-i",vid,"-i",aud,"-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",OUT])
    print(f"DONE -> {OUT} ({dur(OUT):.1f}s)",flush=True)

if __name__=="__main__": main()

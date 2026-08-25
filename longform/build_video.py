#!/usr/bin/env python3
"""General long-form builder: Flux images (free) + ElevenLabs voice + Ken-Burns pan. One config -> one video."""
import os, sys, json, time, subprocess, tempfile, urllib.request
HERE=os.path.dirname(os.path.abspath(__file__))
CFG=json.load(open(sys.argv[1]))
HF=open(os.path.expanduser("~/.config/hf/.env")).read().split("=",1)[1].strip()
EL=open(os.path.expanduser("~/.config/elevenlabs/.env")).read().split("=",1)[1].strip()
W,H,FPS,TAIL=1920,1080,30,0.35
ASSETS=os.path.join(HERE,CFG["title"]+"_assets"); os.makedirs(ASSETS,exist_ok=True)
OUT=os.path.join(HERE,CFG["title"]+"_final.mp4")
IMG_URL="https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"
VOICE=CFG.get("voice_id","vIdhHAZdn1bGjKe1dFw8")
def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],capture_output=True,text=True).stdout.strip())
def flux(prompt,out):
    if os.path.exists(out): return True
    body=json.dumps({"inputs":prompt,"parameters":{"width":1280,"height":720}}).encode()
    for _ in range(5):
        try:
            req=urllib.request.Request(IMG_URL,data=body,headers={"Authorization":f"Bearer {HF}","Content-Type":"application/json"})
            d=urllib.request.urlopen(req,timeout=180).read()
            if d[:3]==b'\xff\xd8\xff' or d[:8]==b'\x89PNG\r\n\x1a\n': open(out,"wb").write(d); return True
            time.sleep(8)
        except urllib.error.HTTPError as e: time.sleep(15 if e.code in(429,503) else 8)
        except Exception: time.sleep(8)
    return False
def eleven(text,out):
    if os.path.exists(out): return
    body=json.dumps({"text":text,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.5,"similarity_boost":0.75,"use_speaker_boost":True,"speed":CFG.get("speed",1.15)}}).encode()
    req=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}",data=body,headers={"xi-api-key":EL,"Content-Type":"application/json"})
    open(out,"wb").write(urllib.request.urlopen(req,timeout=120).read())
def main():
    tmp=tempfile.mkdtemp(prefix="bv_"); style=CFG.get("style",""); hero=CFG.get("hero","")
    segs=CFG["segments"]; clips=[];auds=[];last=None
    for i,s in enumerate(segs):
        mp3=os.path.join(ASSETS,f"v{i}.mp3"); eleven(s["hi"],mp3)
        wav=os.path.join(tmp,f"v{i}.wav"); run(["ffmpeg","-y","-i",mp3,"-ar","44100","-ac","1",wav])
        d=dur(wav); clen=d+TAIL
        img=os.path.join(ASSETS,f"img{i}.png"); prompt=s["img"].replace("$HERO",hero)+style
        if not flux(prompt,img): img=last or img
        if os.path.exists(img): last=img
        T=f"{clen:.2f}"
        cx=f"(in_w-{W})*(0.32+0.36*t/{T})"; cxr=f"(in_w-{W})*(0.68-0.36*t/{T})"
        cy=f"(in_h-{H})*(0.32+0.36*t/{T})"; cyr=f"(in_h-{H})*(0.68-0.36*t/{T})"
        midx=f"(in_w-{W})/2"; midy=f"(in_h-{H})/2"
        mx,my=[(cx,midy),(cxr,midy),(midx,cy),(midx,cyr)][i%4]
        zp=f"scale=2304:1296,crop={W}:{H}:x='{mx}':y='{my}',format=yuv420p"
        clip=os.path.join(tmp,f"c{i}.mp4")
        run(["ffmpeg","-y","-loop","1","-t",f"{clen:.2f}","-i",img,"-vf",zp,"-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-r",str(FPS),clip])
        clips.append(clip)
        apad=os.path.join(tmp,f"a{i}.wav"); run(["ffmpeg","-y","-i",wav,"-af",f"apad=pad_dur={TAIL}","-t",f"{clen:.2f}",apad]); auds.append(apad)
        print(f"[{i+1}/{len(segs)}] {d:.1f}s img={'ok' if os.path.exists(img) else 'fb'}",flush=True)
    vl=os.path.join(tmp,"v.txt"); open(vl,"w").write("".join(f"file '{c}'\n" for c in clips))
    al=os.path.join(tmp,"a.txt"); open(al,"w").write("".join(f"file '{a}'\n" for a in auds))
    vid=os.path.join(tmp,"vid.mp4"); aud=os.path.join(tmp,"aud.wav")
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",vl,"-c","copy",vid])
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",al,"-c","copy",aud])
    run(["ffmpeg","-y","-i",vid,"-i",aud,"-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",OUT])
    print(f"DONE -> {OUT} ({dur(OUT):.1f}s)",flush=True)
if __name__=="__main__": main()

#!/usr/bin/env python3
"""Add Ken-Burns motion (alternating zoom in/out) to cached stills + voice. Free, reuses assets."""
import os, json, subprocess, tempfile
HERE=os.path.dirname(os.path.abspath(__file__))
CFG=json.load(open(os.path.join(HERE,"ashwatthama.json")))
ASSETS=os.path.join(HERE,CFG["title"]+"_assets")
OUT=os.path.join(HERE,CFG["title"]+"_final.mp4")
W,H,FPS,TAIL=1920,1080,30,0.35
def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],capture_output=True,text=True).stdout.strip())
tmp=tempfile.mkdtemp(prefix="mo_")
segs=CFG["segments"]; clips=[];auds=[]
for i in range(len(segs)):
    img=os.path.join(ASSETS,f"img{i}.png"); mp3=os.path.join(ASSETS,f"v{i}.mp3")
    wav=os.path.join(tmp,f"v{i}.wav"); run(["ffmpeg","-y","-i",mp3,"-ar","44100","-ac","1",wav])
    d=dur(wav); clen=d+TAIL; frames=max(1,round(clen*FPS))
    T=f"{clen:.2f}"
    # gentle drift through only the middle ~35% of the overscan (slow glide)
    cx =f"(in_w-{W})*(0.32+0.36*t/{T})"; cxr=f"(in_w-{W})*(0.68-0.36*t/{T})"
    cy =f"(in_h-{H})*(0.32+0.36*t/{T})"; cyr=f"(in_h-{H})*(0.68-0.36*t/{T})"
    midx=f"(in_w-{W})/2"; midy=f"(in_h-{H})/2"
    moves=[ (cx, midy), (cxr, midy), (midx, cy), (midx, cyr) ]
    mx,my=moves[i%4]
    zp=f"scale=2304:1296,crop={W}:{H}:x='{mx}':y='{my}',format=yuv420p"
    clip=os.path.join(tmp,f"c{i}.mp4")
    run(["ffmpeg","-y","-loop","1","-t",f"{clen:.2f}","-i",img,"-vf",zp,"-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-r",str(FPS),clip])
    clips.append(clip)
    apad=os.path.join(tmp,f"a{i}.wav"); run(["ffmpeg","-y","-i",wav,"-af",f"apad=pad_dur={TAIL}","-t",f"{clen:.2f}",apad]); auds.append(apad)
    print(f"[{i+1}/{len(segs)}] motion {'in' if i%2==0 else 'out'} {d:.1f}s",flush=True)
vl=os.path.join(tmp,"v.txt"); open(vl,"w").write("".join(f"file '{c}'\n" for c in clips))
al=os.path.join(tmp,"a.txt"); open(al,"w").write("".join(f"file '{a}'\n" for a in auds))
vid=os.path.join(tmp,"vid.mp4"); aud=os.path.join(tmp,"aud.wav")
run(["ffmpeg","-y","-f","concat","-safe","0","-i",vl,"-c","copy",vid])
run(["ffmpeg","-y","-f","concat","-safe","0","-i",al,"-c","copy",aud])
run(["ffmpeg","-y","-i",vid,"-i",aud,"-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",OUT])
print(f"DONE -> {OUT} ({dur(OUT):.1f}s)",flush=True)

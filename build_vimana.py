#!/usr/bin/env python3
"""Vimana short: 6 stills synced 1:1 to narration lines (George voice) + captions. $0."""
import urllib.request, os, subprocess, tempfile, json, glob
from PIL import Image, ImageDraw, ImageFont

KEY=open(os.path.expanduser("~/.config/elevenlabs/.env")).read().split("=",1)[1].strip()
VOICE="JBFqnCBsd6RMkjVDRZzb"  # George
DL="/Users/satishkosaraju/Downloads"
OUT="/Users/satishkosaraju/EmpireOS/projects/bizshorts/vimana_final.mp4"
FONT="/System/Library/Fonts/Supplemental/Arial Bold.ttf"
W,H,FPS=1080,1920,30
TAIL=0.45

PAIRS=[
 ("Ornate_ancient_flying_chariot",
  "Legends say ancient India had flying machines. And the old texts describe them in detail."),
 ("Close-up_of_an_ancient_palm-leaf",
  "They're called Vimanas. Flying chariots, written about thousands of years ago, in the Mahabharata and Ramayana."),
 ("A_grand_ornate_domed_flying_vehicle",
  "And these aren't vague myths. The texts describe craft that moved across the sky, between cities... some say, between worlds."),
 ("A_blinding_white_explosion",
  "One passage describes a single weapon. A flash brighter than a thousand suns, that burned a city to ash."),
 ("Modern_hands_turning_pages",
  "The people who study this still can't agree. Ancient imagination... or a memory of something we forgot?"),
 ("An_ornate_vimana_craft_rising",
  "Someone wrote this down, thousands of years ago. The question is... what did they see?"),
]

def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],capture_output=True,text=True).stdout.strip())
def find(stub):
    h=glob.glob(os.path.join(DL,f"*{stub}*"));
    if not h: raise SystemExit("missing "+stub)
    return h[0]
def wrap(d,t,f,m):
    w=t.split();L=[];c=""
    for x in w:
        s=(c+" "+x).strip()
        if d.textlength(s,font=f)<=m:c=s
        else:L.append(c);c=x
    if c:L.append(c)
    return L
def cap_png(t,p):
    im=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(im);f=ImageFont.truetype(FONT,56)
    ls=wrap(d,t,f,W-180);lh=78;y=H-380-lh*len(ls)
    for ln in ls:
        d.text((W//2,y),ln,font=f,anchor="ma",fill=(255,255,255,255),stroke_width=4,stroke_fill=(0,0,0,255));y+=lh
    im.save(p)

tmp=tempfile.mkdtemp(prefix="vim_")
VF=f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS},format=yuv420p"
clips=[];auds=[];events=[];cursor=0.0
for i,(stub,line) in enumerate(PAIRS):
    # voice
    mp3=os.path.join(tmp,f"v{i}.mp3");wav=os.path.join(tmp,f"v{i}.wav")
    body=json.dumps({"text":line,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.55,"similarity_boost":0.75,"use_speaker_boost":True}}).encode()
    req=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}",data=body,headers={"xi-api-key":KEY,"Content-Type":"application/json"})
    open(mp3,"wb").write(urllib.request.urlopen(req,timeout=120).read())
    run(["ffmpeg","-y","-i",mp3,"-ar","44100","-ac","1",wav])
    d=dur(wav); clen=d+TAIL
    # image clip of exact length
    img=find(stub); clip=os.path.join(tmp,f"c{i}.mp4")
    run(["ffmpeg","-y","-loop","1","-t",f"{clen:.2f}","-i",img,"-vf",VF,"-c:v","libx264","-pix_fmt","yuv420p","-r",str(FPS),clip])
    clips.append(clip)
    # audio padded to clen so it aligns to image window
    apad=os.path.join(tmp,f"a{i}.wav")
    run(["ffmpeg","-y","-i",wav,"-af",f"apad=pad_dur={TAIL}","-t",f"{clen:.2f}",apad]); auds.append(apad)
    events.append((cursor,cursor+d,line)); cursor+=clen
    print(f"  scene {i+1}/6 {d:.1f}s")

# concat video + audio (hard cuts = perfect sync)
vl=os.path.join(tmp,"v.txt");open(vl,"w").write("".join(f"file '{c}'\n" for c in clips))
al=os.path.join(tmp,"a.txt");open(al,"w").write("".join(f"file '{a}'\n" for a in auds))
vid=os.path.join(tmp,"vid.mp4");aud=os.path.join(tmp,"aud.wav")
run(["ffmpeg","-y","-f","concat","-safe","0","-i",vl,"-c","copy",vid])
run(["ffmpeg","-y","-f","concat","-safe","0","-i",al,"-c","copy",aud])
av=os.path.join(tmp,"av.mp4")
run(["ffmpeg","-y","-i",vid,"-i",aud,"-c:v","copy","-c:a","aac","-b:a","192k","-shortest",av])
# caption overlays
ins=["-i",av];chains=[];prev="0:v"
for i,(a,b,t) in enumerate(events):
    p=os.path.join(tmp,f"cap{i}.png");cap_png(t,p);ins+=["-i",p]
    chains.append(f"[{prev}][{i+1}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[o{i}]");prev=f"o{i}"
run(["ffmpeg","-y"]+ins+["-filter_complex",";".join(chains),"-map",f"[{prev}]","-map","0:a","-c:v","libx264","-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart",OUT])
print(f"DONE -> {OUT} ({dur(OUT):.1f}s)")

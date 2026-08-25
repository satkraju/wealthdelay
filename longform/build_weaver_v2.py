#!/usr/bin/env python3
"""Layer ASMR sound + hook + story beats + CTA onto the clean weaver footage."""
import os,json,subprocess,urllib.request
from PIL import Image,ImageDraw,ImageFont
DIR="/Users/satishkosaraju/EmpireOS/projects/bizshorts/longform"
BASE=f"{DIR}/stitched.mp4"            # clean, no text
OUT=f"{DIR}/weaver_short_v2.mp4"
FONT="/System/Library/Fonts/Supplemental/Arial Bold.ttf"
KEY=open(os.path.expanduser("~/.config/elevenlabs/.env")).read().split("=",1)[1].strip()
W,H=1080,1920
def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],capture_output=True,text=True).stdout.strip())

# 1) ASMR sound via ElevenLabs sound-generation
print("generating ASMR sound...",flush=True)
body=json.dumps({"text":"continuous gentle forest ambience, soft rustling of dry grass being woven, delicate small bird chirps, calm ASMR","duration_seconds":20,"prompt_influence":0.4}).encode()
req=urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation",data=body,headers={"xi-api-key":KEY,"Content-Type":"application/json"})
open(f"{DIR}/asmr.mp3","wb").write(urllib.request.urlopen(req,timeout=120).read())

# 2) caption beats (text, start, end, y_pos)
beats=[
 ("No teacher.\nNo blueprint.",0.0,3.0,260),
 ("Just instinct.",3.0,7.5,1480),
 ("Strand by strand,\nit weaves a home.",7.5,13.0,1380),
 ("Perfect.\nEvery time.",13.0,17.5,1420),
 ("Which animal builds best?",17.5,20.4,1480),
]
def png(text,path,y0,size=72):
    im=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(im);f=ImageFont.truetype(FONT,size)
    y=y0
    for ln in text.split("\n"):
        d.text((W//2,y),ln,font=f,anchor="ma",fill=(255,255,255,255),stroke_width=6,stroke_fill=(0,0,0,255));y+=size+14
    im.save(path)
ins=["-i",BASE];chains=[];prev="0:v"
for i,(t,a,b,y) in enumerate(beats):
    p=f"{DIR}/b{i}.png"; png(t,p,y); ins+=["-i",p]
    chains.append(f"[{prev}][{i+1}:v]overlay=0:0:enable='between(t,{a},{b})'[o{i}]");prev=f"o{i}"

# 3) mux video+overlays+asmr
ins+=["-i",f"{DIR}/asmr.mp3"]
audio_idx=len(beats)+1
run(["ffmpeg","-y"]+ins+["-filter_complex",";".join(chains),"-map",f"[{prev}]","-map",f"{audio_idx}:a",
     "-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",OUT])
print(f"DONE -> {OUT} ({dur(OUT):.1f}s)",flush=True)

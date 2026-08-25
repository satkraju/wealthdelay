#!/usr/bin/env python3
"""Burn captions via PIL PNG overlays (no libass needed). Uses _av.mp4 (video+voice)."""
import os, subprocess, glob, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

BASE = "/Users/satishkosaraju/EmpireOS/projects/bizshorts/_av.mp4"
OUT = "/Users/satishkosaraju/EmpireOS/projects/bizshorts/temple_restore_final.mp4"
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
W, H = 1080, 1920
GAP = 0.30
LINES = [
    "This temple has been dead for five hundred years.",
    "But it didn't always look like this.",
    "Watch... as time runs backwards.",
    "The stone heals. The pillars rise. The cracks close.",
    "Color floods back across carvings no one has seen in centuries.",
    "The lamps light. The smoke returns. The people come home.",
    "This is what it may have looked like when it was alive.",
    "And almost no one alive today remembers it stood like this.",
]


def dur(p):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=nw=1:nk=1",p],capture_output=True,text=True).stdout.strip())


def wrap(draw, text, fnt, maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if draw.textlength(t,font=fnt)<=maxw: cur=t
        else: lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines


def make_png(text, path):
    img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    fnt=ImageFont.truetype(FONT,56)
    lines=wrap(d,text,fnt,W-180); lh=78
    total=lh*len(lines); y=H-360-total
    for ln in lines:
        d.text((W//2,y),ln,font=fnt,anchor="ma",fill=(255,255,255,255),
               stroke_width=4,stroke_fill=(0,0,0,255))
        y+=lh
    img.save(path)


def main():
    tmpdirs=sorted(glob.glob("/tmp/claude-501/voice_*"),key=os.path.getmtime)
    if not tmpdirs: sys.exit("no voice tmp dir")
    vt=tmpdirs[-1]
    # recompute timings from per-line wavs
    events=[]; cursor=0.0
    for i,line in enumerate(LINES):
        wav=os.path.join(vt,f"l{i}.wav"); d=dur(wav)
        events.append((cursor,cursor+d,line)); cursor+=d
        if i<len(LINES)-1: cursor+=GAP
    tmp=tempfile.mkdtemp(prefix="cap_")
    pngs=[]
    for i,(a,b,txt) in enumerate(events):
        p=os.path.join(tmp,f"c{i}.png"); make_png(txt,p); pngs.append((p,a,b))
    inputs=["-i",BASE]
    for p,_,_ in pngs: inputs+=["-i",p]
    chains=[]; prev="0:v"
    for i,(p,a,b) in enumerate(pngs):
        out=f"t{i}"
        chains.append(f"[{prev}][{i+1}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[{out}]")
        prev=out
    fc=";".join(chains)
    subprocess.run(["ffmpeg","-y"]+inputs+["-filter_complex",fc,"-map",f"[{prev}]","-map","0:a",
        "-c:v","libx264","-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart",OUT],
        check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    print(f"DONE -> {OUT}  ({dur(OUT):.1f}s)")


if __name__=="__main__":
    main()

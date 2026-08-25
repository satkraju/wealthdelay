#!/usr/bin/env python3
"""Satellite time-lapse short from NASA GIBS (public domain). Aral Sea vanishing. Free + legal."""
import os,urllib.request,subprocess,tempfile,math
import numpy as np, wave
from PIL import Image,ImageDraw,ImageFont
DIR=os.path.dirname(os.path.abspath(__file__))
OUT=f"{DIR}/aral_short.mp4"
FONT="/System/Library/Fonts/Supplemental/Arial Bold.ttf"
W,H,FPS=1080,1920,30
BBOX="42,58,48,62"   # lat_min,lon_min,lat_max,lon_max  (portrait-ish)
LAYER="MODIS_Terra_CorrectedReflectance_TrueColor"
YEARS=list(range(2000,2025))   # yearly
HOLD=1.8; XF=0.6
def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def fetch(date,path):
    url=("https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0"
         f"&LAYERS={LAYER}&CRS=EPSG:4326&BBOX={BBOX}&WIDTH=900&HEIGHT=1350&FORMAT=image/jpeg&TIME={date}")
    open(path,"wb").write(urllib.request.urlopen(url,timeout=60).read())

tmp=tempfile.mkdtemp(prefix="sat_")
fbig=ImageFont.truetype(FONT,150); ftitle=ImageFont.truetype(FONT,56); fhook=ImageFont.truetype(FONT,72)
def frame_png(sat_path,year,out):
    canvas=Image.new("RGB",(W,H),(8,10,16))
    im=Image.open(sat_path).convert("RGB")
    im=im.resize((W,int(im.height*W/im.width)))
    canvas.paste(im,(0,(H-im.height)//2))
    d=ImageDraw.Draw(canvas)
    d.text((W//2,90),"THE ARAL SEA",font=ftitle,anchor="ma",fill=(255,255,255),stroke_width=3,stroke_fill=(0,0,0))
    d.text((W//2,H-260),str(year),font=fbig,anchor="ma",fill=(255,255,255),stroke_width=6,stroke_fill=(0,0,0))
    canvas.save(out)

clips=[]
for i,y in enumerate(YEARS):
    s=f"{tmp}/s{i}.jpg"
    try: fetch(f"{y}-08-15",s)
    except Exception:
        if clips: continue
        fetch(f"{y}-07-15",s)
    p=f"{tmp}/f{i}.png"; frame_png(s,y,p)
    c=f"{tmp}/c{i}.mp4"; run(["ffmpeg","-y","-loop","1","-t",f"{HOLD}","-i",p,"-vf",f"fps={FPS},format=yuv420p","-c:v","libx264","-preset","veryfast","-r",str(FPS),c]); clips.append(c)
    print(f"[{i+1}/{len(YEARS)}] {y}",flush=True)

# xfade chain
inp=[];
for c in clips: inp+=["-i",c]
fc=[]; prev="0:v"; run_t=HOLD
for i in range(1,len(clips)):
    off=run_t-XF; fc.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[v{i}]"); prev=f"v{i}"; run_t+=HOLD-XF
montage=f"{tmp}/m.mp4"; run(["ffmpeg","-y"]+inp+["-filter_complex",";".join(fc),"-map",f"[{prev}]","-c:v","libx264","-pix_fmt","yuv420p",montage])
total=run_t

# hook + end overlays
def textpng(lines,path,size,y0):
    im=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(im);f=ImageFont.truetype(FONT,size);y=y0
    for ln in lines: d.text((W//2,y),ln,font=f,anchor="ma",fill=(255,255,255,255),stroke_width=6,stroke_fill=(0,0,0,255));y+=size+16
    im.save(path)
hk=f"{tmp}/hk.png"; textpng(["Watch a whole sea","disappear from space."],hk,68,640)
en=f"{tmp}/en.png"; textpng(["Gone in a generation.","Where did it go?"],en,64,640)
ov=f"{tmp}/ov.mp4"
run(["ffmpeg","-y","-i",montage,"-i",hk,"-i",en,"-filter_complex",
     f"[0:v][1:v]overlay=0:0:enable='between(t,0,2.5)'[a];[a][2:v]overlay=0:0:enable='between(t,{total-2.5:.2f},{total})'[v]",
     "-map","[v]","-c:v","libx264","-pix_fmt","yuv420p",ov])

# eerie ambient (synth)
SR=44100; n=int(SR*total); t=np.arange(n)/SR
drone=0.10*np.sin(2*np.pi*70*t)+0.06*np.sin(2*np.pi*105*t)*np.sin(2*np.pi*0.1*t)
wind=np.convolve(np.random.RandomState(3).randn(n),np.ones(120)/120,mode='same')*0.05
buf=np.tanh((drone+wind)*1.1)*0.8
wav=f"{tmp}/amb.wav"
with wave.open(wav,"w") as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes((buf*32767).astype(np.int16).tobytes())
run(["ffmpeg","-y","-i",ov,"-i",wav,"-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",OUT])
print(f"DONE -> {OUT} ({total:.1f}s)")

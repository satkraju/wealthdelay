#!/usr/bin/env python3
"""CRAFTED Aral Sea piece — emotional script + cinematic slow push-in + color grade + voice + music. NASA PD imagery."""
import os,urllib.request,subprocess,tempfile,json
from PIL import Image,ImageDraw,ImageFont
DIR=os.path.dirname(os.path.abspath(__file__)); OUT=f"{DIR}/aral_craft.mp4"
FONT="/System/Library/Fonts/Avenir Next.ttc"
def AV(size,bold=False): return ImageFont.truetype(FONT,size,index=0 if bold else 2)
EL=open(os.path.expanduser("~/.config/elevenlabs/.env")).read().split("=",1)[1].strip()
VOICE="JBFqnCBsd6RMkjVDRZzb"  # George, warm/reflective
MUSIC=f"{DIR}/music.mp3"
W,H,FPS=1080,1920,30
BBOX="42,57.5,48,61.5"
YEARS=[2000,2002,2004,2006,2008,2010,2012,2014,2016,2018,2020,2022,2024]
LINES=["This is a real place on Earth.","Can you guess where?","Watch what happens to it.",
 "It was one of the largest lakes in the world.","Ships sailed here. Millions lived on its shores.",
 "Then... it began to vanish.","Year by year, the water pulled away.","Until almost nothing was left.",
 "This is the Aral Sea.","Once the size of Ireland. Now, a desert.",
 "We drained it in a single generation.","Can you guess which place is next?"]
REVEAL_IDX=8   # the line that reveals the name (rendered big)
def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],capture_output=True,text=True).stdout.strip())
def fetch(date,path):
    u=(f"https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0"
       f"&LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor&CRS=EPSG:4326&BBOX={BBOX}&WIDTH=1100&HEIGHT=1650&FORMAT=image/jpeg&TIME={date}")
    open(path,"wb").write(urllib.request.urlopen(u,timeout=60).read())
def vo(text,path):
    b=json.dumps({"text":text,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.6,"similarity_boost":0.75,"use_speaker_boost":True}}).encode()
    r=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}",data=b,headers={"xi-api-key":EL,"Content-Type":"application/json"})
    open(path,"wb").write(urllib.request.urlopen(r,timeout=120).read())
tmp=tempfile.mkdtemp(prefix="craft_")

# 1) voiceover per line -> durations & total
auds=[];events=[];cursor=1.2  # 1.2s breath before first line
for i,ln in enumerate(LINES):
    m=f"{tmp}/v{i}.mp3";vo(ln,m);w=f"{tmp}/v{i}.wav";run(["ffmpeg","-y","-i",m,"-ar","44100","-ac","1",w])
    d=dur(w);events.append((cursor,cursor+d,ln));auds.append((w,cursor));cursor+=d+0.55
TOTAL=cursor+1.8

# 2) fetch frames + build progressive-zoom clips (continuous push-in)
seg=TOTAL/len(YEARS)
clips=[]
def clarity(path):  # higher = clearer (less cloud/black). clouds=bright white, nodata=black
    try:
        im=Image.open(path).convert("L");h=im.histogram();tot=im.width*im.height
        return 1.0 - (sum(h[235:])+sum(h[:18]))/tot
    except Exception: return -1
for i,y in enumerate(YEARS):
    s=f"{tmp}/s{i}.jpg"; best=None;bestsc=-1
    for dt in [f"{y}-08-15",f"{y}-07-20",f"{y}-09-10",f"{y}-06-25",f"{y}-08-01",f"{y}-09-25",f"{y}-07-05"]:
        cand=f"{tmp}/cand.jpg"
        try: fetch(dt,cand)
        except Exception: continue
        sc=clarity(cand)
        if sc>bestsc: bestsc=sc; import shutil; shutil.copy(cand,s)
        if sc>0.82: break   # clear enough
    z=1.0+0.020*i                       # gentle progressive zoom (won't push past the lake)
    sw,sh=int(W*z),int(H*z)
    # color grade (melancholic: desaturate + warm + contrast) + crop center
    vf=(f"scale={sw}:{sh}:force_original_aspect_ratio=increase,crop={W}:{H},"
        f"eq=saturation=0.82:contrast=1.08:brightness=-0.02,setsar=1,fps={FPS},format=yuv420p")
    c=f"{tmp}/c{i}.mp4";run(["ffmpeg","-y","-loop","1","-t",f"{seg+0.6:.2f}","-i",s,"-vf",vf,"-c:v","libx264","-preset","veryfast","-r",str(FPS),c]);clips.append(c)
    print(f"frame {i+1}/{len(YEARS)} {y}",flush=True)

# 3) crossfade chain -> montage exact-ish length
inp=[];
for c in clips: inp+=["-i",c]
XF=0.6;fc=[];prev="0:v";rt=seg+0.6
for k in range(1,len(clips)):
    fc.append(f"[{prev}][{k}:v]xfade=transition=fade:duration={XF}:offset={rt-XF:.3f}[v{k}]");prev=f"v{k}";rt+=seg
montage=f"{tmp}/m.mp4";run(["ffmpeg","-y"]+inp+["-filter_complex",";".join(fc),"-map",f"[{prev}]","-c:v","libx264","-pix_fmt","yuv420p",montage])

# 4) elegant captions (lowercase-ish, letter-spaced, soft) timed to VO
def cap(text,path,big=False):  # SHORTS style: bold, big, punchy, high-contrast
    im=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
    size=104 if big else 78
    f=ImageFont.truetype(FONT,size,index=0); lh=size+18; cx=W//2   # Avenir Next Bold
    words=text.split();lines=[];cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=f)<=W-150:cur=t
        else:lines.append(cur);cur=w
    if cur:lines.append(cur)
    y=int(H*0.74)-lh*len(lines)//2          # lower third (clear of center + bottom UI)
    fill=(255,228,90) if big else (255,255,255)   # reveal pops yellow
    for ln in lines:
        d.text((cx,y),ln,font=f,anchor="ma",fill=fill,stroke_width=9,stroke_fill=(0,0,0,255)); y+=lh
    im.save(path)
ins=["-i",montage];ch=[];prev="0:v"
for i,(a,b,ln) in enumerate(events):
    p=f"{tmp}/cap{i}.png";cap(ln,p,big=(i==REVEAL_IDX));ins+=["-i",p]
    ch.append(f"[{prev}][{i+1}:v]overlay=0:0:enable='between(t,{a:.2f},{b+0.4:.2f})'[o{i}]");prev=f"o{i}"
# vignette for cinematic depth
ch.append(f"[{prev}]vignette=PI/4.5[vv]")
withcap=f"{tmp}/withcap.mp4";run(["ffmpeg","-y"]+ins+["-filter_complex",";".join(ch),"-map","[vv]","-t",f"{TOTAL:.2f}","-c:v","libx264","-pix_fmt","yuv420p",withcap])

# 5) audio: music bed (soft) + VO at offsets
voins=[]
for w,off in auds: voins.append(f"amovie={w},adelay={int(off*1000)}|{int(off*1000)},volume=1.0")
bg=f"amovie={MUSIC}:loop=0,aloop=loop=-1:size=2e9,atrim=0:{TOTAL},afade=t=in:st=0:d=2,afade=t=out:st={TOTAL-2.5:.2f}:d=2.5,volume=0.26"
filt=";".join([f"{bg}[bg]"]+[f"{v}[a{i}]" for i,v in enumerate(voins)])+";[bg]"+"".join(f"[a{i}]" for i in range(len(voins)))+f"amix=inputs={len(voins)+1}:normalize=0:duration=first[mx];[mx]loudnorm=I=-15:TP=-1.5[out]"
run(["ffmpeg","-y","-i",withcap,"-filter_complex",filt,"-map","0:v","-map","[out]","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",OUT])
print(f"DONE -> {OUT} ({dur(OUT):.1f}s)",flush=True)

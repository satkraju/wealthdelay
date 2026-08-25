#!/usr/bin/env python3
"""Batch craft engine: guess->reveal satellite Shorts. NASA PD imagery + ElevenLabs voice + CC-BY music. One loop -> N videos."""
import os,urllib.request,subprocess,tempfile,json,shutil
from PIL import Image,ImageDraw,ImageFont
DIR=os.path.dirname(os.path.abspath(__file__))
FONT="/System/Library/Fonts/Avenir Next.ttc"
EL=open(os.path.expanduser("~/.config/elevenlabs/.env")).read().split("=",1)[1].strip()
VOICE="JBFqnCBsd6RMkjVDRZzb"; MUSIC=f"{DIR}/music.mp3"
W,H,FPS=1080,1920,30
YEARS=[2000,2002,2004,2006,2008,2010,2012,2014,2016,2018,2020,2022,2024]

LOCATIONS=[
 {"title":"urmia","bbox":"36.4,44.8,38.8,46.4","reveal":8,"lines":[
   "This is a real place on Earth.","Can you guess where?","Watch what happens to it.",
   "It was the largest lake in the Middle East.","Flamingos once gathered here by the thousands.",
   "Then the water began to retreat.","Year by year, the shoreline pulled back.",
   "Until most of it was salt and dust.","This is Lake Urmia, in Iran.",
   "It has lost most of its water in a single generation.","Dams and farms drank its rivers dry.",
   "Can you guess which place is next?"]},
 {"title":"poopo","bbox":"-19.8,-67.8,-17.4,-66.2","reveal":8,"lines":[
   "This is a real place on Earth.","Can you guess where?","Watch what happens to it.",
   "It was Bolivia's second largest lake.","Fishermen lived on its shores for generations.",
   "Then, year by year, it began to shrink.","The boats were left stranded on dry ground.",
   "Until one day, it was simply gone.","This was Lake Poopo.",
   "By 2015, it had completely dried up.","Drought and diverted rivers erased it.",
   "Can you guess which place is next?"]},
 {"title":"amazon","bbox":"-11.5,-63.5,-8.5,-61.5","reveal":8,"lines":[
   "This is a real place on Earth.","Can you guess where?","Watch what happens to it.",
   "This was untouched rainforest.","Home to species found nowhere else.",
   "Then the clearing began.","Roads cut in. Then farms, in a fishbone pattern.",
   "And the green kept disappearing.","This is the Amazon, in Brazil.",
   "An area larger than France has been cleared.","Burned and cut for cattle, year after year.",
   "Can you guess which place is next?"]},
 {"title":"toshka","bbox":"21.6,29.6,23.6,31.6","reveal":8,"lines":[
   "This is a real place on Earth.","Can you guess where?","Watch what happens to it.",
   "There was nothing here but desert.","Some of the driest land on the planet.",
   "Then, almost overnight, lakes appeared.","Vast new lakes, in the middle of the Sahara.",
   "And then... they began to vanish again.","These are the Toshka Lakes, in Egypt.",
   "They were born from a flood in the 1990s.","Then slowly swallowed by the desert sun.",
   "Can you guess which place is next?"]},
]

def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],capture_output=True,text=True).stdout.strip())
def fetch(bbox,date,path):
    u=("https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0"
       f"&LAYERS=MODIS_Terra_CorrectedReflectance_TrueColor&CRS=EPSG:4326&BBOX={bbox}&WIDTH=1100&HEIGHT=1650&FORMAT=image/jpeg&TIME={date}")
    open(path,"wb").write(urllib.request.urlopen(u,timeout=60).read())
def clarity(p):
    try:
        im=Image.open(p).convert("L");h=im.histogram();t=im.width*im.height
        return 1.0-(sum(h[235:])+sum(h[:18]))/t
    except Exception: return -1
def vo(text,path):
    b=json.dumps({"text":text,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.6,"similarity_boost":0.75,"use_speaker_boost":True}}).encode()
    r=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}",data=b,headers={"xi-api-key":EL,"Content-Type":"application/json"})
    open(path,"wb").write(urllib.request.urlopen(r,timeout=120).read())
def cap(text,path,big=False):
    im=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
    size=104 if big else 78; f=ImageFont.truetype(FONT,size,index=0); lh=size+18; cx=W//2
    words=text.split();lines=[];cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if d.textlength(t,font=f)<=W-150:cur=t
        else:lines.append(cur);cur=w
    if cur:lines.append(cur)
    y=int(H*0.74)-lh*len(lines)//2; fill=(255,228,90) if big else (255,255,255)
    for ln in lines: d.text((cx,y),ln,font=f,anchor="ma",fill=fill,stroke_width=9,stroke_fill=(0,0,0,255));y+=lh
    im.save(path)

def build(cfg):
    bbox=cfg["bbox"];LINES=cfg["lines"];REVEAL=cfg["reveal"];OUT=f"{DIR}/{cfg['title']}_craft.mp4"
    tmp=tempfile.mkdtemp(prefix=f"c_{cfg['title']}_")
    auds=[];events=[];cursor=1.2
    for i,ln in enumerate(LINES):
        m=f"{tmp}/v{i}.mp3";vo(ln,m);w=f"{tmp}/v{i}.wav";run(["ffmpeg","-y","-i",m,"-ar","44100","-ac","1",w])
        d=dur(w);events.append((cursor,cursor+d,ln));auds.append((w,cursor));cursor+=d+0.55
    TOTAL=cursor+1.8; seg=TOTAL/len(YEARS); clips=[]
    for i,y in enumerate(YEARS):
        s=f"{tmp}/s{i}.jpg";bestsc=-1
        for dt in [f"{y}-08-15",f"{y}-07-20",f"{y}-09-10",f"{y}-06-25",f"{y}-08-01",f"{y}-09-25",f"{y}-07-05"]:
            cand=f"{tmp}/cand.jpg"
            try: fetch(bbox,dt,cand)
            except Exception: continue
            sc=clarity(cand)
            if sc>bestsc: bestsc=sc; shutil.copy(cand,s)
            if sc>0.82: break
        z=1.0+0.020*i; sw,sh=int(W*z),int(H*z)
        vf=(f"scale={sw}:{sh}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"eq=saturation=0.82:contrast=1.08:brightness=-0.02,setsar=1,fps={FPS},format=yuv420p")
        c=f"{tmp}/c{i}.mp4";run(["ffmpeg","-y","-loop","1","-t",f"{seg+0.6:.2f}","-i",s,"-vf",vf,"-c:v","libx264","-preset","veryfast","-r",str(FPS),c]);clips.append(c)
    inp=[]
    for c in clips: inp+=["-i",c]
    XF=0.6;fc=[];prev="0:v";rt=seg+0.6
    for k in range(1,len(clips)): fc.append(f"[{prev}][{k}:v]xfade=transition=fade:duration={XF}:offset={rt-XF:.3f}[v{k}]");prev=f"v{k}";rt+=seg
    montage=f"{tmp}/m.mp4";run(["ffmpeg","-y"]+inp+["-filter_complex",";".join(fc),"-map",f"[{prev}]","-c:v","libx264","-pix_fmt","yuv420p",montage])
    ins=["-i",montage];ch=[];prev="0:v"
    for i,(a,b,ln) in enumerate(events):
        p=f"{tmp}/cap{i}.png";cap(ln,p,big=(i==REVEAL));ins+=["-i",p]
        ch.append(f"[{prev}][{i+1}:v]overlay=0:0:enable='between(t,{a:.2f},{b+0.4:.2f})'[o{i}]");prev=f"o{i}"
    ch.append(f"[{prev}]vignette=PI/4.5[vv]")
    withcap=f"{tmp}/wc.mp4";run(["ffmpeg","-y"]+ins+["-filter_complex",";".join(ch),"-map","[vv]","-t",f"{TOTAL:.2f}","-c:v","libx264","-pix_fmt","yuv420p",withcap])
    voins=[f"amovie={w},adelay={int(o*1000)}|{int(o*1000)},volume=1.0" for w,o in auds]
    bg=f"amovie={MUSIC}:loop=0,aloop=loop=-1:size=2e9,atrim=0:{TOTAL},afade=t=in:st=0:d=2,afade=t=out:st={TOTAL-2.5:.2f}:d=2.5,volume=0.26"
    filt=";".join([f"{bg}[bg]"]+[f"{v}[a{i}]" for i,v in enumerate(voins)])+";[bg]"+"".join(f"[a{i}]" for i in range(len(voins)))+f"amix=inputs={len(voins)+1}:normalize=0:duration=first[mx];[mx]loudnorm=I=-15:TP=-1.5[out]"
    run(["ffmpeg","-y","-i",withcap,"-filter_complex",filt,"-map","0:v","-map","[out]","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",OUT])
    print(f"DONE -> {OUT} ({dur(OUT):.1f}s)",flush=True); shutil.rmtree(tmp,ignore_errors=True)

for cfg in LOCATIONS:
    print(f"=== building {cfg['title']} ===",flush=True)
    try: build(cfg)
    except Exception as e: print(f"FAIL {cfg['title']}: {e}",flush=True)
print("ALL DONE",flush=True)

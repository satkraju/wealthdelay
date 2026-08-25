#!/usr/bin/env python3
"""'Top 10 Places Changing From Space' — 5-min long-form + 10 shorts. NASA imagery (PD) + ElevenLabs VO + CC-BY music."""
import os,urllib.request,subprocess,tempfile,json
from PIL import Image,ImageDraw,ImageFont
DIR=os.path.dirname(os.path.abspath(__file__))
FONT="/System/Library/Fonts/Supplemental/Arial Bold.ttf"
EL=open(os.path.expanduser("~/.config/elevenlabs/.env")).read().split("=",1)[1].strip()
VOICE="pqHfZKP75CvOlQylNhV4"  # Bill, documentary male
MUSIC=f"{DIR}/music.mp3"
W,H,FPS=1080,1920,30
YEARS=[2000,2003,2006,2009,2012,2015,2018,2021,2024]
HOLD=3.0; XF=0.6
LAYER="MODIS_Terra_CorrectedReflectance_TrueColor"
LOC=[  # order = countdown #10 -> #1 (all LARGE features that render at MODIS 250m)
 (10,"SHENZHEN, CHINA","22.0,113.4,23.2,114.6","Shenzhen grew from a fishing town into a megacity of millions in just a few decades."),
 (9,"SAUDI DESERT FARMS","29.0,37.0,31.0,38.4","In the Saudi desert, thousands of circular farms appeared, fed by ancient underground water."),
 (8,"POYANG LAKE, CHINA","28.3,115.6,30.0,117.0","China's largest freshwater lake, Poyang, now shrinks to record lows in the dry season."),
 (7,"MESOPOTAMIAN MARSHES, IRAQ","30.0,46.0,32.0,47.8","Iraq's ancient marshes were drained, briefly revived, then hammered by drought."),
 (6,"TOSHKA LAKES, EGYPT","21.6,29.6,23.6,31.6","In Egypt's desert, new lakes appeared almost overnight, then slowly vanished again."),
 (5,"THE AMAZON, BRAZIL","-11.5,-63.5,-8.5,-61.5","In the Amazon, forest is cleared in a fishbone pattern, replaced by farmland year after year."),
 (4,"LAKE URMIA, IRAN","36.4,44.8,38.8,46.4","Iran's Lake Urmia, once the largest lake in the Middle East, shrank to a fraction of its size."),
 (3,"LAKE POOPO, BOLIVIA","-19.8,-67.8,-17.4,-66.2","Bolivia's Lake Poopo was its second largest lake. By 2015, it had completely dried up."),
 (2,"LAKE CHAD, AFRICA","12.4,13.0,14.6,15.2","Lake Chad, a lifeline for millions in Africa, has collapsed to a fraction of its former size."),
 (1,"THE ARAL SEA","42,57.5,48,61.5","The Aral Sea was once the fourth largest lake on Earth. After its rivers were diverted, it lost over ninety percent of its water."),
]
HOOK="These ten places are changing so fast, you can see it from space. Number one is hard to believe."
OUTRO="Our planet is changing faster than ever. Which one shocked you the most? Tell me below."
def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],capture_output=True,text=True).stdout.strip())
def fetch(bbox,date,path):
    u=(f"https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?SERVICE=WMS&REQUEST=GetMap&VERSION=1.3.0"
       f"&LAYERS={LAYER}&CRS=EPSG:4326&BBOX={bbox}&WIDTH=900&HEIGHT=1350&FORMAT=image/jpeg&TIME={date}")
    open(path,"wb").write(urllib.request.urlopen(u,timeout=60).read())
def is_blank(p):
    try:
        im=Image.open(p).convert("L"); h=im.histogram()
        return sum(h[:18])/(im.width*im.height) > 0.90   # mostly black = no data/cloud
    except Exception: return True
def fetch_good(bbox,year,path):
    for dt in [f"{year}-08-15",f"{year}-07-20",f"{year}-09-12",f"{year}-06-25",f"{year}-08-01",
               f"{year+1}-08-15",f"{year-1}-08-15",f"{year}-10-05"]:
        try:
            fetch(bbox,dt,path)
            if not is_blank(path): return True
        except Exception: continue
    return False
def vo(text,path):
    if os.path.exists(path):return
    b=json.dumps({"text":text,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.5,"similarity_boost":0.75,"use_speaker_boost":True}}).encode()
    r=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}",data=b,headers={"xi-api-key":EL,"Content-Type":"application/json"})
    open(path,"wb").write(urllib.request.urlopen(r,timeout=120).read())
ft=ImageFont.truetype(FONT,52); frank=ImageFont.truetype(FONT,120); fyr=ImageFont.truetype(FONT,110)
def seg_frame(sat,rank,name,year,out):
    cv=Image.new("RGB",(W,H),(8,10,16)); im=Image.open(sat).convert("RGB"); im=im.resize((W,int(im.height*W/im.width)))
    cv.paste(im,(0,(H-im.height)//2)); d=ImageDraw.Draw(cv)
    d.text((60,70),f"#{rank}",font=frank,anchor="la",fill=(255,220,90),stroke_width=5,stroke_fill=(0,0,0))
    d.text((W//2,210),name,font=ft,anchor="ma",fill=(255,255,255),stroke_width=3,stroke_fill=(0,0,0))
    d.text((W//2,H-250),str(year),font=fyr,anchor="ma",fill=(255,255,255),stroke_width=6,stroke_fill=(0,0,0)); cv.save(out)
def card(lines,out,size=78,y0=820):
    cv=Image.new("RGB",(W,H),(6,8,16)); d=ImageDraw.Draw(cv); f=ImageFont.truetype(FONT,size); y=y0
    for ln in lines: d.text((W//2,y),ln,font=f,anchor="ma",fill=(255,255,255),stroke_width=5,stroke_fill=(0,0,0));y+=size+18
    cv.save(out)

ASS=f"{DIR}/lf_assets"; os.makedirs(ASS,exist_ok=True)
tmp=tempfile.mkdtemp(prefix="lf_")
segs=[]; seg_durs=[]
for idx,(rank,name,bbox,line) in enumerate(LOC):
    clips=[]
    for j,y in enumerate(YEARS):
        s=f"{tmp}/s{idx}_{j}.jpg"
        if not fetch_good(bbox,y,s):
            print(f"  skip blank {name} {y}",flush=True); continue
        p=f"{tmp}/f{idx}_{j}.png"; seg_frame(s,rank,name,y,p)
        c=f"{tmp}/c{idx}_{j}.mp4"; run(["ffmpeg","-y","-loop","1","-t",str(HOLD),"-i",p,"-vf",f"fps={FPS},format=yuv420p","-c:v","libx264","-preset","veryfast","-r",str(FPS),c]); clips.append(c)
    inp=[];
    for c in clips: inp+=["-i",c]
    fc=[];prev="0:v";rt=HOLD
    for k in range(1,len(clips)): fc.append(f"[{prev}][{k}:v]xfade=transition=fade:duration={XF}:offset={rt-XF:.3f}[v{k}]");prev=f"v{k}";rt+=HOLD-XF
    seg=f"{ASS}/seg{idx}.mp4"; run(["ffmpeg","-y"]+inp+["-filter_complex",";".join(fc),"-map",f"[{prev}]","-c:v","libx264","-pix_fmt","yuv420p",seg])
    segs.append(seg); seg_durs.append(dur(seg)); print(f"segment #{rank} {name} done",flush=True)

# intro/outro cards
intro=f"{tmp}/intro.mp4"; card(["TOP 10 PLACES","CHANGING ON EARTH","(from space)"],f"{tmp}/intro.png",84,720); run(["ffmpeg","-y","-loop","1","-t","6","-i",f"{tmp}/intro.png","-vf",f"fps={FPS},format=yuv420p","-c:v","libx264","-r",str(FPS),intro])
outro=f"{tmp}/outro.mp4"; card(["Our planet is changing.","Which shocked you most?","Comment below."],f"{tmp}/outro.png",74,760); run(["ffmpeg","-y","-loop","1","-t","7","-i",f"{tmp}/outro.png","-vf",f"fps={FPS},format=yuv420p","-c:v","libx264","-r",str(FPS),outro])

# concat silent
order=[intro]+segs+[outro]
lst=f"{tmp}/l.txt"; open(lst,"w").write("".join(f"file '{p}'\n" for p in order))
silent=f"{tmp}/silent.mp4"; run(["ffmpeg","-y","-f","concat","-safe","0","-i",lst,"-c","copy",silent])
total=dur(silent)

# VO
vo(HOOK,f"{ASS}/vo_hook.mp3"); vo(OUTRO,f"{ASS}/vo_out.mp3")
for idx,(rank,name,bbox,line) in enumerate(LOC): vo(line,f"{ASS}/vo{idx}.mp3")

# audio mix: music bed (looped) low + VOs at offsets
starts=[]; acc=6.0
for d in seg_durs: starts.append(acc); acc+=d
voins=[("amovie="+f"{ASS}/vo_hook.mp3"+f",adelay=500|500,volume=1.0")]
for idx in range(len(LOC)):
    ms=int((starts[idx]+1.0)*1000); voins.append(f"amovie={ASS}/vo{idx}.mp3,adelay={ms}|{ms},volume=1.0")
outms=int((6.0+sum(seg_durs)+0.8)*1000); voins.append(f"amovie={ASS}/vo_out.mp3,adelay={outms}|{outms},volume=1.0")
bg=f"amovie={MUSIC}:loop=0,aloop=loop=-1:size=2e9,atrim=0:{total},volume=0.18"
filt=";".join([f"{bg}[bg]"]+[f"{v}[v{i}]" for i,v in enumerate(voins)])+";"+"[bg]"+"".join(f"[v{i}]" for i in range(len(voins)))+f"amix=inputs={len(voins)+1}:normalize=0:duration=first[aout]"
final=f"{DIR}/top10_longform.mp4"
run(["ffmpeg","-y","-i",silent,"-filter_complex",filt,"-map","0:v","-map","[aout]","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",final])
print(f"LONGFORM -> {final} ({total:.1f}s)",flush=True)

# 10 shorts: each segment + its VO + music + CTA
os.makedirs(f"{DIR}/shorts",exist_ok=True)
for idx,(rank,name,bbox,line) in enumerate(LOC):
    seg=segs[idx]; sd=seg_durs[idx]
    cta=f"{tmp}/cta{idx}.png";
    im=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(im);f=ImageFont.truetype(FONT,60)
    d.text((W//2,H-470),"Follow for more 🌍",font=f,anchor="ma",fill=(255,255,255,255),stroke_width=5,stroke_fill=(0,0,0,255)); im.save(cta)
    sh=f"{DIR}/shorts/short_{rank:02d}_{name.split(',')[0].replace(' ','_')}.mp4"
    af=f"amovie={ASS}/vo{idx}.mp3,adelay=800|800,volume=1.0[vo];amovie={MUSIC}:loop=0,aloop=loop=-1:size=2e9,atrim=0:{sd},volume=0.18[m];[m][vo]amix=inputs=2:normalize=0:duration=first[a]"
    run(["ffmpeg","-y","-i",seg,"-i",cta,"-filter_complex",f"[0:v][1:v]overlay=0:0:enable='between(t,{sd-3},{sd})'[v];{af}","-map","[v]","-map","[a]","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart",sh])
    print(f"short #{rank} -> {sh}",flush=True)
print("ALL DONE",flush=True)

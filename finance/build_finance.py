#!/usr/bin/env python3
"""401k explainer — WealthDelay brand (Plus Jakarta Sans, green/forest/cream), Apple-grade, scroll-stopper hook."""
import os,urllib.request,subprocess,tempfile,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
DIR=os.path.dirname(os.path.abspath(__file__)); OUT=f"{DIR}/401k_match.mp4"
FONTF=f"{DIR}/PlusJakartaSans.ttf"
EL=open(os.path.expanduser("~/.config/elevenlabs/.env")).read().split("=",1)[1].strip()
VOICE="21m00Tcm4TlvDq8ikWAM"   # Rachel
W,H,FPS=1080,1920,30
GREEN=(22,163,74); FOREST=(5,46,22); CREAM=(239,232,216); MIST=(247,242,232)
INK=(29,29,31); LGREEN=(220,252,231); MGREEN=(134,239,172); GREY=(110,110,115); WHITE=(255,255,255); GOLD=(240,178,55)
def F(sz,w="Bold"):
    f=ImageFont.truetype(FONTF,sz)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],capture_output=True,text=True).stdout.strip())
def vo(text,path):
    b=json.dumps({"text":text,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.45,"similarity_boost":0.8,"use_speaker_boost":True}}).encode()
    r=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}",data=b,headers={"xi-api-key":EL,"Content-Type":"application/json"})
    open(path,"wb").write(urllib.request.urlopen(r,timeout=120).read())

def grad(c1,c2,diag=False):
    yy,xx=np.mgrid[0:H,0:W].astype(float)
    t=((xx/W+yy/H)/2) if diag else (yy/H)
    arr=np.zeros((H,W,3),np.uint8)
    for i in range(3): arr[...,i]=np.clip(c1[i]+(c2[i]-c1[i])*t,0,255).astype(np.uint8)
    return Image.fromarray(arr)
def hero_bg():  # rich forest->green diagonal + soft glow
    img=grad(FOREST,GREEN,diag=True)
    gl=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(gl)
    d.ellipse([W-700,-300,W+300,500],fill=(134,239,172,60)); gl=gl.filter(ImageFilter.GaussianBlur(120))
    return Image.alpha_composite(img.convert("RGBA"),gl).convert("RGB")
def soft_bg():  # white -> light green, subtle
    return grad((255,255,255),(240,253,244))
def wordmark(d,dark=False):
    f=F(38,"ExtraBold"); col=GREEN if dark else (235,255,240)
    d.text((W//2,72),"WEALTHDELAY",font=f,anchor="ma",fill=col)
def wrap(d,t,f,mw):
    out=[];cur=""
    for w in t.split():
        s=(cur+" "+w).strip()
        if d.textlength(s,font=f)<=mw:cur=s
        else:out.append(cur);cur=w
    if cur:out.append(cur);return out
def block(d,lines,f,cy,fill,lh=None):
    lh=lh or int(f.size*1.12); y=cy-lh*len(lines)//2
    for ln in lines: d.text((W//2,y),ln,font=f,anchor="ma",fill=fill);y+=lh
def shadow_card(img,box,r,fill):
    sh=Image.new("RGBA",(W,H),(0,0,0,0));ds=ImageDraw.Draw(sh)
    ds.rounded_rectangle([box[0],box[1]+12,box[2],box[3]+16],radius=r,fill=(5,46,22,70));sh=sh.filter(ImageFilter.GaussianBlur(18))
    img.paste(Image.alpha_composite(img.convert("RGBA"),sh).convert("RGB"),(0,0))
    ImageDraw.Draw(img).rounded_rectangle(box,radius=r,fill=fill)
def coin(d,cx,cy,r,label,fill,txt=WHITE):
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=fill,outline=WHITE,width=7)
    fs=int(r*1.1) if len(label)<=2 else int(r*0.78)
    d.text((cx,cy),label,font=F(fs,"ExtraBold"),anchor="mm",fill=txt)
def jar(img,cx,top,w,h,frac,label,sub=""):
    d=ImageDraw.Draw(img);x0,x1=cx-w//2,cx+w//2;y0,y1=top,top+h
    d.rounded_rectangle([x0,y0,x1,y1],radius=32,outline=INK,width=9)
    if frac>0: d.rounded_rectangle([x0+12,y1-12-int((h-28)*frac),x1-12,y1-12],radius=22,fill=GREEN)
    d.text((cx,y0-54),label,font=F(40,"ExtraBold"),anchor="ma",fill=INK)
    if sub: d.text((cx,y1+22),sub,font=F(30,"Medium"),anchor="ma",fill=GREY)
def arrow(d,x1,y1,x2,y2,color=GREEN,wd=12):
    import math;d.line([x1,y1,x2,y2],fill=color,width=wd);a=math.atan2(y2-y1,x2-x1);l=26
    d.polygon([(x2,y2),(x2-l*math.cos(a-0.5),y2-l*math.sin(a-0.5)),(x2-l*math.cos(a+0.5),y2-l*math.sin(a+0.5))],fill=color)

def s1(p):  # SCROLL-STOPPER
    img=hero_bg();d=ImageDraw.Draw(img);wordmark(d)
    # bright FREE badge
    shadow_card(img,[W//2-150,330,W//2+150,440],28,GOLD);d=ImageDraw.Draw(img)
    d.text((W//2,385),"FREE $",font=F(56,"ExtraBold"),anchor="mm",fill=FOREST)
    block(d,wrap(d,"Your boss owes you money.",F(96,"ExtraBold"),W-130),F(96,"ExtraBold"),830,WHITE)
    block(d,wrap(d,"And you're saying no to it.",F(60,"Bold"),W-160),F(60,"Bold"),1150,MGREEN)
    img.save(p)
def s2(p):
    img=soft_bg();d=ImageDraw.Draw(img);wordmark(d,dark=True)
    d.text((W//2,260),"Here's how it works",font=F(62,"ExtraBold"),anchor="ma",fill=INK)
    d.polygon([(W//2-26,352),(W//2+26,352),(W//2,388)],fill=GREEN)
    shadow_card(img,[W//2-160,460,W//2+160,590],26,GREEN);d=ImageDraw.Draw(img)
    d.text((W//2,525),"EMPLOYER",font=F(40,"ExtraBold"),anchor="mm",fill=WHITE)
    arrow(d,W//2,620,W//2,740,GREEN)
    jar(img,W//2,790,300,420,0.78,"YOUR 401(k)");d=ImageDraw.Draw(img)
    shadow_card(img,[120,890,360,1010],22,WHITE);d=ImageDraw.Draw(img)
    d.text((240,950),"PAYCHECK",font=F(34,"ExtraBold"),anchor="mm",fill=INK)
    arrow(d,370,950,W//2-160,980,(120,170,140))
    block(d,wrap(d,"Many employers add money on top — automatically.",F(48,"Bold"),W-150),F(48,"Bold"),1480,INK)
    img.save(p)
def s3(p):
    img=soft_bg();d=ImageDraw.Draw(img);wordmark(d,dark=True)
    d.text((W//2,400),"A common match:",font=F(60,"ExtraBold"),anchor="ma",fill=INK)
    coin(d,W//2-220,730,95,"$1",GREEN); d.text((W//2,730),"+",font=F(90,"ExtraBold"),anchor="mm",fill=INK)
    coin(d,W//2+210,730,82,"50¢",FOREST)
    d.text((W//2,910),"for every dollar you contribute",font=F(44,"Medium"),anchor="ma",fill=GREY)
    block(d,wrap(d,"…up to a limit. Varies by company — check your plan.",F(46,"Bold"),W-160),F(46,"Bold"),1320,INK)
    img.save(p)
def s4(p):
    img=soft_bg();d=ImageDraw.Draw(img);wordmark(d,dark=True)
    d.text((W//2,360),"The difference:",font=F(60,"ExtraBold"),anchor="ma",fill=INK)
    jar(img,300,560,300,440,0.0,"$0 IN","$0 match")
    jar(img,780,560,300,440,0.85,"YOU PUT IN","employer adds more")
    d=ImageDraw.Draw(img)
    block(d,wrap(d,"Skip the match and you turn down part of your pay.",F(50,"ExtraBold"),W-150),F(50,"ExtraBold"),1320,GREEN)
    img.save(p)
def s5(p):
    img=hero_bg();d=ImageDraw.Draw(img);wordmark(d)
    coin(d,W//2,500,100,"%",WHITE,txt=GREEN)
    block(d,["Check your plan.","Find your match %."],F(80,"ExtraBold"),880,WHITE)
    shadow_card(img,[W//2-410,1140,W//2+410,1280],40,WHITE);d=ImageDraw.Draw(img)
    d.text((W//2,1210),"Free calculator → wealthdelay.com",font=F(44,"ExtraBold"),anchor="mm",fill=GREEN)
    img.save(p)

SCENES=[
 (s1,"If your job offers a four-oh-one-k match, and you're not using it... you're leaving free money on the table."),
 (s2,"When you put money into your four-oh-one-k, many employers add more money on top, automatically. It's part of your compensation, not a bonus."),
 (s3,"A common setup: your employer matches fifty cents for every dollar you put in, up to a certain percent of your paycheck. The exact match varies by company, so check your plan documents."),
 (s4,"If you're not contributing at least enough to get the full match, you're literally turning down part of your pay."),
 (s5,"Want to see how this adds up over time? Free calculator on wealthdelay dot com."),
]
DISCLAIMER="Source: U.S. Department of Labor. General info, not financial advice — check your plan administrator for your specific match."

def main():
    tmp=tempfile.mkdtemp(prefix="fin_"); clips=[]
    for i,(draw,line) in enumerate(SCENES):
        png=f"{tmp}/s{i}.png"; draw(png)
        m=f"{tmp}/v{i}.mp3"; vo(line,m); wv=f"{tmp}/v{i}.wav"; run(["ffmpeg","-y","-i",m,"-ar","44100","-ac","1","-af","atempo=1.13",wv])
        d=dur(wv)+0.15; frames=int(d*FPS)
        zc=f"{tmp}/z{i}.mp4"
        run(["ffmpeg","-y","-loop","1","-i",png,"-vf",
             f"scale=1620:2880,zoompan=z='min(zoom+0.0009,1.09)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},format=yuv420p",
             "-frames:v",str(frames),"-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-r",str(FPS),zc])
        clip=f"{tmp}/c{i}.mp4"; run(["ffmpeg","-y","-i",zc,"-i",wv,"-c:v","copy","-c:a","aac","-b:a","192k","-shortest",clip]); clips.append(clip)
    lst=f"{tmp}/l.txt"; open(lst,"w").write("".join(f"file '{c}'\n" for c in clips))
    base_v=f"{tmp}/base.mp4"; run(["ffmpeg","-y","-f","concat","-safe","0","-i",lst,"-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac",base_v])
    dl=Image.new("RGBA",(W,H),(0,0,0,0));dd=ImageDraw.Draw(dl);f=F(28,"Medium")
    lines=wrap(dd,DISCLAIMER,f,W-120);dd.rectangle([0,H-330,W,H-150],fill=(255,255,255,225));y=H-312
    for ln in lines: dd.text((W//2,y),ln,font=f,anchor="ma",fill=INK);y+=40
    dlp=f"{tmp}/dl.png";dl.save(dlp)
    vdur=dur(base_v); bar=f"drawbox=x=0:y={H-14}:w='iw*t/{vdur:.2f}':h=14:color=0x16A34A@1.0:t=fill:enable=1"
    run(["ffmpeg","-y","-i",base_v,"-i",dlp,"-filter_complex",f"[0:v][1:v]overlay=0:0:enable='gte(t,{vdur-3:.2f})'[d];[d]{bar}[v]","-map","[v]","-map","0:a","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart",OUT])
    print(f"DONE -> {OUT} ({dur(OUT):.1f}s)",flush=True); shutil.rmtree(tmp,ignore_errors=True)
main()

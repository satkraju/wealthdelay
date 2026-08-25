#!/usr/bin/env python3
"""Compound-interest comparison/prediction short — WealthDelay brand. Guess->reveal: two savers, same $/mo, one starts 10yrs earlier.
Numbers computed live (7% annual, monthly compounding) so they are never invented. Reveal funnels to wealthdelay.com calculator."""
import os,urllib.request,subprocess,tempfile,json,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
DIR=os.path.dirname(os.path.abspath(__file__)); OUT=f"{DIR}/compound_gap.mp4"
FONTF=f"{DIR}/PlusJakartaSans.ttf"
EL=open(os.path.expanduser("~/.config/elevenlabs/.env")).read().split("=",1)[1].strip()
VOICE="nPczCjzI2devNBz1zQrb"   # Brian — confident conversational male (DEFAULT). Ed alt: 3IwIPyXc0WRkgKBE8KXP
W,H,FPS=1080,1920,30
GREEN=(22,163,74); FOREST=(5,46,22); CREAM=(239,232,216); MIST=(247,242,232)
INK=(29,29,31); LGREEN=(220,252,231); MGREEN=(134,239,172); GREY=(110,110,115); WHITE=(255,255,255); GOLD=(240,178,55)

# ---- live math (never hardcode a finance number) ----
MONTHLY=200; ANNUAL=0.07
def fv(p,annual,years):
    r=annual/12; n=years*12
    return p*(((1+r)**n-1)/r)
EMMA=fv(MONTHLY,ANNUAL,40); LIAM=fv(MONTHLY,ANNUAL,30)   # start 25 vs 35, both to 65
EMMA_IN=MONTHLY*12*40; LIAM_IN=MONTHLY*12*30
GAP=EMMA-LIAM; EXTRA_IN=EMMA_IN-LIAM_IN
def k(n): return f"${round(n/1000)}k"

def F(sz,w="Bold"):
    f=ImageFont.truetype(FONTF,sz)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],capture_output=True,text=True).stdout.strip())
def vo(text,path):
    b=json.dumps({"text":text,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.35,"similarity_boost":0.85,"style":0.45,"use_speaker_boost":True}}).encode()
    r=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}",data=b,headers={"xi-api-key":EL,"Content-Type":"application/json"})
    open(path,"wb").write(urllib.request.urlopen(r,timeout=120).read())
def grad(c1,c2,diag=False):
    yy,xx=np.mgrid[0:H,0:W].astype(float)
    t=((xx/W+yy/H)/2) if diag else (yy/H)
    arr=np.zeros((H,W,3),np.uint8)
    for i in range(3): arr[...,i]=np.clip(c1[i]+(c2[i]-c1[i])*t,0,255).astype(np.uint8)
    return Image.fromarray(arr)
def hero_bg():
    img=grad(FOREST,GREEN,diag=True)
    gl=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(gl)
    d.ellipse([W-700,-300,W+300,500],fill=(134,239,172,60)); gl=gl.filter(ImageFilter.GaussianBlur(120))
    return Image.alpha_composite(img.convert("RGBA"),gl).convert("RGB")
def soft_bg(): return grad((255,255,255),(240,253,244))
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
def avatar(img,cx,cy,r,fill,age):  # simple flat person token + age tag
    d=ImageDraw.Draw(img)
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=fill,outline=WHITE,width=8)
    d.ellipse([cx-r*0.34,cy-r*0.42,cx+r*0.34,cy+r*0.24],fill=WHITE)        # head
    d.pieslice([cx-r*0.6,cy+r*0.05,cx+r*0.6,cy+r*1.05],180,360,fill=WHITE) # shoulders
    d.text((cx,cy+r+44),age,font=F(40,"ExtraBold"),anchor="ma",fill=INK)
def bar(img,cx,base_y,w,h_full,frac,fill,top_label,sub):
    d=ImageDraw.Draw(img);x0,x1=cx-w//2,cx+w//2
    h=int(h_full*frac); y0=base_y-h
    shadow_card(img,[x0,y0,x1,base_y],26,fill);d=ImageDraw.Draw(img)
    d.text((cx,y0-58),top_label,font=F(58,"ExtraBold"),anchor="ma",fill=INK)
    d.text((cx,base_y+18),sub,font=F(34,"Bold"),anchor="ma",fill=GREY)

def s1(p):  # SCROLL-STOPPER: prediction gap
    img=hero_bg();d=ImageDraw.Draw(img);wordmark(d)
    block(d,wrap(d,"Two people. Same $200 a month.",F(82,"ExtraBold"),W-130),F(82,"ExtraBold"),720,WHITE)
    block(d,wrap(d,"One ends up with DOUBLE.",F(78,"ExtraBold"),W-150),F(78,"ExtraBold"),1000,GOLD)
    block(d,wrap(d,"Can you guess why?",F(58,"Bold"),W-160),F(58,"Bold"),1230,MGREEN)
    img.save(p)
def s2(p):  # meet the two
    img=soft_bg();d=ImageDraw.Draw(img);wordmark(d,dark=True)
    d.text((W//2,250),"Same $200/month. Same 7% return.",font=F(46,"ExtraBold"),anchor="ma",fill=INK)
    avatar(img,300,720,150,GREEN,"starts at 25")
    avatar(img,780,720,150,FOREST,"starts at 35")
    d=ImageDraw.Draw(img)
    d.text((300,470),"EMMA",font=F(52,"ExtraBold"),anchor="ma",fill=INK)
    d.text((780,470),"LIAM",font=F(52,"ExtraBold"),anchor="ma",fill=INK)
    block(d,wrap(d,"Both invest until 65. The only difference: when they started.",F(46,"Bold"),W-150),F(46,"Bold"),1180,INK)
    img.save(p)
def s3(p):  # build tension, ask to predict
    img=soft_bg();d=ImageDraw.Draw(img);wordmark(d,dark=True)
    block(d,["Emma started just","10 years earlier."],F(78,"ExtraBold"),560,INK)
    shadow_card(img,[W//2-300,760,W//2+300,900],30,LGREEN);d=ImageDraw.Draw(img)
    d.text((W//2,830),"+10 years",font=F(64,"ExtraBold"),anchor="mm",fill=GREEN)
    block(d,wrap(d,"How big is the gap at 65? Take a guess…",F(52,"Bold"),W-150),F(52,"Bold"),1150,INK)
    img.save(p)
def s4(p):  # REVEAL — bars + numbers
    img=soft_bg();d=ImageDraw.Draw(img);wordmark(d,dark=True)
    d.text((W//2,250),"At age 65:",font=F(62,"ExtraBold"),anchor="ma",fill=INK)
    base=1340; full=820
    bar(img,310,base,300,full,1.0,GREEN,k(EMMA),"Emma · started 25")
    bar(img,780,base,300,full,LIAM/EMMA,FOREST,k(LIAM),"Liam · started 35")
    img.save(p)
def s5(p):  # twist + CTA
    img=hero_bg();d=ImageDraw.Draw(img);wordmark(d)
    block(d,wrap(d,f"Emma put in just {k(EXTRA_IN)} more…",F(60,"ExtraBold"),W-150),F(60,"ExtraBold"),560,WHITE)
    block(d,wrap(d,f"…and ended with {k(GAP)} more.",F(66,"ExtraBold"),W-150),F(66,"ExtraBold"),760,GOLD)
    block(d,["Time did the rest."],F(58,"Bold"),960,MGREEN)
    shadow_card(img,[W//2-450,1160,W//2+450,1360],40,WHITE);d=ImageDraw.Draw(img)
    d.text((W//2,1218),"Free calculator — link below",font=F(46,"ExtraBold"),anchor="mm",fill=GREEN)
    d.text((W//2,1300),"wealthdelay.com",font=F(40,"Bold"),anchor="mm",fill=INK)
    d.polygon([(W//2-26,1420),(W//2+26,1420),(W//2,1462)],fill=GREEN)
    img.save(p)

mE,mL,mG,mI=k(EMMA),k(LIAM),k(GAP),k(EXTRA_IN)
SCENES=[
 (s1,"Two people invest the same two hundred dollars a month. One ends up with nearly double the other. Can you guess why?"),
 (s2,"Meet Emma and Liam. Same two hundred a month, same seven percent return, both stop at sixty-five. The only difference is when they started."),
 (s3,"Emma started just ten years earlier, at twenty-five. Liam waited until thirty-five. Before I show you the gap... take a guess how big it is."),
 (s4,f"At sixty-five, Emma has about {mE.replace('$','').replace('k',' thousand dollars')}. Liam, about {mL.replace('$','').replace('k',' thousand dollars')}. Almost double, for the same monthly amount."),
 (s5,f"Here's the twist. Emma only put in about {mI.replace('$','').replace('k',' thousand dollars')} more than Liam... but she ended up with around {mG.replace('$','').replace('k',' thousand dollars')} more. That's compounding. Want to run your own numbers? There's a free calculator on wealthdelay dot com. Link's right below."),
]
DISCLAIMER="Hypothetical example: $200/month at a 7% average annual return, compounded monthly. Not a guarantee or financial advice. Real returns vary."

def main():
    tmp=tempfile.mkdtemp(prefix="cmp_"); clips=[]
    for i,(draw,line) in enumerate(SCENES):
        png=f"{tmp}/s{i}.png"; draw(png)
        m=f"{tmp}/v{i}.mp3"; vo(line,m); wv=f"{tmp}/v{i}.wav"; run(["ffmpeg","-y","-i",m,"-ar","44100","-ac","1","-af","atempo=1.18",wv])
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
    print(f"DONE -> {OUT} ({dur(OUT):.1f}s)  Emma={mE} Liam={mL} gap={mG}",flush=True); shutil.rmtree(tmp,ignore_errors=True)
main()

#!/usr/bin/env python3
"""WealthDelay batch renderer — data-driven comparison/reveal Shorts from ideas.json.
Same proven engine as build_compound.py, parameterized. Numbers come pre-verified in ideas.json.

  python3 build_batch.py <id>        # render one idea -> out/<id>.mp4 (+ <id>.txt description)
  python3 build_batch.py --all       # render every idea
  python3 build_batch.py --list      # list ids
"""
import os,sys,json,urllib.request,subprocess,tempfile,shutil
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
DIR=os.path.dirname(os.path.abspath(__file__)); OUTDIR=f"{DIR}/out"; os.makedirs(OUTDIR,exist_ok=True)
FONTF=f"{DIR}/PlusJakartaSans.ttf"
VOICE="en-US-BrianNeural"   # default edge-tts Brian — confident, free, unlimited (the daily workhorse)
RATE="+25%"
# Optional ElevenLabs voices for occasional "hero" videos (set "voice":"ed" in ideas.json). Quota-limited.
EL_VOICES={"ed":"3IwIPyXc0WRkgKBE8KXP","brian":"nPczCjzI2devNBz1zQrb","bill":"pqHfZKP75CvOlQylNhV4"}
def _el_key():
    try: return open(os.path.expanduser("~/.config/elevenlabs/.env")).read().split("=",1)[1].strip()
    except Exception: return None
W,H,FPS=1080,1920,30
GREEN=(22,163,74); GREEN_D=(21,128,61); FOREST=(5,46,22); INK=(39,39,42); MUTE=(82,82,91)
MGREEN=(134,239,172); GREY=(120,120,128); WHITE=(255,255,255); GOLD=(240,178,55); RED=(220,38,38)
LGREEN=(220,252,231); CREAM=(253,250,245); CREAM2=(247,242,232); TINT=(220,252,231)
def F(sz,w="Bold"):
    f=ImageFont.truetype(FONTF,sz)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
def run(c): subprocess.run(c,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],capture_output=True,text=True).stdout.strip())
def vo(text,path,voice=None):
    """voice=None -> free edge-tts Brian. voice in EL_VOICES (e.g. 'ed') -> ElevenLabs (quota-limited)."""
    if voice and voice in EL_VOICES:
        key=_el_key()
        if not key: sys.exit("ElevenLabs key missing; can't use voice '%s'."%voice)
        b=json.dumps({"text":text,"model_id":"eleven_multilingual_v2","voice_settings":{"stability":0.4,"similarity_boost":0.8,"style":0.4,"use_speaker_boost":True}}).encode()
        r=urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{EL_VOICES[voice]}",data=b,headers={"xi-api-key":key,"Content-Type":"application/json"})
        try:
            open(path,"wb").write(urllib.request.urlopen(r,timeout=120).read())
        except urllib.error.HTTPError as ex:
            sys.exit(f"ElevenLabs voice '{voice}' failed ({ex.code}): {ex.read().decode()[:200]}\n(quota likely exhausted — drop the \"voice\" flag to use free edge-tts.)")
        return
    run(["edge-tts","--voice",VOICE,"--rate",RATE,"--text",text,"--write-media",path])
def grad(c1,c2,diag=False):
    yy,xx=np.mgrid[0:H,0:W].astype(float); t=((xx/W+yy/H)/2) if diag else (yy/H)
    arr=np.zeros((H,W,3),np.uint8)
    for i in range(3): arr[...,i]=np.clip(c1[i]+(c2[i]-c1[i])*t,0,255).astype(np.uint8)
    return Image.fromarray(arr)
def cream_bg():   # Apple-clean warm cream + subtle green corner glow (matches banner/profile)
    img=grad(CREAM,CREAM2,diag=True).convert("RGBA")
    gl=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(gl)
    d.ellipse([W-620,-360,W+260,460],fill=(*TINT,150)); d.ellipse([-300,H-520,420,H+240],fill=(*TINT,110))
    gl=gl.filter(ImageFilter.GaussianBlur(170)); return Image.alpha_composite(img,gl).convert("RGB")
_WM=None
def _wordmark_img():   # 'Wealth' italic green + 'Delay' ink, baseline-aligned (same as channel art)
    global _WM
    if _WM: return _WM
    fsz=120; fw=F(fsz,"ExtraBold"); CW=2200; CH=int(fsz*4); base=int(CH*0.70); sh=0.20
    main=Image.new("RGBA",(CW,CH),(0,0,0,0))
    lw=Image.new("RGBA",(CW,CH),(0,0,0,0)); ImageDraw.Draw(lw).text((120,base),"Wealth",font=fw,fill=GREEN,anchor="ls")
    lw=lw.transform((CW,CH),Image.AFFINE,(1,sh,-sh*base,0,1,0),resample=Image.BICUBIC); main.alpha_composite(lw)
    rb=lw.getbbox(); ImageDraw.Draw(main).text((rb[2]+6,base),"Delay",font=F(fsz,"ExtraBold"),fill=INK,anchor="ls")
    _WM=main.crop(main.getbbox()); return _WM
def wordmark(img,y=46,h=52):   # paste centered wordmark at top
    wm=_wordmark_img(); w=int(wm.width*h/wm.height); wm=wm.resize((w,h),Image.LANCZOS)
    img.paste(wm,(W//2-w//2,y),wm)
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
def avatar(img,cx,cy,r,fill,sub):
    d=ImageDraw.Draw(img); d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=fill,outline=WHITE,width=8)
    d.ellipse([cx-r*0.34,cy-r*0.42,cx+r*0.34,cy+r*0.24],fill=WHITE)
    d.pieslice([cx-r*0.6,cy+r*0.05,cx+r*0.6,cy+r*1.05],180,360,fill=WHITE)
    for i,ln in enumerate(wrap(d,sub,F(34,"Bold"),360)): d.text((cx,cy+r+30+i*40),ln,font=F(34,"Bold"),anchor="ma",fill=INK)
def bar(img,cx,base_y,w,h_full,frac,fill,top_label,sub):
    d=ImageDraw.Draw(img);x0,x1=cx-w//2,cx+w//2; h=int(h_full*max(0.08,frac)); y0=base_y-h
    shadow_card(img,[x0,y0,x1,base_y],26,fill);d=ImageDraw.Draw(img)
    d.text((cx,y0-58),top_label,font=F(58,"ExtraBold"),anchor="ma",fill=INK)
    subf=F(30,"Bold"); y=base_y+18
    for ln in wrap(d,sub,subf,420): d.text((cx,y),ln,font=subf,anchor="ma",fill=GREY); y+=38

def render(e):
    S=e["scenes"]; AC=RED if e.get("accent")=="red" else GREEN   # accent legible on cream
    def s1(p):
        img=cream_bg();d=ImageDraw.Draw(img);wordmark(img)
        block(d,wrap(d,S["hook"]["big"],F(82,"ExtraBold"),W-130),F(82,"ExtraBold"),700,INK)
        block(d,wrap(d,S["hook"]["accent"],F(76,"ExtraBold"),W-150),F(76,"ExtraBold"),1000,AC)
        block(d,wrap(d,S["hook"]["sub"],F(54,"Bold"),W-160),F(54,"Bold"),1240,GREEN_D);img.save(p)
    def s2(p):
        img=cream_bg();d=ImageDraw.Draw(img);wordmark(img)
        for i,ln in enumerate(wrap(d,S["setup"]["title"],F(46,"ExtraBold"),W-150)): d.text((W//2,250+i*56),ln,font=F(46,"ExtraBold"),anchor="ma",fill=INK)
        avatar(img,300,760,150,GREEN,S["setup"]["a"]["sub"]); avatar(img,780,760,150,FOREST,S["setup"]["b"]["sub"]);d=ImageDraw.Draw(img)
        d.text((300,510),S["setup"]["a"]["label"],font=F(50,"ExtraBold"),anchor="ma",fill=INK)
        d.text((780,510),S["setup"]["b"]["label"],font=F(50,"ExtraBold"),anchor="ma",fill=INK)
        block(d,wrap(d,S["setup"]["foot"],F(44,"Bold"),W-150),F(44,"Bold"),1200,MUTE);img.save(p)
    def s3(p):
        img=cream_bg();d=ImageDraw.Draw(img);wordmark(img)
        bf=F(74,"ExtraBold"); raw=S["tension"]["big"]; raw=raw if isinstance(raw,list) else [raw]
        big_lines=[ln2 for ln in raw for ln2 in wrap(d,ln,bf,W-150)]
        block(d,big_lines,bf,560,INK)
        shadow_card(img,[W//2-300,760,W//2+300,900],30,LGREEN);d=ImageDraw.Draw(img)
        d.text((W//2,830),S["tension"]["pill"],font=F(60,"ExtraBold"),anchor="mm",fill=GREEN_D)
        block(d,wrap(d,S["tension"]["ask"],F(50,"Bold"),W-150),F(50,"Bold"),1150,MUTE);img.save(p)
    def s4(p):
        img=cream_bg();d=ImageDraw.Draw(img);wordmark(img)
        block(d,wrap(d,S["reveal"]["head"],F(54,"ExtraBold"),W-150),F(54,"ExtraBold"),270,INK)
        a,b=S["reveal"]["a"],S["reveal"]["b"]; mx=max(a["val"],b["val"]); base=1340;full=820
        bar(img,310,base,300,full,a["val"]/mx,GREEN,a["valt"],f'{a["label"]} · {a["sub"]}')
        bar(img,780,base,300,full,b["val"]/mx,FOREST,b["valt"],f'{b["label"]} · {b["sub"]}');img.save(p)
    def s5(p):
        img=cream_bg();d=ImageDraw.Draw(img);wordmark(img)
        l1_lines=wrap(d,S["twist"]["l1"],F(56,"ExtraBold"),W-150)
        l2_lines=wrap(d,S["twist"]["l2"],F(62,"ExtraBold"),W-150)
        l3_lines=wrap(d,S["twist"]["l3"],F(44,"Bold"),W-160)
        lh1=int(56*1.15);lh2=int(62*1.15);lh3=int(44*1.18)
        y=380
        for ln in l1_lines: d.text((W//2,y),ln,font=F(56,"ExtraBold"),anchor="ma",fill=INK);y+=lh1
        y+=28
        for ln in l2_lines: d.text((W//2,y),ln,font=F(62,"ExtraBold"),anchor="ma",fill=AC);y+=lh2
        y+=36
        for ln in l3_lines: d.text((W//2,y),ln,font=F(44,"Bold"),anchor="ma",fill=GREEN_D);y+=lh3
        shadow_card(img,[W//2-450,1160,W//2+450,1360],40,GREEN);d=ImageDraw.Draw(img)
        d.text((W//2,1218),"Free calculator — link below",font=F(46,"ExtraBold"),anchor="mm",fill=WHITE)
        d.text((W//2,1300),"wealthdelay.com",font=F(40,"Bold"),anchor="mm",fill=LGREEN)
        d.polygon([(W//2-26,1430),(W//2+26,1430),(W//2,1472)],fill=GREEN);img.save(p)
    SCENES=[(s1,e["vo"]["hook"]),(s2,e["vo"]["setup"]),(s3,e["vo"]["tension"]),(s4,e["vo"]["reveal"]),(s5,e["vo"]["twist"])]
    OUT=f"{OUTDIR}/{e['id']}.mp4"; tmp=tempfile.mkdtemp(prefix=f"b_{e['id']}_"); clips=[]
    for i,(draw,line) in enumerate(SCENES):
        png=f"{tmp}/s{i}.png"; draw(png)
        m=f"{tmp}/v{i}.mp3"; vo(line,m,e.get("voice")); wv=f"{tmp}/v{i}.wav"
        af=["-af","atempo=1.12"] if e.get("voice") in EL_VOICES else []   # EL voices need speed-up; edge uses RATE
        run(["ffmpeg","-y","-i",m,"-ar","44100","-ac","1",*af,wv])
        d=dur(wv)+0.15; frames=int(d*FPS); zc=f"{tmp}/z{i}.mp4"
        run(["ffmpeg","-y","-loop","1","-i",png,"-vf",
             f"scale=1620:2880,zoompan=z='min(zoom+0.0009,1.09)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},format=yuv420p",
             "-frames:v",str(frames),"-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-r",str(FPS),zc])
        clip=f"{tmp}/c{i}.mp4"; run(["ffmpeg","-y","-i",zc,"-i",wv,"-c:v","copy","-c:a","aac","-b:a","192k","-shortest",clip]);clips.append(clip)
    lst=f"{tmp}/l.txt"; open(lst,"w").write("".join(f"file '{c}'\n" for c in clips))
    base_v=f"{tmp}/base.mp4"; run(["ffmpeg","-y","-f","concat","-safe","0","-i",lst,"-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac",base_v])
    dl=Image.new("RGBA",(W,H),(0,0,0,0));dd=ImageDraw.Draw(dl);f=F(28,"Medium")
    lines=wrap(dd,e["disclaimer"],f,W-120);dd.rectangle([0,H-330,W,H-150],fill=(255,255,255,225));y=H-312
    for ln in lines: dd.text((W//2,y),ln,font=f,anchor="ma",fill=INK);y+=40
    dlp=f"{tmp}/dl.png";dl.save(dlp)
    vdur=dur(base_v); barfx=f"drawbox=x=0:y={H-14}:w='iw*t/{vdur:.2f}':h=14:color=0x16A34A@1.0:t=fill:enable=1"
    run(["ffmpeg","-y","-i",base_v,"-i",dlp,"-filter_complex",f"[0:v][1:v]overlay=0:0:enable='gte(t,{vdur-3:.2f})'[d];[d]{barfx}[v]","-map","[v]","-map","0:a","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-movflags","+faststart",OUT])
    desc=(f"{S['hook']['big']} {S['hook']['accent']}\n\n👉 Run your own numbers (free): {e['tool_url']}\n\n{e['disclaimer']}\n\n"
          +" ".join(f"#{t.replace(' ','')}" for t in e["tags"])+" #Shorts")
    open(f"{OUTDIR}/{e['id']}.txt","w").write(desc)
    print(f"DONE -> {OUT} ({dur(OUT):.1f}s)",flush=True); shutil.rmtree(tmp,ignore_errors=True); return OUT

if __name__=="__main__":
    ideas_file="ideas.json"
    if "--ideas-file" in sys.argv:
        ideas_file=sys.argv[sys.argv.index("--ideas-file")+1]
    ideas=json.load(open(f"{DIR}/{ideas_file}")); byid={e["id"]:e for e in ideas}
    a=sys.argv[1] if len(sys.argv)>1 else ""
    if a=="--list": [print(e["id"],"—",e["title"]) for e in ideas]
    elif a=="--all": [render(e) for e in ideas]
    elif a in byid: render(byid[a])
    else: sys.exit("usage: build_batch.py <id> | --all | --list [--ideas-file FILE]")

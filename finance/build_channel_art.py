#!/usr/bin/env python3
"""WealthDelay YouTube channel art — matched to the live wealthdelay.com site (light warm-cream, green accent,
'Wealth' italic wordmark, zinc ink). Apple-clean: generous whitespace, one focal point, restrained.
Outputs banner (2560x1440, safe-area aware) + profile pic (800x800)."""
import os
import numpy as np
from PIL import Image,ImageDraw,ImageFont
DIR=os.path.dirname(os.path.abspath(__file__)); FONTF=f"{DIR}/PlusJakartaSans.ttf"
# --- exact site palette ---
CREAM=(253,250,245); CREAM2=(247,242,232); GREEN=(22,163,74); GREEN_D=(21,128,61)
TINT=(220,252,231); INK=(39,39,42); MUTE=(82,82,91); WHITE=(255,255,255)
def F(sz,w="Bold"):
    f=ImageFont.truetype(FONTF,sz)
    try: f.set_variation_by_name(w)
    except Exception: pass
    return f
def grad(W,H,c1,c2,vert=True):
    yy,xx=np.mgrid[0:H,0:W].astype(float); t=(yy/H) if vert else (xx/W)
    arr=np.zeros((H,W,3),np.uint8)
    for i in range(3): arr[...,i]=np.clip(c1[i]+(c2[i]-c1[i])*t,0,255).astype(np.uint8)
    return Image.fromarray(arr)
def wordmark(scale):
    """'Wealth' italic green + 'Delay' upright ink — drawn on ONE shared baseline so they align.
    Italic is faked by shearing only the Wealth layer; shear keeps the baseline fixed (no shift at y=base)."""
    fsz=int(150*scale); fw=F(fsz,"ExtraBold"); fd=F(fsz,"ExtraBold")
    CW=3200; CH=int(fsz*4); base=int(CH*0.70); sh=0.20
    main=Image.new("RGBA",(CW,CH),(0,0,0,0))
    # Wealth (italic): render on own layer at shared baseline, then shear about the baseline
    lw=Image.new("RGBA",(CW,CH),(0,0,0,0))
    ImageDraw.Draw(lw).text((150,base),"Wealth",font=fw,fill=GREEN,anchor="ls")
    lw=lw.transform((CW,CH),Image.AFFINE,(1,sh,-sh*base,0,1,0),resample=Image.BICUBIC)
    main.alpha_composite(lw)
    rb=lw.getbbox(); gx=rb[2]+int(8*scale)         # place Delay right after sheared Wealth
    ImageDraw.Draw(main).text((gx,base),"Delay",font=fd,fill=INK,anchor="ls")
    return main.crop(main.getbbox())

# ---------- BANNER 2560x1440 (safe text area ~1235x338 centered) ----------
W,Ht=2560,1440
img=grad(W,Ht,CREAM,CREAM2).convert("RGBA")
# soft green corner glow
gl=Image.new("RGBA",(W,Ht),(0,0,0,0)); dg=ImageDraw.Draw(gl)
dg.ellipse([W-1000,-450,W+250,650],fill=(*TINT,150)); dg.ellipse([-350,Ht-450,450,Ht+250],fill=(*TINT,110))
from PIL import ImageFilter; gl=gl.filter(ImageFilter.GaussianBlur(200)); img=Image.alpha_composite(img,gl)
d=ImageDraw.Draw(img); cx,cy=W//2,Ht//2
wm=wordmark(1.0); img.alpha_composite(wm,(cx-wm.width//2,cy-185))
d.text((cx,cy+25),"Money, explained in under a minute.",font=F(54,"Medium"),anchor="mm",fill=MUTE)
# restrained solid-green pill — auto-sized to text (kept inside TV-safe area, bottom < 931px)
pill_f=F(42,"Bold"); pill_t="30+ free calculators  ·  wealthdelay.com"
tw=d.textlength(pill_t,font=pill_f); ph=92; pw=int(tw)+96
px0,py0=cx-pw//2,cy+105
d.rounded_rectangle([px0,py0,px0+pw,py0+ph],radius=ph//2,fill=GREEN)
d.text((cx,py0+ph//2),pill_t,font=pill_f,anchor="mm",fill=WHITE)
img.convert("RGB").save(f"{DIR}/yt_banner.png")

# ---------- PROFILE 800x800 (renders as circle) ----------
S=800; p=grad(S,S,CREAM,CREAM2).convert("RGBA"); dp=ImageDraw.Draw(p)
dp.ellipse([34,34,S-34,S-34],outline=GREEN,width=12)
wm2=wordmark(1.7)
# scale wordmark to fit within circle width
maxw=S-220
if wm2.width>maxw: wm2=wm2.resize((maxw,int(wm2.height*maxw/wm2.width)),Image.LANCZOS)
p.alpha_composite(wm2,(S//2-wm2.width//2,S//2-wm2.height//2))
p.convert("RGB").save(f"{DIR}/yt_profile.png")
print("DONE -> yt_banner.png + yt_profile.png (site-matched: cream/green, italic Wealth)")

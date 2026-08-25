#!/usr/bin/env python3
"""
WealthDelay HAL-style Long-form renderer
Dark aesthetic · split panel · progress blades · running total
Horizontal 1920×1080

Usage:
  python3 build_hal_long.py <json_file>
  python3 build_hal_long.py rent_vs_buy_hal.json
"""
import os, sys, json, subprocess, tempfile, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

DIR = os.path.dirname(os.path.abspath(__file__))
OUTDIR = f"{DIR}/out"; os.makedirs(OUTDIR, exist_ok=True)
FONTF = f"{DIR}/PlusJakartaSans.ttf"
VOICE = "en-US-BrianNeural"
RATE = "+20%"   # slightly slower for long-form comprehension
W, H, FPS = 1920, 1080, 30
LP = 820   # left panel right edge (content width)
RP = 880   # right panel left edge

# HAL dark palette
BG      = (5, 12, 7)
WHITE   = (255, 255, 255)
GREY    = (130, 145, 134)
DIM     = (70, 85, 73)
YELLOW  = (245, 197, 24)
CYAN    = (0, 210, 170)
GREEN   = (22, 163, 74)
LGREEN  = (134, 239, 172)
DGREEN  = (5, 46, 22)
MGREEN  = (10, 80, 35)
GRID    = (11, 20, 14)
RED_NEG = (239, 68, 68)
SPLIT   = (18, 38, 24)   # divider between panels

def F(sz, w="Bold"):
    f = ImageFont.truetype(FONTF, sz)
    try: f.set_variation_by_name(w)
    except: pass
    return f

def run(c): subprocess.run(c, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.run(
    ["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],
    capture_output=True,text=True).stdout.strip())

def vo_tts(text, path):
    run(["edge-tts","--voice",VOICE,"--rate",RATE,"--text",text,"--write-media",path])

def dark_bg():
    arr = np.zeros((H, W, 3), np.uint8)
    for y in range(H):
        t = y / H
        arr[y,:,0] = int(BG[0]+3*(1-t))
        arr[y,:,1] = int(BG[1]+9*(1-t))
        arr[y,:,2] = int(BG[2]+4*(1-t))
    img = Image.fromarray(arr).convert("RGBA")
    gi = Image.new("RGBA",(W,H),(0,0,0,0))
    dg = ImageDraw.Draw(gi)
    for x in range(0,W,90): dg.line([(x,0),(x,H)],fill=(*GRID,140),width=1)
    for y in range(0,H,90): dg.line([(0,y),(W,y)],fill=(*GRID,140),width=1)
    img = Image.alpha_composite(img,gi)
    gl = Image.new("RGBA",(W,H),(0,0,0,0))
    dgl = ImageDraw.Draw(gl)
    dgl.ellipse([-200,-200,600,600],fill=(0,70,25,32))
    dgl.ellipse([W-600,H-600,W+200,H+200],fill=(0,50,18,22))
    gl = gl.filter(ImageFilter.GaussianBlur(160))
    return Image.alpha_composite(img,gl).convert("RGB")

def wrap(d, t, f, mw):
    out=[]; cur=""
    for word in t.split():
        s=(cur+" "+word).strip()
        if d.textlength(s,font=f)<=mw: cur=s
        else: out.append(cur); cur=word
    if cur: out.append(cur)
    return out

def progress_blades(img, current_idx, total):
    """Top-right blade progress indicator"""
    d = ImageDraw.Draw(img)
    bw, bh, gap = 36, 18, 8
    total_w = total*(bw+gap)-gap
    x0 = W-60-total_w; y0 = 28
    for i in range(total):
        x = x0 + i*(bw+gap)
        color = GREEN if i <= current_idx else (25,45,30)
        d.rounded_rectangle([x,y0,x+bw,y0+bh], radius=4, fill=color)
    label = f"FINDING {current_idx+1:02d} / {total:02d}"
    d.text((W-60, y0+bh+10), label, font=F(22,"ExtraBold"), anchor="ra", fill=DIM)

def running_total(img, total_val, label="WEALTH DELTA"):
    """Top-right running dollar total"""
    d = ImageDraw.Draw(img)
    is_neg = total_val < 0
    color = RED_NEG if is_neg else YELLOW
    val_str = f"{'–' if is_neg else '+'}${abs(total_val):,}"
    d.text((W-60, 72), val_str, font=F(42,"ExtraBold"), anchor="ra", fill=color)
    d.text((W-60, 118), label, font=F(22,"ExtraBold"), anchor="ra", fill=DIM)

def draw_left_panel(img, finding, total, finding_idx):
    d = ImageDraw.Draw(img)
    n = finding["number"]
    lpad = 60
    rpad = LP - 30

    # Large finding number + divider
    d.text((lpad, 28), n, font=F(90,"ExtraBold"), fill=(30,55,36), anchor="la")
    d.line([(lpad,130),(rpad,130)], fill=SPLIT, width=2)

    # Headline
    hf = F(62,"ExtraBold")
    y = 150
    for ln in wrap(d, finding["headline"], hf, rpad-lpad):
        d.text((lpad, y), ln, font=hf, anchor="la", fill=WHITE)
        y += int(62*1.18)

    if finding.get("subtitle"):
        sf = F(30,"Medium")
        for ln in wrap(d, finding["subtitle"], sf, rpad-lpad):
            d.text((lpad, y+4), ln, font=sf, anchor="la", fill=GREY)
            y += 36
    y += 14

    # YOU AVOID
    if finding.get("you_avoid"):
        d.text((lpad, y), "YOU AVOID", font=F(22,"ExtraBold"), fill=DIM, anchor="la")
        y += 30
        st = finding["you_avoid"]
        stf = F(30,"Bold")
        stw = int(d.textlength(st, font=stf))
        d.text((lpad, y), st, font=stf, fill=GREY, anchor="la")
        d.line([(lpad,y+16),(lpad+stw,y+16)], fill=GREY, width=2)
        d.text((lpad+stw+14, y), "→  $0", font=F(30,"ExtraBold"), fill=GREEN, anchor="la")
        y += 40

    # Money callout
    if finding.get("money_callout"):
        mc = finding["money_callout"]
        is_neg = mc.startswith("–") or mc.startswith("-")
        mc_color = RED_NEG if is_neg else YELLOW
        d.text((lpad, y+6), mc, font=F(88,"ExtraBold"), anchor="la", fill=mc_color)
        y += 98
    if finding.get("money_sub"):
        for ln in wrap(d, finding["money_sub"], F(28,"Medium"), rpad-lpad):
            d.text((lpad, y), ln, font=F(28,"Medium"), anchor="la", fill=GREY)
            y += 34
    y += 10
    d.line([(lpad,y),(rpad,y)], fill=SPLIT, width=2)
    y += 18

    d.text((lpad, y), "WHY THIS MATTERS", font=F(22,"ExtraBold"), fill=DIM, anchor="la")
    y += 36
    for b in finding.get("bullets",[]):
        d.rounded_rectangle([lpad,y+2,lpad+38,y+36], radius=6, fill=DGREEN)
        d.text((lpad+19,y+19), b["n"], font=F(20,"ExtraBold"), anchor="mm", fill=LGREEN)
        bf = F(30,"ExtraBold")
        bw = int(d.textlength(b["bold"], font=bf))
        d.text((lpad+50,y+20), b["bold"], font=bf, anchor="lm", fill=WHITE)
        rf = F(28,"Medium")
        rest_lines = wrap(d, b["rest"], rf, rpad-lpad-50-bw-12)
        d.text((lpad+50+bw+10,y+20), rest_lines[0] if rest_lines else "", font=rf, anchor="lm", fill=GREY)
        y += 58
        for extra in rest_lines[1:]:
            d.text((lpad+50,y), extra, font=rf, anchor="la", fill=GREY); y+=36

    # Honest catch
    if finding.get("honest_catch") and y < H-180:
        y += 12
        catch_bg = (50,38,0)
        hct = "⚠  " + finding["honest_catch"]
        hcf = F(26,"Bold")
        hc_lines = wrap(d, hct, hcf, rpad-lpad-16)
        bh2 = len(hc_lines)*34+18
        if y + bh2 < H-60:
            d.rounded_rectangle([lpad,y,rpad,y+bh2], radius=12, fill=catch_bg)
            ty = y+9
            for ln in hc_lines:
                d.text((lpad+8,ty), ln, font=hcf, anchor="la", fill=YELLOW); ty+=34

def draw_right_panel(img, rp_data):
    """Draw the right panel data visual"""
    if not rp_data: return
    d = ImageDraw.Draw(img)
    rx0, rx1 = RP, W-40
    panel_w = rx1 - rx0
    cy = H//2
    t = rp_data.get("type","")

    if t == "vs":
        # Two column comparison
        col_w = panel_w//2 - 20
        for idx, (col, xc) in enumerate([(rp_data,"a"),(rp_data,"b")]):
            lbl_key = f"{xc}_label"; sub_key = f"{xc}_sub"
            cx = rx0 + (idx * (col_w+40)) + col_w//2
            color = GREEN if idx==0 else DGREEN
            r = 65
            d.ellipse([cx-r,cy-r-80,cx+r,cy+r-80], fill=color)
            d.ellipse([cx-r*0.32,cy-r*0.38-80,cx+r*0.32,cy+r*0.22-80], fill=WHITE)
            d.pieslice([cx-r*0.56,cy+r*0.08-80,cx+r*0.56,cy+r*0.98-80],180,360,fill=WHITE)
            d.text((cx,cy+r-68), rp_data[lbl_key], font=F(36,"ExtraBold"), anchor="ma", fill=WHITE)
            sf = F(28,"Medium")
            for i,ln in enumerate(rp_data[sub_key].split("\n")):
                d.text((cx, cy+r-20+i*34), ln, font=sf, anchor="ma", fill=GREY)
        if rp_data.get("question"):
            d.text((rx0+panel_w//2, cy+120), rp_data["question"],
                   font=F(34,"ExtraBold"), anchor="ma", fill=GREY)

    elif t == "bar_comparison":
        a_v, b_v = rp_data["a_val"], rp_data["b_val"]
        mx = max(a_v, b_v); base_y = H-120; full_h = 600
        bar_w = 180; gap = 120
        cx_a = rx0 + panel_w//3
        cx_b = rx0 + 2*panel_w//3
        for cx,val,fill,valt,lbl,sub in [
            (cx_a,a_v,GREEN,rp_data["a_valt"],rp_data["a_label"],rp_data["a_sub"]),
            (cx_b,b_v,DGREEN,rp_data["b_valt"],rp_data["b_label"],rp_data["b_sub"])]:
            bh = int(full_h*(val/mx))
            y0 = base_y-bh
            d.rounded_rectangle([cx-bar_w//2,y0,cx+bar_w//2,base_y],radius=18,fill=fill)
            d.text((cx,y0-46),valt,font=F(44,"ExtraBold"),anchor="ma",fill=WHITE)
            d.text((cx,base_y+24),lbl,font=F(32,"ExtraBold"),anchor="ma",fill=WHITE)
            for i,ln in enumerate(sub.split("\n")):
                d.text((cx,base_y+62+i*30),ln,font=F(24,"Medium"),anchor="ma",fill=GREY)

    elif t == "loss_timeline":
        years = rp_data["years"]; vals = rp_data["values"]
        label = rp_data.get("label","")
        d.text((rx0+panel_w//2, 60), label, font=F(32,"ExtraBold"), anchor="ma", fill=GREY)
        base_y = H-120; max_v=max(abs(v) for v in vals)
        total_w = rx1-rx0-80
        bar_w = total_w//len(years)-18
        x0s = [rx0+40+i*(bar_w+18) for i in range(len(years))]
        d.line([(rx0+20,base_y),(rx1-20,base_y)], fill=SPLIT, width=2)
        for i,(yr,val) in enumerate(zip(years,vals)):
            cx = x0s[i]+bar_w//2
            bh = int(400*abs(val)/max_v)
            color = GREEN if val>=0 else RED_NEG
            if val>=0:
                d.rounded_rectangle([x0s[i],base_y-bh,x0s[i]+bar_w,base_y],radius=10,fill=color)
                d.text((cx,base_y-bh-28),f"+${val//1000}K",font=F(22,"ExtraBold"),anchor="ma",fill=YELLOW)
            else:
                d.rounded_rectangle([x0s[i],base_y,x0s[i]+bar_w,base_y+bh],radius=10,fill=color)
                d.text((cx,base_y+bh+12),f"–${abs(val)//1000}K",font=F(22,"ExtraBold"),anchor="ma",fill=RED_NEG)
            d.text((cx,base_y+28),f"Yr{yr}",font=F(22,"Bold"),anchor="ma",fill=GREY)

    elif t == "crossover":
        years=rp_data["years"]; r_vals=rp_data["renter"]; b_vals=rp_data["buyer"]
        label=rp_data.get("label","")
        d.text((rx0+panel_w//2,52),label,font=F(30,"ExtraBold"),anchor="ma",fill=GREY)
        mx=max(max(b_vals),max(r_vals)); mn=min(min(b_vals),0)
        rng=mx-mn; base_y=H-130; chart_h=700; chart_w=rx1-rx0-80
        def py(v): return int(base_y - chart_h*(v-mn)/rng)
        def px(i): return rx0+40+int(i*chart_w/(len(years)-1))
        d.line([(rx0+20,base_y),(rx1-20,base_y)],fill=SPLIT,width=2)
        d.line([(rx0+20,py(0)),(rx1-20,py(0))],fill=(40,80,50),width=1)
        # Renter line (green)
        for i in range(len(years)-1):
            d.line([(px(i),py(r_vals[i])),(px(i+1),py(r_vals[i+1]))],fill=GREEN,width=5)
        # Buyer line (yellow)
        for i in range(len(years)-1):
            d.line([(px(i),py(b_vals[i])),(px(i+1),py(b_vals[i+1]))],fill=YELLOW,width=5)
        # Labels at end
        d.text((px(len(years)-1)+10,py(r_vals[-1])),"RENTER",font=F(26,"ExtraBold"),anchor="lm",fill=GREEN)
        d.text((px(len(years)-1)+10,py(b_vals[-1])),"BUYER",font=F(26,"ExtraBold"),anchor="lm",fill=YELLOW)
        # Year labels
        for i,yr in enumerate(years):
            if i%2==0:
                d.text((px(i),base_y+22),f"Yr{yr}",font=F(22,"Bold"),anchor="ma",fill=GREY)
        # Crossover annotation
        cross_x = px(6); cross_y = py(38000)
        d.line([(cross_x,base_y),(cross_x,cross_y+40)],fill=CYAN,width=2)
        d.text((cross_x,cross_y-10),"BREAK-EVEN",font=F(24,"ExtraBold"),anchor="ma",fill=CYAN)

    elif t == "decision":
        rows = rp_data["rows"]
        d.text((rx0+panel_w//2, 60),"WHAT SHOULD YOU DO?",font=F(32,"ExtraBold"),anchor="ma",fill=GREY)
        row_h = min(130, (H-160)//len(rows))
        for i, row in enumerate(rows):
            ry = 120 + i*row_h
            bg = (8,30,14) if row["color"]=="green" else (50,38,0)
            d.rounded_rectangle([rx0+20,ry,rx1-20,ry+row_h-12],radius=14,fill=bg)
            d.text((rx0+50,ry+row_h//2-2),row["label"],
                   font=F(30,"Bold"),anchor="lm",fill=GREY)
            rc = GREEN if row["color"]=="green" else YELLOW
            d.text((rx1-50,ry+row_h//2-2),row["result"],
                   font=F(30,"ExtraBold"),anchor="rm",fill=rc)

def draw_transition(total, completed):
    """Dark transition card between findings"""
    img = dark_bg()
    d = ImageDraw.Draw(img)
    # Blades
    bw,bh,gap = 60,28,12
    total_w = total*(bw+gap)-gap
    x0 = W//2-total_w//2; y0 = H//2-80
    for i in range(total):
        x = x0+i*(bw+gap)
        color = GREEN if i < completed else (20,40,24)
        d.rounded_rectangle([x,y0,x+bw,y0+bh],radius=6,fill=color)
    label = f"{completed} finding{'s' if completed!=1 else ''} revealed.  {total-completed} to go"
    d.text((W//2,H//2+20),label,font=F(48,"ExtraBold"),anchor="ma",fill=WHITE)
    for i,word in enumerate(["revealed","to go"]):
        pass  # already in label
    return img

def wordmark(img, y=28, h=38):
    fsz=120; fw=F(fsz,"ExtraBold"); CW=2200; CH=int(fsz*4); base=int(CH*0.70); sh=0.20
    main=Image.new("RGBA",(CW,CH),(0,0,0,0))
    lw=Image.new("RGBA",(CW,CH),(0,0,0,0))
    ImageDraw.Draw(lw).text((120,base),"Wealth",font=fw,fill=GREEN,anchor="ls")
    lw=lw.transform((CW,CH),Image.AFFINE,(1,sh,-sh*base,0,1,0),resample=Image.BICUBIC)
    main.alpha_composite(lw)
    rb=lw.getbbox()
    ImageDraw.Draw(main).text((rb[2]+6,base),"Delay",font=F(fsz,"ExtraBold"),fill=WHITE,anchor="ls")
    wm=main.crop(main.getbbox())
    w=int(wm.width*h/wm.height); wm=wm.resize((w,h),Image.LANCZOS)
    img.paste(wm,(60,y),wm)

def panel_divider(img):
    d = ImageDraw.Draw(img)
    d.line([(LP,0),(LP,H)], fill=SPLIT, width=2)

def render(data):
    findings = data["findings"]
    total = len(findings)
    vid_id = data["id"]
    OUT = f"{OUTDIR}/{vid_id}_long.mp4"
    tmp = tempfile.mkdtemp(prefix=f"hal_l_{vid_id}_")
    clips = []

    # Running total accumulates per finding (use money_callout if numeric-ish)
    running = 0

    for i, finding in enumerate(findings):
        img = dark_bg()
        wordmark(img)
        panel_divider(img)
        progress_blades(img, i, total)

        # Parse running total from money_callout if possible
        mc = finding.get("money_callout","")
        try:
            sign = -1 if mc.startswith("–") or mc.startswith("-") else 1
            num = int("".join(c for c in mc if c.isdigit()))
            running += sign * num
        except: pass
        running_total(img, running, "CUMULATIVE WEALTH SHIFT")

        draw_left_panel(img, finding, total, i)
        draw_right_panel(img, finding.get("right_panel"))

        png = f"{tmp}/s{i}.png"; img.save(png)
        m = f"{tmp}/v{i}.mp3"; vo_tts(finding["vo"], m)
        wv = f"{tmp}/v{i}.wav"
        run(["ffmpeg","-y","-i",m,"-ar","44100","-ac","1",wv])
        d_sec = dur(wv)+0.2; frames=int(d_sec*FPS)
        zc = f"{tmp}/z{i}.mp4"
        run(["ffmpeg","-y","-loop","1","-i",png,"-vf",
             f"scale={int(W*1.3)}:{int(H*1.3)},"
             f"zoompan=z='min(zoom+0.0004,1.04)':d={frames}"
             f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
             "format=yuv420p",
             "-frames:v",str(frames),"-c:v","libx264","-preset","veryfast",
             "-pix_fmt","yuv420p","-r",str(FPS),zc])
        clip=f"{tmp}/c{i}.mp4"
        run(["ffmpeg","-y","-i",zc,"-i",wv,"-c:v","copy","-c:a","aac","-b:a","192k","-shortest",clip])
        clips.append(clip)

        # Transition card (except after last finding)
        if i < total-1:
            trans_img = draw_transition(total, i+1)
            tp = f"{tmp}/t{i}.png"; trans_img.save(tp)
            tc = f"{tmp}/tc{i}.mp4"
            run(["ffmpeg","-y","-loop","1","-i",tp,"-vf","scale=1920:1080,format=yuv420p",
                 "-t","2.5","-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-r",str(FPS),tc])
            # Silent audio for transition
            sa = f"{tmp}/sa{i}.wav"
            run(["ffmpeg","-y","-f","lavfi","-i","anullsrc=r=44100:cl=mono","-t","2.5","-ar","44100",sa])
            tclip = f"{tmp}/tclip{i}.mp4"
            run(["ffmpeg","-y","-i",tc,"-i",sa,"-c:v","copy","-c:a","aac","-b:a","64k","-shortest",tclip])
            clips.append(tclip)

    lst=f"{tmp}/l.txt"; open(lst,"w").write("".join(f"file '{c}'\n" for c in clips))
    base=f"{tmp}/base.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",lst,
         "-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac",base])

    # Disclaimer overlay
    vdur=dur(base)
    dl=Image.new("RGBA",(W,H),(0,0,0,0)); dd=ImageDraw.Draw(dl)
    df=F(24,"Medium")
    dlines=wrap(dd,data.get("disclaimer",""),df,W-120)
    dh=len(dlines)*34+20
    dd.rectangle([0,H-dh-16,W,H],fill=(5,12,7,210))
    dy=H-dh-4
    for ln in dlines:
        dd.text((W//2,dy),ln,font=df,anchor="ma",fill=(*GREY,220)); dy+=34
    dlp=f"{tmp}/dl.png"; dl.save(dlp)

    barfx=f"drawbox=x=0:y={H-8}:w='iw*t/{vdur:.2f}':h=8:color=0x16A34A@1.0:t=fill:enable=1"
    run(["ffmpeg","-y","-i",base,"-i",dlp,"-filter_complex",
         f"[0:v][1:v]overlay=0:0:enable='gte(t,{vdur-3:.2f})'[d];[d]{barfx}[v]",
         "-map","[v]","-map","0:a","-c:v","libx264","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",OUT])

    tags=" ".join(f"#{t.replace(' ','')}" for t in data.get("tags",[]))
    open(f"{OUTDIR}/{vid_id}_long.txt","w").write(
        f"{data['title']}\n\n"
        f"👉 Run your own numbers (free): {data['tool_url']}\n\n"
        f"{data.get('disclaimer','')}\n\n{tags} #WealthDelay #PersonalFinance")

    print(f"DONE → {OUT} ({dur(OUT):.1f}s)", flush=True)
    shutil.rmtree(tmp,ignore_errors=True)
    return OUT

if __name__ == "__main__":
    if len(sys.argv)<2: sys.exit("usage: build_hal_long.py <json_file>")
    data=json.load(open(sys.argv[1]))
    render(data)

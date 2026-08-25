#!/usr/bin/env python3
"""
WealthDelay HAL-style Shorts renderer
Dark aesthetic · numbered findings · yellow money callouts
Vertical 1080×1920 · all findings → one Short video

Usage:
  python3 build_hal_short.py <json_file>
  python3 build_hal_short.py rent_vs_buy_hal.json
"""
import os, sys, json, subprocess, tempfile, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

DIR = os.path.dirname(os.path.abspath(__file__))
OUTDIR = f"{DIR}/out"; os.makedirs(OUTDIR, exist_ok=True)
FONTF = f"{DIR}/PlusJakartaSans.ttf"
VOICE = "en-US-BrianNeural"
RATE = "+25%"
W, H, FPS = 1080, 1920, 30

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
GRID    = (12, 22, 15)
RED_NEG = (239, 68, 68)

def F(sz, w="Bold"):
    f = ImageFont.truetype(FONTF, sz)
    try: f.set_variation_by_name(w)
    except: pass
    return f

def run(c): subprocess.run(c, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def dur(p): return float(subprocess.run(
    ["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],
    capture_output=True, text=True).stdout.strip())

def vo_tts(text, path):
    run(["edge-tts","--voice",VOICE,"--rate",RATE,"--text",text,"--write-media",path])

def dark_bg():
    arr = np.zeros((H, W, 3), np.uint8)
    for y in range(H):
        t = y / H
        arr[y,:,0] = int(BG[0] + 4*(1-t))
        arr[y,:,1] = int(BG[1] + 10*(1-t))
        arr[y,:,2] = int(BG[2] + 5*(1-t))
    img = Image.fromarray(arr).convert("RGBA")
    # Faint grid
    gi = Image.new("RGBA", (W, H), (0,0,0,0))
    dg = ImageDraw.Draw(gi)
    for x in range(0, W, 90):
        dg.line([(x,0),(x,H)], fill=(*GRID,160), width=1)
    for y in range(0, H, 90):
        dg.line([(0,y),(W,y)], fill=(*GRID,160), width=1)
    img = Image.alpha_composite(img, gi)
    # Corner glows
    gl = Image.new("RGBA", (W, H), (0,0,0,0))
    dgl = ImageDraw.Draw(gl)
    dgl.ellipse([-250,-250,650,650], fill=(0,80,30,38))
    dgl.ellipse([W-650,H-650,W+250,H+250], fill=(0,55,20,28))
    gl = gl.filter(ImageFilter.GaussianBlur(150))
    return Image.alpha_composite(img, gl).convert("RGB")

def wordmark(img, y=48, h=46):
    fsz = 120; fw = F(fsz,"ExtraBold"); CW=2200; CH=int(fsz*4); base=int(CH*0.70); sh=0.20
    main = Image.new("RGBA",(CW,CH),(0,0,0,0))
    lw = Image.new("RGBA",(CW,CH),(0,0,0,0))
    ImageDraw.Draw(lw).text((120,base),"Wealth",font=fw,fill=GREEN,anchor="ls")
    lw = lw.transform((CW,CH),Image.AFFINE,(1,sh,-sh*base,0,1,0),resample=Image.BICUBIC)
    main.alpha_composite(lw)
    rb = lw.getbbox()
    ImageDraw.Draw(main).text((rb[2]+6,base),"Delay",font=F(fsz,"ExtraBold"),fill=WHITE,anchor="ls")
    wm = main.crop(main.getbbox())
    w = int(wm.width * h / wm.height)
    wm = wm.resize((w,h), Image.LANCZOS)
    img.paste(wm,(W//2-w//2, y), wm)

def wrap(d, t, f, mw):
    out=[]; cur=""
    for word in t.split():
        s=(cur+" "+word).strip()
        if d.textlength(s,font=f)<=mw: cur=s
        else: out.append(cur); cur=word
    if cur: out.append(cur)
    return out

def draw_finding(img, finding, total):
    d = ImageDraw.Draw(img)
    n = finding["number"]
    total_str = f"{total:02d}"

    # ── FINDING PILL ──────────────────────────────────────────
    pill_text = f"FINDING {n} · {total_str}"
    pf = F(30,"ExtraBold")
    pw = d.textlength(pill_text, font=pf)
    px0 = W//2 - pw//2 - 28; px1 = W//2 + pw//2 + 28
    d.rounded_rectangle([px0, 118, px1, 170], radius=30, fill=MGREEN)
    d.text((W//2, 144), pill_text, font=pf, anchor="mm", fill=CYAN)

    # ── HEADLINE ─────────────────────────────────────────────
    hf = F(76,"ExtraBold")
    hlines = wrap(d, finding["headline"], hf, W-100)
    y = 205
    for ln in hlines:
        d.text((W//2, y), ln, font=hf, anchor="ma", fill=WHITE)
        y += int(76*1.20)

    # ── SUBTITLE ─────────────────────────────────────────────
    if finding.get("subtitle"):
        sf = F(36,"Medium")
        for ln in wrap(d, finding["subtitle"], sf, W-130):
            d.text((W//2, y+6), ln, font=sf, anchor="ma", fill=GREY)
            y += 44
    y += 20

    # ── DIVIDER ──────────────────────────────────────────────
    d.line([(70, y), (W-70, y)], fill=(28,52,35), width=2)
    y += 34

    # ── YOU AVOID (optional) ─────────────────────────────────
    if finding.get("you_avoid"):
        d.text((80, y), "YOU AVOID", font=F(26,"ExtraBold"), fill=DIM, anchor="la")
        y += 36
        st = finding["you_avoid"]
        stf = F(36,"Bold")
        stw = int(d.textlength(st, font=stf))
        d.text((80, y), st, font=stf, fill=GREY, anchor="la")
        d.line([(80, y+19),(80+stw, y+19)], fill=GREY, width=3)
        ax = 80 + stw + 18
        d.text((ax, y), "→  $0", font=F(36,"ExtraBold"), fill=GREEN, anchor="la")
        y += 52

    # ── MONEY CALLOUT ─────────────────────────────────────────
    if finding.get("money_callout"):
        mc = finding["money_callout"]
        is_neg = mc.startswith("–") or mc.startswith("-")
        mc_color = RED_NEG if is_neg else YELLOW
        mf = F(110,"ExtraBold")
        d.text((W//2, y+10), mc, font=mf, anchor="ma", fill=mc_color)
        y += 122
    if finding.get("money_sub"):
        d.text((W//2, y), finding["money_sub"], font=F(34,"Bold"), anchor="ma", fill=GREY)
        y += 48

    y += 18
    d.line([(70, y),(W-70, y)], fill=(28,52,35), width=2)
    y += 32

    # ── WHY THIS MATTERS ─────────────────────────────────────
    d.text((80, y), "WHY THIS MATTERS", font=F(26,"ExtraBold"), fill=DIM, anchor="la")
    y += 48

    for b in finding.get("bullets", []):
        # Number badge
        d.rounded_rectangle([80, y+2, 122, y+44], radius=8, fill=DGREEN)
        d.text((101, y+23), b["n"], font=F(24,"ExtraBold"), anchor="mm", fill=LGREEN)
        # Bold label
        bf = F(38,"ExtraBold")
        bw = int(d.textlength(b["bold"], font=bf))
        d.text((136, y+24), b["bold"], font=bf, anchor="lm", fill=WHITE)
        # Rest text
        rf = F(36,"Medium")
        rest_lines = wrap(d, b["rest"], rf, W - 136 - bw - 18 - 80)
        d.text((136+bw+14, y+24), rest_lines[0] if rest_lines else "", font=rf, anchor="lm", fill=GREY)
        y += 78
        for extra in rest_lines[1:]:
            d.text((136, y), extra, font=rf, anchor="lm", fill=GREY)
            y += 46

    y += 22

    # ── HONEST CATCH ─────────────────────────────────────────
    if finding.get("honest_catch"):
        catch_bg = (52, 40, 0)
        hct = "⚠  " + finding["honest_catch"]
        hcf = F(32,"Bold")
        hc_lines = wrap(d, hct, hcf, W-120)
        box_h = len(hc_lines)*40 + 26
        d.rounded_rectangle([60, y, W-60, y+box_h], radius=16, fill=catch_bg)
        ty = y+13
        for ln in hc_lines:
            d.text((W//2, ty), ln, font=hcf, anchor="ma", fill=YELLOW)
            ty += 40
        y += box_h

    # ── CTA (anchored bottom) ─────────────────────────────────
    cta_y = H - 258
    d.rounded_rectangle([60, cta_y, W-60, H-58], radius=26, fill=DGREEN)
    d.text((W//2, cta_y+50), "Free calculator — link below", font=F(40,"ExtraBold"), anchor="ma", fill=WHITE)
    d.text((W//2, cta_y+108), "wealthdelay.com", font=F(34,"Bold"), anchor="ma", fill=LGREEN)
    cta_kw = finding.get("cta_keyword","")
    if cta_kw:
        d.text((W//2, cta_y+158), f"Comment {cta_kw} for the full breakdown",
               font=F(28,"Medium"), anchor="ma", fill=GREY)
    # down arrow
    d.polygon([(W//2-20,H-42),(W//2+20,H-42),(W//2,H-18)], fill=GREEN)

def render(data):
    findings = data["findings"]
    total = len(findings)
    vid_id = data["id"]
    OUT = f"{OUTDIR}/{vid_id}.mp4"
    tmp = tempfile.mkdtemp(prefix=f"hal_s_{vid_id}_")
    clips = []

    for i, finding in enumerate(findings):
        # Inject cta_keyword from root if not per-finding
        if "cta_keyword" not in finding:
            finding["cta_keyword"] = data.get("cta_keyword","")

        img = dark_bg()
        wordmark(img)
        draw_finding(img, finding, total)

        png = f"{tmp}/s{i}.png"; img.save(png)
        m = f"{tmp}/v{i}.mp3"; vo_tts(finding["vo"], m)
        wv = f"{tmp}/v{i}.wav"
        run(["ffmpeg","-y","-i",m,"-ar","44100","-ac","1",wv])
        d_sec = dur(wv) + 0.2
        frames = int(d_sec * FPS)
        zc = f"{tmp}/z{i}.mp4"
        run(["ffmpeg","-y","-loop","1","-i",png,"-vf",
             f"scale={int(W*1.5)}:{int(H*1.5)},"
             f"zoompan=z='min(zoom+0.0006,1.05)':d={frames}"
             f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={FPS},"
             "format=yuv420p",
             "-frames:v",str(frames),"-c:v","libx264","-preset","veryfast",
             "-pix_fmt","yuv420p","-r",str(FPS),zc])
        clip = f"{tmp}/c{i}.mp4"
        run(["ffmpeg","-y","-i",zc,"-i",wv,"-c:v","copy","-c:a","aac",
             "-b:a","192k","-shortest",clip])
        clips.append(clip)

    lst = f"{tmp}/l.txt"
    open(lst,"w").write("".join(f"file '{c}'\n" for c in clips))
    base = f"{tmp}/base.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",lst,
         "-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac",base])

    # Disclaimer overlay last 3 seconds
    vdur = dur(base)
    dl = Image.new("RGBA",(W,H),(0,0,0,0)); dd = ImageDraw.Draw(dl)
    df = F(26,"Medium")
    dlines = wrap(dd, data.get("disclaimer",""), df, W-120)
    dh = len(dlines)*38 + 24
    dd.rectangle([0,H-dh-20,W,H], fill=(5,12,7,220))
    dy = H-dh-6
    for ln in dlines:
        dd.text((W//2,dy),ln,font=df,anchor="ma",fill=(*GREY,230)); dy+=38
    dlp = f"{tmp}/dl.png"; dl.save(dlp)

    barfx = f"drawbox=x=0:y={H-10}:w='iw*t/{vdur:.2f}':h=10:color=0x16A34A@1.0:t=fill:enable=1"
    run(["ffmpeg","-y","-i",base,"-i",dlp,"-filter_complex",
         f"[0:v][1:v]overlay=0:0:enable='gte(t,{vdur-3:.2f})'[d];[d]{barfx}[v]",
         "-map","[v]","-map","0:a","-c:v","libx264","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k","-movflags","+faststart",OUT])

    # Description file
    hook = findings[0]["headline"]
    tags = " ".join(f"#{t.replace(' ','')}" for t in data.get("tags",[]))
    open(f"{OUTDIR}/{vid_id}.txt","w").write(
        f"{hook}\n\n{data['title']}\n\n"
        f"👉 Run your own numbers (free): {data['tool_url']}\n\n"
        f"{data.get('disclaimer','')}\n\n{tags} #Shorts #WealthDelay")

    print(f"DONE → {OUT} ({dur(OUT):.1f}s)", flush=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return OUT

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: build_hal_short.py <json_file>")
    data = json.load(open(sys.argv[1]))
    render(data)

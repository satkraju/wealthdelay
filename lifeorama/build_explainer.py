#!/usr/bin/env python3
"""Life-O-Rama explainer builder — AI images + Kokoro voice + captions.

  python3 build_explainer.py <id>             # horizontal long-form -> out/<id>.mp4
  python3 build_explainer.py <id> --short     # vertical Shorts funnel cut -> out/<id>.mp4
  python3 build_explainer.py --list

Each scene has a "prompt" for Pollinations.ai (free, no key) that generates a
cinematic AI image matching the narration, plus the narration line itself.
Default output is horizontal 1920x1080 long-form (LOR monetization). The --short
flag renders vertical 1080x1920 for the discovery funnel. Both use Kokoro studio
TTS, burned-in captions, and Ken Burns motion on each image.
"""
import os, sys, json, glob, subprocess, tempfile, urllib.request, urllib.parse, time, datetime

DIR = os.path.dirname(os.path.abspath(__file__))
OUTDIR = f"{DIR}/out"; CACHEDIR = f"{DIR}/cache"; SCRIPTDIR = f"{DIR}/scripts"
os.makedirs(OUTDIR, exist_ok=True); os.makedirs(CACHEDIR, exist_ok=True)

UPLOADER  = os.path.join(os.path.dirname(DIR), "youtube_upload.py")
LOR_TOKEN = os.path.expanduser("~/.config/empireos/yt_token_lor.json")
# Mon/Wed/Fri at 15:00 UTC
PUBLISH_WEEKDAYS = {0, 2, 4}
PUBLISH_HOUR_UTC = 15

def _next_publish_slot():
    """Return the next Mon/Wed/Fri 15:00 UTC after the last already-scheduled video."""
    # find the latest scheduled date from existing txt files
    last = datetime.date.today()
    for txt in glob.glob(f"{OUTDIR}/*.txt"):
        try:
            mtime = datetime.date.fromtimestamp(os.path.getmtime(txt))
            if mtime > last: last = mtime
        except Exception:
            pass
    # walk forward from tomorrow until we land on a publish weekday
    d = last + datetime.timedelta(days=1)
    while d.weekday() not in PUBLISH_WEEKDAYS:
        d += datetime.timedelta(days=1)
    return datetime.datetime(d.year, d.month, d.day, PUBLISH_HOUR_UTC, 0, 0,
                             tzinfo=datetime.timezone.utc)

def auto_upload(e, mp4, txt):
    if not os.path.exists(LOR_TOKEN):
        print("⚠  LOR channel not connected — skipping auto-upload.")
        print("   Run once: python3 schedule_lor.py --auth")
        return
    txt_lines = open(txt).read().split("\n")
    title     = txt_lines[0].strip() or e.get("id","video")
    tags_line = next((l for l in reversed(txt_lines) if l.strip().startswith("#")), "")
    when      = _next_publish_slot()
    iso       = when.strftime("%Y-%m-%dT%H:%M:%SZ")
    cmd = ["python3", UPLOADER,
           "--video",      mp4,
           "--title",      title,
           "--desc-file",  txt,
           "--tags",       tags_line,
           "--publish-at", iso,
           "--token-file", LOR_TOKEN]
    if not VERTICAL:
        cmd.append("--no-shorts-tag")
    print(f"   uploading to LOR → scheduled {when.strftime('%a %Y-%m-%d %H:%M UTC')} …", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip().splitlines()
    print("   " + (out[-1] if out else "(no output)"))

W, H, FPS = 1920, 1080, 30          # default: horizontal long-form
VERTICAL = False
VOICE = "am_michael"                # Kokoro voice (am_michael / bm_george / af_heart ...)
SPEED = 1.15                        # narration speed (1.0 = normal, 1.15 = slightly faster)
XF = 0.2
FONT = "/System/Library/Fonts/Supplemental/Arial Black.ttf"

STYLE_BASE = "cinematic dramatic lighting dark moody photorealistic 8k"

def set_orientation(vertical):
    global W, H, VERTICAL
    VERTICAL = vertical
    W, H = (1080, 1920) if vertical else (1920, 1080)

def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def dur(p):
    return float(subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",p],
        capture_output=True, text=True).stdout.strip())

_KOKORO = None
def _kokoro():
    global _KOKORO
    if _KOKORO is None:
        from kokoro import KPipeline
        _KOKORO = KPipeline(lang_code="a")   # 'a' = American English
    return _KOKORO

def vo(text, wav_path):
    """Studio-quality narration via Kokoro -> 44100 Hz mono wav. Falls back to edge-tts."""
    try:
        import soundfile as sf, numpy as np
        raw = wav_path + ".raw.wav"
        audio = np.concatenate([a for _, _, a in _kokoro()(text, voice=VOICE, speed=SPEED)])
        sf.write(raw, audio, 24000)
        run(["ffmpeg","-y","-i",raw,"-ar","44100","-ac","1",wav_path])
    except Exception as ex:
        print(f"   Kokoro failed ({ex}); falling back to edge-tts", file=sys.stderr)
        mp3 = wav_path + ".mp3"
        run(["edge-tts","--voice","en-US-BrianNeural","--rate","+8%","--text",text,"--write-media",mp3])
        run(["ffmpeg","-y","-i",mp3,"-ar","44100","-ac","1",wav_path])

def make_caption(text, png):
    """Render a bold, centered, stroked caption as a full-frame transparent PNG (muted viewing)."""
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # vertical Shorts: big center-lower captions. horizontal long-form: tasteful lower-third.
    if VERTICAL:
        size, maxw_frac, y_center, stroke = 78, 0.86, 0.66, 10
    else:
        size, maxw_frac, y_center, stroke = 58, 0.80, 0.86, 7
    font = ImageFont.truetype(FONT, size)
    maxw = W * maxw_frac
    words, lines, cur = text.replace("—", "-").split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= maxw:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    lh = size * 1.22
    total = lh * len(lines)
    y0 = H * y_center - total / 2
    for i, ln in enumerate(lines):
        w = d.textlength(ln, font=font)
        x, y = (W - w) / 2, y0 + i * lh
        d.text((x, y), ln, font=font, fill=(255, 255, 255, 255),
               stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    img.save(png)

def ai_image(prompt, idx):
    safe = "".join(c if c.isalnum() else "_" for c in prompt.lower())[:60]
    orient = "v" if VERTICAL else "h"
    cached = f"{CACHEDIR}/ai_{orient}{idx:02d}_{safe}.jpg"
    if os.path.exists(cached):
        return cached
    style = STYLE_BASE + (", vertical composition" if VERTICAL else ", wide cinematic composition")
    full = f"{prompt}, {style}"
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(full)}?width={W}&height={H}&nologo=true&seed={idx*7}"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=90) as r, open(cached, "wb") as f:
                f.write(r.read())
            print(f"   img {idx}: {prompt[:50]}", file=sys.stderr)
            return cached
        except Exception as e:
            print(f"   img {idx} attempt {attempt+1} failed: {e}", file=sys.stderr)
            time.sleep(3)
    sys.exit(f"Failed to fetch AI image for: {prompt}")

def kenburns_clip(photo, voice_wav, caption_png, out_clip, pan="zoom-in"):
    d = dur(voice_wav) + 0.3
    frames = int(d * FPS)
    scale_w, scale_h = W * 2, H * 2
    if pan == "zoom-in":
        zexpr = "min(zoom+0.0010,1.2)"
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif pan == "pan-right":
        zexpr = "1.12"
        x = f"(iw-iw/zoom)*on/{frames}"
        y = "ih/2-(ih/zoom/2)"
    else:
        zexpr = "1.12"
        x = f"(iw-iw/zoom)*(1-on/{frames})"
        y = "ih/2-(ih/zoom/2)"
    # bg image gets Ken Burns motion; caption PNG is overlaid static so text stays crisp
    fc = (f"[0:v]scale={scale_w}:{scale_h}:force_original_aspect_ratio=increase,"
          f"crop={scale_w}:{scale_h},"
          f"zoompan=z='{zexpr}':d={frames}:x='{x}':y='{y}':s={W}x{H}:fps={FPS},"
          f"format=yuv420p[bg];[bg][1:v]overlay=0:0[v]")
    run(["ffmpeg","-y","-loop","1","-i",photo,"-i",caption_png,"-filter_complex",fc,
         "-map","[v]","-frames:v",str(frames),
         "-c:v","libx264","-preset","veryfast","-pix_fmt","yuv420p","-r",str(FPS), out_clip])
    final = out_clip.replace(".mp4","_a.mp4")
    run(["ffmpeg","-y","-i",out_clip,"-i",voice_wav,"-c:v","copy","-c:a","aac","-b:a","192k","-shortest", final])
    return final

def render(e, upload=True):
    tmp = tempfile.mkdtemp(prefix=f"lor_{e['id']}_")
    clips = []
    pans = ["zoom-in","pan-right","pan-left"]
    for i, scene in enumerate(e["scenes"]):
        wav = f"{tmp}/v{i}.wav"
        vo(scene["narration"], wav)
        photo = ai_image(scene["prompt"], i)
        cap = f"{tmp}/cap{i}.png"
        make_caption(scene["narration"], cap)
        clip = kenburns_clip(photo, wav, cap, f"{tmp}/c{i}.mp4", pans[i % 3])
        clips.append(clip)
        print(f"   scene {i+1}/{len(e['scenes'])} done", file=sys.stderr)

    cur = clips[0]
    for i in range(1, len(clips)):
        nxt = clips[i]; out = f"{tmp}/x{i}.mp4"
        offset = max(0, dur(cur) - XF)
        run(["ffmpeg","-y","-i",cur,"-i",nxt,"-filter_complex",
             f"[0:v][1:v]xfade=transition=fade:duration={XF}:offset={offset:.3f}[v];"
             f"[0:a][1:a]acrossfade=d={XF}[a]",
             "-map","[v]","-map","[a]","-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",out])
        cur = out

    final = f"{OUTDIR}/{e['id']}.mp4"
    run(["ffmpeg","-y","-i",cur,"-c:v","libx264","-pix_fmt","yuv420p","-c:a","aac",
         "-b:a","192k","-movflags","+faststart",final])
    with open(f"{OUTDIR}/{e['id']}.txt","w") as f:
        title = e.get("title") or e.get("description","")[:80]
        desc  = e.get("description","")
        tags  = " ".join(f"#{t}" for t in e.get("tags",[]))
        f.write(f"{title}\n\n{desc}\n\n{tags}")
    txt = f"{OUTDIR}/{e['id']}.txt"
    print(f"DONE -> {final}  ({dur(final):.1f}s)")
    if upload:
        auto_upload(e, final, txt)
    else:
        print("   (skipped upload — pass nothing/omit --no-upload to auto-schedule)")
    return final

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h","--help"):
        sys.exit(__doc__)
    if sys.argv[1] == "--list":
        for p in sorted(glob.glob(f"{SCRIPTDIR}/*.json")):
            print(os.path.splitext(os.path.basename(p))[0])
        sys.exit(0)
    upload = "--no-upload" not in sys.argv
    set_orientation("--short" in sys.argv)
    positional = [a for a in sys.argv[1:] if not a.startswith("--")]
    eid = positional[0]
    path = f"{SCRIPTDIR}/{eid}.json"
    if not os.path.exists(path): sys.exit(f"No script file: {path}")
    e = json.load(open(path)); e["id"] = eid
    render(e, upload=upload)

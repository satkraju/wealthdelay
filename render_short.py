#!/usr/bin/env python3
"""
Faceless business short — 100% local, no CapCut, no paid API.
macOS `say` = voiceover. PIL = kinetic text cards. ffmpeg = assembly.
Each sentence becomes one full-screen caption synced to its own narration clip.
"""
import os, subprocess, tempfile, textwrap, sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30
VOICE = "Daniel"          # built-in British male; authoritative. fallback handled below.
BG = (12, 14, 22)
ACCENT = (245, 245, 245)
KICKER = (120, 200, 255)
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

# (on-screen kicker, spoken+shown sentence)
BEATS = [
    ("IT'S NOT RARE", "The diamond on her finger isn't rare. You were trained to think it is."),
    ("THE QUESTION", "Why do we spend three months' salary on a rock that's basically common?"),
    ("THE TRICK",    "Diamonds aren't scarce. One company hoarded the supply to fake the scarcity."),
    ("1938",         "Before 1938, almost nobody proposed with a diamond. Then De Beers hired an ad agency."),
    ("THE SLOGAN",   "They invented the line: A Diamond Is Forever. And the rule that a ring should cost months of pay. They made it up."),
    ("MIND CONTROL", "One slogan rewired how the entire planet gets engaged. That's not a gem. It's mind control with a markup."),
    ("YOU DIDN'T CHOOSE IT", "You didn't choose the tradition. An ad from 1938 chose it for you."),
]


def font(sz):
    return ImageFont.truetype(FONT, sz)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def card(kicker, body, idx, path):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # subtle vignette bar at top + bottom for that "short" look
    d.rectangle([0, 0, W, 12], fill=KICKER)
    d.rectangle([0, H - 12, W, H], fill=KICKER)
    fk, fb = font(58), font(86)
    # kicker near top third
    d.text((W // 2, 430), kicker.upper(), font=fk, anchor="mm", fill=KICKER)
    # body centered
    lines = wrap(d, body, fb, W - 160)
    lh = 112
    total = lh * len(lines)
    y = H // 2 - total // 2
    for ln in lines:
        d.text((W // 2, y), ln, font=fb, anchor="ma", fill=ACCENT)
        y += lh
    # progress dots
    n = len(BEATS)
    dot_w = 26
    start_x = W // 2 - (n * dot_w) // 2
    for i in range(n):
        c = KICKER if i <= idx else (60, 64, 80)
        cx = start_x + i * dot_w + dot_w // 2
        d.ellipse([cx - 7, H - 150, cx + 7, H - 136], fill=c)
    img.save(path)


def dur(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", path],
        capture_output=True, text=True).stdout.strip()
    return float(out)


def voice_ok(v):
    return subprocess.run(["say", "-v", v, "-o", "/dev/null", "test"],
                          capture_output=True).returncode == 0


def main():
    out_path = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "debeers.mp4")
    v = VOICE if voice_ok(VOICE) else "Samantha"
    tmp = tempfile.mkdtemp(prefix="short_")
    segs = []
    for i, (kicker, body) in enumerate(BEATS):
        aiff = os.path.join(tmp, f"a{i}.aiff")
        # write text to file so apostrophes/quotes never hit the shell
        txt = os.path.join(tmp, f"t{i}.txt")
        open(txt, "w").write(body)
        subprocess.run(["say", "-v", v, "-r", "180", "-f", txt, "-o", aiff], check=True)
        wav = os.path.join(tmp, f"a{i}.wav")
        subprocess.run(["ffmpeg", "-y", "-i", aiff, wav],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        d = dur(wav) + 0.35                       # tiny tail so it doesn't feel clipped
        png = os.path.join(tmp, f"c{i}.png")
        card(kicker, body, i, png)
        seg = os.path.join(tmp, f"s{i}.mp4")
        subprocess.run(
            ["ffmpeg", "-y", "-loop", "1", "-i", png, "-i", wav,
             "-c:v", "libx264", "-t", f"{d:.2f}", "-r", str(FPS), "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "160k", "-vf", f"scale={W}:{H}",
             "-af", "apad", "-shortest", "-movflags", "+faststart", seg],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        segs.append(seg)
        print(f"  beat {i+1}/{len(BEATS)}  {d:.1f}s", file=sys.stderr)

    listf = os.path.join(tmp, "list.txt")
    open(listf, "w").write("".join(f"file '{s}'\n" for s in segs))
    subprocess.run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", listf,
         "-c", "copy", "-movflags", "+faststart", out_path],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    total = dur(out_path)
    print(f"DONE -> {out_path}  ({total:.1f}s, voice={v})")


if __name__ == "__main__":
    main()

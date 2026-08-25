#!/usr/bin/env python3
"""
Faceless "restoration morph" short — end-to-end automation.

  Gemini (images)  ->  Veo (morph clips)  ->  ElevenLabs (voice)  ->  ffmpeg (assemble + captions)

One config.json defines a whole video. Run:

    python3 pipeline.py config.temple.json
    python3 pipeline.py config.temple.json --skip-images   # reuse existing scene images
    python3 pipeline.py config.temple.json --skip-video     # reuse existing clips, just re-voice/assemble

Keys (each on its own line `NAME=value`, chmod 600):
    ~/.config/gemini/.env        GEMINI_API_KEY=...
    ~/.config/elevenlabs/.env    ELEVENLABS_API_KEY=...

Deps:  pip install google-genai pillow   (ffmpeg/ffprobe already on PATH)
"""
import os, sys, json, time, subprocess, tempfile, urllib.request, argparse
from PIL import Image, ImageDraw, ImageFont

# ---------- config / keys ----------
def load_key(path, name):
    p = os.path.expanduser(path)
    if not os.path.exists(p):
        return None
    for line in open(p):
        if line.strip().startswith(name + "="):
            return line.split("=", 1)[1].strip()
    return None

GEMINI_KEY = load_key("~/.config/gemini/.env", "GEMINI_API_KEY")
ELEVEN_KEY = load_key("~/.config/elevenlabs/.env", "ELEVENLABS_API_KEY")
FONT = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
W, H, FPS = 1080, 1920, 30
XF = 0.6          # crossfade between clips (s)
GAP = 0.30        # silence between voice lines (s)


# ---------- ffmpeg helpers ----------
def run(cmd):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def dur(p):
    return float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","default=nw=1:nk=1",p], capture_output=True, text=True).stdout.strip())


# ---------- 1. IMAGES (Gemini / Imagen) ----------
def gen_image(client, model, prompt, out_path, aspect):
    """Generate one still. Uses google-genai Imagen API."""
    from google.genai import types
    resp = client.models.generate_images(
        model=model, prompt=prompt,
        config=types.GenerateImagesConfig(number_of_images=1, aspect_ratio=aspect))
    resp.generated_images[0].image.save(out_path)
    print(f"   image -> {os.path.basename(out_path)}", file=sys.stderr)


# ---------- 2. VIDEO (Veo) ----------
def gen_clip(client, model, prompt, first_img, last_img, out_path, aspect):
    """
    Generate one Veo clip. If last_img is given, attempt first+last frame morph
    (Veo 3.1 'ingredients'); else fall back to image-to-video on first frame.
    """
    from google.genai import types
    cfg_kwargs = dict(aspect_ratio=aspect, number_of_videos=1, generate_audio=False)
    last = None
    if last_img:
        try:
            last = types.Image.from_file(location=last_img)
            cfg_kwargs["last_frame"] = last            # supported on Veo 3.1
        except Exception:
            last = None
    op = client.models.generate_videos(
        model=model, prompt=prompt,
        image=types.Image.from_file(location=first_img),
        config=types.GenerateVideosConfig(**cfg_kwargs))
    while not op.done:
        time.sleep(10)
        op = client.operations.get(op)
    vid = op.response.generated_videos[0].video
    client.files.download(file=vid)
    vid.save(out_path)
    print(f"   clip -> {os.path.basename(out_path)}", file=sys.stderr)


# ---------- 3. VOICE (ElevenLabs) ----------
def gen_voice(voice_id, lines, workdir):
    """Per-line TTS -> concatenated wav + caption timing events."""
    model = "eleven_multilingual_v2"
    sil = os.path.join(workdir, "sil.wav")
    run(["ffmpeg","-y","-f","lavfi","-i","anullsrc=r=44100:cl=mono","-t",str(GAP),sil])
    concat, events, cursor = [], [], 0.0
    for i, line in enumerate(lines):
        mp3 = os.path.join(workdir, f"l{i}.mp3"); wav = os.path.join(workdir, f"l{i}.wav")
        body = json.dumps({"text": line, "model_id": model,
            "voice_settings": {"stability":0.55,"similarity_boost":0.75,"style":0.0,"use_speaker_boost":True}}).encode()
        req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            data=body, headers={"xi-api-key": ELEVEN_KEY, "Content-Type":"application/json"})
        with urllib.request.urlopen(req, timeout=120) as r, open(mp3,"wb") as f:
            f.write(r.read())
        run(["ffmpeg","-y","-i",mp3,"-ar","44100","-ac","1",wav])
        d = dur(wav); events.append((cursor, cursor+d, line)); concat.append(wav); cursor += d
        if i < len(lines)-1: concat.append(sil); cursor += GAP
        print(f"   voice {i+1}/{len(lines)} ({d:.1f}s)", file=sys.stderr)
    listf = os.path.join(workdir,"a.txt"); open(listf,"w").write("".join(f"file '{w}'\n" for w in concat))
    full = os.path.join(workdir,"full.wav")
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",listf,"-c","copy",full])
    return full, events


# ---------- 4. ASSEMBLE (ffmpeg) ----------
def normalize(src, seg, is_video):
    vf = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"setsar=1,fps={FPS},format=yuv420p")
    if is_video:
        run(["ffmpeg","-y","-i",src,"-an","-vf",vf,"-c:v","libx264","-pix_fmt","yuv420p","-r",str(FPS),seg])
    else:
        run(["ffmpeg","-y","-loop","1","-t","3.8","-i",src,"-vf",vf,"-c:v","libx264","-pix_fmt","yuv420p","-r",str(FPS),seg])

def xfade_chain(segs, workdir):
    durs = [dur(s) for s in segs]
    inputs = []
    for s in segs: inputs += ["-i", s]
    fc, prev, running = [], "0:v", durs[0]
    for i in range(1, len(segs)):
        off = running - XF; out = f"v{i}"
        fc.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[{out}]")
        prev = out; running = running + durs[i] - XF
    montage = os.path.join(workdir, "montage.mp4")
    run(["ffmpeg","-y"]+inputs+["-filter_complex",";".join(fc),"-map",f"[{prev}]",
         "-c:v","libx264","-pix_fmt","yuv420p",montage])
    return montage

def wrap(draw, text, fnt, maxw):
    words=text.split(); lines=[]; cur=""
    for w in words:
        t=(cur+" "+w).strip()
        if draw.textlength(t,font=fnt)<=maxw: cur=t
        else: lines.append(cur); cur=w
    if cur: lines.append(cur)
    return lines

def caption_png(text, path):
    img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    fnt=ImageFont.truetype(FONT,56); lines=wrap(d,text,fnt,W-180); lh=78
    y=H-360-lh*len(lines)
    for ln in lines:
        d.text((W//2,y),ln,font=fnt,anchor="ma",fill=(255,255,255,255),stroke_width=4,stroke_fill=(0,0,0,255)); y+=lh
    img.save(path)

def assemble(montage, voice_wav, events, workdir, out_path):
    vdur, adur = dur(montage), dur(voice_wav)
    final = max(vdur, adur) + 0.3
    pad = final - vdur
    av = os.path.join(workdir,"av.mp4")
    vf = f"[0:v]tpad=stop_mode=clone:stop_duration={pad:.2f}[v]" if pad>0.05 else "[0:v]copy[v]"
    run(["ffmpeg","-y","-i",montage,"-i",voice_wav,"-filter_complex",f"{vf};[1:a]apad[a]",
         "-map","[v]","-map","[a]","-t",f"{final:.2f}","-c:v","libx264","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","192k",av])
    # caption overlays (PIL PNGs — no libass dependency)
    pngs=[]
    for i,(a,b,txt) in enumerate(events):
        p=os.path.join(workdir,f"c{i}.png"); caption_png(txt,p); pngs.append((p,a,b))
    inputs=["-i",av]
    for p,_,_ in pngs: inputs+=["-i",p]
    chains=[]; prev="0:v"
    for i,(p,a,b) in enumerate(pngs):
        out=f"t{i}"; chains.append(f"[{prev}][{i+1}:v]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[{out}]"); prev=out
    run(["ffmpeg","-y"]+inputs+["-filter_complex",";".join(chains),"-map",f"[{prev}]","-map","0:a",
         "-c:v","libx264","-pix_fmt","yuv420p","-c:a","copy","-movflags","+faststart",out_path])


# ---------- orchestrator ----------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("config")
    ap.add_argument("--skip-images", action="store_true", help="reuse scene.image paths, no Gemini")
    ap.add_argument("--skip-video", action="store_true", help="reuse scene.clip paths, no Veo")
    a = ap.parse_args()
    cfg = json.load(open(a.config))
    aspect = cfg.get("aspect","9:16")
    assets = os.path.join(os.path.dirname(os.path.abspath(a.config)), cfg["title"] + "_assets")
    os.makedirs(assets, exist_ok=True)
    work = tempfile.mkdtemp(prefix="pipe_")
    client = None
    if not (a.skip_images and a.skip_video):
        if not GEMINI_KEY: sys.exit("Missing GEMINI_API_KEY (~/.config/gemini/.env)")
        from google import genai
        client = genai.Client(api_key=GEMINI_KEY)
    if not ELEVEN_KEY: sys.exit("Missing ELEVENLABS_API_KEY (~/.config/elevenlabs/.env)")

    scenes = cfg["scenes"]
    # 1. images
    print("[1/4] images", file=sys.stderr)
    for i, sc in enumerate(scenes):
        if a.skip_images or sc.get("image"):
            sc["image"] = sc["image"]; continue
        out = os.path.join(assets, f"img_{i}.png")
        gen_image(client, cfg.get("image_model","imagen-4.0-generate-001"), sc["image_prompt"], out, aspect)
        sc["image"] = out

    # 2. video (morph clips between consecutive scenes)
    print("[2/4] veo clips", file=sys.stderr)
    clips = []
    if a.skip_video:
        clips = [sc["clip"] for sc in scenes if sc.get("clip")]
    elif cfg.get("morph", True):
        for i in range(len(scenes)-1):
            out = os.path.join(assets, f"clip_{i}.mp4")
            gen_clip(client, cfg.get("veo_model","veo-3.0-fast-generate-001"),
                     scenes[i].get("anim_prompt","slow cinematic restoration, gradual rebuild"),
                     scenes[i]["image"], scenes[i+1]["image"], out, aspect)
            clips.append(out)
    else:
        for i, sc in enumerate(scenes):
            out = os.path.join(assets, f"clip_{i}.mp4")
            gen_clip(client, cfg.get("veo_model","veo-3.0-fast-generate-001"),
                     sc.get("anim_prompt","slow cinematic camera push"), sc["image"], None, out, aspect)
            clips.append(out)

    # 3. voice
    print("[3/4] voice", file=sys.stderr)
    voice_wav, events = gen_voice(cfg.get("voice_id","pNInz6obpgDQGcFmaJgB"), cfg["voiceover_lines"], work)

    # 4. assemble
    print("[4/4] assemble", file=sys.stderr)
    segs = []
    for i, c in enumerate(clips):
        seg = os.path.join(work, f"s{i}.mp4"); normalize(c, seg, is_video=True); segs.append(seg)
    montage = xfade_chain(segs, work)
    out_path = os.path.join(assets, cfg["title"] + "_final.mp4")
    assemble(montage, voice_wav, events, work, out_path)
    print(f"\nDONE -> {out_path}  ({dur(out_path):.1f}s)")


if __name__ == "__main__":
    main()

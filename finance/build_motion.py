#!/usr/bin/env python3
"""WealthDelay MOTION builder — code-driven animated diagrams via the shared
Remotion motion-engine (lifeorama/motion-engine), WealthDelay brand.

Replaces the static-PNG + Ken-Burns approach (build_batch.py / build_compound.py)
with real animated finance diagrams: growth curves that draw on, bars that rise,
numbers that count up, milestone timelines. Same Zod scene schema as LOR — this
just renders with theme="wealthdelay" (cream / forest-green / gold, Plus Jakarta
Sans) at vertical 1080x1920, narrated with the WealthDelay brand voice
(edge-tts Brian, the build_batch.py workhorse).

  python3 build_motion.py <id>          # render motion_scripts/<id>.json -> out/<id>.mp4
  python3 build_motion.py --list
  python3 build_motion.py <id> --landscape   # 1920x1080 instead of vertical
"""
import os, sys, json, glob, shutil, subprocess, tempfile

DIR        = os.path.dirname(os.path.abspath(__file__))
OUTDIR     = f"{DIR}/out"
SCRIPTDIR  = f"{DIR}/motion_scripts"
ENGINE_DIR = os.path.normpath(f"{DIR}/../lifeorama/motion-engine")
os.makedirs(OUTDIR, exist_ok=True)

VOICE = "en-US-BrianNeural"   # WealthDelay brand voice (matches build_batch.py)
RATE  = "+10%"
SPEED = 1.25                  # extra tempo on top of RATE — Shorts pace (1x == old 1.25x playback)

def run(c):
    subprocess.run(c, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def dur(p):
    return float(subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration",
         "-of","default=nw=1:nk=1", p],
        capture_output=True, text=True).stdout.strip())

def vo(text, wav):
    """edge-tts Brian -> mp3 -> mono 44.1k wav (what Remotion consumes)."""
    mp3 = wav.replace(".wav", ".mp3")
    run(["edge-tts","--voice",VOICE,"--rate",RATE,"--text",text,"--write-media",mp3])
    run(["ffmpeg","-y","-i",mp3,"-af",f"atempo={SPEED}","-ar","44100","-ac","1",wav])

def render(e, landscape=False):
    eid    = e["id"]
    scenes = e["scenes"]
    W, H   = (1920, 1080) if landscape else (1080, 1920)
    vertical = not landscape

    tmp     = tempfile.mkdtemp(prefix=f"wdmo_{eid}_")
    pub_dir = f"{ENGINE_DIR}/public/audio/{eid}"
    os.makedirs(pub_dir, exist_ok=True)

    remotion_scenes = []
    n = len(scenes)
    for i, scene in enumerate(scenes):
        print(f"   scene {i+1}/{n}: narrating + measuring...", flush=True)
        wav = f"{tmp}/v{i}.wav"
        vo(scene["narration"], wav)
        d = dur(wav) + 0.25            # small tail so captions don't clip
        shutil.copyfile(wav, f"{pub_dir}/scene{i}.wav")
        remotion_scenes.append({
            "narration":   scene["narration"],
            "audioFile":   f"audio/{eid}/scene{i}.wav",
            "durationSec": d,
            "visual":      scene["visual"],
        })
        print(f"   scene {i+1}/{n} ready ({d:.1f}s)", flush=True)

    props = {"scenes": remotion_scenes, "width": W, "height": H,
             "vertical": vertical, "theme": "wealthdelay"}
    props_path = f"{tmp}/props.json"
    json.dump(props, open(props_path, "w"))

    final = f"{OUTDIR}/{eid}.mp4"
    print("   rendering with Remotion...", flush=True)
    result = subprocess.run(
        ["npx","remotion","render","src/index.ts","SceneVideo", final,
         f"--props={props_path}"],
        cwd=ENGINE_DIR, capture_output=True, text=True)

    shutil.rmtree(pub_dir, ignore_errors=True)
    shutil.rmtree(tmp, ignore_errors=True)

    if result.returncode != 0:
        raise RuntimeError(f"Remotion render failed:\n{result.stdout[-2500:]}\n{result.stderr[-2500:]}")

    print(f"\nDONE -> {final}  ({dur(final):.1f}s)")
    return final

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h","--help"):
        sys.exit(__doc__)
    if sys.argv[1] == "--list":
        for p in sorted(glob.glob(f"{SCRIPTDIR}/*.json")):
            print(os.path.splitext(os.path.basename(p))[0])
        sys.exit(0)
    landscape = "--landscape" in sys.argv
    pos = [a for a in sys.argv[1:] if not a.startswith("--")]
    eid = pos[0]
    path = f"{SCRIPTDIR}/{eid}.json"
    if not os.path.exists(path):
        sys.exit(f"No script: {path}")
    e = json.load(open(path)); e["id"] = eid
    render(e, landscape=landscape)

#!/usr/bin/env python3
"""Life-O-Rama VISUAL builder — Remotion diagrams + subtitle captions + Kokoro TTS.

Each scene: a code-drawn animated diagram (labeled arrows, before/after
compares, simple figures) matched to the scene's "visual" spec, white
subtitle caption at the bottom, Kokoro narration. No stock photos.

  python3 build_motion.py <id>            # render out/<id>.mp4
  python3 build_motion.py <id> --short    # vertical 1080x1920 Shorts cut
  python3 build_motion.py <id> --upload   # render + schedule to LOR channel
  python3 build_motion.py --list
"""
import os, sys, json, glob, shutil, subprocess, tempfile

DIR        = os.path.dirname(os.path.abspath(__file__))
OUTDIR     = f"{DIR}/out"
SCRIPTDIR  = f"{DIR}/scripts"
ENGINE_DIR = f"{DIR}/motion-engine"
os.makedirs(OUTDIR, exist_ok=True)
sys.path.insert(0, DIR)
from build_explainer import vo, auto_upload

# ── canvas ───────────────────────────────────────────────────────────────────
W, H = 1920, 1080
VERTICAL = False

def set_orientation(v):
    global W, H, VERTICAL
    VERTICAL = v
    W, H = (1080, 1920) if v else (1920, 1080)

def dur(p):
    return float(subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration",
         "-of","default=nw=1:nk=1", p],
        capture_output=True, text=True).stdout.strip())

# ── top-level ─────────────────────────────────────────────────────────────────
def render(e, upload=False, short=False):
    scenes = e["scenes"]
    if short:
        if "short_scenes" in e:
            scenes = [scenes[i] for i in e["short_scenes"] if i < len(scenes)]
        else:
            scenes = scenes[:12]

    tmp     = tempfile.mkdtemp(prefix=f"lormo_{e['id']}_")
    n       = len(scenes)
    suffix  = "short" if short else "full"
    pub_dir = f"{ENGINE_DIR}/public/audio/{e['id']}_{suffix}"
    os.makedirs(pub_dir, exist_ok=True)

    remotion_scenes = []
    for i, scene in enumerate(scenes):
        print(f"   scene {i+1}/{n}: narrating + measuring...", flush=True)
        wav = f"{tmp}/v{i}.wav"
        vo(scene["narration"], wav)
        duration_sec = dur(wav)

        audio_rel = f"{e['id']}_{suffix}/scene{i}.wav"
        shutil.copyfile(wav, f"{pub_dir}/scene{i}.wav")

        remotion_scenes.append({
            "narration":   scene["narration"],
            "audioFile":   f"audio/{audio_rel}",
            "durationSec": duration_sec,
            "visual":      scene["visual"],
        })
        print(f"   scene {i+1}/{n} ready ({duration_sec:.1f}s)", flush=True)

    brand = e.get("brand", None)
    props = {"scenes": remotion_scenes, "width": W, "height": H, "vertical": VERTICAL}
    if brand:
        props["theme"] = brand
    props_path = f"{tmp}/props.json"
    json.dump(props, open(props_path, "w"))

    out_suffix = "_short" if short else ""
    final = f"{OUTDIR}/{e['id']}{out_suffix}.mp4"

    print(f"   rendering with Remotion...", flush=True)
    result = subprocess.run(
        ["npx", "remotion", "render", "src/index.ts", "SceneVideo", final,
         f"--props={props_path}"],
        cwd=ENGINE_DIR, capture_output=True, text=True)

    shutil.rmtree(pub_dir, ignore_errors=True)

    if result.returncode != 0:
        raise RuntimeError(f"Remotion render failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}")

    d = dur(final)
    print(f"\nDONE -> {final}  ({d:.1f}s)")

    if short and d > 61:
        print(f"   ⚠️  {d:.0f}s > 60s — trim short_scenes in JSON")

    if upload:
        import tempfile as _tf, os as _os
        _desc = e.get("description", e.get("title", e["id"]))
        _tmp  = _tf.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
        _tmp.write(_desc); _tmp.close()
        auto_upload(e, final, _tmp.name)
        _os.unlink(_tmp.name)
    else:
        print("   (no upload — review first, then --upload)")
    return final

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ("-h","--help"):
        sys.exit(__doc__)
    if sys.argv[1] == "--list":
        for p in sorted(glob.glob(f"{SCRIPTDIR}/*.json")):
            print(os.path.splitext(os.path.basename(p))[0])
        sys.exit(0)

    short  = "--short"  in sys.argv
    upload = "--upload" in sys.argv
    set_orientation(short)

    pos  = [a for a in sys.argv[1:] if not a.startswith("--")]
    eid  = pos[0]
    path = f"{SCRIPTDIR}/{eid}.json"
    if not os.path.exists(path):
        sys.exit(f"No script: {path}")
    e = json.load(open(path)); e["id"] = eid
    render(e, upload=upload, short=short)

#!/usr/bin/env python3
"""Assemble the temple ruin->glory short locally from 1 mp4 + 8 stills. No paid API."""
import os, subprocess, tempfile, glob, sys

DL = "/Users/satishkosaraju/Downloads"
OUT = "/Users/satishkosaraju/EmpireOS/projects/bizshorts/temple_restore_silent.mp4"
W, H, FPS = 1080, 1920, 30
STILL = 3.8        # seconds per still
OPEN = 5.0         # seconds of the animated opener
XF = 0.8           # crossfade seconds

# ordered scene -> filename prefix (the animated mp4 is scene 1)
ORDER = [
    ("MP4", "Dust_drifting"),                       # scene 1 ruined (animated)
    ("IMG", "Same_temple,_faint_golden_light"),     # 2
    ("IMG", "Same_temple,_cracks_sealing"),         # 3
    ("IMG", "Same_temple_fully_rebuilt"),           # 4
    ("IMG", "Same_temple_with_vivid_paint"),        # 5
    ("IMG", "Dark_temple_sanctum"),                 # 6
    ("IMG", "Temple_courtyard_filling_with_priests"),  # 7
    ("IMG", "Ornate_main_shrine_glowing"),          # 8
    ("IMG", "Wide_cinematic_reveal"),               # 9
]

VF = (f"scale={W}:{H}:force_original_aspect_ratio=increase,"
      f"crop={W}:{H},setsar=1,fps={FPS},format=yuv420p")


def find(prefix):
    hits = glob.glob(os.path.join(DL, prefix + "*"))
    if not hits:
        sys.exit(f"MISSING: {prefix}*")
    return hits[0]


def main():
    tmp = tempfile.mkdtemp(prefix="restore_")
    segs, durs = [], []
    for i, (kind, prefix) in enumerate(ORDER):
        src = find(prefix)
        seg = os.path.join(tmp, f"s{i}.mp4")
        if kind == "MP4":
            cmd = ["ffmpeg", "-y", "-i", src, "-t", str(OPEN), "-an",
                   "-vf", VF, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                   "-r", str(FPS), seg]
            durs.append(OPEN)
        else:
            cmd = ["ffmpeg", "-y", "-loop", "1", "-t", str(STILL), "-i", src,
                   "-vf", VF, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                   "-r", str(FPS), seg]
            durs.append(STILL)
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        segs.append(seg)
        print(f"  normalized scene {i+1}/{len(ORDER)}", file=sys.stderr)

    # build xfade chain
    inputs = []
    for s in segs:
        inputs += ["-i", s]
    fc = []
    prev = "0:v"
    running = durs[0]
    for i in range(1, len(segs)):
        off = running - XF
        out = f"v{i}"
        fc.append(f"[{prev}][{i}:v]xfade=transition=fade:duration={XF}:offset={off:.3f}[{out}]")
        prev = out
        running = running + durs[i] - XF
    filt = ";".join(fc)
    cmd = ["ffmpeg", "-y"] + inputs + ["-filter_complex", filt,
           "-map", f"[{prev}]", "-c:v", "libx264", "-pix_fmt", "yuv420p",
           "-movflags", "+faststart", OUT]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", OUT], capture_output=True, text=True).stdout.strip()
    print(f"DONE -> {OUT}  ({float(dur):.1f}s)")


if __name__ == "__main__":
    main()

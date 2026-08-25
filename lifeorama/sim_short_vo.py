#!/usr/bin/env python3
"""VO for the WealthDelay Short: 'Renters got richer than homeowners' (contrarian hook)."""
import os, json, subprocess, urllib.request, urllib.error, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_WAV = os.path.join(HERE, "motion-engine", "public", "audio", "sim", "short_vo.wav")
os.makedirs(os.path.dirname(OUT_WAV), exist_ok=True)

raw = open(os.path.expanduser("~/.config/elevenlabs/.env")).read().strip()
KEY = raw.split("=", 1)[1].strip()
VOICE = "JBFqnCBsd6RMkjVDRZzb"  # George

SCRIPT = (
    "Renters got richer than homeowners. During the 2008 crash. "
    "It didn't last. "
    "Thirty years later, buyers ended up two hundred seventy thousand dollars ahead. "
    "Same salary. Same starting line. Completely different endings. "
    "Which one are you?"
)


def tts(text, out_mp3, model):
    vs = {"stability": 0.42, "similarity_boost": 0.75, "style": 0.2, "use_speaker_boost": True, "speed": 1.15}
    body = json.dumps({"text": text, "model_id": model, "voice_settings": vs}).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}",
        data=body, headers={"xi-api-key": KEY, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        open(out_mp3, "wb").write(r.read())


mp3 = OUT_WAV.replace(".wav", ".mp3")
try:
    tts(SCRIPT, mp3, "eleven_multilingual_v2")
except urllib.error.HTTPError as e:
    print("VOICE FAIL", e.code, e.read()[:300].decode(errors="ignore"), file=sys.stderr)
    sys.exit(1)

subprocess.run(["ffmpeg", "-y", "-i", mp3, "-ar", "44100", "-ac", "1", OUT_WAV], check=True, capture_output=True)
dur = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration", "-of", "csv=p=0", OUT_WAV],
                     capture_output=True, text=True).stdout.strip()
print(f"VO OK -> {OUT_WAV}")
print(f"DURATION_SEC={dur}")

#!/usr/bin/env python3
"""Generate the ElevenLabs voiceover for the Life-O-Rama simulation sample.
Writes a mono 44.1k WAV into motion-engine/public/audio/sim/vo.wav and prints duration."""
import os, json, subprocess, urllib.request, urllib.error, sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_WAV = os.path.join(HERE, "motion-engine", "public", "audio", "sim", "vo.wav")
os.makedirs(os.path.dirname(OUT_WAV), exist_ok=True)

raw = open(os.path.expanduser("~/.config/elevenlabs/.env")).read().strip()
KEY = raw.split("=", 1)[1].strip()

VOICE = "JBFqnCBsd6RMkjVDRZzb"  # ElevenLabs "George" — deep documentary narrator, not the overused "Adam" default

SCRIPT = (
    "Here's a question families argue about for years. "
    "A thousand households, all earning the same sixty thousand dollar salary. "
    "Half of them rent, and invest the difference in the market. Half of them buy a home. "
    "We ran all thirty years, using long run historical averages for stocks and housing. Watch every family at once. "
    "At first, they move together. But slowly, the buyers pull ahead. "
    "Each mortgage payment quietly builds equity, and the home drifts upward. "
    "Then, year seventeen. The crash. In this model, markets fall by about half. "
    "Watch the renters' portfolios plunge. Home prices sink too. "
    "But the buyers aren't selling, so they simply hold on. "
    "And then, the recovery. Both sides climb back. "
    "Thirty years in, here is the actual trade-off. "
    "The typical buyer ends up richer on paper — just over one and a half million dollars. "
    "But almost all of it is locked inside one house. To spend any of it, they'd have to sell. "
    "The typical renter ends up close behind — just over one point two million. "
    "And every single dollar of it is liquid, ready to spend tomorrow if they needed to. "
    "So the real question was never just rent or buy. "
    "It was this: do you want more wealth you can't touch, or less wealth you can spend today? "
    "A thousand families. One question. This is Life O Rama."
)


def tts(text, out_mp3, model):
    vs = {"stability": 0.42, "similarity_boost": 0.75, "style": 0.15, "use_speaker_boost": True, "speed": 1.15}
    body = json.dumps({"text": text, "model_id": model, "voice_settings": vs}).encode()
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE}",
        data=body,
        headers={"xi-api-key": KEY, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as r:
        open(out_mp3, "wb").write(r.read())


mp3 = OUT_WAV.replace(".wav", ".mp3")
model = "eleven_multilingual_v2"
try:
    tts(SCRIPT, mp3, model)
except urllib.error.HTTPError as e:
    print("VOICE FAIL", e.code, e.read()[:300].decode(errors="ignore"), file=sys.stderr)
    sys.exit(1)

subprocess.run(["ffmpeg", "-y", "-i", mp3, "-ar", "44100", "-ac", "1", OUT_WAV],
               check=True, capture_output=True)
dur = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
                      "-of", "csv=p=0", OUT_WAV], capture_output=True, text=True).stdout.strip()
print(f"VO OK ({model}) -> {OUT_WAV}")
print(f"DURATION_SEC={dur}")

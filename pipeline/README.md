# Restoration-Short Pipeline

One config → a finished faceless short:
**Gemini (images) → Veo (morph clips) → ElevenLabs (voice) → ffmpeg (assemble + captions)**

## One-time setup

```bash
# 1. deps (in the Terminal app)
pip3 install google-genai pillow      # ffmpeg/ffprobe already installed

# 2. keys (each on its own line, locked to your user)
mkdir -p ~/.config/gemini && printf 'GEMINI_API_KEY=YOUR_KEY\n' > ~/.config/gemini/.env && chmod 600 ~/.config/gemini/.env
# ElevenLabs key already saved at ~/.config/elevenlabs/.env
```

Get a Gemini key at **aistudio.google.com → "Get API key"**, and enable billing (Veo is paid).

## Run

```bash
cd ~/EmpireOS/projects/bizshorts/pipeline

# Full auto (generate everything):
python3 pipeline.py config.temple.json

# Reuse the 9 temple images you already made (skip image cost, only pay Veo morphs):
python3 pipeline.py config.temple.json --skip-images

# Reuse already-generated clips, just re-voice/re-assemble (free):
python3 pipeline.py config.temple.json --skip-video
```

Output: `temple_restore_assets/temple_restore_final.mp4` (voiced + captioned, 9:16).

## Make a NEW video

Copy `config.temple.json`, change `title`, the 9 `scenes` (image prompts or paths + anim prompts),
and the `voiceover_lines`. Run it. That's the whole workflow.

## Cost per run (Veo dominates; voice ≈ pennies; assembly free)

| Veo tier (`veo_model`) | ~40s video |
|---|---|
| `veo-3.1-fast-...` | ~$6 (recommended) |
| `veo-3.0-fast-generate-001` | ~$6 |
| quality tier | ~$16 |

Confirm live model IDs + rates: https://ai.google.dev/gemini-api/docs/pricing

## Notes
- `morph: true` makes Veo generate the rebuild *between* consecutive scene images
  (first-frame → last-frame). If your Veo model doesn't support `last_frame`, it
  auto-falls back to image-to-video on each scene.
- Captions are rendered as PNG overlays (this machine's ffmpeg has no libass).
- Watermark: Veo output via the paid API is watermark-free (no "Veo" tag like the free Flow app).
```

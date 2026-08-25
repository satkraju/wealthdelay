# Life-O-Rama (LOR) — Channel Operating Doctrine

Everyday science explainer "encyclopedia." Format: why/how curiosity questions
(why mirrors flip, why ships don't sink, why the sky is blue), 2–8min, all ages, faceless.

---

## Algorithm Moat Doctrine (RATIFIED · 2026-07-03)

**Every produced element — idea, hook, visual, voice, script, title, thumbnail, pacing —
must be evaluated against what demonstrably favors the YouTube algorithm before it is
considered "done." This is a hard gate, not a style preference.**

Nothing ships because it looks good. It ships because it is built, with evidence, to win
retention, CTR, and session value — the signals YouTube's system actually optimizes for.

Shared with Project TITAN. Full five-surface evaluation in `projects/titan/DOCTRINE_ALGO_MOAT.md`.
Apply that doctrine, verbatim, to every LOR asset.

### The five surfaces — check every episode before render/publish

1. **Idea/topic** — Real search demand? Evergreen or decaying trend?
2. **Hook (first 3–8s)** — Does it open a curiosity loop? Would a stranger stop scrolling?
3. **Visual** — Does it sustain watch time, or is it just decoration?
4. **Voice** — Distinct enough to not read as generic AI narration?
5. **Script/pacing/conclusion** — ONE clear repeatable takeaway a viewer could say back to a friend?

Evidence hierarchy: official YouTube docs → Creator Insider / YT engineering statements
→ our own analytics → case studies. Never invented data.

---

## Emotional Arc (mandatory on every script)

Every episode must alternate emotion beats. Science explainer pattern:
**curiosity → surprise/shock → "aha" relief → new curiosity**

Flat narration = passive viewing = no retention. Each beat resets viewer attention.

---

## Content System

- **Audience:** 45–54, US-based. The IDEA is everything. Power = curiosity gap.
- **Title formula:** "Why [everyday thing] [surprising twist]?"
- **Engine:** Remotion animated diagrams from Zod-validated scene schema — NOT stock photos
- **TTS:** Kokoro
- **Script format:** `projects/bizshorts/lifeorama/scripts/<id>.json`
- **Upload cadence target:** Mon/Wed/Fri 15:00 UTC
- **Auto-dub:** Enable on every upload (YouTube Studio → Settings → Channel → Advanced → Auto dub)

---

## Upload Rules

1. **Self-verify EVERY video via `/watch` before uploading.** No exceptions.
2. **Verify channel identity via YouTube API before every upload.**
   Token: `~/.config/empireos/yt_token_lor.json`
   Reason: WealthDelay Shorts were posted on LOR in error once.
3. Upload as Unlisted → set Language to English → enable auto-dub → set Public.
4. Rename export file to a keyword before exporting.

---

## Channel Setup Checklist (do once)

1. Channel name + handle — standalone-clear
2. Logo — face or clean icon, NOT a random photo
3. Banner — simple and clean
4. Description — VidIQ → Research → search "science explained" / "psychology facts" / "human behavior" → 5 high-volume keywords → Abacus AI: "Write a YouTube channel description for an everyday science explainer channel. Keywords: [paste]. Tell viewers what they'll learn."
5. Channel keywords — YouTube Studio → Settings → Channel → paste same 5 keywords
6. Country — set to US
7. Auto-dub — YouTube Studio → Settings → Channel → Advanced Settings → Enable
8. Video watermark — subscriber button PNG → upload → set to "entire video"
9. Phone verification — Settings → Feature Eligibility → verify phone number

---

## Pre-Script Research (mandatory)

VidIQ → Research → Videos tab → find 5 channels in science/psychology niche → paste links
into Abacus AI competitor prompt → extract what's working BEFORE writing any script.

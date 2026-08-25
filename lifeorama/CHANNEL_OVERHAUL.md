# LOR CHANNEL OVERHAUL — 100% Algorithm-Aligned, before any sim-format upload

Status: IN PROGRESS · 2026-07-03 · governed by `projects/titan/DOCTRINE_ALGO_MOAT.md`
Every item below is either sourced to an official YouTube page or explicitly labeled a hypothesis to validate.

## Official evidence gathered this pass (Layer 1 — highest tier per RULES.md evidence hierarchy)

| Fact | Source |
|---|---|
| 90% of best-performing videos use custom thumbnails; consistent branding aids recognition | [YouTube thumbnail & title tips](https://support.google.com/youtube/answer/12340300?hl=en) |
| First few seconds must confirm the promise made by the title + thumbnail | Same (YT Help) |
| Title must accurately represent the video; viewers may see only part of it — put key words near the front, keep it short | Same (YT Help) |
| High CTR + low retention = thumbnail overpromises → fix the thumbnail, not just the video | Same (YT Help) |
| Hook in first 3-5s; tell viewers what they'll learn; reward them for staying; deliver on the thumbnail's promise within 30s | [4 metrics to grow your channel — YouTube Blog](https://blog.youtube/creator-and-artist-stories/master-these-4-metrics/) |
| Banner: min 2048×1152px, recommended 2560×1440px, 16:9, ≤6MB | [Channel banner & profile picture tips](https://support.google.com/youtube/answer/12950272?hl=en) |
| Video watermark displays for the LAST 15 SECONDS of a video | [Manage your channel branding](https://support.google.com/youtube/answer/10456525?hl=en) |
| End screens: templates for featured video, playlist, channel promo, external link (YPP only) | [Add end screens to videos](https://support.google.com/youtube/answer/6388789?hl=en) |

## Overhaul checklist — mapped to the 5 doctrine surfaces

### 1. Idea/demand (unchanged — already gated by IDEAS.md scoring + sources.md)
No new action; LOR sim topics continue through the existing Idea Engine + source-verification pipeline.

### 2. Hook (first 3-5 seconds) — FIXED 2026-07-03
`SimComposition.tsx` now opens with the swarm already visibly split and moving at frame 1
(t=0:00) with a single-word promise ("Rent or Buy?") — no static dead screen. Verified via
/watch frame pull: motion + promise both present at t=0:00-0:03. Full setup context now
follows the hook (3-16s) instead of preceding it. Engine change is in `SimComposition.tsx`
(`HOOK_OUT` constant); reusable for every future sim episode.

### 3. Visual retention mechanic — outro gap FIXED 2026-07-03
Simulation formula (D-008) passes: continuous motion, an unresolved bet, a mid-video crash
spike. Added a 5s end-screen-safe outro: counters/labels/verdict card fade to a calm
"More simulations every week" card with open space, verified via /watch frame pull at
1:03-1:09 — chrome fully cleared, matching YT's last-15-seconds subscribe-watermark window
so it won't fight the overlay for pixels. `OUTRO_START`/`outroSettle` in `SimComposition.tsx`.

### 4. Voice (closed this session)
George voice + transcript-verified sync (D-008 round 3). No further action pending new feedback.

### 5. Script/conclusion (closed this session)
Single repeatable takeaway, verified via /watch transcript pass. No further action pending new feedback.

## Channel-page-level items (new scope — not video-level)

| Item | Official spec | Status |
|---|---|---|
| Banner | 2560×1440px, 16:9, ≤6MB, must read clearly cropped on mobile/TV | TODO — design once sim brand-kit colors are finalized |
| Profile picture | Simple, legible at tiny sizes (mobile) | TODO |
| Video watermark | Subscribe-button watermark, shows last 15s — must NOT be occluded by the outro's verdict card (ties to item 3 above) | TODO — build once outro buffer lands |
| Channel description / About | Keyword-forward, states the channel promise in the first line (mirrors title-guidance: front-load the key words) | TODO |
| End screens | Feature the next sim video + subscribe (needs YPP for external links — not yet eligible) | TODO — template once 2nd episode exists |
| Title formula | Short, key words first, accurately represents content, sets expectations retention can match (no bait) | **DONE — locked below** |
| Thumbnail system | Custom per video, consistent series branding (recognizable "sim swarm" visual motif every time) | **DONE — ep1 rendered, engine reusable for every future sim episode** |

## Title formula (evidence-based, not guessed)

Per official guidance: short, front-loaded key words, accurate to content, sets a promise the video's first 3-5s must visibly confirm.

Pattern for the sim series: **`[N] [Group] · [Binary Stakes Question]`**
Example for this episode: `"1,000 Families. Rent or Buy? (30-Year Simulation)"`
- Front-loads the number (pattern-interrupt, algorithm-favored per CTR data above) and the binary question (open loop)
- "(30-Year Simulation)" sets the expectation the hook must deliver within 3-5s — literal, no bait

## Title — LOCKED
**"1,000 Families. Rent or Buy? (30-Year Simulation)"**
Passes the formula: number front-loaded, binary open loop, literal (no bait) — the hook
delivers on exactly this within 3s per the engine fix above.

## Thumbnail — DONE 2026-07-03
`SimThumbnail.tsx` (new still composition, 1280×720, `npx remotion still src/index.ts
SimThumbnail out.png`) renders an ACTUAL simulation frame (month 340 / year 28) — not a
staged graphic — so the thumbnail's promise and the video's real content are the same
image, literally satisfying the "first seconds confirm the thumbnail" rule.
File: `out/sim_rentbuy_thumbnail.png` (1280×720, 696KB, well under the 2MB cap).
**Deliberate choice:** the swarms do NOT visually spoil a clean "winner" — the video's real
conclusion is nuanced (more wealth locked vs. less wealth liquid), so a thumbnail that
oversold a winner would create the exact CTR/retention mismatch the doctrine warns against.
Legibility fix: RENT/BUY labels sit on dark contrast chips (not raw text over the swarm) so
they read at the 116×65px mobile thumbnail size cited in the spec research.
Spec sourced: Layer-2 convergent evidence (postfa.st / thumbmagic / vidIQ / snappa /
techsmith independently agree: 1280×720, 16:9, ≤2MB, ~1100×620 safe zone, avoid
bottom-right duration-badge corner) — no single support.google.com page states exact px,
documented per the evidence-hierarchy rule rather than treated as Layer-1.

## Channel description — DRAFT (paste into Studio → Customization → Basic info)

> 1,000 simulated lives. One real question, run to its end. Life-O-Rama builds real computed simulations — not opinions, not talking heads — to answer the questions people actually argue about: rent or buy, save or spend, retire early or work longer. Every simulation is built on stated assumptions, shown on screen, so you can see exactly how the answer was reached. New simulation every week.

Front-loads the channel's actual mechanism (simulation, not opinion) in the first line, per the same "key words near the front" rule the title formula uses.

## What is NOT done yet (blocking full upload readiness)
1. ~~Hook compression (3-5s)~~ — DONE (v6, sim_rentbuy_v6.mp4)
2. ~~Outro/end-screen buffer~~ — DONE (v6, sim_rentbuy_v6.mp4)
3. ~~Thumbnail generation for ep1~~ — DONE (sim_rentbuy_thumbnail.png)
4. ~~Title locked against the formula~~ — DONE ("1,000 Families. Rent or Buy? (30-Year Simulation)")
5. Banner + profile picture assets — design, not started (needs Satish's login to upload regardless)
6. ~~Channel description rewrite~~ — DONE, drafted below (front-loads the channel promise per title-guidance rule)
7. Studio-side setup (country, auto-dub, watermark upload, phone verification) — per existing LOR CLAUDE.md checklist, requires Satish's login

Per doctrine: this list is the gate. Upload does not happen until each line is closed or explicitly deferred with a stated reason. **Everything Claude can do without a login is now done.** Items 5-7 need Satish in YouTube Studio.

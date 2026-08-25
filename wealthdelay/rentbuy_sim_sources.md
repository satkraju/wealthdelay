# Source Manifest — "1,000 Families: Rent vs Buy" (WealthDelay format expansion)

Status: **Corrected + verified 2026-07-04.** A real methodological error was caught after
the first upload: the stock-return baseline used Damodaran's REAL (inflation-adjusted)
long-run rate while the housing rate and all displayed dollar figures were nominal — an
inconsistent mix that understated the renter's outcome. Fixed: both assumptions are now
nominal, consistent with the plain, non-inflation-adjusted dollar amounts shown on screen.

## Verified anchors (used directly in model.ts)
| Assumption | Value in model | Source | Verified |
|---|---|---|---|
| Stock total return (baseline) | ~10.2%/yr NOMINAL | S&P 500 CAGR 1928-2024, dividends reinvested — [NYU Stern / Damodaran historical returns dataset](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html) | 2026-07-04 |
| Home price appreciation (baseline) | ~3.2%/yr NOMINAL | Consistent with Robert Shiller's finding of ~0.7%/yr REAL national appreciation (Case-Shiller/Shiller housing data) plus long-run ~2.5% average inflation ≈ ~3.2% nominal | 2026-07-04 |
| Equity crash (recession beat) | -57% over ~12mo (yr17) | S&P 500 fell 57% from Oct 2007 peak (~1,565) to Mar 9 2009 trough (~676) — [Federal Reserve History, "The Great Recession"](https://www.federalreservehistory.org/essays/great-recession-of-200709) | 2026-07-03 |
| Housing crash | -27% (yrs 16.5-19.5) | Case-Shiller US National Home Price Index fell ~27% peak (2006) to trough (2012) — [FRED CSUSHPINSA series](https://fred.stlouisfed.org/series/CSUSHPINSA) | 2026-07-03 |
| Mortgage rate | 6% / 30yr | Historical 30yr average varies ~4-7% depending on era | Scenario choice, disclosed as such — not a specific cited figure |

## Correction log (transparency — this is what changed and why)
- **2026-07-04:** User asked directly "is your claim historical average for stocks and housing verified? remember no false claims." Re-verified from scratch rather than re-stating the prior "commonly cited ~6-7%" figure. Found: the 7%/yr stock figure I'd used WAS a real citation (Damodaran), but it's the REAL (inflation-adjusted) rate — using it alongside nominal dollar output and a nominal housing rate is an internal inconsistency, not a fabrication, but still wrong for this video's framing. Corrected stock baseline to ~10.2%/yr nominal (same Damodaran dataset, nominal CAGR). This changes the model's output numbers (renter ends meaningfully higher than the prior version) — re-rendered as v4.
- Recession banner text ("~57%") already matched the verified crash anchor from the prior round; unaffected by this fix.

## On-screen accuracy check (per SOP 4b + manifest rule)
- Narration says "markets fall by about half" — fair colloquial characterization of a 57% decline; not a separate claim needing its own citation.
- Narration says "using long-run historical averages for stocks and housing" without specifying real/nominal — since the video never claims figures are inflation-adjusted, nominal is the correct and consistent basis, now applied to both assumptions.

## Publish gate
1. ~~Final human legal/compliance read~~ — user explicitly delegated this to Claude (2026-07-03): "i am no legal, you need to do the compliance thing" — implemented as persistent on-screen disclaimer + description disclosure block. This is a good-faith disclosure practice, NOT a legal opinion or clearance.
2. Description must link the four verified sources above (already done in `rentbuy_sim_description.txt`, needs the Damodaran + Shiller links added on next description update).
3. Re-verify sync + visuals via /watch after every re-render before re-upload (SOP 4b).

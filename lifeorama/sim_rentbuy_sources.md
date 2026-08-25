# Source Manifest — LOR sim sample "1,000 Families: Rent vs Buy"

Status: **SAMPLE / look-test.** The on-screen dollar figures are OUTPUT of an illustrative
model built on long-run historical *averages*, not a backtest of real households. The video
says so on screen ("Illustrative model on historical averages · not financial advice") and the
VO frames every number as model output ("in this model…", "the typical buyer ends near…").

## Anchor assumptions used by the model (model.ts)
| Assumption | Value in model | Real-world anchor it approximates | Verification status |
|---|---|---|---|
| Long-run stock total return | ~7%/yr real (1.07) | S&P 500 long-run real return commonly cited ~6–7% | ⚠️ VERIFY before publish (WebSearch rate-limited 2026-07-02) |
| Home price appreciation | ~3.2%/yr | Case-Shiller long-run US nominal ~3–4%/yr | ⚠️ VERIFY before publish |
| Recession equity drawdown | ~-45% over ~12mo (yr17) | S&P 2007→2009 peak-to-trough ≈ -50% to -57% | ⚠️ VERIFY exact figure |
| Housing crash | ~-30% (yrs17-19) | Case-Shiller national 2006→2012 ≈ -27% | ⚠️ VERIFY exact figure |
| Mortgage rate | 6% / 30yr | Historical 30yr avg varies ~4–7% | ⚠️ scenario choice, disclose |

## BLOCKING before this publishes to the channel
1. Replace illustrative constants with a specific, cited historical window (e.g. FRED S&P 500
   total-return series + Case-Shiller national index, a named 30-year span). Each series → a
   FRED/S&P/Census URL in this table, verified.
2. Re-verify the four ⚠️ anchors against primary sources (search was rate-limited this session).
3. Keep the on-screen disclaimer + "not financial advice"; add sources to the description.
4. Legal review of framing (YMYL): present as an illustration of a principle (dollar-cost
   investing discipline), never as personalized advice or a prediction.

Until items 1–3 are done, this asset is a STYLE/FORMAT sample only — not for upload.

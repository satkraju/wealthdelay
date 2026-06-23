#!/usr/bin/env python3
"""
Phase 7 — roll the NerdWallet-inspired / Apple-clean hero redesign (shipped on
the 8 Step-2 calculators via calc-common.css) out to the original 29
calculator pages, which carry their own duplicated inline <style> block
instead of the shared file.

Applies the same two find/replace edits made to calc-common.css:
  1. :root token block — adds --lime/--lime-dark, deepens shadows/radius,
     keeps --green identical so existing inline hex accents don't clash.
  2. nav + .tool-hero block — dark gradient hero, lime accent on highlighted
     phrase, glass badges — replacing the old flat white hero.

Idempotent: skips any file that already contains "--lime:". Run from repo root:

    python3 scripts/phase7-redesign-hero.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARKER = "--lime:"

PAGES = [
    "401k-contribution-calculator", "coffee-habit-true-cost", "daily-habit-true-cost-calculator",
    "buy-now-pay-later-true-cost", "debt-avalanche-vs-snowball", "car-loan-true-cost-calculator",
    "eating-out-vs-cooking-calculator", "compound-interest-early-vs-late", "credit-card-true-cost-calculator",
    "fire-number-calculator", "gym-membership-roi-calculator", "how-long-will-savings-last",
    "emergency-fund-calculator", "inflation-savings-erosion-calculator", "lifestyle-inflation-calculator",
    "index-fund-vs-stock-picking", "investment-fee-drag-calculator", "net-worth-target-calculator",
    "mortgage-overpayment-calculator", "luxury-car-opportunity-cost", "rent-vs-buy-calculator",
    "retirement-wealth-estimator", "smoking-financial-cost-calculator", "salary-negotiation-calculator",
    "side-hustle-investment-value", "student-loan-payoff-calculator", "streaming-subscription-cost-calculator",
    "true-cost-of-bigger-house", "true-hourly-rate-calculator",
]

OLD_ROOT = """  --ink: #1d1d1f; --ink2: #3d3d3f; --muted: #6e6e73; --faint: #aeaeb2;
  --border: rgba(0,0,0,0.08); --border-strong: rgba(0,0,0,0.12);
  --bg: #FDFAF5; --bg2: #F7F2E8; --white: #ffffff;
  --green: #16A34A; --green-dark: #14532D; --green-light: #F0FDF4; --green-mid: #BBF7D0;
  --red: #ff3b30; --amber: #ff9500; --blue: #0071e3; --purple: #8b5cf6;
  --font: 'Plus Jakarta Sans', system-ui, sans-serif;
  --shadow-xs: 0 1px 2px rgba(0,0,0,.04);
  --shadow-sm: 0 2px 8px rgba(0,0,0,.06),0 1px 3px rgba(0,0,0,.04);
  --shadow: 0 8px 32px rgba(0,0,0,.08),0 2px 8px rgba(0,0,0,.04);
  --radius: 18px; --radius-sm: 12px; --radius-xs: 8px;"""

NEW_ROOT = """  --ink: #1d1d1f; --ink2: #3d3d3f; --muted: #6e6e73; --faint: #aeaeb2;
  --border: rgba(0,0,0,0.08); --border-strong: rgba(0,0,0,0.12);
  --bg: #FDFAF5; --bg2: #F7F2E8; --white: #ffffff;
  --green: #16A34A; --green-dark: #0b3d2e; --green-light: #F0FDF4; --green-mid: #BBF7D0;
  --lime: #A3E635; --lime-dark: #65a30d;
  --red: #ff3b30; --amber: #ff9500; --blue: #0071e3; --purple: #8b5cf6;
  --font: 'Plus Jakarta Sans', system-ui, sans-serif;
  --shadow-xs: 0 1px 2px rgba(0,0,0,.04);
  --shadow-sm: 0 2px 10px rgba(0,0,0,.07),0 1px 3px rgba(0,0,0,.05);
  --shadow: 0 16px 48px rgba(11,61,46,.14),0 2px 8px rgba(0,0,0,.05);
  --radius: 20px; --radius-sm: 14px; --radius-xs: 10px;"""

OLD_HERO = """nav{position:sticky;top:0;z-index:200;height:52px;background:rgba(253,250,245,.92);backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);border-bottom:1px solid rgba(0,0,0,.1);display:flex;align-items:center;justify-content:space-between;padding:0 22px;}
.nav-left{display:flex;align-items:center;gap:16px;}
.nav-logo{display:flex;align-items:center;gap:9px;text-decoration:none;}
.logo-text{font-size:17px;font-weight:800;letter-spacing:-.03em;line-height:1;}
.logo-text .w{color:var(--green);}.logo-text .d{color:var(--ink);}
.nav-back{font-size:13px;color:var(--blue);text-decoration:none;font-weight:500;display:flex;align-items:center;gap:4px;}
.nav-back:hover{text-decoration:underline;}
.nav-pill{font-size:12px;font-weight:500;color:var(--green);background:var(--green-light);border:1px solid var(--green-mid);padding:4px 12px;border-radius:20px;display:flex;align-items:center;gap:5px;}
.nav-pill::before{content:'';width:6px;height:6px;background:var(--green);border-radius:50%;animation:pulse 2s ease infinite;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(.85)}}
.tool-hero{text-align:center;padding:64px 22px 52px;background:var(--white);border-bottom:1px solid var(--border);}
.tool-eyebrow{display:inline-flex;align-items:center;gap:8px;font-size:12px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.07em;margin-bottom:16px;}
.tool-eyebrow .cat{color:var(--green);}
.tool-h1{font-size:clamp(32px,5vw,56px);font-weight:700;letter-spacing:-.05em;line-height:1.05;color:var(--ink);max-width:720px;margin:0 auto 16px;}
.tool-h1 .red{color:var(--red);font-style:italic;}
.tool-h1 .green{color:var(--green);}
.tool-sub{font-size:clamp(16px,1.8vw,19px);color:var(--muted);max-width:520px;margin:0 auto 32px;line-height:1.6;letter-spacing:-.01em;}
.hero-badges{display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;}
.badge{font-size:13px;font-weight:500;color:var(--muted);background:var(--bg);border:1px solid var(--border);padding:6px 14px;border-radius:20px;}"""

NEW_HERO = """nav{position:sticky;top:0;z-index:200;height:56px;background:rgba(253,250,245,.85);backdrop-filter:saturate(180%) blur(20px);-webkit-backdrop-filter:saturate(180%) blur(20px);border-bottom:1px solid rgba(0,0,0,.08);display:flex;align-items:center;justify-content:space-between;padding:0 24px;}
.nav-left{display:flex;align-items:center;gap:16px;}
.nav-logo{display:flex;align-items:center;gap:9px;text-decoration:none;}
.logo-text{font-size:17px;font-weight:800;letter-spacing:-.03em;line-height:1;}
.logo-text .w{color:var(--green);}.logo-text .d{color:var(--ink);}
.nav-back{font-size:13px;color:var(--green-dark);text-decoration:none;font-weight:600;display:flex;align-items:center;gap:4px;transition:opacity .15s;}
.nav-back:hover{opacity:.7;}
.nav-pill{font-size:12px;font-weight:600;color:var(--green-dark);background:var(--green-light);border:1px solid var(--green-mid);padding:4px 12px;border-radius:20px;display:flex;align-items:center;gap:5px;}
.nav-pill::before{content:'';width:6px;height:6px;background:var(--lime-dark);border-radius:50%;animation:pulse 2s ease infinite;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(.85)}}
.tool-hero{text-align:center;padding:72px 22px 80px;background:radial-gradient(120% 140% at 15% 0%,#1a6b4c 0%,#0f4d39 45%,#0b3d2e 100%);position:relative;overflow:hidden;}
.tool-hero::after{content:'';position:absolute;inset:0;background:radial-gradient(60% 80% at 85% 100%,rgba(163,230,53,.16) 0%,transparent 70%);pointer-events:none;}
.tool-eyebrow{position:relative;display:inline-flex;align-items:center;gap:8px;font-size:12px;font-weight:600;color:rgba(255,255,255,.62);text-transform:uppercase;letter-spacing:.07em;margin-bottom:18px;}
.tool-eyebrow .cat{color:var(--lime);}
.tool-h1{position:relative;font-size:clamp(34px,5vw,58px);font-weight:800;letter-spacing:-.05em;line-height:1.05;color:#fff;max-width:740px;margin:0 auto 18px;}
.tool-h1 .red{color:#ff8a80;font-style:italic;}
.tool-h1 .green{color:var(--lime);}
.tool-sub{position:relative;font-size:clamp(16px,1.8vw,19px);color:rgba(255,255,255,.74);max-width:520px;margin:0 auto 32px;line-height:1.6;letter-spacing:-.01em;}
.hero-badges{position:relative;display:flex;align-items:center;justify-content:center;gap:8px;flex-wrap:wrap;}
.badge{font-size:13px;font-weight:600;color:rgba(255,255,255,.92);background:rgba(255,255,255,.10);border:1px solid rgba(255,255,255,.16);padding:7px 15px;border-radius:20px;backdrop-filter:blur(8px);}"""


def process(path: Path) -> str:
    text = path.read_text()
    if MARKER in text:
        return "have"
    if OLD_ROOT not in text or OLD_HERO not in text:
        return "no-match"
    text = text.replace(OLD_ROOT, NEW_ROOT, 1)
    text = text.replace(OLD_HERO, NEW_HERO, 1)
    path.write_text(text)
    return "patched"


def main() -> int:
    patched = already = missing = 0
    for slug in PAGES:
        path = REPO / f"{slug}.html"
        if not path.exists():
            print(f"  [WARN  ] {slug}.html not found")
            missing += 1
            continue
        result = process(path)
        if result == "patched":
            print(f"  [redo  ] {slug}.html")
            patched += 1
        elif result == "have":
            print(f"  [have  ] {slug}.html")
            already += 1
        else:
            print(f"  [WARN  ] {slug}.html: template text didn't match, skipped")
            missing += 1

    print()
    print(f"Patched: {patched}  Already had: {already}  Missing/warn: {missing}  Total: {len(PAGES)}")
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

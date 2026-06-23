#!/usr/bin/env python3
"""
Phase 8 — AEO backfill: add a "Quick Answer" box to the 25 calculator pages
that don't have one yet. This is the single block LLMs / Google AI Overviews
pull from when citing a page, so missing it is the biggest citability gap.

Does NOT invent new facts: extracts each page's own first FAQ question +
answer (already sourced, already in that page's FAQPage JSON-LD) and
reformats it into the same .wd-quick-answer markup used on the 8 Step-2
calculators. Inserted right after the .wd-hub-link div, matching the
established pattern.

Idempotent: skips any file that already has "wd-quick-answer". Run from
repo root:

    python3 scripts/phase8-quick-answer-backfill.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARKER = "wd-quick-answer"

PAGES = [
    "buy-now-pay-later-true-cost", "car-loan-true-cost-calculator", "coffee-habit-true-cost",
    "credit-card-true-cost-calculator", "daily-habit-true-cost-calculator", "debt-avalanche-vs-snowball",
    "eating-out-vs-cooking-calculator", "gym-membership-roi-calculator", "how-long-will-savings-last",
    "index-fund-vs-stock-picking", "inflation-savings-erosion-calculator", "investment-fee-drag-calculator",
    "lifestyle-inflation-calculator", "luxury-car-opportunity-cost", "mortgage-overpayment-calculator",
    "net-worth-target-calculator", "retirement-wealth-estimator", "salary-negotiation-calculator",
    "side-hustle-investment-value", "smoking-financial-cost-calculator", "streaming-subscription-cost-calculator",
    "student-loan-payoff-calculator", "true-cost-of-bigger-house", "true-hourly-rate-calculator",
]

HUB_LINK_RE = re.compile(r'(<div class="wd-hub-link"[^>]*>.*?</div>\n?)', re.DOTALL)
FIRST_FAQ_RE = re.compile(
    r'<div class="faq-item"><div class="faq-q" onclick="toggleFaq\(this\)">(.*?)<div class="faq-ico">\+</div></div>'
    r'<div class="faq-a">(.*?)</div></div>',
    re.DOTALL,
)


def quick_answer_html(question: str, answer: str) -> str:
    return (
        '<section class="wd-quick-answer" style="max-width:760px;margin:24px auto 0;padding:24px;'
        'background:#F0FDF4;border:1px solid #BBF7D0;border-radius:14px;'
        "font-family:'Plus Jakarta Sans',system-ui,sans-serif;\">"
        '<div style="font-size:11px;font-weight:700;color:#16A34A;text-transform:uppercase;'
        'letter-spacing:.08em;margin-bottom:10px;">Quick Answer</div>'
        f'<p style="font-size:17px;line-height:1.55;color:#1d1d1f;margin:0;font-weight:500;">'
        f"<strong>{question.strip()}</strong> {answer.strip()}</p>"
        "</section>\n"
    )


def process(path: Path) -> str:
    text = path.read_text()
    if MARKER in text:
        return "have"
    hub_match = HUB_LINK_RE.search(text)
    faq_match = FIRST_FAQ_RE.search(text)
    if not hub_match or not faq_match:
        return "no-match"
    qa_html = quick_answer_html(faq_match.group(1), faq_match.group(2))
    insert_at = hub_match.end()
    new_text = text[:insert_at] + qa_html + text[insert_at:]
    path.write_text(new_text)
    return "inserted"


def main() -> int:
    inserted = already = missing = 0
    for slug in PAGES:
        path = REPO / f"{slug}.html"
        if not path.exists():
            print(f"  [WARN  ] {slug}.html not found")
            missing += 1
            continue
        result = process(path)
        if result == "inserted":
            print(f"  [added ] {slug}.html")
            inserted += 1
        elif result == "have":
            print(f"  [have  ] {slug}.html")
            already += 1
        else:
            print(f"  [WARN  ] {slug}.html: no hub-link or FAQ match, skipped")
            missing += 1

    print()
    print(f"Inserted: {inserted}  Already had: {already}  Missing/warn: {missing}  Total: {len(PAGES)}")
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

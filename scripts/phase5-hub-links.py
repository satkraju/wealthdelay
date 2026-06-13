#!/usr/bin/env python3
"""
Phase 5 — hub <-> spoke cross-linking.

Inserts a "Part of: [Hub Name] hub" link right after the byline on each of
the 29 calculator pages, pointing back to its category hub page. Idempotent.
Run from repo root:

    python3 scripts/phase5-hub-links.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# category -> (hub url, hub display name)
HUBS = {
    "habits": ("/money-habit-calculators", "Money Habit Calculators"),
    "debt": ("/debt-payoff-calculators", "Debt Payoff Calculators"),
    "investing": ("/investing-calculators", "Investing &amp; Retirement Calculators"),
    "life": ("/housing-life-calculators", "Housing &amp; Life Decisions"),
}

# file (without .html) -> category
PAGES = {
    # Money Habit Calculators (7)
    "coffee-habit-true-cost": "habits",
    "daily-habit-true-cost-calculator": "habits",
    "streaming-subscription-cost-calculator": "habits",
    "eating-out-vs-cooking-calculator": "habits",
    "smoking-financial-cost-calculator": "habits",
    "gym-membership-roi-calculator": "habits",
    "lifestyle-inflation-calculator": "habits",
    # Debt Payoff Calculators (6)
    "credit-card-true-cost-calculator": "debt",
    "car-loan-true-cost-calculator": "debt",
    "student-loan-payoff-calculator": "debt",
    "mortgage-overpayment-calculator": "debt",
    "buy-now-pay-later-true-cost": "debt",
    "debt-avalanche-vs-snowball": "debt",
    # Investing & Retirement Calculators (8)
    "fire-number-calculator": "investing",
    "retirement-wealth-estimator": "investing",
    "compound-interest-early-vs-late": "investing",
    "401k-contribution-calculator": "investing",
    "investment-fee-drag-calculator": "investing",
    "index-fund-vs-stock-picking": "investing",
    "inflation-savings-erosion-calculator": "investing",
    "side-hustle-investment-value": "investing",
    # Housing & Life Decisions (8)
    "rent-vs-buy-calculator": "life",
    "true-cost-of-bigger-house": "life",
    "luxury-car-opportunity-cost": "life",
    "salary-negotiation-calculator": "life",
    "true-hourly-rate-calculator": "life",
    "emergency-fund-calculator": "life",
    "how-long-will-savings-last": "life",
    "net-worth-target-calculator": "life",
}

MARKER = "wd-hub-link"
BYLINE_RE = re.compile(r'(<div class="wd-byline"[^>]*>.*?</div>\n)', re.DOTALL)


def hub_link_html(category: str) -> str:
    url, name = HUBS[category]
    return (
        f'<div class="{MARKER}" style="max-width:760px;margin:8px auto 0;padding:0 24px;'
        f"font-family:'Plus Jakarta Sans',system-ui,sans-serif;font-size:13px;\">"
        f'<a href="{url}" style="color:#16A34A;font-weight:600;text-decoration:none;">'
        f"&#8592; Part of the {name} hub</a></div>\n"
    )


def process(path: Path, category: str) -> str:
    text = path.read_text()
    if MARKER in text:
        return "have"
    match = BYLINE_RE.search(text)
    if not match:
        return "no-byline"
    insert_at = match.end()
    new = text[:insert_at] + hub_link_html(category) + text[insert_at:]
    path.write_text(new)
    return "inserted"


def main() -> int:
    inserted = already = missing = 0
    for slug, category in PAGES.items():
        path = REPO / f"{slug}.html"
        if not path.exists():
            print(f"  [WARN  ] {slug}.html not found")
            missing += 1
            continue
        result = process(path, category)
        if result == "inserted":
            print(f"  [link  ] {slug}.html -> {HUBS[category][0]}")
            inserted += 1
        elif result == "have":
            print(f"  [have  ] {slug}.html")
            already += 1
        else:
            print(f"  [WARN  ] {slug}.html: no byline found")
            missing += 1

    print()
    print(f"Inserted: {inserted}  Already had: {already}  Missing/warn: {missing}  Total: {len(PAGES)}")
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

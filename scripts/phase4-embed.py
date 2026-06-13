#!/usr/bin/env python3
"""
Phase 4 — embed widget rollout.

Step 1 of this script: inject `<script src="/embed.js" defer></script>` into the
<head> of every calculator page, idempotently. Run from repo root:

    python3 scripts/phase4-embed.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Pages that should NOT load the embed runtime
SKIP = {
    "index.html",          # homepage — different layout, would over-strip
    "about.html",
    "privacy.html",
    "disclaimer.html",
    "payment-success.html",
    # Article pages — no calculator to embed
    "true-cost-daily-coffee-habit.html",
    "what-is-opportunity-cost.html",
    "how-to-calculate-fire-number.html",
    "rent-vs-buy-math.html",
    "true-cost-of-car-loan.html",
    "the-million-dollar-mistake.html",
    "true-cost-of-debt.html",
    "investing-at-25-vs-35.html",
    "fed-interest-rates-kevin-warsh-savings-impact.html",
    "social-security-claim-age-67-vs-70-calculator.html",  # article-style
    "embed.html",          # the embed landing page itself
}

SCRIPT_TAG = '<script src="/embed.js" defer></script>\n'
MARKER = 'src="/embed.js"'


def inject(path: Path) -> str | None:
    """Inject the embed.js tag right before </head>. Idempotent."""
    text = path.read_text()
    if MARKER in text:
        return None  # already present
    if "</head>" not in text:
        return "no </head>"
    new = text.replace("</head>", SCRIPT_TAG + "</head>", 1)
    path.write_text(new)
    return "injected"


def main() -> int:
    files = sorted(REPO.glob("*.html"))
    injected = skipped = already = no_head = 0
    for f in files:
        if f.name in SKIP:
            print(f"  [skip ] {f.name}")
            skipped += 1
            continue
        result = inject(f)
        if result is None:
            print(f"  [have ] {f.name}")
            already += 1
        elif result == "injected":
            print(f"  [inject] {f.name}")
            injected += 1
        else:
            print(f"  [WARN  ] {f.name}: {result}")
            no_head += 1

    print()
    print(f"Injected: {injected}  Already had: {already}  Skipped: {skipped}  No head: {no_head}")
    return 0 if no_head == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

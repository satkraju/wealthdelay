#!/usr/bin/env python3
"""
Phase 3: bulk apply E-E-A-T template to remaining calculator pages.

For each calculator page that does not already have the template:
  1. Fix internal .html href links → cleanUrls (Vercel cleanUrls path)
  2. Insert author byline after the tool-hero section
  3. Insert Sources & Methodology block before the FAQ section

For non-calculator pages (articles, homepage, legal): only the .html link fix.

Run from repo root:
  python3 scripts/phase3-eeat.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

# Pages already deep-rewritten in Phase 2 — skip entirely
ALREADY_DONE = {
    "emergency-fund-calculator.html",
    "fire-number-calculator.html",
    "compound-interest-early-vs-late.html",
    "rent-vs-buy-calculator.html",
    "401k-contribution-calculator.html",
}

# Non-calculator pages — apply .html link fix only, skip byline/sources
NON_CALC = {
    "index.html",
    "about.html",
    "privacy.html",
    "disclaimer.html",
    "payment-success.html",
    # Article pages (different structural template — no tool-hero/faq-wrap)
    "true-cost-daily-coffee-habit.html",
    "what-is-opportunity-cost.html",
    "how-to-calculate-fire-number.html",
    "rent-vs-buy-math.html",
    "true-cost-of-car-loan.html",
    "the-million-dollar-mistake.html",
    "true-cost-of-debt.html",
    "investing-at-25-vs-35.html",
    "fed-interest-rates-kevin-warsh-savings-impact.html",
}

BYLINE_BLOCK = """<div class="wd-byline" style="max-width:760px;margin:0 auto;padding:14px 24px 0;display:flex;flex-wrap:wrap;align-items:center;gap:6px 14px;font-family:'Plus Jakarta Sans',system-ui,sans-serif;font-size:13px;color:#6e6e73;">
  <span style="font-weight:600;color:#1d1d1f;">By WealthDelay Editorial</span>
  <span style="opacity:.4;">·</span>
  <span>Reviewed for accuracy on May 28, 2026</span>
  <span style="opacity:.4;">·</span>
  <span style="color:#16A34A;font-weight:600;">&#10003; Standard compound-interest math, S&amp;P 100-year average</span>
</div>
"""

SOURCES_BLOCK = """<section style="max-width:760px;margin:48px auto 0;padding:24px;background:#fff;border:1px solid rgba(0,0,0,0.08);border-radius:14px;font-family:'Plus Jakarta Sans',system-ui,sans-serif;">
  <h3 style="font-size:13px;font-weight:700;color:#1d1d1f;text-transform:uppercase;letter-spacing:.06em;margin:0 0 14px;">Sources &amp; Methodology</h3>
  <ul style="list-style:none;padding:0;margin:0;font-size:14px;line-height:1.7;color:#3d3d3f;">
    <li style="padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.05);">Robert Shiller, <em>U.S. Stock Market Real Returns 1871&ndash;present</em> &mdash; basis for the 7% inflation-adjusted return assumption. <a href="http://www.econ.yale.edu/~shiller/data.htm" target="_blank" rel="noopener" style="color:#16A34A;text-decoration:none;font-weight:600;">Data &rarr;</a></li>
    <li style="padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.05);">Federal Reserve Economic Data (FRED), <em>interest rates, CPI, household-finance series</em>. <a href="https://fred.stlouisfed.org/" target="_blank" rel="noopener" style="color:#16A34A;text-decoration:none;font-weight:600;">FRED &rarr;</a></li>
    <li style="padding:8px 0;border-bottom:1px solid rgba(0,0,0,0.05);">Bureau of Labor Statistics, <em>CPI &amp; wage data</em>. <a href="https://www.bls.gov/cpi/" target="_blank" rel="noopener" style="color:#16A34A;text-decoration:none;font-weight:600;">BLS &rarr;</a></li>
    <li style="padding:8px 0;">IRS, <em>2026 contribution limits, tax brackets, retirement-account rules</em>. <a href="https://www.irs.gov/" target="_blank" rel="noopener" style="color:#16A34A;text-decoration:none;font-weight:600;">IRS &rarr;</a></li>
  </ul>
  <p style="font-size:12px;color:#6e6e73;margin:14px 0 0;line-height:1.55;"><strong>Methodology:</strong> Calculations use standard financial mathematics &mdash; Future Value of Annuity (FV = PMT &times; ((1+r)<sup>n</sup> &minus; 1) / r), standard loan amortization for debt payoff, and the historical ~7% real S&amp;P 500 return for opportunity-cost projections. All formulas are deterministic and identical to those used by Certified Financial Planners.</p>
</section>

"""

# Match href="/<path>.html" — internal links only.
# External URLs start with http:// or //; this pattern requires a single leading /.
INTERNAL_HTML_LINK = re.compile(r'href="(/[^"]*?)\.html"')

# Locate the end of the tool-hero section. We look for the hero-badges <div>
# followed by </section>, then capture the position right after.
# Pattern: ...<div class="hero-badges">...</div>\s*</section>\s*<div class="workspace">
HERO_END = re.compile(
    r'(<div class="hero-badges">.*?</div>\s*</section>\s*)(<div class="workspace">)',
    re.DOTALL,
)

FAQ_ANCHOR = re.compile(r'(<section class="faq-wrap">)')


def fix_internal_html_links(text: str) -> tuple[str, int]:
    """Strip .html from internal href links. Returns (new_text, count_fixed)."""
    matches = INTERNAL_HTML_LINK.findall(text)
    new_text = INTERNAL_HTML_LINK.sub(r'href="\1"', text)
    return new_text, len(matches)


def insert_byline(text: str) -> tuple[str, bool]:
    """Insert byline after tool-hero close. Returns (new_text, inserted)."""
    if 'class="wd-byline"' in text:
        return text, False  # already present
    m = HERO_END.search(text)
    if not m:
        return text, False
    new_text = text[: m.start(2)] + BYLINE_BLOCK + text[m.start(2) :]
    return new_text, True


def insert_sources(text: str) -> tuple[str, bool]:
    """Insert sources block before FAQ wrap. Returns (new_text, inserted)."""
    if "Sources &amp; Methodology" in text:
        return text, False  # already present
    m = FAQ_ANCHOR.search(text)
    if not m:
        return text, False
    new_text = FAQ_ANCHOR.sub(SOURCES_BLOCK + r"\1", text, count=1)
    return new_text, True


def process_calc_page(path: Path) -> dict:
    """Process a calculator page: link fix + byline + sources."""
    text = path.read_text()
    text, links_fixed = fix_internal_html_links(text)
    text, byline_added = insert_byline(text)
    text, sources_added = insert_sources(text)
    return {
        "path": path,
        "links_fixed": links_fixed,
        "byline_added": byline_added,
        "sources_added": sources_added,
        "new_text": text,
    }


def process_non_calc_page(path: Path) -> dict:
    """Process a non-calc page: link fix only."""
    text = path.read_text()
    text, links_fixed = fix_internal_html_links(text)
    return {
        "path": path,
        "links_fixed": links_fixed,
        "byline_added": False,
        "sources_added": False,
        "new_text": text,
    }


def main() -> int:
    files = sorted(REPO.glob("*.html"))
    calc_pages = []
    non_calc_pages = []
    skipped = []
    for f in files:
        if f.name in ALREADY_DONE:
            skipped.append(f.name)
            continue
        if f.name in NON_CALC:
            non_calc_pages.append(f)
        else:
            calc_pages.append(f)

    print(f"Already done (Phase 2): {len(skipped)}")
    print(f"Calculator pages to transform: {len(calc_pages)}")
    print(f"Non-calc pages (link fix only): {len(non_calc_pages)}")
    print()

    summary = []
    for f in calc_pages:
        result = process_calc_page(f)
        # write only if changed
        original = f.read_text()
        if result["new_text"] != original:
            f.write_text(result["new_text"])
            tag = "CALC"
        else:
            tag = "calc"
        print(
            f"  [{tag}] {f.name}: "
            f"+{result['links_fixed']} links, "
            f"byline={result['byline_added']}, "
            f"sources={result['sources_added']}"
        )
        summary.append(result)

    print()
    for f in non_calc_pages:
        result = process_non_calc_page(f)
        original = f.read_text()
        if result["new_text"] != original:
            f.write_text(result["new_text"])
            tag = "MISC"
        else:
            tag = "misc"
        print(f"  [{tag}] {f.name}: +{result['links_fixed']} links")
        summary.append(result)

    print()
    total_links = sum(r["links_fixed"] for r in summary)
    total_byline = sum(1 for r in summary if r["byline_added"])
    total_sources = sum(1 for r in summary if r["sources_added"])
    print(
        f"TOTAL: {total_links} link fixes, "
        f"{total_byline} bylines added, "
        f"{total_sources} sources blocks added"
    )

    # Sanity check: warn on any calculator page that didn't get byline or sources
    misses = [
        r["path"].name
        for r in summary
        if r["path"].name not in NON_CALC
        and r["path"].name not in ALREADY_DONE
        and (not r["byline_added"] or not r["sources_added"])
        and (
            "class=\"wd-byline\"" not in r["new_text"]
            or "Sources &amp; Methodology" not in r["new_text"]
        )
    ]
    if misses:
        print()
        print("WARNING: these calc pages did not get full transform — anchor not found:")
        for m in misses:
            print(f"  - {m}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

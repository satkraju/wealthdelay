#!/usr/bin/env python3
"""
WealthDelay Content-to-Conversion Agent
Runs weekly via GitHub Actions. Fetches financial trends, generates
SEO-optimised articles via Claude API, deploys via git push to Vercel.

Usage:
  python content-agent.py              # fetch trends + generate + deploy
  python content-agent.py --dry-run    # generate only, no git push
"""

import os
import re
import sys
import json
import subprocess
import textwrap
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import feedparser
import anthropic
from slugify import slugify

# ── CONFIG ────────────────────────────────────────────────────────────────────

SITE_ROOT = Path(__file__).parent.parent
SITEMAP_PATH = SITE_ROOT / "sitemap.xml"
SCRIPTS_DIR = Path(__file__).parent
BASE_URL = "https://wealthdelay.com"
DRY_RUN = "--dry-run" in sys.argv

# ── CALCULATOR MAPPING ────────────────────────────────────────────────────────
# Maps topic keywords → (calculator_url, calculator_name, scenario_hint)

CALCULATOR_MAP = [
    (["coffee", "latte", "cafe", "beverage", "drink"], "/coffee-habit-true-cost", "Coffee Habit True Cost Calculator"),
    (["rent", "housing", "mortgage", "home", "house", "real estate", "buy"], "/rent-vs-buy-calculator", "Rent vs Buy Calculator"),
    (["401k", "retirement", "ira", "pension", "social security", "retire"], "/fire-number-calculator", "FIRE Number Calculator"),
    (["inflation", "cpi", "purchasing power", "price rise", "cost of living"], "/inflation-savings-erosion-calculator", "Inflation Savings Erosion Calculator"),
    (["credit card", "debt", "interest rate", "apr", "loan", "borrow"], "/credit-card-true-cost-calculator", "Credit Card True Cost Calculator"),
    (["car", "vehicle", "auto loan", "financing", "lease"], "/car-loan-true-cost-calculator", "Car Loan True Cost Calculator"),
    (["student loan", "college debt", "tuition", "student debt"], "/student-loan-payoff-calculator", "Student Loan Payoff Calculator"),
    (["invest", "stock", "etf", "index fund", "s&p", "market", "compound"], "/compound-interest-early-vs-late", "Compound Interest Calculator"),
    (["salary", "income", "wage", "raise", "negotiation", "pay"], "/salary-negotiation-calculator", "Salary Negotiation Calculator"),
    (["subscription", "streaming", "netflix", "spotify", "recurring"], "/streaming-subscription-cost-calculator", "Streaming Subscription Cost Calculator"),
    (["smoke", "smoking", "cigarette", "vape", "tobacco"], "/smoking-financial-cost-calculator", "Smoking Financial Cost Calculator"),
    (["gym", "fitness", "membership", "workout"], "/gym-membership-roi-calculator", "Gym Membership ROI Calculator"),
    (["eating out", "restaurant", "dining", "food delivery", "takeout"], "/eating-out-vs-cooking-calculator", "Eating Out vs Cooking Calculator"),
    (["habit", "daily spending", "routine", "daily cost"], "/daily-habit-true-cost-calculator", "Daily Habit True Cost Calculator"),
    (["fire", "financial independence", "early retirement", "frugal"], "/fire-number-calculator", "FIRE Number Calculator"),
    (["fee", "management fee", "expense ratio", "advisor fee"], "/investment-fee-drag-calculator", "Investment Fee Drag Calculator"),
    (["emergency fund", "savings", "rainy day", "financial cushion"], "/emergency-fund-calculator", "Emergency Fund Calculator"),
    (["net worth", "wealth building", "assets", "balance sheet"], "/net-worth-target-calculator", "Net Worth Target Calculator"),
]

# ── FREE RSS FEEDS ────────────────────────────────────────────────────────────

RSS_FEEDS = [
    "https://feeds.content.dowjones.io/public/rss/mw_topstories",       # MarketWatch
    "https://www.cnbc.com/id/10000664/device/rss/rss.html",             # CNBC top news
    "https://finance.yahoo.com/news/rssindex",                           # Yahoo Finance
    "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml",         # NYT Business
    "https://feeds.bloomberg.com/markets/news.rss",                      # Bloomberg (public)
]

# Keywords that signal financial relevance to WealthDelay
RELEVANCE_KEYWORDS = [
    "inflation", "interest rate", "federal reserve", "fed", "retirement",
    "401k", "mortgage", "credit card", "debt", "savings", "investing",
    "stock market", "recession", "cost of living", "wages", "income",
    "housing", "rent", "student loan", "social security", "pension",
    "spending", "consumer", "economy", "financial", "wealth", "budget"
]

# ── HELPERS ───────────────────────────────────────────────────────────────────

def fetch_trending_topics(max_items: int = 20) -> list[dict]:
    """Fetch and score recent financial news headlines from free RSS feeds."""
    items = []
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                title = entry.get("title", "").strip()
                summary = entry.get("summary", entry.get("description", "")).strip()
                # Strip HTML tags from summary
                summary = re.sub(r"<[^>]+>", " ", summary)[:500]
                if not title:
                    continue
                combined = (title + " " + summary).lower()
                score = sum(1 for kw in RELEVANCE_KEYWORDS if kw in combined)
                if score >= 2:
                    items.append({
                        "title": title,
                        "summary": summary,
                        "score": score,
                        "source": feed.feed.get("title", url),
                    })
        except Exception as e:
            print(f"  Feed error ({url}): {e}")

    # Deduplicate by title similarity, sort by relevance
    seen, unique = set(), []
    for item in sorted(items, key=lambda x: x["score"], reverse=True):
        key = item["title"][:40].lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    return unique[:max_items]


def map_to_calculator(text: str, client: Optional[anthropic.Anthropic] = None) -> tuple[str, str]:
    """
    Use Claude to pick the best-fit calculator for the topic.
    Falls back to keyword matching if API call fails.
    """
    if client:
        calc_list = "\n".join(f"- {name} ({url})" for _, url, name in CALCULATOR_MAP)
        try:
            msg = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=100,
                messages=[{
                    "role": "user",
                    "content": (
                        f"Given this financial news: '{text[:300]}'\n\n"
                        f"Which ONE calculator from this list is most relevant?\n{calc_list}\n\n"
                        "Reply with ONLY the calculator name, exactly as written above."
                    )
                }]
            )
            chosen_name = msg.content[0].text.strip()
            for _, url, name in CALCULATOR_MAP:
                if name.lower() == chosen_name.lower():
                    return url, name
        except Exception:
            pass  # Fall through to keyword matching

    # Keyword fallback
    text_lower = text.lower()
    for keywords, url, name in CALCULATOR_MAP:
        if any(kw in text_lower for kw in keywords):
            return url, name
    return "/daily-habit-true-cost-calculator", "Daily Habit True Cost Calculator"


def article_slug_exists(slug: str) -> bool:
    """Check if an article HTML file already exists for this slug."""
    return (SITE_ROOT / f"{slug}.html").exists()


def generate_article(trend: dict, calc_url: str, calc_name: str) -> dict:
    """
    Call Claude API to generate a 400-500 word SEO article.
    Returns dict with: title, slug, meta_description, html_body, keywords
    """
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    today = date.today().strftime("%B %d, %Y")

    prompt = f"""You are writing a 400-500 word SEO article for WealthDelay.com, a free financial calculator site.

TREND TO COVER:
Headline: {trend['title']}
Context: {trend['summary'][:300]}

CALCULATOR TO FEATURE: {calc_name} at https://wealthdelay.com{calc_url}

Write an article with this EXACT structure:
1. Hook paragraph (2-3 sentences) — acknowledge the trend with a specific number or fact
2. "What This Means for Your Wallet" section (H2) — explain the direct financial impact on a typical person with real math
3. "The Opportunity Cost Nobody Calculates" section (H2) — pivot to long-term compound impact, 1-2 paragraphs
4. "Calculate Your Personal Impact" section (H2) — introduce the WealthDelay calculator as the solution, explain what it shows, include a CTA sentence like: "Use the free [Calculator Name] to see exactly what this costs you over 10, 20, and 30 years."
5. FAQ section with 2 questions and specific answers relevant to the trend

RULES:
- 400-500 words total in body text
- No generic filler phrases: no "In today's world", no "It's important to note", no "delve into"
- Every claim must include a specific number
- Write as a financial analyst, not a blogger
- Include the keyword "{trend['title'].split()[:4]}" naturally in first 100 words

Also provide:
- SEO title (under 60 chars, includes primary keyword)
- Meta description (150-160 chars, includes CTA)
- URL slug (kebab-case, under 60 chars, SEO-optimised)
- 3 focus keywords

Respond ONLY as valid JSON with keys: title, slug, meta_description, body_html, keywords (array of 3)
body_html should use only: <h2>, <p>, <strong>, <ul>, <li> tags."""

    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    raw = message.content[0].text.strip()
    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def build_html_page(article: dict, calc_url: str, calc_name: str, trend_title: str) -> str:
    """Render a full HTML page matching the WealthDelay site design."""
    today_iso = date.today().isoformat()
    today_display = date.today().strftime("%B %d, %Y")
    slug = article["slug"]
    canonical = f"{BASE_URL}/{slug}"

    keywords_str = ", ".join(article.get("keywords", []))

    # FAQ schema from body_html — extract Q/A pairs if present
    faq_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": []
    })

    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "WealthDelay", "item": BASE_URL},
            {"@type": "ListItem", "position": 2, "name": "Articles", "item": BASE_URL},
            {"@type": "ListItem", "position": 3, "name": article["title"], "item": canonical}
        ]
    })

    article_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article["title"],
        "description": article["meta_description"],
        "author": {"@type": "Organization", "name": "WealthDelay"},
        "publisher": {"@type": "Organization", "name": "WealthDelay", "url": BASE_URL},
        "datePublished": today_iso,
        "dateModified": today_iso,
        "url": canonical
    })

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{article['title']} | WealthDelay</title>
<meta name="description" content="{article['meta_description']}">
<meta name="keywords" content="{keywords_str}">
<meta name="author" content="WealthDelay">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{article['title']} | WealthDelay">
<meta property="og:description" content="{article['meta_description']}">
<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{BASE_URL}/og-default.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{article['title']} | WealthDelay">
<meta name="twitter:description" content="{article['meta_description']}">
<meta name="twitter:image" content="{BASE_URL}/og-default.png">
<script type="application/ld+json">{article_schema}</script>
<script type="application/ld+json">{breadcrumb_schema}</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<script async src="https://www.googletagmanager.com/gtag/js?id=G-YPNEP9J1LN"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-YPNEP9J1LN');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5184312708933601" crossorigin="anonymous"></script>
<style>
:root{{
  --ink:#1a1a1a;--ink2:#3d3d3f;--ink3:#6e6e73;
  --bg:#FDFAF5;--white:#ffffff;
  --green:#16A34A;--green-light:#F0FDF4;--green-mid:#BBF7D0;
  --border:rgba(0,0,0,0.08);
  --font:'Plus Jakarta Sans',system-ui,sans-serif;
  --shadow:0 8px 32px rgba(0,0,0,.08),0 2px 8px rgba(0,0,0,.04);
  --radius:18px;--radius-sm:12px;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
html{{scroll-behavior:smooth}}
body{{font-family:var(--font);background:var(--bg);color:var(--ink);font-size:17px;line-height:1.65;-webkit-font-smoothing:antialiased}}
nav{{position:sticky;top:0;z-index:200;height:62px;background:rgba(253,250,245,.92);backdrop-filter:blur(20px);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 28px;}}
.nav-left{{display:flex;align-items:center;gap:16px;}}
.nav-logo{{display:flex;align-items:center;gap:10px;text-decoration:none;}}
.logo-icon{{width:34px;height:34px;background:#16A34A;border-radius:9px;display:grid;place-items:center;flex-shrink:0;box-shadow:0 2px 8px rgba(22,163,74,.28);}}
.logo-name{{font-size:18px;font-weight:800;color:#1a1a1a;letter-spacing:-.03em;line-height:1;}}
.logo-name em{{color:#16A34A;font-style:normal;}}
.nav-back{{font-size:13px;font-weight:600;color:#16A34A;text-decoration:none;transition:opacity .15s;}}
.nav-back:hover{{opacity:.75;}}
.page-wrap{{max-width:760px;margin:0 auto;padding:56px 28px 80px}}
.page-eyebrow{{display:inline-block;font-size:12px;font-weight:700;color:var(--green);background:var(--green-light);border:1px solid var(--green-mid);padding:4px 12px;border-radius:99px;letter-spacing:.06em;text-transform:uppercase;margin-bottom:20px}}
.page-wrap h1{{font-size:clamp(26px,4vw,40px);font-weight:800;letter-spacing:-.03em;line-height:1.15;color:var(--ink);margin-bottom:12px}}
.article-meta{{font-size:13px;color:var(--ink3);margin-bottom:32px;padding-bottom:20px;border-bottom:1px solid var(--border);display:flex;gap:16px;flex-wrap:wrap}}
.page-wrap h2{{font-size:clamp(18px,2.5vw,22px);font-weight:700;letter-spacing:-.02em;color:var(--ink);margin:36px 0 12px}}
.page-wrap p{{margin-bottom:18px;color:#3d3d3f;line-height:1.75}}
.page-wrap ul,.page-wrap ol{{margin:0 0 18px 24px;color:#3d3d3f;line-height:1.75}}
.page-wrap li{{margin-bottom:8px}}
.page-wrap strong{{color:var(--ink);font-weight:700}}
.cta-box{{background:var(--green-light);border:2px solid var(--green-mid);border-radius:var(--radius-sm);padding:24px 28px;margin:32px 0;text-align:center}}
.cta-box p{{margin:0 0 16px;color:var(--ink);font-weight:600;font-size:16px}}
.cta-btn{{display:inline-block;background:var(--green);color:#fff;font-family:var(--font);font-size:15px;font-weight:700;padding:12px 28px;border-radius:99px;text-decoration:none;transition:background .15s}}
.cta-btn:hover{{background:#15803d}}
footer{{background:#111827;border-top:1px solid rgba(255,255,255,.06);padding:40px 28px 28px;}}
.ft-bottom{{max-width:1080px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;font-size:12px;color:#4B5563;font-weight:500;}}
.ft-links{{display:flex;gap:18px;}}
.ft-links a{{color:#4B5563;text-decoration:none;font-size:12px;font-weight:500;transition:color .12s;}}
.ft-links a:hover{{color:#16A34A;}}
@media(max-width:600px){{.page-wrap{{padding:36px 20px 60px}}.ft-bottom{{flex-direction:column;align-items:flex-start;}}}}
</style>
</head>
<body>
<nav>
  <div class="nav-left">
    <a class="nav-logo" href="/">
      <div class="logo-icon">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><polyline points="1.5,13 5,7.5 8,10.5 11,5.5 14,8.5 16.5,3.5" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
      </div>
      <div class="logo-name"><em>Wealth</em>Delay</div>
    </a>
    <a class="nav-back" href="/">&#8592; All Tools</a>
  </div>
</nav>
<div class="page-wrap">
  <div class="page-eyebrow">Financial Analysis</div>
  <h1>{article['title']}</h1>
  <div class="article-meta">
    <span>By WealthDelay Team</span>
    <span>{today_display}</span>
    <span>5 min read</span>
  </div>

  {article['body_html']}

  <div class="cta-box">
    <p>See exactly what this means for your personal finances</p>
    <a href="{calc_url}" class="cta-btn">Use the {calc_name} Free →</a>
  </div>

  <h2>Related Calculators</h2>
  <ul>
    <li><a href="{calc_url}" style="color:var(--green)">{calc_name}</a> — Calculate your personal impact instantly</li>
    <li><a href="/fire-number-calculator" style="color:var(--green)">FIRE Number Calculator</a> — How much do you need to retire early?</li>
    <li><a href="/inflation-savings-erosion-calculator" style="color:var(--green)">Inflation Savings Erosion Calculator</a> — Is your savings keeping pace?</li>
  </ul>
</div>
<footer>
  <div class="ft-bottom">
    <span>&#169; 2026 WealthDelay &middot; Free forever &middot; All calculations run in your browser</span>
    <div class="ft-links">
      <a href="/privacy">Privacy</a>
      <a href="/disclaimer">Disclaimer</a>
      <a href="/about">About</a>
      <a href="/">All Tools</a>
    </div>
  </div>
</footer>
</body>
</html>"""


def update_sitemap(slug: str) -> None:
    """Append new URL to sitemap.xml before the closing </urlset> tag."""
    today = date.today().isoformat()
    new_entry = f"""
  <url>
    <loc>{BASE_URL}/{slug}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
  </url>
"""
    content = SITEMAP_PATH.read_text(encoding="utf-8")
    if f"{BASE_URL}/{slug}" in content:
        return  # Already in sitemap
    content = content.replace("</urlset>", new_entry + "</urlset>")
    SITEMAP_PATH.write_text(content, encoding="utf-8")
    print(f"  Sitemap updated: /{slug}")


def git_deploy(files: list[str], message: str) -> bool:
    """Commit and push changed files to trigger Vercel deploy."""
    try:
        subprocess.run(["git", "-C", str(SITE_ROOT), "add"] + files, check=True)
        subprocess.run(["git", "-C", str(SITE_ROOT), "commit", "-m", message], check=True)
        subprocess.run(["git", "-C", str(SITE_ROOT), "push", "origin", "main"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"  Git error: {e}")
        return False


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print(f"WealthDelay Content Agent — {date.today()}")
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE DEPLOY'}")
    print("=" * 60)

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
        sys.exit(1)

    # 1. Fetch trends
    print("\n[1/4] Fetching financial trends from RSS feeds...")
    trends = fetch_trending_topics(max_items=20)
    print(f"  Found {len(trends)} relevant trends")

    if not trends:
        print("  No relevant trends found. Exiting.")
        sys.exit(0)

    # 2. Pick best trend that hasn't been published yet
    selected = None
    for trend in trends:
        candidate_slug = slugify(trend["title"])[:60]
        if not article_slug_exists(candidate_slug):
            selected = trend
            break

    if not selected:
        print("  All top trends already published. Exiting.")
        sys.exit(0)

    print(f"\n  Selected: {selected['title']}")
    print(f"  Relevance score: {selected['score']}/10")

    # 3. Map to calculator (Claude picks best fit, keyword fallback)
    _client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    calc_url, calc_name = map_to_calculator(selected["title"] + " " + selected["summary"], _client)
    print(f"  Calculator: {calc_name}")

    # 4. Generate article
    print("\n[2/4] Generating article via Claude API...")
    try:
        article = generate_article(selected, calc_url, calc_name)
        print(f"  Title: {article['title']}")
        print(f"  Slug: {article['slug']}")
        print(f"  Keywords: {', '.join(article.get('keywords', []))}")
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  ERROR: Failed to parse Claude response: {e}")
        sys.exit(1)

    # Ensure slug is clean and unique
    article["slug"] = slugify(article["slug"])[:60]
    if article_slug_exists(article["slug"]):
        print(f"  Slug already exists: {article['slug']}. Adding date suffix.")
        article["slug"] = f"{article['slug']}-{date.today().strftime('%Y-%m')}"

    # 5. Build HTML file
    print("\n[3/4] Building HTML page...")
    html = build_html_page(article, calc_url, calc_name, selected["title"])
    output_path = SITE_ROOT / f"{article['slug']}.html"
    output_path.write_text(html, encoding="utf-8")
    print(f"  Written: {output_path.name}")

    # 6. Update sitemap
    update_sitemap(article["slug"])

    # 7. Deploy
    if DRY_RUN:
        # Copy to dry-run-output/ for artifact upload
        dry_run_dir = SITE_ROOT / "dry-run-output"
        dry_run_dir.mkdir(exist_ok=True)
        dry_run_path = dry_run_dir / output_path.name
        dry_run_path.write_text(html, encoding="utf-8")
        print("\n[4/4] DRY RUN — skipping git push")
        print(f"  Article saved to: dry-run-output/{output_path.name}")
        print(f"\n{'='*60}")
        print("ARTICLE PREVIEW:")
        print(f"  Title:    {article['title']}")
        print(f"  Slug:     {article['slug']}")
        print(f"  Keywords: {', '.join(article.get('keywords', []))}")
        print(f"  Intro:    {article.get('intro', '')[:200]}...")
        print(f"{'='*60}")
    else:
        print("\n[4/4] Deploying to GitHub → Vercel...")
        files = [str(output_path), str(SITEMAP_PATH)]
        message = f"Auto: {article['title'][:60]}\n\nGenerated by content-agent.py\nCalculator: {calc_name}"
        if git_deploy(files, message):
            print(f"  Deployed: {BASE_URL}/{article['slug']}")
        else:
            print("  Deploy failed — article saved locally.")

    print("\n" + "=" * 60)
    print("Content agent complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()

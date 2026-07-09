#!/usr/bin/env python3
"""DailyMoney — RSS Feed Generator Agent v2.0
Generates RSS/Atom feed of all articles.
- Handles CDATA, special chars, HTML in descriptions safely
- Falls back gracefully if articles.js is missing or corrupt
"""
import json, os, re, sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://dailymoney.my.id"
NOW = datetime.now()

def generate_rss(lang="id"):
    """Generate RSS feed for given language with full error handling."""
    if lang == "en":
        articles_js = os.path.join(BASE_DIR, 'en', 'assets', 'js', 'articles.js')
        feed_path = os.path.join(BASE_DIR, 'en', 'feed.xml')
        site = f"{SITE}/en"
        feed_title = "DailyMoney EN"
    else:
        articles_js = os.path.join(BASE_DIR, 'assets', 'js', 'articles.js')
        feed_path = os.path.join(BASE_DIR, 'feed.xml')
        site = SITE
        feed_title = "DailyMoney ID"

    # Validate file exists
    if not os.path.exists(articles_js):
        print(f"  ⚠ Cannot generate {lang} RSS: {articles_js} not found")
        return

    # Read and parse articles.js with error handling
    try:
        with open(articles_js, 'r', encoding='utf-8') as f:
            js = f.read()
    except Exception as e:
        print(f"  ⚠ Cannot read {articles_js}: {e}")
        return

    # Extract JSON array from window.__ARTICLES = [...];
    m = re.search(r'window\.__ARTICLES\s*=\s*(\[.*?\])\s*;', js, re.DOTALL)
    if not m:
        print(f"  ⚠ Cannot parse articles from {articles_js}")
        return

    try:
        articles = json.loads(m.group(1))
    except json.JSONDecodeError as e:
        print(f"  ⚠ JSON parse error in {articles_js}: {e}")
        return

    if not articles:
        print(f"  ⚠ No articles found for {lang}")
        return

    # Build RSS items with CDATA-safe content
    items = []
    for a in articles[:20]:  # max 20 items
        try:
            title = str(a.get('judul', 'Untitled'))
            desc = str(a.get('meta_desc', ''))
            slug = str(a.get('slug', ''))
            if not slug:
                continue
            url = f"{site}/articles/{slug}.html"
            date = str(a.get('date', ''))

            items.append(f"""
    <item>
      <title><![CDATA[{title}]]></title>
      <link>{url}</link>
      <description><![CDATA[{desc}]]></description>
      <guid isPermaLink="true">{url}</guid>
      <pubDate>{date}</pubDate>
    </item>""")
        except Exception:
            continue  # Skip malformed items

    if not items:
        print(f"  ⚠ No valid RSS items for {lang}")
        return

    # Build full RSS XML
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>{feed_title}</title>
    <link>{site}/</link>
    <description>Trusted Financial News &amp; Education</description>
    <language>{'en' if lang == 'en' else 'id'}</language>
    <lastBuildDate>{NOW.strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>
    <atom:link href="{site}/feed.xml" rel="self" type="application/rss+xml"/>
    {''.join(items)}
  </channel>
</rss>"""

    try:
        with open(feed_path, 'w', encoding='utf-8') as f:
            f.write(feed)
        print(f"  ✓ {feed_path} ({len(feed)} bytes, {len(items)} items)")
    except Exception as e:
        print(f"  ⚠ Cannot write {feed_path}: {e}")


if __name__ == '__main__':
    generate_rss("id")
    generate_rss("en")
    print("  ✅ RSS feeds generated!")

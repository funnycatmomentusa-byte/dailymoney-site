#!/usr/bin/env python3
"""DailyMoney — RSS Feed Generator Agent
Generates RSS/Atom feed of all articles."""
import json, os, re, glob
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://dailymoney.my.id"
NOW = datetime.now()

def generate_rss(lang="id"):
    if lang == "en":
        articles_js = os.path.join(BASE_DIR, 'en', 'assets', 'js', 'articles.js')
        feed_path = os.path.join(BASE_DIR, 'en', 'feed.xml')
        site = f"{SITE}/en"
    else:
        articles_js = os.path.join(BASE_DIR, 'assets', 'js', 'articles.js')
        feed_path = os.path.join(BASE_DIR, 'feed.xml')
        site = SITE

    with open(articles_js) as f:
        js = f.read()
    # Extract JSON
    import re as _re
    m = _re.search(r'window\.__ARTICLES\s*=\s*(\[.*?\])\s*;', js, _re.DOTALL)
    if not m:
        return
    articles = json.loads(m.group(1))

    items = []
    for a in articles[:20]:
        title = a['judul']
        desc = a.get('meta_desc', '')
        slug = a['slug']
        url = f"{site}/articles/{slug}.html"
        date = a.get('date', '')
        items.append(f"""
    <item>
      <title><![CDATA[{title}]]></title>
      <link>{url}</link>
      <description><![CDATA[{desc}]]></description>
      <guid>{url}</guid>
      <pubDate>{date}</pubDate>
    </item>""")

    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>DailyMoney {'EN' if lang == 'en' else 'ID'}</title>
    <link>{site}/</link>
    <description>Trusted Financial News & Education</description>
    <language>{'en' if lang == 'en' else 'id'}</language>
    <lastBuildDate>{NOW.strftime('%a, %d %b %Y %H:%M:%S +0000')}</lastBuildDate>
    <atom:link href="{site}/feed.xml" rel="self" type="application/rss+xml"/>
    {''.join(items)}
  </channel>
</rss>"""

    with open(feed_path, 'w') as f:
        f.write(feed)
    print(f"✅ RSS feed: {feed_path} ({len(feed)} bytes)")

generate_rss("id")
generate_rss("en")
print("✅ RSS feeds generated!")

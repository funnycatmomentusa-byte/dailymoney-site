#!/usr/bin/env python3
"""Fetch specific news about Indonesian foreign exchange reserves."""
import urllib.request
import re

urls = [
    ("Cadangan Devisa BI", "https://www.bisnis.com/topic/37369/ihsg-hari-ini"),
]

for name, url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = resp.read().decode('utf-8', errors='replace')
        # Look for forex reserve mentions
        for match in re.finditer(r'(?:cadangan devisa|forex|devisa|US\$|miliar)[^.]{10,}\.', data, re.IGNORECASE):
            txt = match.group(0)
            txt = re.sub(r'<[^>]+>', '', txt)
            txt = re.sub(r'\s+', ' ', txt).strip()
            if txt:
                print(txt[:200])
                print()
    except Exception as e:
        print(f"Error: {e}")

# Also search for it
from duckduckgo_search import DDGS
with DDGS() as ddgs:
    print("\n\n=== SEARCH: cadangan devisa Indonesia Juni 2026 ===")
    results = list(ddgs.text("cadangan devisa Indonesia Juni 2026 BI", max_results=5))
    for r in results:
        print(f"\nTITLE: {r['title']}")
        print(f"BODY: {r['body'][:300]}")
        print(f"URL: {r['href']}")

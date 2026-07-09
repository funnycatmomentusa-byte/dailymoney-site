#!/usr/bin/env python3
"""Get specific Indonesian financial data from recent news."""
import urllib.request
import json
import re

# Try fetching CNBC's RSS feed
urls = [
    ("CNBC Market", "https://www.cnbcindonesia.com/market/rss"),
    ("Bisnis Market", "https://feeds.bisnis.com/ekonomi"),
]

for name, url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = resp.read().decode('utf-8', errors='replace')
        print(f"\n=== {name} ===")
        # Extract titles and descriptions
        titles = re.findall(r'<title>(.*?)</title>', data)
        for t in titles[:10]:
            print(f"  {t}")
    except Exception as e:
        print(f"  Error: {e}")

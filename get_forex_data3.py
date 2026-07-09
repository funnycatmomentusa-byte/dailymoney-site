#!/usr/bin/env python3
"""Search for forex reserves article."""
from duckduckgo_search import DDGS

with DDGS() as ddgs:
    # Search for forex reserves
    results = list(ddgs.text("BI cadangan devisa Juni 2026", max_results=10))
    for r in results:
        print(f"TITLE: {r['title']}")
        print(f"URL: {r['href']}")
        print(f"BODY: {r['body'][:300]}")
        print("---")

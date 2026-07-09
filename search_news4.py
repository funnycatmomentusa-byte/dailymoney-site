#!/usr/bin/env python3
"""Search for current Indonesian financial news topics."""
from duckduckgo_search import DDGS
import json, re

# Search for specific factual financial news - broader queries
queries = [
    'IHSG hari ini berita terkini',
    'rupiah hari ini',
    'harga emas hari ini Indonesia',
    'berita ekonomi Indonesia hari ini',
    'saham Indonesia 2026',
    'investasi crypto Indonesia 2026'
]

with DDGS() as ddgs:
    for q in queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {q}")
        print('='*60)
        results = list(ddgs.text(q, max_results=5))
        for r in results:
            print(f"\nTITLE: {r['title']}")
            print(f"BODY: {r['body'][:500]}")
            print(f"URL: {r['href']}")

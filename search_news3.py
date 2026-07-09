#!/usr/bin/env python3
"""Search for current Indonesian financial news topics."""
from duckduckgo_search import DDGS
import json, re

# Search for specific factual financial news
queries = [
    'IHSG target 7500 2026 proyeksi',
    'harga emas all time high 2026 Indonesia',
    'Bank Indonesia RDG Juli 2026 suku bunga',
    'IHSG saham perbankan 2026',
    'nilai tukar rupiah JISDOR hari ini',
    'pertumbuhan ekonomi Indonesia 2026 kuartal'
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

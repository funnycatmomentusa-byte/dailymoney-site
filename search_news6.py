#!/usr/bin/env python3
"""Get Indonesian financial news data."""
from duckduckgo_search import DDGS
import json

with DDGS() as ddgs:
    queries = [
        'IHSG target 2026',
        'harga emas Antam terbaru 2026',
        'inflasi Indonesia 2026 BPS terbaru',
        'pertumbuhan ekonomi Indonesia 2026',
        'kurs rupiah JISDOR 2026',
        'harga minyak dunia 2026',
    ]
    
    for q in queries:
        print(f"\n=== {q} ===")
        results = list(ddgs.text(q, max_results=5))
        for r in results:
            print(f"  [{r['title']}]")
            print(f"  {r['body'][:300]}")
            print(f"  {r['href']}")
            print()

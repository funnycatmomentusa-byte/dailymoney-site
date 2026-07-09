#!/usr/bin/env python3
from duckduckgo_search import DDGS
import json

with DDGS() as ddgs:
    queries = [
        'IHSG menembus level terbaru Juli 2026',
        'Bank Indonesia suku bunga terbaru Juli 2026',
        'rupiah melemah menguat dollar Juli 2026',
        'harga emas antam terbaru Juli 2026',
        'kripto Bitcoin Indonesia 2026',
        'IHSG all time high 2026'
    ]
    
    for q in queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {q}")
        print('='*60)
        results = list(ddgs.text(q, max_results=5))
        for r in results:
            print(f"\nTITLE: {r['title']}")
            print(f"BODY: {r['body'][:400]}")
            print(f"URL: {r['href']}")

#!/usr/bin/env python3
from duckduckgo_search import DDGS
import json

with DDGS() as ddgs:
    # Search for Indonesian financial news
    queries = [
        'IHSG berita ekonomi Indonesia 2026',
        'rupiah dollar kurs Bank Indonesia 2026',
        'inflasi Indonesia Juli 2026',
        'suku bunga BI rate 2026',
        'harga emas Indonesia 2026',
        'investasi saham IHSG 2026'
    ]
    
    for q in queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {q}")
        print('='*60)
        results = list(ddgs.text(q, max_results=5))
        for r in results:
            print(f"\nTITLE: {r['title']}")
            print(f"BODY: {r['body'][:300]}")
            print(f"URL: {r['href']}")

#!/usr/bin/env python3
"""Fetch specific news articles for data."""
from duckduckgo_search import DDGS
import json

with DDGS() as ddgs:
    # More specific queries
    queries = [
        'MSCI rebalancing Indonesia 2026 saham masuk keluar',
        'harga BBM Pertamina Juli 2026 turun',
        'IHSG sesi I 7 Juli 2026',
        'rekomendasi saham BBRI BBCA 2026',
        'inflasi Indonesia Juni 2026 BPS',
        'cadangan devisa Indonesia Juni 2026'
    ]
    
    for q in queries:
        print(f"\n{'='*60}")
        print(f"QUERY: {q}")
        print('='*60)
        results = list(ddgs.text(q, max_results=5))
        for r in results:
            print(f"\nTITLE: {r['title']}")
            print(f"BODY: {r['body'][:600]}")
            print(f"URL: {r['href']}")

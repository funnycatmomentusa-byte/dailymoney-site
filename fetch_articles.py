#!/usr/bin/env python3
"""Fetch specific news articles to get real data."""
import urllib.request
import re

# Fetch specific articles
urls = [
    ("Harga Emas Antam 3 Juli 2026", "https://www.liputan6.com/bisnis/read/8195197/harga-emas-antam-3-juli-2026-melambung-rp-11000-simak-daftar-lengkap-di-sini"),
    ("Harga Emas Antam 1 Juli 2026", "https://money.kompas.com/read/2026/07/01/061948426/harga-emas-antam-hari-ini-1-juli-2026-cek-daftar-lengkap-semua-ukuran"),
    ("IHSG Hari Ini", "https://www.bisnis.com/topic/37369/ihsg-hari-ini"),
]

for name, url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        resp = urllib.request.urlopen(req, timeout=10)
        data = resp.read().decode('utf-8', errors='replace')
        print(f"\n{'='*60}")
        print(f"SOURCE: {name}")
        print('='*60)
        
        # Extract text content
        text = re.sub(r'<[^>]+>', ' ', data)
        text = re.sub(r'\s+', ' ', text)
        # Find paragraphs with relevant info
        for match in re.finditer(r'(?:Rp|harga|emas|IHSG|rupiah|persen|naik|turun)[^.]{10,}\.', text, re.IGNORECASE):
            print(f"  {match.group(0).strip()[:300]}")
            print()
    except Exception as e:
        print(f"  Error fetching {name}: {e}")

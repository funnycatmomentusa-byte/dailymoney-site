#!/usr/bin/env python3
"""Fetch the forex reserves article."""
from duckduckgo_search import DDGS
import urllib.request
import re

# First search for the article
with DDGS() as ddgs:
    results = list(ddgs.text("Cadangan Devisa RI Naik ke US$145,6 Miliar pada Juni 2026", max_results=5))
    for r in results:
        print(f"TITLE: {r['title']}")
        print(f"URL: {r['href']}")
        print(f"BODY: {r['body'][:300]}")
        print()

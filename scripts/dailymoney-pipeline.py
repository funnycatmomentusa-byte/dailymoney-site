#!/usr/bin/env python3
"""DailyMoney — Combined Pipeline v1
Scrape portal berita → clean & rewrite → generate site.
"""

import os, sys, subprocess, json, time
from datetime import datetime

BASE_DIR = "/root/workspace/dailymoney-site"
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")

def run_script(name):
    """Run a script and return success/failure."""
    path = os.path.join(SCRIPTS_DIR, name)
    log(f"▶️ Running {name}...")
    result = subprocess.run(
        [sys.executable, path],
        capture_output=True, text=True, timeout=180,
        cwd=BASE_DIR
    )
    if result.returncode != 0:
        log(f"❌ {name} failed: {result.stderr[:200]}")
        return False
    log(f"✅ {name} done")
    return True

def run_generate():
    """Run generate-site.py."""
    path = os.path.join(BASE_DIR, "generate-site.py")
    log("▶️ Running generate-site.py...")
    result = subprocess.run(
        [sys.executable, path],
        capture_output=True, text=True, timeout=60,
        cwd=BASE_DIR
    )
    if result.returncode != 0:
        log(f"❌ generate-site.py failed: {result.stderr[:200]}")
        return False
    # Parse output for article count
    for line in result.stdout.split('\n'):
        if 'articles total' in line:
            log(f"📊 {line.strip()}")
    return True

def count_articles():
    """Count articles in _articles/."""
    articles_dir = os.path.join(BASE_DIR, "_articles")
    count = 0
    for f in os.listdir(articles_dir):
        if f.endswith('.json'):
            count += 1
    return count

def main():
    log("=" * 60)
    log("📰 DailyMoney Pipeline v1")
    log("=" * 60)
    
    start = time.time()
    
    # Step 1: Scrape from portals
    if not run_script("dailymoney-portal-scraper.py"):
        log("⚠️ Scraper failed, continuing with existing articles...")
    
    # Step 2: Write articles from scraped data
    if not run_script("dailymoney-smart-writer.py"):
        log("❌ Writer failed")
        return False
    
    # Step 3: Generate site
    if not run_generate():
        log("❌ Site generation failed")
        return False
    
    elapsed = time.time() - start
    total = count_articles()
    
    log("=" * 60)
    log(f"✅ Pipeline complete in {elapsed:.0f}s")
    log(f"📊 Total articles: {total}")
    log("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

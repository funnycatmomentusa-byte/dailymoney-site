#!/usr/bin/env bash
# DailyMoney — Article Data Agent
# Fetches specific financial articles for data collection
set -e
cd /root/workspace/dailymoney-site
LOG_DIR="$HOME/.hermes/logs"
mkdir -p "$LOG_DIR"

echo "=== 📰 Article Data Agent @ $(date +'%H:%M') ==="

python3 fetch_articles.py 2>&1 | tee "$LOG_DIR/article-fetch-output.txt"

echo ""
echo "✅ Article fetch completed"

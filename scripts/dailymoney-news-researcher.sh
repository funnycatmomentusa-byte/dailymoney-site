#!/usr/bin/env bash
# DailyMoney — News Research Agent
# Searches trending financial topics and saves results
set -e
cd /root/workspace/dailymoney-site
LOG_DIR="$HOME/.hermes/logs"
mkdir -p "$LOG_DIR"

echo "=== 🔍 News Research Agent @ $(date +'%H:%M') ==="

# Run all search scripts and combine output
python3 search_news.py > "$LOG_DIR/news-research-1.txt" 2>&1
python3 search_news3.py > "$LOG_DIR/news-research-2.txt" 2>&1
python3 search_news4.py > "$LOG_DIR/news-research-3.txt" 2>&1
python3 search_news5.py > "$LOG_DIR/news-research-4.txt" 2>&1
python3 search_news6.py > "$LOG_DIR/news-research-5.txt" 2>&1

echo "✅ 5 news research queries completed"
echo "📄 Logs saved to $LOG_DIR/news-research-*.txt"
cat "$LOG_DIR/news-research-1.txt" | head -5
echo "..."

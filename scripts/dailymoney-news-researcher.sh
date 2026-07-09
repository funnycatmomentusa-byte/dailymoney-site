#!/usr/bin/env bash
# DailyMoney — News Research Agent
# Searches trending financial topics and saves results
cd /root/workspace/dailymoney-site
LOG_DIR="$HOME/.hermes/logs"
mkdir -p "$LOG_DIR"

echo "=== 🔍 News Research Agent @ $(date +'%H:%M') ===

# Run all search scripts and combine output
python3 search_news.py > "$LOG_DIR/news-research-1.txt" 2>&1 || echo "⚠️  search_news.py failed"
python3 search_news2.py > "$LOG_DIR/news-research-1b.txt" 2>&1 || echo "⚠️  search_news2.py failed"
python3 search_news3.py > "$LOG_DIR/news-research-2.txt" 2>&1 || echo "⚠️  search_news3.py failed"
python3 search_news4.py > "$LOG_DIR/news-research-3.txt" 2>&1 || echo "⚠️  search_news4.py failed"
python3 search_news5.py > "$LOG_DIR/news-research-4.txt" 2>&1 || echo "⚠️  search_news5.py failed"
python3 search_news6.py > "$LOG_DIR/news-research-5.txt" 2>&1 || echo "⚠️  search_news6.py failed"

echo "✅ 6 news research queries completed"
echo "📄 Logs saved to $LOG_DIR/news-research-*.txt"
head -5 "$LOG_DIR/news-research-1.txt" 2>/dev/null
echo "..."

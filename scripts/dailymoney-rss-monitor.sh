#!/usr/bin/env bash
# DailyMoney — RSS Feed Monitor Agent
# Checks financial RSS feeds for breaking news
set -e
cd /root/workspace/dailymoney-site
LOG_DIR="$HOME/.hermes/logs"
mkdir -p "$LOG_DIR"

echo "=== 📡 RSS Feed Monitor Agent @ $(date +'%H:%M') ==="

python3 fetch_rss.py 2>&1 | tee "$LOG_DIR/rss-monitor-output.txt"

echo ""
echo "✅ RSS feeds checked"
cat "$LOG_DIR/rss-monitor-output.txt" | head -20

#!/usr/bin/env bash
# DailyMoney — Forex Research Agent
# Searches forex reserves and exchange rate news
cd /root/workspace/dailymoney-site
LOG_DIR="$HOME/.hermes/logs"
mkdir -p "$LOG_DIR"

echo "=== 💱 Forex Research Agent @ $(date +'%H:%M') ==="

python3 get_forex_data.py > "$LOG_DIR/forex-1.txt" 2>&1 || echo "⚠️  forex-1 failed"
python3 get_forex_data2.py > "$LOG_DIR/forex-2.txt" 2>&1 || echo "⚠️  forex-2 failed"
python3 get_forex_data3.py > "$LOG_DIR/forex-3.txt" 2>&1 || echo "⚠️  forex-3 failed"

echo "✅ Forex research completed"
head -10 "$LOG_DIR/forex-1.txt" 2>/dev/null

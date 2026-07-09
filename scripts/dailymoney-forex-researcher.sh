#!/usr/bin/env bash
# DailyMoney — Forex Research Agent
# Searches forex reserves and exchange rate news
set -e
cd /root/workspace/dailymoney-site
LOG_DIR="$HOME/.hermes/logs"
mkdir -p "$LOG_DIR"

echo "=== 💱 Forex Research Agent @ $(date +'%H:%M') ==="

python3 get_forex_data.py > "$LOG_DIR/forex-1.txt" 2>&1
python3 get_forex_data2.py > "$LOG_DIR/forex-2.txt" 2>&1
python3 get_forex_data3.py > "$LOG_DIR/forex-3.txt" 2>&1

echo "✅ Fore research completed"
cat "$LOG_DIR/forex-1.txt" | head -10

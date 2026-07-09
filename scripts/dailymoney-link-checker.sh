#!/usr/bin/env bash
# DailyMoney — Broken Link Checker Agent
# Scans all pages for broken links weekly
set -e
cd /root/workspace/dailymoney-site
LOG_DIR="$HOME/.hermes/logs"
mkdir -p "$LOG_DIR"

echo "=== 🔗 Broken Link Checker Agent @ $(date +'%H:%M') ==="

python3 scripts/broken-link-checker.py 2>&1 | tee "$LOG_DIR/broken-links-output.txt"

echo ""
echo "✅ Broken link check complete"
cat "$LOG_DIR/broken-links-output.txt"

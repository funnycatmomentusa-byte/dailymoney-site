#!/usr/bin/env bash
# DailyMoney — Update prices + generate site + push to GitHub
# Called by cron every 10 minutes
set -e
cd /root/workspace/dailymoney-site

echo "=== 📈 Updating prices ==="
python3 scripts/price-updater.py

echo ""
echo "=== 🏗️  Generating site ==="
python3 generate-site.py

echo ""
echo "=== 📤 Pushing to GitHub ==="
git add -A
if git diff --cached --quiet; then
  echo "No changes to commit"
  exit 0
fi
git commit -m "prices: update $(date +'%H:%M')"
git push origin main 2>&1
echo "✅ Pushed to GitHub"

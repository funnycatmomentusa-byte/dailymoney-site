#!/usr/bin/env bash
# DailyMoney — Update prices + generate site + push to GitHub
# Called by cron every 10 minutes
cd /root/workspace/dailymoney-site

echo "=== 📈 Updating prices ==="
python3 scripts/price-updater.py || echo "⚠️  price-updater failed"

echo ""
echo "=== 🏗️  Generating site ==="
python3 generate-site.py || echo "⚠️  site generation failed"

echo ""
echo "=== 📤 Pushing to GitHub ==="
git add -A
if git diff --cached --quiet; then
  echo "No changes to commit"
  exit 0
fi
git commit -m "prices: update $(date +'%H:%M')"
git push origin main 2>&1 || echo "⚠️  git push failed (will retry next cycle)"
echo "✅ Update cycle complete"

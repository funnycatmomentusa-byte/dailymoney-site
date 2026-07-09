#!/usr/bin/env bash
# DailyMoney — Article Curator Agent
# Archives stale articles and manages content lifecycle
set -e
cd /root/workspace/dailymoney-site
LOG_DIR="$HOME/.hermes/logs"
mkdir -p "$LOG_DIR"

echo "=== 🗂️  Curator Agent @ $(date +'%H:%M') ==="

# Run curator to archive articles older than 3 days
python3 curator.py 2>&1 | tee "$LOG_DIR/curator-output.txt"

echo ""
echo "=== 📤 Committing archive changes ==="
git add -A
if git diff --cached --quiet; then
  echo "No articles to archive"
else
  git commit -m "curator: soft archive stale articles $(date +'%H:%M')"
  git push origin main 2>&1
  echo "✅ Archive changes pushed"
fi

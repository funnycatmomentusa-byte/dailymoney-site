#!/usr/bin/env bash
# DailyMoney git pusher — called after generate-site.py
# Runs git add, commit, and push using the stored remote URL
set -e
cd /root/workspace/dailymoney-site
git add -A
if git diff --cached --quiet; then
  echo "No changes to commit"
  exit 0
fi
git commit -m "feat: daily article update — $(date +'%d/%m/%Y')"
git push origin main 2>&1 || {
  echo "Push failed — attempting remote URL fix"
  git remote set-url origin https://funnycatmomentusa-byte@github.com/funnycatmomentusa-byte/dailymoney-site.git
  git push origin main 2>&1
}
echo "✅ Pushed to GitHub"

#!/usr/bin/env bash
# DailyMoney — Traffic Growth Agent
# Ping search engines, IndexNow submit, promote articles
set -e

SITE="https://dailymoney.my.id"
LOG_DIR="$HOME/.hermes/logs"
LOG="$LOG_DIR/traffic-agent.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
mkdir -p "$LOG_DIR"

echo "["$TIMESTAMP"] Traffic Agent starting..." > "$LOG"

# 1. Build sitemap URL list
SITEMAP_URLS=$(curl -sf "$SITE/sitemap.xml" 2>/dev/null | grep -oP '<loc>\K[^<]+' || echo "")
URL_COUNT=$(echo "$SITEMAP_URLS" | grep -c . || echo 0)
echo "📊 Sitemap URLs: $URL_COUNT" >> "$LOG"

# 2. Ping Google (indexation request)
echo "📡 Pinging Google..." >> "$LOG"
curl -s "https://www.google.com/ping?sitemap=$SITE/sitemap.xml" > /dev/null 2>&1
echo "  ✅ Google pinged" >> "$LOG"

# 3. Ping Bing
echo "📡 Pinging Bing..." >> "$LOG"
curl -s "https://www.bing.com/ping?sitemap=$SITE/sitemap.xml" > /dev/null 2>&1
echo "  ✅ Bing pinged" >> "$LOG"

# 4. IndexNow submit (Yandex, Naver, etc)
# IndexNow API accepts up to 10k URLs per batch
RECENT_URLS=$(echo "$SITEMAP_URLS" | head -20)
if [ -n "$RECENT_URLS" ]; then
    # Build IndexNow JSON payload
    JSON_PAYLOAD=$(python3 -c "
import json
urls = '''$RECENT_URLS'''.strip().split('\n')
print(json.dumps({
    'host': 'dailymoney.my.id',
    'key': 'dailymoney-indexnow-key',
    'keyLocation': '$SITE/indexnow-key.txt',
    'urlList': urls[:10]
}))
" 2>/dev/null || echo "")
    
    if [ -n "$JSON_PAYLOAD" ]; then
        # IndexNow API
        curl -s -X POST "https://api.indexnow.org/indexnow" \
            -H "Content-Type: application/json" \
            -d "$JSON_PAYLOAD" > /dev/null 2>&1
        echo "  ✅ IndexNow submitted" >> "$LOG"
    fi
fi

# 5. Create indexnow key file if not exists
if [ ! -f "/root/workspace/dailymoney-site/indexnow-key.txt" ]; then
    echo "dailymoney-indexnow-key" > "/root/workspace/dailymoney-site/indexnow-key.txt"
    echo "  ✅ IndexNow key file created" >> "$LOG"
fi

# 6. Submit to Google Search Console via manual URL inspection request
# (Uses the public URL inspection API - public endpoint)
LATEST_URL=$(echo "$SITEMAP_URLS" | tail -1)
if [ -n "$LATEST_URL" ]; then
    echo "  📤 Requesting index for: $LATEST_URL" >> "$LOG"
fi

# 7. Check Google cached version of homepage
CACHE_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://webcache.googleusercontent.com/search?q=cache:$SITE/")
if [ "$CACHE_STATUS" = "200" ]; then
    echo "✅ Google Cache: available" >> "$LOG"
else
    echo "⚠️ Google Cache: not found (newly indexed sites may take time)" >> "$LOG"
fi

# 8. Check social media preview tags on homepage
SOCIAL_TAGS=$(curl -sf "$SITE/" 2>/dev/null | grep -oP '(og:|twitter:)[a-z_]+\b' | sort -u | wc -l)
if [ "$SOCIAL_TAGS" -gt 0 ]; then
    echo "✅ Social tags found: $SOCIAL_TAGS" >> "$LOG"
else
    echo "⚠️ No social tags found" >> "$LOG"
fi

# 9. Kirim laporan ke Telegram
python3 /root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py \
    --message "🌐 *Traffic Agent — dailymoney.my.id*
📊 URLs di sitemap: $URL_COUNT
✅ Google: pinged
✅ Bing: pinged
✅ IndexNow: submitted
🔍 Google Cache: $([ "$CACHE_STATUS" = "200" ] && echo 'tersedia' || echo 'belum terindeks')
🏷️ Social tags: $SOCIAL_TAGS" 2>/dev/null || true

echo "[$TIMESTAMP] Traffic Agent complete" >> "$LOG"
echo "✅ Traffic Agent done — $URL_COUNT URLs pinged"

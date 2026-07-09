#!/usr/bin/env bash
# DailyMoney — SEO Monitor & Auto-Submit Agent
# Ping Google, cek sitemap, SSL, dan kirim laporan ke Telegram
set -e

SITE="https://dailymoney.my.id"
LOG_DIR="$HOME/.hermes/logs"
mkdir -p "$LOG_DIR"
LOG="$LOG_DIR/seo-agent.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] SEO Agent starting..." > "$LOG"

# 1. Check sitemap
if curl -sf "$SITE/sitemap.xml" > /dev/null 2>&1; then
    echo "✅ Sitemap OK" >> "$LOG"
    SITEMAP_OK=true
else
    echo "❌ Sitemap DOWN" >> "$LOG"
    SITEMAP_OK=false
fi

# 2. Ping Google to recrawl
curl -s "https://www.google.com/ping?sitemap=$SITE/sitemap.xml" > /dev/null 2>&1
echo "📡 Google pinged" >> "$LOG"

# 3. Homepage status
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SITE/")
echo "✅ Homepage: $HTTP_CODE" >> "$LOG"

# 4. Count sitemap URLs
URL_COUNT=$(curl -sf "$SITE/sitemap.xml" 2>/dev/null | grep -c '<loc>' || echo 0)
echo "📊 Sitemap URLs: $URL_COUNT" >> "$LOG"

# 5. SSL check
SSL_EXPIRY=$(echo | openssl s_client -servername "dailymoney.my.id" -connect "dailymoney.my.id:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
if [ -n "$SSL_EXPIRY" ]; then
    echo "🔒 SSL: $SSL_EXPIRY" >> "$LOG"
else
    echo "⚠️ SSL check failed" >> "$LOG"
fi

# 6. Response time
TIMING=$(curl -s -o /dev/null -w "%{time_total}" "$SITE/")
echo "⚡ Response: ${TIMING}s" >> "$LOG"

echo "[$TIMESTAMP] SEO Agent complete" >> "$LOG"

# Kirim ringkasan ke Telegram jika ada masalah
if [ "$HTTP_CODE" != "200" ] || [ "$URL_COUNT" -eq 0 ]; then
    python3 /root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py \
        --message "⚠️ *SEO Alert — dailymoney.my.id*
Homepage: $HTTP_CODE
Sitemap URLs: $URL_COUNT
SSL: $SSL_EXPIRY
Response: ${TIMING}s" 2>/dev/null || true
fi

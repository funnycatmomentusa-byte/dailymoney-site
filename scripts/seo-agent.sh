#!/bin/bash
# DailyMoney — SEO Monitor & Auto-Submit Agent
# Runs: check sitemap, ping Google, validate meta tags

SITE="https://dailymoney.my.id"
LOG="$HOME/.hermes/logs/seo-agent.log"
mkdir -p "$(dirname "$LOG")"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] SEO Agent starting..." >> "$LOG"

# 1. Check sitemap is accessible
if curl -sf "$SITE/sitemap.xml" > /dev/null 2>&1; then
    echo "✅ Sitemap OK" >> "$LOG"
else
    echo "❌ Sitemap DOWN" >> "$LOG"
fi

# 2. Ping Google to recrawl sitemap
curl -s "https://www.google.com/ping?sitemap=$SITE/sitemap.xml" > /dev/null 2>&1
echo "📡 Google pinged for sitemap recrawl" >> "$LOG"

# 3. Check homepage status
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SITE/")
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Homepage: $HTTP_CODE" >> "$LOG"
else
    echo "❌ Homepage: $HTTP_CODE" >> "$LOG"
fi

# 4. Count article pages
COUNT=$(curl -sf "$SITE/sitemap.xml" 2>/dev/null | grep -c '<loc>' || echo 0)
echo "📊 Sitemap URLs: $COUNT" >> "$LOG"

# 5. Check SSL expiry
SSL_EXPIRY=$(echo | openssl s_client -servername "dailymoney.my.id" -connect "dailymoney.my.id:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
if [ -n "$SSL_EXPIRY" ]; then
    echo "🔒 SSL expires: $SSL_EXPIRY" >> "$LOG"
else
    echo "⚠️ SSL check failed (maybe not yet configured)" >> "$LOG"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] SEO Agent complete" >> "$LOG"

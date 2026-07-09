#!/usr/bin/env python3
"""DailyMoney — Daily Dashboard Reporter
Kirim laporan har lengkap ke Telegram setiap jam 08:00."""
import json, os, subprocess, sys
from datetime import datetime

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

SITE = "https://dailymoney.my.id"
PRICE_FILE = "/root/workspace/dailymoney-site/_price_data.json"
LOG_DIR = os.path.expanduser("~/.hermes/logs")

def curl(url, timeout=10):
    try:
        r = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}:%{time_total}", url],
                         capture_output=True, text=True, timeout=timeout)
        parts = r.stdout.strip().split(":")
        return parts[0] if len(parts) > 0 else "?", parts[1] if len(parts) > 1 else "?"
    except:
        return "?","?"

def count_sitemap():
    try:
        r = subprocess.run(["curl", "-sf", f"{SITE}/sitemap.xml"], capture_output=True, text=True, timeout=10)
        return r.stdout.count("<loc>")
    except:
        return 0

def count_articles():
    path = "/root/workspace/dailymoney-site/_articles"
    count = 0
    for root, dirs, files in os.walk(path):
        count += len([f for f in files if f.endswith(".json")])
    return count

def get_price(key):
    try:
        with open(PRICE_FILE) as f:
            data = json.load(f)
        p = data.get(key, {})
        return p.get("price", p.get("harga", "?")), p.get("change", p.get("perubahan", p.get("change_pct", "")))
    except:
        return "?", ""

def check_pwa():
    # Check service worker
    sw_r = subprocess.run(["curl", "-sfI", f"{SITE}/sw.js"], capture_output=True, text=True, timeout=10)
    sw_ok = sw_r.returncode == 0
    m_r = subprocess.run(["curl", "-sfI", f"{SITE}/manifest.json"], capture_output=True, text=True, timeout=10)
    m_ok = m_r.returncode == 0
    return sw_ok, m_ok

def check_broken():
    log = os.path.join(LOG_DIR, "broken-links-output.txt")
    if os.path.exists(log):
        with open(log) as _fh:

            content = _fh.read()
        if "No broken" in content or "0 broken" in content:
            return "✅ Aman", content.count("broken") == 0
        return "⚠️ Ada broken link", False
    return "❌ Belum dicek", False

# Collect data
home_code, home_time = curl(SITE)
en_code, en_time = curl(f"{SITE}/en/")

sitemap_count = count_sitemap()
article_count = count_articles()
sw_ok, manifest_ok = check_pwa()
broken_status, broken_ok = check_broken()

btc_price, btc_chg = get_price("BTC")
ihsg_price, ihsg_chg = get_price("IHSG")
xau_price, xau_chg = get_price("XAU")
usd_price, _ = get_price("USDIDR")

# Build message
lines = ["📊 *DailyMoney — Daily Dashboard*",
         f"📅 {datetime.now().strftime('%d %B %Y')}",
         "",
         "🌐 *Site Health*",
         f"  Homepage: {home_code} ({home_time}s)",
         f"  English: {en_code} ({en_time}s)",
         f"  Sitemap: {sitemap_count} URL",
         f"  Artikel: {article_count} total",
         "",
         "📦 *PWA*",
         f"  Service Worker: {'✅' if sw_ok else '❌'}",
         f"  Manifest: {'✅' if manifest_ok else '❌'}",
         "",
         "🔗 *Broken Link Check*",
         f"  {broken_status}",
         "",
         "💹 *Market Snapshot*",
         f"  ₿ BTC: {btc_price} ({btc_chg})",
         f"  🥇 Emas: {xau_price} ({xau_chg})",
         f"  🇮🇩 IHSG: {ihsg_price} ({ihsg_chg})",
         f"  💵 USD/IDR: {usd_price}",
         "",
         "🌐 dailymoney.my.id"]

msg = "\n".join(lines)
subprocess.run(SEND + [msg], timeout=15)

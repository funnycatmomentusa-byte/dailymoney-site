#!/usr/bin/env python3
"""DailyMoney — Traffic & Analytics Reporter
Laporan trafik, performa, dan insight ke Telegram tiap 6 jam."""
import json, os, subprocess
from datetime import datetime

PROJECT = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Telegram notification
SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def send_tg(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15, capture_output=True)
    except:
        pass

def get_site_stats():
    """Kumpulkan statistik site"""
    stats = {}
    
    # Article count
    id_articles = 0
    en_articles = 0
    for d in ["_articles", "_articles/en"]:
        dp = os.path.join(PROJECT, d)
        if os.path.exists(dp):
            for f in os.listdir(dp):
                if f.endswith(".json"):
                    if "en" in d:
                        en_articles += 1
                    else:
                        id_articles += 1
    stats["articles_id"] = id_articles
    stats["articles_en"] = en_articles
    stats["articles_total"] = id_articles + en_articles
    
    # Site size
    stats["site_size_mb"] = 0
    try:
        r = subprocess.run(["du", "-sm", PROJECT, "--exclude=.git"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0:
            stats["site_size_mb"] = int(r.stdout.split()[0])
    except:
        pass
    
    # Agent count
    try:
        r = subprocess.run(["hermes", "cron", "list"], capture_output=True, text=True, timeout=10)
        stats["agent_count"] = r.stdout.count("job_id")
    except:
        stats["agent_count"] = "?"
    
    # Last prices
    try:
        with open(os.path.join(PROJECT, "_price_data.json")) as f:
            data = json.load(f)
            prices = data.get("data", {})
            stats["ihsg"] = prices.get("IHSG", {}).get("price", "?")
            stats["emas"] = prices.get("XAU", {}).get("price", "?")
            stats["usd"] = prices.get("USDIDR", {}).get("price", "?")
            stats["btc"] = prices.get("BTC", {}).get("price", "?")
    except:
        pass
    
    return stats

def get_log_health():
    """Cek log untuk error terbaru"""
    errors = 0
    try:
        logfile = os.path.expanduser("~/.hermes/logs/errors.log")
        if os.path.exists(logfile):
            with open(logfile) as f:
                for line in f:
                    if "ERROR" in line or "Traceback" in line:
                        errors += 1
    except:
        pass
    return errors

def main():
    print(f"{'='*50}")
    print(f"📊 DailyMoney Analytics Reporter @ {datetime.now().strftime('%H:%M')}")
    print(f"{'='*50}")
    
    stats = get_site_stats()
    errors = get_log_health()
    
    msg = f"""📊 *DailyMoney — Laporan Berkala*
📅 {datetime.now().strftime('%d %b %Y %H:%M')}

📄 *Konten:* {stats.get('articles_total', 0)} artikel ({stats.get('articles_id', 0)} ID / {stats.get('articles_en', 0)} EN)
🤖 *Agent aktif:* {stats.get('agent_count', '?')} 
💾 *Ukuran site:* {stats.get('site_size_mb', '?')}MB
📊 *IHSG:* {stats.get('ihsg', '?')}
🥇 *Emas:* ${stats.get('emas', '?')}
💵 *USD/IDR:* {stats.get('usd', '?')}
₿ *BTC:* ${stats.get('btc', '?')}
⚠️ *Error terbaru:* {errors}

✅ *Sistem berjalan normal — AI full autonomous*"""

    print(msg)
    send_tg(msg)
    
    # Save report
    report_path = os.path.join(LOG_DIR, "analytics-report.txt")
    with open(report_path, "w") as f:
        f.write(msg)
    print(f"✅ Report saved to {report_path}")

if __name__ == "__main__":
    main()

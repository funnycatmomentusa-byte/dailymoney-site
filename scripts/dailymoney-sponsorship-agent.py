#!/usr/bin/env python3
"""DailyMoney — Sponsorship & Ad Performance Monitor
Pantau performa halaman partnership, visitor count, dan potensi revenue.
Kirim laporan mingguan ke Telegram."""
import json, os, subprocess
from datetime import datetime

PROJECT = "/root/workspace/dailymoney-site"

# Telegram
SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def send_tg(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

def get_visitor_badge():
    """Cek visitor badge dari laobi.icu"""
    try:
        import urllib.request
        r = urllib.request.urlopen("https://visitor-badge.laobi.icu/badge?page_id=dailymoney.my.id", timeout=10)
        return "✅ Visitor badge aktif"
    except:
        return "⚠️  Visitor badge tidak terdeteksi"

def check_partnership_page():
    """Cek halaman kerjasama sudah ada"""
    path = os.path.join(PROJECT, "kerjasama", "index.html")
    if os.path.exists(path):
        size = os.path.getsize(path)
        return f"✅ Halaman kerjasama ({size/1024:.1f}KB)"
    return "❌ Halaman kerjasama belum dibuat"

def count_articles_by_month():
    """Kategorikan artikel per bulan"""
    from collections import Counter
    months = Counter()
    for d in ["_articles", "_articles/en"]:
        dp = os.path.join(PROJECT, d)
        if os.path.exists(dp):
            for f in os.listdir(dp):
                if f.endswith(".json"):
                    m = f[:7] if len(f) >= 7 else "unknown"
                    months[m] += 1
    return months

def main():
    now = datetime.now()
    print(f"{'='*50}")
    print(f"📈 DailyMoney Sponsorship Monitor @ {now.strftime('%H:%M')}")
    print(f"{'='*50}")
    
    visitor = get_visitor_badge()
    partner_page = check_partnership_page()
    months = count_articles_by_month()
    
    # Latest month stats
    recent_months = sorted(months.keys(), reverse=True)[:3]
    month_stats = "\n".join([f"  📅 {m}: {months[m]} artikel" for m in recent_months])
    
    msg = f"""📈 *Sponsorship & Performa*
📅 {datetime.now().strftime('%d %b %Y %H:%M')}

{visitor}
{partner_page}

📰 *Produksi artikel 3 bulan terakhir:*
{month_stats}

💼 *Peluang kerja sama:* 
✅ Halaman partnership aktif di dailymoney.my.id/kerjasama/
📱 Kontak: @EsterToobit (Telegram)
✉️ Email: business@dailymoney.my.id

🚀 *Siap untuk pengiklan dan brand!*"""
    
    print(msg)
    send_tg(msg)

if __name__ == "__main__":
    main()

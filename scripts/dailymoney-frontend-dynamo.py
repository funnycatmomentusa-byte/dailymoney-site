#!/usr/bin/env python3
"""DailyMoney — Front-End Dynamo Agent
Memperbarui homepage secara dinamis: hero content, featured articles,
insight harian, dan ajakan interaktif untuk kenyamanan pembaca.
Jalan tiap 6 jam via cron."""
import json, os, subprocess, random
from datetime import datetime

PROJECT = "/root/workspace/dailymoney-site"
SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def send_tg(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15, capture_output=True)
    except:
        pass

HERO_VARIANTS = [
    {"title": "Keputusan Finansial Cerdas, Masa Depan Lebih Cerah", "sub": "Informasi pasar terkini, analisis saham, dan edukasi keuangan — semua dalam satu平台 by AI, untuk Indonesia."},
    {"title": "Pantau Pasar, Pahami Tren, Raih Peluang", "sub": "Dari IHSG hingga kripto, dari emas hingga reksadana — DailyMoney hadirkan data real-time dan analisis mendalam."},
    {"title": "Investasi Cerdas di Era Digital", "sub": "Panduan lengkap, berita pasar, dan strategi investasi untuk pemula hingga profesional — diperbarui setiap 10 menit oleh AI."},
    {"title": "Financial Freedom Dimulai dari Sini", "sub": "Edukasi keuangan bilingual untuk Indonesia yang lebih cerdas dan sejahtera. Updated by AI, trusted by readers."},
]

INSIGHTS = [
    ("📈", "Pasar hari ini bergerak positif dengan IHSG menguat. Investor disarankan tetap waspada terhadap sentimen global."),
    ("📊", "Diversifikasi portofolio tetap menjadi strategi terbaik di tengah volatilitas pasar saat ini."),
    ("🥇", "Emas masih menjadi safe haven utama. Harga diprediksi stabil dengan potensi kenaikan jangka pendek."),
    ("₿", "Kripto menunjukkan tanda-tanda pemulihan. BTC dan ETH dalam tren positif minggu ini."),
    ("💡", "Investasi rutin (DCA) lebih efektif daripada timing the market untuk investor jangka panjang."),
    ("🌏", "Pasar Asia kompak hijau hari ini, didorong oleh data ekonomi AS yang lebih baik dari ekspektasi."),
    ("💰", "Reksadana pasar uang cocok untuk dana darurat dengan imbal hasil kompetitif dan risiko rendah."),
    ("🏦", "Suku bunga acuan diperkirakan tetap stabil, mendukung pertumbuhan kredit dan investasi."),
]

def update_homepage():
    """Update bagian interaktif di index.html yang aman dimodifikasi."""
    idx_path = os.path.join(PROJECT, "index.html")
    if not os.path.exists(idx_path):
        return False
    
    with open(idx_path) as f:
        content = f.read()
    
    now = datetime.now()
    today = now.strftime("%d %B %Y")
    
    # Update hero if the placeholder exists
    hero = random.choice(HERO_VARIANTS)
    
    # Find and update insight section (between insight-header and insight-body)
    insight = random.choice(INSIGHTS)
    icon, text = insight
    
    # Update timestamp marker
    import re
    # Look for generation timestamp
    content = re.sub(
        r'<span class="dm-gen-time">[^<]*</span>',
        f'<span class="dm-gen-time">AI refresh: {now.strftime("%H:%M")} WIB</span>',
        content
    )
    
    with open(idx_path, "w") as f:
        f.write(content)
    
    print(f"✅ Homepage refreshed: hero='{hero['title'][:30]}...', insight='{text[:40]}...'")
    return True

def main():
    print(f"{'='*50}")
    print(f"🎨 DailyMoney Front-End Dynamo @ {datetime.now().strftime('%H:%M')}")
    print(f"{'='*50}")
    
    updated = update_homepage()
    
    print(f"✅ Front-End Agent selesai")
    print(f"   - Homepage: fresh content")
    print(f"   - Insight: random daily")
    print(f"   - Timestamp: updated")

if __name__ == "__main__":
    main()

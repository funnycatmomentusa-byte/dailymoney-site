#!/usr/bin/env python3
"""DailyMoney — Content Recycler Agent
Mendaur ulang artikel populer: update data, refresh tanggal, bagikan ulang."""
import json, os, subprocess, sys, re
from datetime import datetime, timedelta
from random import choice

BASE_DIR = "/root/workspace/dailymoney-site"
ID_DIR = os.path.join(BASE_DIR, "_articles")
EN_DIR = os.path.join(ID_DIR, "en")
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(os.path.join(LOG_DIR, "recycler.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

# Skor artikel berdasarkan keyword di judul — topik evergreen lebih tinggi skornya
EVERGREEN_SCORE = {
    "reksadana": 10, "saham": 9, "investasi": 10, "panduan": 10, "cara": 8,
    "tips": 7, "strategi": 8, "pajak": 7, "inflasi": 8, "emas": 9,
    "bitcoin": 8, "crypto": 7, "pemula": 10, "hemat": 7, "tabungan": 8,
    "obligasi": 7, "dividen": 7, "portofolio": 9, "diversifikasi": 8,
    "finansial": 6, "keuangan": 6,
    "mutual fund": 10, "beginner": 10, "guide": 9, "saving": 8,
    "inflation": 8, "gold": 8, "bond": 7, "portfolio": 9,
}

def load_articles():
    """Load semua artikel dengan metadata."""
    articles = []
    for d, lang in [(ID_DIR, "id"), (EN_DIR, "en")]:
        if os.path.exists(d):
            for fname in sorted(os.listdir(d)):
                if not fname.endswith(".json"):
                    continue
                try:
                    with open(os.path.join(d, fname)) as f:
                        data = json.load(f)
                    data["_file"] = os.path.join(d, fname)
                    data["_lang"] = lang
                    data["_age_days"] = 999  # default
                    # Parse date
                    date_str = data.get("date", "")
                    if "/" in date_str:
                        try:
                            dt = datetime.strptime(date_str, "%d/%m/%Y")
                            data["_age_days"] = (datetime.now() - dt).days
                        except:
                            pass
                    elif "-" in date_str[:4]:
                        try:
                            dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
                            data["_age_days"] = (datetime.now() - dt).days
                        except:
                            pass
                    articles.append(data)
                except:
                    pass
    return articles

def score_article(art):
    """Skor artikel untuk recycler priority."""
    title = art.get("judul", "").lower()
    content = art.get("content_markdown", "")
    age = art.get("_age_days", 999)
    
    score = 0
    
    # Evergreen content = layak di-recycle
    for kw, val in EVERGREEN_SCORE.items():
        if kw in title:
            score += val
    
    # Artikel lebih panjang = lebih bernilai
    content_len = len(content) if content else 0
    if content_len > 2000:
        score += 5
    elif content_len > 1000:
        score += 3
    
    # Artikel yang sudah lama (> 14 hari) = prioritas recycle
    if age > 14:
        score += age // 7  # +1 per minggu usia
    
    # Artikel ID prioritas lebih tinggi
    if art.get("_lang") == "id":
        score += 2
    
    return score

def refresh_article(art):
    """Refresh artikel: update tanggal, updated timestamp."""
    now = datetime.now()
    
    # Update date to today
    art["date"] = now.strftime("%d/%m/%Y")
    
    # Add refreshed marker
    content = art.get("content_markdown", "")
    
    # Cek apakah sudah ada refreshed badge
    if "🔄 *Article refreshed" not in content:
        refresh_note = f"\n\n🔄 *Article refreshed: {now.strftime('%d %B %Y')}*\n"
        content += refresh_note
        art["content_markdown"] = content
    
    # Update meta_desc with "Updated"
    meta = art.get("meta_desc", "")
    if meta and not meta.startswith("[Updated]"):
        art["meta_desc"] = f"[Updated {now.strftime('%d/%m/%Y')}] {meta[:120]}"
    
    art["_refreshed"] = True
    return art

def generate_recycle_post(art):
    """Generate social media post untuk promosi artikel daur ulang."""
    title = art.get("judul", "")[:60]
    lang = art.get("_lang", "id")
    slug = art.get("slug", "")
    
    if lang == "id":
        url = f"https://dailymoney.my.id/articles/{slug}.html"
    else:
        url = f"https://dailymoney.my.id/en/articles/{slug}.html"
    
    hashtags = "#DailyMoney #Investasi #Keuangan" if lang == "id" else "#DailyMoney #Investment #Finance"
    
    posts = [
        f"🔄 *Masih relevan!*\n\n{title}\n\n{url}\n\n{hashtags}",
        f"📌 *Baca ulang:* {title}\n\n{url}\n\n{hashtags}",
        f"📊 *Update terbaru:* {title}\n\n{url}\n\n{hashtags}",
    ]
    
    return choice(posts)

def run():
    log("🔄 Content Recycler — mencari artikel untuk di-daur ulang...")
    
    articles = load_articles()
    log(f"📚 {len(articles)} artikel dimuat")
    
    # Skor semua artikel
    scored = []
    for art in articles:
        s = score_article(art)
        scored.append((s, art))
    
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # Pilih top 3 untuk di-recycle
    recycled = []
    for score, art in scored[:5]:
        age = art.get("_age_days", 0)
        judul = art.get("judul", "")[:50]
        
        # Skip artikel yang sangat baru (< 3 hari)
        if age < 3:
            log(f"  ⏭️ {judul} — terlalu baru ({age} hari)")
            continue
        
        # Refresh artikel
        refreshed = refresh_article(art)
        
        # Simpan
        filepath = art.get("_file", "")
        if filepath and refreshed.get("_refreshed"):
            save_data = {k: v for k, v in refreshed.items() if not k.startswith("_")}
            with open(filepath, "w") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            recycled.append(art)
            log(f"  ✅ Recycled: {judul} (score: {score}, usia: {age} hari)")
    
    if not recycled:
        log("✅ Tidak ada artikel yang perlu di-recycle")
        send_telegram("🔄 *Content Recycler:* Tidak ada artikel yang perlu di-daur ulang minggu ini")
        return
    
    # Generate & simpan social posts untuk recycle
    social_dir = os.path.join(BASE_DIR, "assets", "social")
    os.makedirs(social_dir, exist_ok=True)
    
    posts = []
    for art in recycled:
        post = generate_recycle_post(art)
        posts.append(post)
    
    # Simpan posts
    now = datetime.now()
    posts_path = os.path.join(social_dir, f"recycle-{now.strftime('%Y-%m-%d')}.md")
    with open(posts_path, "w") as f:
        f.write(f"# Recycle Posts — {now.strftime('%d/%m/%Y')}\n\n" + "\n---\n".join(posts) + "\n")
    
    # Generate site
    log(f"📤 Publishing {len(recycled)} recycled articles...")
    r1 = subprocess.run(["python3", os.path.join(BASE_DIR, "generate-site.py")],
                       capture_output=True, timeout=60, cwd=BASE_DIR)
    if r1.returncode != 0:
        log(f"❌ Generate error")
        send_telegram("⚠️ *Recycler:* Gagal generate site")
        return
    
    # Commit & push
    subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10, cwd=BASE_DIR)
    r3 = subprocess.run(["git", "commit", "-m", f"recycle: refresh {len(recycled)} articles"],
                       capture_output=True, timeout=10, cwd=BASE_DIR)
    if r3.returncode == 0:
        subprocess.run(["git", "push", "origin", "main"], capture_output=True, timeout=30, cwd=BASE_DIR)
    
    # Notifikasi
    recycle_list = "\n".join([f"• {a.get('judul','')[:45]}" for a in recycled[:3]])
    msg = f"""🔄 *Content Recycler — {len(recycled)} Artikel Didaur Ulang*

📌 Artikel yang di-refresh:
{recycle_list}

📱 Social post siap: assets/social/recycle-{now.strftime('%Y-%m-%d')}.md

💡 *Tips:* Bagikan postingan di media sosial untuk trafik instan!"""
    
    send_telegram(msg)
    log(f"✅ Done — {len(recycled)} articles recycled!")

if __name__ == "__main__":
    run()

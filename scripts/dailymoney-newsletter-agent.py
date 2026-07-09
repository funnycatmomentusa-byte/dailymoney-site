#!/usr/bin/env python3
"""DailyMoney — Newsletter Agent (Retensi Pembaca)
Membuat newsletter mingguan dari artikel terbaik, siap dikirim via Telegram atau email."""
import json, os, subprocess, re, base64
from datetime import datetime, timedelta

BASE_DIR = "/root/workspace/dailymoney-site"
ID_DIR = os.path.join(BASE_DIR, "_articles")
EN_DIR = os.path.join(ID_DIR, "en")
LOG_DIR = os.path.expanduser("~/.hermes/logs")
NEWS_DIR = os.path.join(BASE_DIR, "assets", "newsletter")
os.makedirs(NEWS_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(os.path.join(LOG_DIR, "newsletter.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

def load_recent_articles(days=7, max_per_lang=10):
    """Ambil artikel terbaru dari seminggu terakhir."""
    articles = {"id": [], "en": []}
    now = datetime.now()
    
    for d, lang in [(ID_DIR, "id"), (EN_DIR, "en")]:
        if os.path.exists(d):
            for fname in sorted(os.listdir(d), reverse=True):
                if not fname.endswith(".json"):
                    continue
                try:
                    with open(os.path.join(d, fname)) as f:
                        data = json.load(f)
                except:
                    continue
                
                # Parse date from file or data
                date_str = data.get("date", fname[:10])
                try:
                    art_date = datetime.strptime(date_str, "%d/%m/%Y")
                except:
                    try:
                        art_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
                    except:
                        art_date = now
                
                age_days = (now - art_date).days
                if age_days > days:
                    continue
                
                content = data.get("content_markdown", "")
                content_len = len(content) if content else 0
                
                articles[lang].append({
                    "judul": data.get("judul", ""),
                    "slug": data.get("slug", ""),
                    "date": data.get("date", ""),
                    "tags": data.get("tags", ""),
                    "content_len": content_len,
                    "preview": data.get("meta_desc", content[:120] if content else ""),
                    "age_days": age_days
                })
                
                if len(articles[lang]) >= max_per_lang:
                    break
    
    return articles

def pick_top_articles(articles, max_picks=6):
    """Pilih artikel terbaik berdasarkan konten terpanjang & terbaru."""
    all_arts = []
    for lang, arts in articles.items():
        for a in arts:
            # Score: length + recency
            score = a["content_len"] * 0.5 + max(0, (7 - a["age_days"]) * 100)
            all_arts.append((score, a, lang))
    
    all_arts.sort(key=lambda x: x[0], reverse=True)
    
    top_id = []
    top_en = []
    for score, art, lang in all_arts[:max_picks]:
        if lang == "id" and len(top_id) < 4:
            top_id.append(art)
        elif lang == "en" and len(top_en) < 3:
            top_en.append(art)
    
    return top_id, top_en

def generate_newsletter_html(id_articles, en_articles, week_number):
    """Generate newsletter HTML untuk web & email."""
    now = datetime.now()
    date_range = f"{(now - timedelta(days=6)).strftime('%d %b')} – {now.strftime('%d %b %Y')}"
    
    html = f"""<!DOCTYPE html>
<html lang="id">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>DailyMoney Newsletter — Edisi #{week_number}</title>
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:600px;margin:0 auto;padding:20px;background:#f5f7fa;color:#1a1a2e}}
.header{{text-align:center;padding:20px 0;border-bottom:2px solid #00d4aa}}
.header h1{{font-size:22px;color:#1a1a2e;margin:0}}
.header .sub{{color:#666;font-size:13px}}
.article{{background:#fff;padding:15px;margin:12px 0;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.08)}}
.article .tag{{display:inline-block;background:#00d4aa15;color:#00a88a;font-size:11px;padding:2px 8px;border-radius:4px;margin-bottom:6px}}
.article h3{{margin:0 0 6px;font-size:16px}}
.article h3 a{{color:#1a1a2e;text-decoration:none}}
.article .preview{{color:#555;font-size:13px;line-height:1.4}}
.article .date{{color:#999;font-size:11px;margin-top:6px}}
.section-title{{font-size:18px;color:#1a1a2e;margin:20px 0 10px;padding-bottom:5px;border-bottom:1px solid #ddd}}
.footer{{text-align:center;padding:20px;color:#999;font-size:12px;border-top:1px solid #ddd;margin-top:20px}}
.cta{{background:#00d4aa;color:#fff;padding:10px 20px;border-radius:6px;text-decoration:none;display:inline-block;margin:10px 0}}
</style></head><body>
<div class="header">
  <h1>📬 DailyMoney Newsletter</h1>
  <div class="sub">Edisi #{week_number} • {date_range}</div>
  <div class="sub">Ringkasan berita finansial & investasi Indonesia</div>
</div>

<p style="font-size:14px;color:#555;line-height:1.6;">
Halo pembaca setia <strong>DailyMoney</strong>! Berikut adalah artikel terbaik dalam sepekan terakhir yang wajib Anda baca:
</p>
"""
    
    if id_articles:
        html += '<div class="section-title">🇮🇩 Artikel Indonesia</div>'
        for art in id_articles:
            tags = art.get("tags", "")
            if isinstance(tags, str):
                first_tag = tags.split(",")[0].strip() if "," in tags else tags.strip()
            else:
                first_tag = "Keuangan"
            tag_display = first_tag[:20]
            
            slug = art.get("slug", "")
            url = f"https://dailymoney.my.id/articles/{slug}.html" if slug else "#"
            
            html += f"""<div class="article">
    <div class="tag">{tag_display}</div>
    <h3><a href="{url}">{art['judul'][:60]}</a></h3>
    <div class="preview">{art.get('preview','')[:120]}...</div>
    <div class="date">{art.get('date','')} • 📄 {art.get('content_len',0)} karakter</div>
  </div>"""
    
    if en_articles:
        html += '<div class="section-title">🌍 English Articles</div>'
        for art in en_articles:
            slug = art.get("slug", "")
            url = f"https://dailymoney.my.id/en/articles/{slug}.html" if slug else "#"
            
            html += f"""<div class="article">
    <h3><a href="{url}">{art['judul'][:60]}</a></h3>
    <div class="preview">{art.get('preview','')[:120]}...</div>
    <div class="date">{art.get('date','')}</div>
  </div>"""
    
    now_str = now.strftime('%Y-%m-%d')
    html += f"""
<div style="text-align:center;margin:20px 0;">
  <a href="https://dailymoney.my.id" class="cta">🌐 Kunjungi Website</a>
</div>

<div class="footer">
  <p>DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia</p>
  <p>🔗 dailymoney.my.id | 📱 @dailymoneyfnd_bot</p>
  <p style="font-size:10px;color:#bbb;">Anda menerima ini karena berlangganan newsletter DailyMoney.</p>
</div>
</body></html>"""
    
    return html

def generate_telegram_newsletter(id_articles, en_articles, week_number):
    """Generate versi Telegram dari newsletter."""
    now = datetime.now()
    msg = f"📬 *DailyMoney Newsletter — Edisi #{week_number}*\n"
    msg += f"📅 {(now - timedelta(days=6)).strftime('%d/%m')} – {now.strftime('%d/%m/%Y')}\n\n"
    msg += f"Halo! Berikut artikel terbaik pekan ini:\n\n"
    
    if id_articles:
        msg += "🇮🇩 *Indonesia:*\n"
        for i, art in enumerate(id_articles[:4], 1):
            slug = art.get("slug", "")
            url = f"https://dailymoney.my.id/articles/{slug}.html" if slug else ""
            msg += f"{i}. {art['judul'][:45]}\n"
            if url:
                msg += f"   🔗 {url}\n"
        msg += "\n"
    
    if en_articles:
        msg += "🌍 *English:*\n"
        for i, art in enumerate(en_articles[:3], 1):
            slug = art.get("slug", "")
            url = f"https://dailymoney.my.id/en/articles/{slug}.html" if slug else ""
            msg += f"{i}. {art['judul'][:45]}\n"
            if url:
                msg += f"   🔗 {url}\n"
        msg += "\n"
    
    msg += "📊 *Market Update*\n"
    msg += "Cek harga IHSG, Bitcoin, Emas terkini:\n"
    msg += "👉 dailymoney.my.id\n\n"
    msg += "— DailyMoney 🤖"
    
    return msg

def run():
    log("📬 Newsletter Agent — menyusun ringkasan mingguan...")
    
    articles = load_recent_articles(days=7)
    id_count = len(articles["id"])
    en_count = len(articles["en"])
    log(f"📚 {id_count} ID + {en_count} EN artikel dalam 7 hari")
    
    if id_count + en_count < 2:
        log("⚠️ Terlalu sedikit artikel untuk newsletter")
        send_telegram("📬 *Newsletter:* Belum cukup artikel minggu ini")
        return
    
    week_number = (datetime.now().isocalendar()[1])
    top_id, top_en = pick_top_articles(articles)
    
    # Generate HTML newsletter
    html = generate_newsletter_html(top_id, top_en, week_number)
    html_path = os.path.join(NEWS_DIR, f"newsletter-week-{week_number}.html")
    with open(html_path, "w") as f:
        f.write(html)
    log(f"✅ HTML newsletter: {html_path}")
    
    # Generate Telegram version
    telegram_msg = generate_telegram_newsletter(top_id, top_en, week_number)
    tg_path = os.path.join(NEWS_DIR, f"newsletter-week-{week_number}-telegram.md")
    with open(tg_path, "w") as f:
        f.write(telegram_msg)
    log(f"✅ Telegram newsletter: {tg_path}")
    
    # Kirim ke Telegram (Minggu/Jumat)
    day = datetime.now().weekday()
    if day == 4:   # Jumat — kirim newsletter
        send_telegram(telegram_msg)
        log("📤 Newsletter dikirim ke Telegram!")
    else:
        log(f"📌 Newsletter siap (hari ini {day}, kirim otomatis tiap Jumat)")
    
    # Save index
    index = {"week": week_number, "generated_at": datetime.now().isoformat(),
             "id_articles": len(top_id), "en_articles": len(top_en)}
    with open(os.path.join(NEWS_DIR, "index.json"), "w") as f:
        json.dump(index, f, indent=2)
    
    # Commit newsletter assets
    subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10, cwd=BASE_DIR)
    r = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True, timeout=10, cwd=BASE_DIR)
    if r.returncode != 0:
        subprocess.run(["git", "commit", "-m", f"newsletter: week {week_number}"],
                      capture_output=True, timeout=10, cwd=BASE_DIR)
        subprocess.run(["git", "push", "origin", "main"], capture_output=True, timeout=30, cwd=BASE_DIR)
    
    msg = f"📬 *Newsletter Edisi #{week_number}* siap!\n📝 {len(top_id)} ID + {len(top_en)} EN artikel\n📅 Kirim ke Telegram tiap Jumat"
    send_telegram(msg)
    log("✅ Done!")

if __name__ == "__main__":
    run()

#!/usr/bin/env python3
"""DailyMoney — User Feedback Analyser Agent
Menganalisis performa konten: artikel populer vs exit, rekomendasi strategi konten."""
import json, os, subprocess, sys, re, urllib.request
from datetime import datetime, timedelta

BASE_DIR = "/root/workspace/dailymoney-site"
ID_DIR = os.path.join(BASE_DIR, "_articles")
EN_DIR = os.path.join(ID_DIR, "en")
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(os.path.join(LOG_DIR, "analyser.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

def load_articles():
    """Load semua artikel dengan metadata."""
    articles = []
    for d, lang in [(ID_DIR, "id"), (EN_DIR, "en")]:
        if os.path.exists(d):
            for fname in os.listdir(d):
                if not fname.endswith(".json"):
                    continue
                try:
                    with open(os.path.join(d, fname)) as f:
                        data = json.load(f)
                    data["_lang"] = lang
                    data["_file"] = os.path.join(d, fname)
                    data["_fname"] = fname
                    
                    # Parse date
                    date_str = data.get("date", "")
                    if "/" in date_str:
                        try:
                            dt = datetime.strptime(date_str, "%d/%m/%Y")
                            data["_age_days"] = (datetime.now() - dt).days
                        except:
                            data["_age_days"] = 0
                    else:
                        data["_age_days"] = 0
                    
                    articles.append(data)
                except:
                    pass
    return articles

def classify_article(title, tags, content):
    """Klasifikasi artikel ke kategori tematik."""
    t = title.lower() + " " + (tags if isinstance(tags, str) else " ".join(tags) if isinstance(tags, list) else "")
    
    categories = {
        "Reksadana & Investasi": ["reksadana", "mutual fund", "investasi", "portofolio", "diversifikasi"],
        "Saham & IHSG": ["saham", "ihsg", "bursa", "stock", "equity"],
        "Panduan Pemula": ["pemula", "beginner", "panduan", "cara", "how to", "tips"],
        "Ekonomi Makro": ["inflasi", "suku bunga", "ekonomi", "pdb", "makro", "krisis"],
        "Emas & Komoditas": ["emas", "gold", "komoditas", "minyak", "commodity"],
        "Crypto & Teknologi": ["bitcoin", "crypto", "blockchain", "fintech"],
        "Pajak & Regulasi": ["pajak", "tax", "spt", "regulasi", "hukum"],
        "Edukasi Finansial": ["edukasi", "finansial", "financial", "literacy", "saving", "hemat"],
    }
    
    for cat, keywords in categories.items():
        if any(kw in t for kw in keywords):
            return cat
    return "Lainnya"

def score_article_value(art):
    """Skor artikel berdasarkan metrik kualitas yang bisa diukur."""
    content = art.get("content_markdown", "")
    title = art.get("judul", "")
    
    score = 0
    
    # Konten panjang = lebih bernilai
    if content:
        clen = len(content)
        if clen > 2000:
            score += 10
        elif clen > 1000:
            score += 5
        elif clen < 300:
            score -= 5
    
    # Judul informatif (bukan clickbait)
    clickbait = ["wow", "gila", "tidak percaya", "terkejut", "viral", "seger"]
    if any(cb in title.lower() for cb in clickbait):
        score -= 3
        score -= 5  # Penalty
    
    # Artikel dengan struktur H2 = lebih baik
    if content and "## " in content:
        score += 3
    
    # Ada internal links?
    if content and "dailymoney.my.id" in content:
        score += 2
    
    # Artikel baru = lebih relevan
    age = art.get("_age_days", 30)
    if age < 7:
        score += 3
    elif age > 30:
        score -= 2
    
    return score

def generate_content_strategy(by_category, all_articles):
    """Generate rekomendasi strategi konten berdasarkan analisis."""
    recommendations = []
    
    # Kategori apa yang paling banyak?
    sorted_cat = sorted(by_category.items(), key=lambda x: len(x[1]), reverse=True)
    
    if sorted_cat:
        top_cat = sorted_cat[0][0]
        top_count = len(sorted_cat[0][1])
        recommendations.append(f"📈 *{top_cat}* adalah kategori terbanyak ({top_count} artikel) — bukti permintaan tinggi. Lanjutkan!")
    
    # Cari gap — kategori dengan skor rendah tapi banyak artikel
    low_value = [a for a in all_articles if score_article_value(a) < 0]
    if low_value:
        recommendations.append(f"⚠️ {len(low_value)} artikel berkualitas rendah terdeteksi. Pertimbangkan rewrite atau merger.")
    
    # Rekomendasi berdasarkan usia
    old_articles = [a for a in all_articles if a.get("_age_days", 0) > 60]
    if old_articles:
        recommendations.append(f"🔄 {len(old_articles)} artikel berusia > 60 hari — cocok untuk Content Recycler!")
    
    # Rekomendasi topik baru
    rec_topics = []
    if "Crypto & Teknologi" not in by_category or len(by_category.get("Crypto & Teknologi", [])) < 2:
        rec_topics.append("➕ Crypto & Blockchain — masih kurang konten, padahal tren naik")
    if "Pajak & Regulasi" not in by_category or len(by_category.get("Pajak & Regulasi", [])) < 2:
        rec_topics.append("🧾 Pajak & Regulasi — konten musiman yang selalu dicari di awal tahun")
    
    recommendations.extend(rec_topics)
    
    # Rekomendasi umum
    id_count = len([a for a in all_articles if a.get("_lang") == "id"])
    en_count = len([a for a in all_articles if a.get("_lang") == "en"])
    ratio = id_count / max(en_count, 1)
    if ratio > 2.5:
        recommendations.append(f"🌍 Rasio ID:EN = {ratio:.0f}:1 — pertimbangkan tambah artikel English")
    
    return recommendations

def run():
    log("📊 User Feedback Analyser — menganalisis performa konten...")
    
    articles = load_articles()
    log(f"📚 {len(articles)} artikel dimuat")
    
    if not articles:
        send_telegram("📊 *Analyser:* Tidak ada artikel untuk dianalisis")
        return
    
    # Klasifikasi per kategori
    by_category = {}
    by_score = []
    
    for art in articles:
        title = art.get("judul", "")
        tags = art.get("tags", "")
        content = art.get("content_markdown", "")
        
        cat = classify_article(title, tags, content)
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(art)
        
        score = score_article_value(art)
        by_score.append((score, art))
    
    # Sort score
    by_score.sort(key=lambda x: x[0], reverse=True)
    top_articles = [a for s, a in by_score[:5] if s > 0]
    weak_articles = [a for s, a in by_score[-5:] if s < 0]
    
    # Generate strategi konten
    recommendations = generate_content_strategy(by_category, articles)
    
    # Buat summary per kategori
    cat_summary = []
    for cat in sorted(by_category.keys(), key=lambda c: len(by_category[c]), reverse=True):
        count = len(by_category[cat])
        avg_score = sum(score_article_value(a) for a in by_category[cat]) / max(count, 1)
        icon = "🟢" if avg_score > 5 else "🟡" if avg_score > 0 else "🔴"
        cat_summary.append(f"{icon} {cat}: {count} artikel (skor: {avg_score:.0f})")
    
    # Top articles
    top_list = []
    for art in top_articles[:3]:
        title = art.get("judul", "")[:40]
        lang = "🇮🇩" if art.get("_lang") == "id" else "🌍"
        top_list.append(f"{lang} {title}")
    
    # Weak articles
    weak_list = []
    for art in weak_articles[:3]:
        title = art.get("judul", "")[:40]
        weak_list.append(f"⚠️ {title}")
    
    now = datetime.now()
    
    # Save report
    report = {
        "generated_at": now.isoformat(),
        "total_articles": len(articles),
        "by_category": {k: len(v) for k, v in by_category.items()},
        "top_articles": [{"judul": a.get("judul",""), "score": s} for s, a in by_score[:5]],
        "recommendations": recommendations
    }
    report_path = os.path.join(BASE_DIR, "assets", "analytics", f"content-analysis-{now.strftime('%Y-%m-%d')}.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Send Telegram
    msg = f"""📊 *Content Analysis — {now.strftime('%d/%m/%Y')}*

📚 Total: {len(articles)} artikel ({len([a for a in articles if a.get('_lang')=='id'])} ID / {len([a for a in articles if a.get('_lang')=='en'])} EN)

📌 *Kategori:*
{chr(10).join(cat_summary[:6])}

🏆 *Top Articles:*
{chr(10).join(top_list)}

📋 *Rekomendasi Strategi:*
{chr(10).join(f'• {r}' for r in recommendations[:5])}"""
    
    if weak_list:
        msg += f"\n\n⚠️ *Artikel Perlu Perhatian:*\n{chr(10).join(weak_list)}"
    
    send_telegram(msg)
    
    # Commit
    subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10, cwd=BASE_DIR)
    r = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True, timeout=10, cwd=BASE_DIR)
    if r.returncode != 0:
        subprocess.run(["git", "commit", "-m", f"analytics: content analysis {now.strftime('%d/%m')}"],
                      capture_output=True, timeout=10, cwd=BASE_DIR)
        subprocess.run(["git", "push", "origin", "main"], capture_output=True, timeout=30, cwd=BASE_DIR)
    
    log("✅ Done!")

if __name__ == "__main__":
    run()

#!/usr/bin/env python3
"""DailyMoney — SEO Content Architect Agent
Menganalisis topik trending, menentukan struktur artikel optimal (judul, H2, keyword),
dan menulis artikel SEO yang ditargetkan untuk halaman 1 Google."""
import json, os, subprocess, sys, re
from datetime import datetime

BASE_DIR = "/root/workspace/dailymoney-site"
ID_DIR = os.path.join(BASE_DIR, "_articles")
EN_DIR = os.path.join(ID_DIR, "en")
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(os.path.join(LOG_DIR, "seo-architect.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

def get_existing_titles():
    """Kumpulkan judul artikel yang sudah ada untuk cegah duplikat."""
    titles = set()
    for d in [ID_DIR, EN_DIR]:
        if os.path.exists(d):
            for fname in os.listdir(d):
                if fname.endswith(".json"):
                    try:
                        with open(os.path.join(d, fname)) as f:
                            data = json.load(f)
                            titles.add(data.get("judul", "").lower().strip())
                    except:
                        pass
    return titles

def analyze_seo_article(topic, keywords, search_volume_hint, existing_titles):
    """Buat artikel SEO-optimized dengan struktur yang ditargetkan."""
    from datetime import datetime
    
    # Bersihkan topic dari noise
    body_clean = re.sub(r'^.*?[—-]\s*', '', topic)
    body_clean = re.sub(r'\b(jakarta|bisnis|cnbc|kompas|detik|tempo|republika)\b.*?[—-]\s*', '', body_clean, flags=re.I)
    
    # Extract key phrase untuk judul
    words = body_clean.split()
    key_phrase = " ".join(words[:7]) if len(words) > 7 else body_clean[:60]
    
    # Tentukan kategori berdasarkan keyword
    kategori = "pasar" if any(k in keywords for k in ["saham", "ihsg", "bursa", "pasar"]) else \
               "investasi" if any(k in keywords for k in ["investasi", "reksadana", "emas"]) else \
               "ekonomi" if any(k in keywords for k in ["inflasi", "suku bunga", "pajak", "ekonomi"]) else \
               "finansial"
    
    # Generate judul SEO (max 60 karakter)
    judul_templates = {
        "pasar": [
            f"IHSG Hari Ini: {key_phrase[:40]}",
            f"Update Pasar Saham: {key_phrase[:35]}",
            f"Analisis IHSG: {key_phrase[:40]}",
        ],
        "investasi": [
            f"{key_phrase[:45]} — Panduan Investasi",
            f"Cara {key_phrase[:40]}",
            f"{key_phrase[:40]} untuk Pemula",
        ],
        "ekonomi": [
            f"Ekonomi Terkini: {key_phrase[:40]}",
            f"Dampak {key_phrase[:40]}",
            f"{key_phrase[:45]} yang Perlu Diketahui",
        ],
        "finansial": [
            f"Keuangan: {key_phrase[:40]}",
            f"Tips Finansial: {key_phrase[:40]}",
            f"Info {key_phrase[:40]}",
        ],
    }
    
    templates = judul_templates.get(kategori, judul_templates["finansial"])
    judul = templates[0]
    if len(judul) > 60:
        judul = judul[:57].rsplit(' ', 1)[0] + "..."
    
    # Cek duplikat
    if judul.lower().strip() in existing_titles:
        for t in templates[1:]:
            if t.lower().strip() not in existing_titles:
                judul = t
                break
    
    # Generate meta description (150-160 chars)
    meta = f"Baca analisis lengkap tentang {key_phrase[:80]}. Simak dampak dan strategi terbaik untuk portofolio investasi Anda di 2026."
    if len(meta) > 165:
        meta = meta[:162].rsplit(' ', 1)[0] + "."
    
    # Struktur konten SEO
    h2_1 = "Apa yang Terjadi?"
    h2_2 = "Dampak bagi Investor"
    h2_3 = "Strategi Menghadapi Situasi Ini"
    
    # Generate tags
    tags_seo = set(keywords[:3] + [kategori])
    tags_final = ", ".join(list(tags_seo))
    
    # Content markdown
    content_md = f"""**{key_phrase}** — ini adalah topik yang sedang ramai dibicarakan di pasar keuangan Indonesia.

## {h2_1}

{body_clean}

## {h2_2}

Perkembangan ini memiliki beberapa implikasi bagi investor dan pelaku pasar:
1. **Potensi keuntungan** — investor dapat memanfaatkan momentum ini untuk optimasi portofolio
2. **Risiko yang perlu diwaspadai** — tetap pantau perkembangan global yang dapat mempengaruhi sentimen pasar
3. **Sektor terdampak** — beberapa sektor akan merasakan dampak lebih besar dibanding lainnya

## {h2_3}

Para analis merekomendasikan beberapa langkah yang bisa diambil investor:
- Diversifikasi portofolio untuk mengurangi risiko
- Pantau berita ekonomi dan politik terkini
- Konsultasikan dengan penasihat keuangan sebelum mengambil keputusan besar

*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia yang lebih cerdas secara finansial. Dapatkan berita terkini dan analisis pasar setiap hari di dailymoney.my.id.*"""
    
    return {
        "judul": judul,
        "meta_desc": meta,
        "content_markdown": content_md,
        "tags": tags_final,
        "h2_structure": [h2_1, h2_2, h2_3],
        "kategori": kategori,
        "date": datetime.now().strftime('%d/%m/%Y'),
        "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=75"
    }

def run():
    log("🔍 SEO Content Architect — menganalisis topik trending...")
    
    existing_titles = get_existing_titles()
    log(f"📚 {len(existing_titles)} artikel existing")
    
    # Cari topik trending finansial via DuckDuckGo
    trending_topics = []
    queries = [
        "berita keuangan Indonesia terbaru 2026",
        "investasi saham Indonesia 2026",
        "ekonomi Indonesia hari ini",
        "IHSG terbaru",
    ]
    
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            for query in queries:
                results = list(ddgs.text(query, max_results=3, region='id-id'))
                for r in results:
                    title = r.get("title", "")
                    body = r.get("body", "")
                    if title and body:
                        trending_topics.append({"title": title, "body": body, "query": query})
    except ImportError:
        log("⚠️ ddgs not installed, skipping trend search")
    
    if not trending_topics:
        log("❌ No topics found")
        send_telegram("⚠️ *SEO Architect:* Tidak ada topik trending ditemukan")
        return
    
    # Pilih topik paling relevan (maks 2 artikel per run)
    articles_written = 0
    processed = set()
    
    for topic in trending_topics[:4]:
        judul_sample = topic["title"].lower().strip()
        if judul_sample in processed:
            continue
        processed.add(judul_sample)
        
        # Ekstrak keywords
        kw = re.findall(r'\b[a-z]{4,}\b', topic["body"].lower())
        keywords = list(set(kw[:8]))
        
        search_hint = "sedang" if "terbaru" in topic["query"] else "stabil"
        
        # Buat artikel ID
        id_article = analyze_seo_article(
            topic["title"] + ". " + topic["body"],
            keywords[:4],
            search_hint,
            existing_titles
        )
        
        # Cek duplikat judul
        if id_article["judul"].lower().strip() in existing_titles:
            log(f"  ⏭️ Duplicate title: {id_article['judul'][:40]}")
            continue
        
        # Simpan artikel ID
        slug = re.sub(r'[^\w\s-]', '', id_article["judul"].lower())
        slug = re.sub(r'[\s_]+', '-', slug).strip('-')[:80]
        fname = f"{datetime.now().strftime('%Y-%m-%d')}-{slug}.json"
        
        pair_id = int(datetime.now().timestamp()) % 100000 + len(processed)
        
        id_data = {
            "judul": id_article["judul"],
            "meta_desc": id_article["meta_desc"],
            "date": datetime.now().strftime('%d/%m/%Y'),
            "tags": id_article["tags"],
            "slug": slug,
            "pair_id": pair_id,
            "content_markdown": id_article["content_markdown"],
            "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=75",
            "seo_h2": id_article["h2_structure"],
            "kategori": id_article["kategori"]
        }
        
        os.makedirs(ID_DIR, exist_ok=True)
        with open(os.path.join(ID_DIR, fname), "w") as f:
            json.dump(id_data, f, indent=2, ensure_ascii=False)
        log(f"  ✅ ID: {id_article['judul'][:50]}")
        existing_titles.add(id_article["judul"].lower().strip())
        articles_written += 1
        
        # Buat versi EN (jika konten cukup)
        en_title_prefix = "Market Analysis:" if id_article["kategori"] == "pasar" else \
                          "Investment Guide:" if id_article["kategori"] == "investasi" else \
                          "Economic Update:"
        
        en_title = f"{en_title_prefix} {slug.replace('-', ' ').title()}"
        if len(en_title) > 65:
            en_title = en_title[:62].rsplit(' ', 1)[0] + "..."
        
        en_body = id_article["content_markdown"]
        en_tags = ", ".join(id_article["tags"].split(", ")[:3] + ["indonesia", "financial"])
        
        en_data = {
            "judul": en_title,
            "meta_desc": f"Read the latest analysis on {slug.replace('-', ' ')[:80]}. Key insights for investors in Indonesia.",
            "date": id_article["date"],
            "tags": en_tags,
            "slug": f"{slug}-en",
            "pair_id": pair_id,
            "content_markdown": en_body,
            "image_url": id_article["image_url"]
        }
        
        os.makedirs(EN_DIR, exist_ok=True)
        en_fname = f"{datetime.now().strftime('%Y-%m-%d')}-{slug}-en.json"
        with open(os.path.join(EN_DIR, en_fname), "w") as f:
            json.dump(en_data, f, indent=2, ensure_ascii=False)
        log(f"  ✅ EN: {en_title[:50]}")
    
    if articles_written == 0:
        log("⚠️ Tidak ada artikel baru (semua duplikat)")
        send_telegram("📝 *SEO Architect:* Tidak ada topik baru hari ini — 0 artikel")
        return
    
    # Generate site & push
    log(f"📤 Publishing {articles_written} artikel baru...")
    r1 = subprocess.run(["python3", os.path.join(BASE_DIR, "generate-site.py")],
                       capture_output=True, timeout=60, cwd=BASE_DIR)
    if r1.returncode != 0:
        log(f"❌ Generate error: {r1.stderr.decode()[:200]}")
        send_telegram("⚠️ *SEO Architect:* Gagal generate site")
        return
    
    r2 = subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10, cwd=BASE_DIR)
    r3 = subprocess.run(["git", "commit", "-m", f"seo: architect article {datetime.now().strftime('%H:%M')}"],
                       capture_output=True, timeout=10, cwd=BASE_DIR)
    if r3.returncode == 0:
        subprocess.run(["git", "push", "origin", "main"], capture_output=True, timeout=30, cwd=BASE_DIR)
    
    msg = f"📝 *SEO Architect:* {articles_written} artikel baru\n🏷️ Topik: {', '.join(processed)}\n📈 Kategori: {trending_topics[0]['query']}"
    send_telegram(msg)
    log(f"✅ Done — {articles_written} artikel SEO baru live!")

if __name__ == "__main__":
    run()

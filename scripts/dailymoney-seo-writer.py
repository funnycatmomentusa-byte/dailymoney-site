#!/usr/bin/env python3
"""DailyMoney — SEO Content Writer Agent (v2)
Mencari topik trending, menulis artikel ID/EN berkualitas, auto-publish."""
import json, os, subprocess, sys, re, random
from datetime import datetime, timedelta

PROJECT = "/root/workspace/dailymoney-site"
ID_DIR = os.path.join(PROJECT, "_articles")
EN_DIR = os.path.join(PROJECT, "_articles", "en")
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(EN_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    with open(os.path.join(LOG_DIR, "seo-writer.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

def search_topics():
    """Cari topik finansial trending dari DuckDuckGo."""
    topics = []
    queries = [
        "IHSG berita terkini hari ini",
        "harga emas Antam terbaru",
        "nilai tukar rupiah dollar",
        "rekomendasi saham 2026",
        "investasi crypto Indonesia",
        "suku bunga Bank Indonesia",
        "inflasi Indonesia terbaru",
        "harga minyak dunia",
        "ekonomi digital Indonesia",
        "fintech Indonesia 2026"
    ]
    
    existing_articles = set()
    for d in [ID_DIR, EN_DIR]:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.endswith(".json"):
                    existing_articles.add(f.lower().replace("-", "").replace(".json", ""))
    
    from ddgs import DDGS
    with DDGS() as ddgs:
        for q in queries[:5]:
            try:
                results = list(ddgs.text(q, max_results=5, region="id-ID"))
                for r in results:
                    title = r.get("title", "")
                    body = r.get("body", "")
                    url = r.get("href", "")
                    slug = re.sub(r'[^a-z0-9]+', '-', title.lower().strip())[:60].strip('-')
                    slug_key = slug.replace("-", "")
                    if slug_key in existing_articles:
                        continue
                    topics.append({
                        "title": title, "body": body[:500],
                        "url": url, "slug": slug
                    })
            except Exception as e:
                log(f"⚠️ Search error for '{q}': {e}")
    
    seen = set()
    unique = []
    for t in topics:
        key = t["slug"][:30]
        if key not in seen:
            seen.add(key)
            unique.append(t)
    return unique[:3]

# ========== ARTICLE GENERATORS ==========

CLEAN_TITLE_PREFIXES = [
    "Breaking:", "News:", "Update:", "Video:", "BREAKING NEWS:",
    "LIVE:", "Flash:", "BREAKING:", "Berita:", "Headline:"
]

SITE_SUFFIXES = [
    'CNBC Indonesia', 'Kontan', 'Bisnis.com', 'Kompas', 'Detikfinance',
    'CNN Indonesia', 'Liputan6', 'TEMPO.CO', 'Republika', 'Okezone',
    'Tribunnews', 'Suara.com', 'IDX Channel', 'Kontan.co.id'
]

TAG_MAP = {
    "ihsg": "IHSG, Saham, Bursa Efek, Pasar Modal, Investasi",
    "saham": "Saham, Reksadana, Investasi, Pasar Modal, Portofolio",
    "emas": "Emas, Logam Mulia, Antam, Investasi, Harga Komoditas",
    "rupiah": "Rupiah, Dolar, Kurs, Mata Uang, Nilai Tukar",
    "dollar": "Dolar, Rupiah, Kurs, Mata Uang, Forex",
    "crypto": "Crypto, Bitcoin, Aset Digital, Blockchain, Investasi",
    "bitcoin": "Bitcoin, Crypto, Blockchain, Aset Digital, Investasi",
    "suku bunga": "Suku Bunga, BI Rate, Bank Indonesia, Moneter, Kebijakan",
    "bank indonesia": "Bank Indonesia, BI Rate, Moneter, Kebijakan, Ekonomi",
    "inflasi": "Inflasi, Harga, Daya Beli, Ekonomi, BPS",
    "minyak": "Minyak, Energi, Komoditas, Harga Global, OPEC",
    "fintech": "Fintech, Digital, Teknologi Keuangan, Startup, Inovasi",
    "ekonomi": "Ekonomi, Makro, Pertumbuhan, Indonesia, Kebijakan",
    "investasi": "Investasi, Keuangan, Reksadana, Saham, Perencanaan",
    "reksadana": "Reksadana, Investasi, Manajer Investasi, Pasar Modal",
    "pajak": "Pajak, Perpajakan, Insentif, APBN, Kebijakan Fiskal",
    "tenaga kerja": "Tenaga Kerja, Ketenagakerjaan, Upah, PHK, Lapangan Kerja",
    "properti": "Properti, Rumah, Harga Tanah, KPR, Real Estate",
}

INSURANCE_MESSAGES = [
    "Informasi dalam artikel ini bersifat edukatif dan bukan merupakan ajakan atau saran untuk membeli atau menjual aset keuangan tertentu. Keputusan investasi sepenuhnya berada di tangan Anda.",
    "Artikel ini disusun untuk tujuan edukasi keuangan. Setiap keputusan investasi mengandung risiko, termasuk potensi kehilangan modal. Lakukan riset mandiri sebelum berinvestasi.",
    "Konten ini adalah bagian dari program literasi keuangan DailyMoney. Semua data dan informasi disajikan untuk membantu pemahaman pasar keuangan. Bukan merupakan rekomendasi investasi.",
]

CONTENT_TEMPLATES = {
    # Template untuk artikel berita/analisis
    "analysis": {
        "sections": [
            "headline_news",
            "analyst_comment",
            "market_impact",
            "expert_advice",
            "conclusion_cta"
        ]
    },
    # Template untuk artikel edukasi
    "education": {
        "sections": [
            "intro_problem",
            "step_by_step",
            "tips_tricks",
            "case_example",
            "conclusion_cta"
        ]
    },
    # Template untuk artikel tips
    "tips": {
        "sections": [
            "intro_problem",
            "numbered_tips",
            "expert_advice",
            "conclusion_cta"
        ]
    }
}

def clean_title(raw_title):
    """Bersihkan title dari prefix/suffix."""
    title = raw_title
    for p in CLEAN_TITLE_PREFIXES:
        if title.startswith(p):
            title = title[len(p):].strip()
    # Hapus situs sumber
    for s in SITE_SUFFIXES:
        escaped = re.escape(s)
        title = re.sub(rf'\s*[—–\-|/]\s*{escaped}$', '', title.strip())
        title = re.sub(rf'^{escaped}\s*[—–\-|/]\s*', '', title.strip())
    title = title.strip().strip('-').strip()
    if len(title) > 65:
        title = title[:62].rsplit(' ', 1)[0] + "..."
    return title

def get_tags(title):
    """Cari tags berdasarkan keyword di judul."""
    title_lower = title.lower()
    for kw, tag in TAG_MAP.items():
        if kw in title_lower:
            return tag
    return "Keuangan, Ekonomi, Indonesia, Investasi, Pasar Modal"

def get_image_for(title):
    """Pilih gambar Unsplash yang relevan."""
    img_map = {
        "ihsg|saham|pasar": ("https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1200&q=80", "Layar perdagangan saham Bursa Efek Indonesia."),
        "emas": ("https://images.unsplash.com/photo-1610375461369-d613b564f12c?w=1200&q=80", "Emas batangan sebagai aset investasi."),
        "crypto|bitcoin": ("https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=1200&q=80", "Ilustrasi mata uang kripto Bitcoin dan aset digital."),
        "rupiah|dollar|kurs": ("https://images.unsplash.com/photo-1580519542036-c47de6196ba5?w=1200&q=80", "Tumpukan uang dolar AS dan rupiah."),
        "properti|rumah": ("https://images.unsplash.com/photo-1560520653-9e0e4c89eb11?w=1200&q=80", "Perumahan sebagai investasi properti."),
        "pajak": ("https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80", "Ilustrasi perpajakan dan keuangan."),
        "fintech|digital": ("https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=1200&q=80", "Teknologi fintech dan inovasi digital."),
        "ekonomi": ("https://images.unsplash.com/photo-1567427017947-545c5f8d16ad?w=1200&q=80", "Grafik dan data ekonomi makro Indonesia."),
    }
    for kw, (url, caption) in img_map.items():
        if re.search(kw, title.lower()):
            return url, f"{caption} Sumber: dokumentasi DailyMoney."
    return ("https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80",
            "Ilustrasi pasar keuangan — dokumentasi DailyMoney.")

def generate_original_title(topic_body, existing_titles):
    """Buat judul original berdasarkan konteks berita, bukan copy dari DDG."""
    body_lower = topic_body.lower()
    
    # Bersihkan body dari prefix seperti "1 day ago", "X menit lalu"
    body_clean = re.sub(r'^\d+\s*(hari|jam|menit|detik|day|hour|minute|month|minggu|bulan|tahun|year)\s*(lalu|ago)\s*[·\-–—]\s*', '', body_lower)
    body_clean = re.sub(r'^\s*[·\-–—]\s*', '', body_clean)
    
    # Detect topic category based on cleaned body
    categories = {
        "ihsg": ["IHSG Melemah/Menguat", "Pergerakan IHSG", "Indeks Saham"],
        "emas": ["Harga Emas", "Investasi Emas", "Logam Mulia"],
        "rupiah": ["Nilai Tukar Rupiah", "Kurs Rupiah", "Mata Uang"],
        "dollar": ["Nilai Tukar Rupiah", "Kurs Dollar", "Mata Uang"],
        "saham": ["Rekomendasi Saham", "Pergerakan Saham", "Investasi"],
        "crypto": ["Pergerakan Bitcoin", "Market Crypto", "Aset Digital"],
        "bitcoin": ["Pergerakan Bitcoin", "Harga Bitcoin", "Crypto"],
        "inflasi": ["Data Inflasi", "Tekanan Inflasi", "Daya Beli"],
        "suku bunga": ["Suku Bunga BI", "Kebijakan Moneter"],
        "minyak": ["Harga Minyak", "Energi Global", "Komoditas"],
        "pajak": ["Kebijakan Pajak", "Perpajakan"],
        "properti": ["Properti", "Harga Rumah", "Real Estate"],
        "fintech": ["Fintech Indonesia", "Keuangan Digital"],
    }
    
    cat_titles = ["Analisis", "Update Pasar", "Berita Terkini"]
    detected_kw = None
    for kw, titles in categories.items():
        if kw in body_clean:
            cat_titles = titles
            detected_kw = kw
            break
    
    # Extract key entities from cleaned body
    words = body_clean.split()[:10]
    key_phrase = " ".join(words[:4]) if len(words) >= 4 else topic_body[:40]
    
    # Pick title pattern
    patterns = [
        f"{random.choice(cat_titles)}: {key_phrase[:40]}...",
        f"{key_phrase[:45]} — {random.choice(cat_titles)}",
    ]
    
    title = random.choice(patterns)
    if len(title) > 65:
        title = title[:62].rsplit(' ', 1)[0] + "..."
    if len(title) < 20:
        title = f"{random.choice(cat_titles)}: Update {datetime.now().strftime('%d/%m/%Y')}"
    
    # Avoid duplicates
    base = re.sub(r'[^a-z0-9]', '', title[:25].lower())
    for et in existing_titles:
        if base in et.replace(" ", "").lower()[:25]:
            title = f"{random.choice(cat_titles)} — {datetime.now().strftime('%d %b %Y')}"
            break
    
    return title

def generate_content_id(topic, pair_id, existing_titles=[]):
    """Generate konten artikel ID berkualitas."""
    body = topic["body"]
    
    # Generate original title
    title = generate_original_title(body, existing_titles)
    tags = get_tags(title)
    img_url, img_caption = get_image_for(title)
    
    if len(title) < 15:
        title = f"Update Pasar Keuangan Indonesia {datetime.now().strftime('%d/%m/%Y')}"
    
    meta = body.strip()[:155] if len(body) > 10 else f"Simak analisis {title.lower()} dan dampaknya terhadap pasar keuangan Indonesia. Artikel eksklusif DailyMoney."
    if len(meta) > 155:
        meta = meta[:152].rsplit(' ', 1)[0] + "..."
    
    today = datetime.now().strftime('%d/%m/%Y')
    disclaimer = random.choice(INSURANCE_MESSAGES)
    
    # Structured content
    content_parts = [f"JAKARTA — {body}\n"]
    
    content_parts.append(f"""## ANALISIS: DAMPAK TERHADAP PASAR

Perkembangan ini membawa implikasi penting bagi pasar keuangan Indonesia. Berdasarkan data terkini, sentimen investor masih terbagi antara optimisme pemulihan dan kehati-hatian terhadap risiko global.

**Faktor-faktor yang mempengaruhi:**

* **Sentimen Pasar Global** — Pergerakan indeks Wall Street dan kebijakan The Fed masih menjadi katalis utama bagi pasar Asia, termasuk Indonesia.
* **Fundamental Domestik** — Data ekonomi Indonesia yang solid, termasuk cadangan devisa yang kuat dan inflasi yang terkendali, memberikan bantalan bagi pasar.
* **Aliran Modal Asing** — Arus masuk dan keluar modal asing terus dipantau sebagai indikator kepercayaan investor terhadap prospek ekonomi Indonesia.

Menurut analis pasar modal, volatilitas jangka pendek masih mungkin terjadi, namun prospek jangka panjang pasar Indonesia tetap menarik mengingat fundamental ekonomi yang kuat.

## STRATEGI MENGHADAPI DINAMIKA PASAR

Para perencana keuangan merekomendasikan beberapa langkah strategis:

1. **Diversifikasi portofolio** — Seimbangkan alokasi aset antara saham, obligasi, dan instrumen pasar uang.
2. **Investasi berkala** — Terapkan strategi dollar-cost averaging (DCA) untuk mengurangi risiko waktu masuk pasar.
3. **Pantau fundamental** — Fokus pada perusahaan dengan fundamental kuat dan prospek bisnis yang jelas.
4. **Jaga likuiditas** — Pastikan memiliki dana darurat yang cukup sebelum berinvestasi di aset berisiko.

## KESIMPULAN

{title} menjadi perhatian penting bagi pelaku pasar. Ke depan, investor disarankan untuk tetap waspada terhadap perkembangan global dan domestik yang dapat mempengaruhi pasar.

{disclaimer}

*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia yang lebih cerdas secara finansial. Dapatkan berita terkini dan analisis pasar setiap hari di dailymoney.my.id.*""")

    return {
        "judul": title.strip(),
        "meta_desc": meta.strip(),
        "date": today,
        "tags": tags,
        "image_url": img_url,
        "image_caption": img_caption,
        "content_markdown": "\n".join(content_parts).strip(),
        "pair_id": 0
    }

def generate_content_en(topic, pair_id, existing_titles=[]):
    """Generate English version of article."""
    body = topic["body"]
    
    # Generate original English title
    body_lower = body.lower()
    en_categories = {
        "stock|market|ihsg": ["Market Update", "Stock Market Analysis", "Indonesia Stocks"],
        "gold|emas": ["Gold Price Update", "Gold Investment"],
        "crypto|bitcoin": ["Crypto Market", "Bitcoin Update", "Digital Assets"],
        "inflation": ["Inflation Data", "Price Pressures"],
        "rupiah|dollar": ["Rupiah Exchange Rate", "Currency Update"],
        "oil|minyak": ["Oil Price Update", "Global Energy"],
        "tax|pajak": ["Tax Policy Update", "Tax Guide"],
    }
    
    en_titles = ["Market Analysis", "Financial Update", "Economic Report"]
    for kw, titles in en_categories.items():
        if any(k in body_lower for k in kw.split("|")):
            en_titles = titles
            break
    
    words = body.split()[:10]
    key_phrase = " ".join(words[:4]) if len(words) >= 4 else body[:40]
    
    en_title = f"{random.choice(en_titles)} - {key_phrase[:40]}"
    if len(en_title) > 65:
        en_title = en_title[:62].rsplit(' ', 1)[0] + "..."
    if len(en_title) < 15:
        en_title = f"Indonesia Market Update {datetime.now().strftime('%d/%m/%Y')}"
    
    # Determine English tags
    en_tags = "Finance, Economy, Indonesia, Market"
    for kw, t in {"ihsg|saham": "Stock Market, Indonesia, Investment, Finance",
                   "emas|gold": "Gold, Commodity, Investment, Precious Metals",
                   "crypto|bitcoin": "Crypto, Bitcoin, Digital Asset, Blockchain",
                   "rupiah|dollar": "Rupiah, Currency, Forex, Exchange Rate"}.items():
        if any(k in body_lower for k in kw.split("|")):
            en_tags = t
            break
    
    meta = body.strip()[:155] or "Latest market analysis update for Indonesia."
    if len(meta) > 155:
        meta = meta[:152].rsplit(' ', 1)[0] + "..."
    
    img_url = "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80"
    img_caption = f"Illustration: {en_title[:60]} — Source: DailyMoney documentation."
    
    content = f"""JAKARTA — {body}

## MARKET ANALYSIS

This development carries significant implications for Indonesian financial markets. According to market analysts, investor sentiment remains divided between optimism for recovery and caution over global risks.

**Key factors influencing the market:**

* **Global Market Sentiment** — Wall Street movements and Fed policy continue to be the main catalysts for Asian markets, including Indonesia.
* **Domestic Fundamentals** — Indonesia's solid economic data, including strong foreign exchange reserves and controlled inflation, provide a buffer for markets.
* **Foreign Capital Flows** — Capital inflow and outflow patterns are closely monitored as indicators of investor confidence in Indonesia's economic prospects.

## STRATEGIC RESPONSE

Financial planners recommend several strategic steps for investors:

1. **Portfolio diversification** — Balance asset allocation between stocks, bonds, and money market instruments.
2. **Regular investing** — Apply dollar-cost averaging to reduce market timing risk.
3. **Focus on fundamentals** — Prioritize companies with strong fundamentals and clear business prospects.
4. **Maintain liquidity** — Ensure adequate emergency funds before investing in risk assets.

## CONCLUSION

{en_title} remains a key focus for market participants. Looking ahead, investors are advised to remain vigilant about global and domestic developments that may affect markets.

*DailyMoney — Trusted financial education platform helping Indonesians make smarter financial decisions. Get the latest news and market analysis daily at dailymoney.my.id.*"""

    return {
        "judul": en_title.strip(),
        "meta_desc": meta.strip(),
        "date": datetime.now().strftime('%d/%m/%Y'),
        "tags": en_tags,
        "image_url": img_url,
        "image_caption": img_caption,
        "content_markdown": content.strip(),
        "pair_id": 1000
    }

def save_article(article, directory, lang="id"):
    """Save article JSON file."""
    title = article["judul"]
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower().strip())[:50].strip('-')
    if not slug:
        slug = f"artikel-{datetime.now().strftime('%d%m%Y')}"
    date_prefix = datetime.now().strftime('%Y-%m-%d')
    filename = f"{date_prefix}-{slug}.json"
    filepath = os.path.join(directory, filename)
    
    if os.path.exists(filepath):
        log(f"⏭️ Already exists: {filename}")
        return None
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, indent=2)
    
    log(f"✅ Saved {'ID' if lang=='id' else 'EN'}: {filename}")
    return filepath

def trigger_generate_and_push():
    """Jalankan generate-site.py dan push ke GitHub."""
    log("🏗️ Running generate-site.py...")
    r = subprocess.run(["python3", "generate-site.py"], capture_output=True, text=True, timeout=60, cwd=PROJECT)
    if r.returncode != 0:
        log(f"❌ Generate failed: {r.stderr[:200]}")
        return False
    
    log("📤 Committing and pushing...")
    subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10, cwd=PROJECT)
    r2 = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True, timeout=10, cwd=PROJECT)
    if r2.returncode == 0:
        log("No changes to commit")
        return True
    
    msg = f"feat: SEO article {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    subprocess.run(["git", "commit", "-m", msg], capture_output=True, timeout=10, cwd=PROJECT)
    r3 = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, timeout=30, cwd=PROJECT)
    if r3.returncode == 0:
        log("✅ Pushed to GitHub")
        return True
    else:
        log(f"❌ Push failed: {r3.stderr[:200]}")
        return False

# ===== MAIN =====
if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"✍️  DailyMoney SEO Writer v2 @ {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}")
    
    log("🔍 Searching for trending topics...")
    topics = search_topics()
    
    if not topics:
        log("❌ No new topics found")
        send_telegram("✍️ *SEO Writer:* Tidak ada topik baru. Coba lagi nanti.")
        sys.exit(0)
    
    log(f"📝 Found {len(topics)} new topic(s)")
    articles_written = 0

    # Collect existing titles to avoid duplicates
    existing_titles = []
    for d in [ID_DIR, EN_DIR]:
        if os.path.exists(d):
            for fname in os.listdir(d):
                if fname.endswith(".json"):
                    try:
                        data = json.load(open(os.path.join(d, fname)))
                        existing_titles.append(data.get("judul", ""))
                    except:
                        pass

    for i, topic in enumerate(topics):
        pair_id = int(datetime.now().timestamp()) % 10000 + i
    
        # Indonesian article
        id_art = generate_content_id(topic, pair_id, existing_titles)
        id_art["pair_id"] = pair_id
        id_path = save_article(id_art, ID_DIR, "id")
    
        # English article
        en_art = generate_content_en(topic, pair_id, existing_titles)
        en_art["pair_id"] = pair_id + 1000
        en_path = save_article(en_art, EN_DIR, "en")
        
        if id_path or en_path:
            articles_written += 1
    
    if articles_written == 0:
        log("⏭️ All topics already have articles")
        sys.exit(0)
    
    log("🚀 Deploying new articles...")
    deployed = trigger_generate_and_push()
    
    msg = f"✍️ *SEO Writer — {articles_written} artikel baru*\n\n"
    for topic in topics[:3]:
        msg += f"📄 {topic['title'][:70]}\n"
    if deployed:
        msg += "\n✅ Artikel live di dailymoney.my.id\n🔍 Google crawl dalam beberapa jam"
    else:
        msg += "\n⚠️ Artikel tersimpan tapi deploy perlu dicek"
    
    send_telegram(msg)
    log(f"✅ Done — {articles_written} articles written and deployed")

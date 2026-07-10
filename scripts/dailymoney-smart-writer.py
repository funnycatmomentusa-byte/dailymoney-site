#!/usr/bin/env python3
"""DailyMoney — Smart Writer v1
Ambil artikel dari portal scraper, rewrite agar unik, tambahkan tanggal, sumber, gambar.
Setiap artikel = kombinasi portal asli + rewrite unik + gambar unik.
"""

import json, os, sys, re, random, hashlib
from datetime import datetime, date

BASE_DIR = "/root/workspace/dailymoney-site"
ID_DIR = os.path.join(BASE_DIR, "_articles")
EN_DIR = os.path.join(ID_DIR, "en")
SCRAPED_PATH = os.path.join(BASE_DIR, "_scraped_articles.json")
REGISTRY_PATH = os.path.join(ID_DIR, ".topic-registry.json")
LOG_DIR = os.path.expanduser("~/.hermes/logs")

sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))

# ============================================================
# REWRITE TEMPLATES — Pola kalimat untuk rewrite
# ============================================================
REWRITE_OPENERS = [
    "Berdasarkan data terbaru dari {source}, pergerakan pasar menunjukkan dinamika yang menarik untuk dicermati.",
    "Laporan terkini dari {source} mengungkapkan tren baru dalam pasar keuangan Indonesia.",
    "Informasi terbaru dari {source} memberikan gambaran penting bagi pelaku pasar.",
    "Data yang dirilis {source} hari ini menunjukkan perubahan signifikan dalam pasar keuangan.",
    "Analisis terbaru dari {source} memperlihatkan pola pergerakan yang perlu diperhatikan investor.",
    "Rilis berita terbaru dari {source} mengonfirmasi tren yang sedang berlangsung di pasar.",
    "Update terkini dari {source} mengungkapkan data penting tentang kondisi pasar saat ini.",
    "Temuan terbaru dari {source} menyoroti perubahan dalam dinamika pasar keuangan.",
    "Laporan berita dari {source} hari ini memaparkan perkembangan terkini di pasar modal.",
    "Informasi dari {source} mengungkapkan analisis mendalam tentang pergerakan aset keuangan.",
]

REWRITE_CONNECTORS = [
    "Melihat data lebih lanjut,",
    "Dari sudut pandang analisis teknikal,",
    "Jika dilihat dari perspektif fundamental,",
    "Menurut data yang tersedia,",
    "Dalam konteks pasar yang lebih luas,",
    "Dari analisis yang dilakukan,",
    "Berdasarkan tren historis,",
    "Melihat kondisi terkini,",
    "Dari sudut pandang investor,",
    "Secara keseluruhan data menunjukkan,",
]

REWRITE_INSIGHTS = [
    "Sentimen investor saat ini masih terbagi antara optimisme terhadap prospek ekonomi domestik dan kehati-hatian terhadap risiko global yang masih membayangi.",
    "Volatilitas pasar dalam beberapa pekan terakhir mencerminkan proses penyesaan harga terhadap kondisi fundamental ekonomi yang terus berkembang.",
    "Para analis menyarankan investor untuk tetap fokus pada fundamental jangka panjang dan tidak terpengaruh oleh fluktuasi harga jangka pendek.",
    "Diversifikasi portofolio tetap menjadi strategi yang direkomendasikan oleh para perencana keuangan dalam menghadapi ketidakpastian pasar.",
    "Data makroekonomi Indonesia yang solid memberikan bantalan bagi pasar keuangan domestik meskipun tekanan dari faktor global masih terasa.",
    "Pergerakan indeks dan aset keuangan saat ini perlu dipahami dalam konteks tren yang lebih besar, bukan hanya pergerakan harian.",
    "Kebijakan moneter Bank Indonesia yang akomodatif mendukung likuiditas pasar dan memberikan ruang bagi pertumbuhan ekonomi.",
    "Aliran modal asing ke pasar keuangan Indonesia tetap menjadi indikator penting bagi prospek jangka menengah pasar modal.",
    "Ekspektasi pasar terhadap kebijakan ekonomi pemerintah ke depan menjadi salah satu katalis utama pergerakan harga.",
    "Faktor musiman dan siklus pasar juga berperan dalam membentuk pola pergerakan saat ini.",
]

REWRITE_STRATEGIES = [
    "Bagi investor, strategi yang bijak adalah melakukan riset mandiri dan tidak mengandalkan satu sumber informasi saja.",
    "Pendekatan dollar-cost averaging tetap relevan bagi investor yang ingin membangun portofolio secara bertahap.",
    "Evaluasi berkala terhadap portofolio investasi penting dilakukan untuk memastikan alokasi aset sesuai dengan profil risiko.",
    "Menjaga likuiditas yang cukup adalah kunci untuk bisa memanfaatkan peluang investasi saat pasar bergerak fluktuatif.",
    "Diversifikasi ke berbagai kelas aset membantu mengurangi risiko konsentrasi dalam portofolio investasi.",
]

CLOSINGS = [
    "Pantau terus perkembangan pasar keuangan di DailyMoney untuk mendapatkan analisis dan update terkini setiap hari.",
    "DailyMoney akan terus memberikan liputan komprehensif seputar pasar keuangan Indonesia. Ikuti update terbaru kami di dailymoney.my.id.",
    "Untuk informasi pasar terkini dan analisis mendalam, kunjungi DailyMoney di dailymoney.my.id.",
    "Semoga analisis ini bermanfaat untuk pengambilan keputusan investasi Anda. Pantau DailyMoney untuk update selanjutnya.",
    "Dengan informasi yang tepat, Anda bisa mengambil keputusan investasi yang lebih bijak. Simak analisis lengkapnya di DailyMoney.",
]

DISCLAIMERS = [
    "*Informasi dalam artikel ini bersifat edukatif dan bukan merupakan ajakan untuk membeli atau menjual aset keuangan.*",
    "*Artikel ini disusun untuk tujuan literasi keuangan. Keputusan investasi sepenuhnya berada di tangan Anda.*",
    "*Konten ini merupakan bagian dari program edukasi keuangan DailyMoney. Bukan merupakan rekomendasi investasi.*",
]


def slugify(text):
    """Convert text to URL-safe slug."""
    s = text.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'\s+', '-', s)
    return s[:80].rstrip('-')


def get_unique_image():
    """Get unique image from pool."""
    try:
        from dailymoney_image_pool import get_unique_image as _get
        return _get()
    except Exception:
        return (
            "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80",
            "Pergerakan pasar keuangan Indonesia. Sumber: dokumentasi DailyMoney."
        )


def rewrite_article(scraped, lang='id'):
    """Rewrite a scraped article to be unique."""
    is_en = lang == 'en'
    source_name = scraped["source_name"]
    paragraphs = scraped["paragraphs"]
    original_title = scraped["title"]
    article_date = scraped["date"]
    
    # === BUILD UNIQUE TITLE ===
    # Don't copy original title — create a new one
    clean_title = original_title
    # Remove portal suffixes
    for suffix in [" - CNBC Indonesia", " | CNBCIndonesia.com", " - Kontan", " - Bisnis.com",
                    " - CNN Indonesia", " - Detikfinance", " - Liputan6.com", " - TEMPO.CO",
                    " | Kompas.com", " - IDX Channel", " | Okezone.com", " - Republika",
                    " | Suara.com", " | Tribunnews.com", " | Katadata.co.id", " - VIVA.co.id"]:
        clean_title = clean_title.replace(suffix, "").strip()
    
    # Create new title patterns
    if is_en:
        title_patterns = [
            f"Market Analysis: {clean_title[:50]}",
            f"Financial Update: {clean_title[:50]}",
            f"Indonesia Market Report: {clean_title[:50]}",
        ]
    else:
        title_patterns = [
            f"Analisis Pasar: {clean_title[:50]}",
            f"Update Keuangan: {clean_title[:50]}",
            f"Laporan Pasar: {clean_title[:50]}",
            f"Berita Terkini: {clean_title[:50]}",
            f"Rangkuman Pasar: {clean_title[:50]}",
        ]
    
    judul = random.choice(title_patterns)
    if len(judul) > 70:
        judul = judul[:67].rsplit(' ', 1)[0] + "..."
    
    # === BUILD REWRITTEN CONTENT ===
    content_parts = []
    
    # Opening — use first 2-3 paragraphs from source, slightly reworded
    opener = random.choice(REWRITE_OPENERS).format(source=source_name)
    content_parts.append(opener)
    content_parts.append("")
    
    # Add source paragraphs (rewrite first few)
    source_paras = paragraphs[:5] if len(paragraphs) >= 5 else paragraphs
    for i, para in enumerate(source_paras):
        if i == 2 and len(source_paras) > 3:
            # Insert a connector + insight in the middle
            connector = random.choice(REWRITE_CONNECTORS)
            insight = random.choice(REWRITE_INSIGHTS)
            content_parts.append(f"\n{connector} {insight}\n")
        # Light rewrite: swap some words, add context
        rewritten = light_rewrite(para, source_name)
        content_parts.append(rewritten)
        content_parts.append("")
    
    # Add section heading
    if is_en:
        content_parts.append("\n## ANALYSIS & MARKET OUTLOOK\n")
    else:
        content_parts.append("\n## ANALISIS DAN PANDANGAN PASAR\n")
    
    # Add insights
    for _ in range(2):
        content_parts.append(random.choice(REWRITE_INSIGHTS))
        content_parts.append("")
    
    # Add more source paragraphs if available
    if len(paragraphs) > 5:
        for para in paragraphs[5:8]:
            content_parts.append(light_rewrite(para, source_name))
            content_parts.append("")
    
    # Add strategy section
    if is_en:
        content_parts.append("\n## INVESTMENT STRATEGY\n")
    else:
        content_parts.append("\n## STRATEGI INVESTASI\n")
    
    strategy = random.choice(REWRITE_STRATEGIES)
    content_parts.append(strategy)
    content_parts.append("")
    
    # Closing
    content_parts.append(random.choice(CLOSINGS))
    content_parts.append("")
    content_parts.append(random.choice(DISCLAIMERS))
    
    content = "\n".join(content_parts)
    
    # Ensure minimum length
    if len(content) < 3000:
        # Add more paragraphs
        extra_paras = random.sample(REWRITE_INSIGHTS, min(3, len(REWRITE_INSIGHTS)))
        for ep in extra_paras:
            content_parts.insert(-3, ep)
            content_parts.insert(-3, "")
        content = "\n".join(content_parts)
    
    # Get image
    img_url, img_caption = get_unique_image()
    
    # Meta description
    meta = content.strip()[:155].rsplit(' ', 1)[0] + "..."
    
    # Tags based on content
    tags = detect_tags(original_title + " " + content)
    
    article = {
        "judul": judul,
        "slug": slugify(judul),
        "meta_desc": meta,
        "date": article_date,
        "source": source_name,
        "source_url": scraped.get("source_url", ""),
        "tags": tags,
        "image_url": img_url,
        "image_caption": img_caption,
        "content_markdown": content.strip(),
    }
    
    return article


def light_rewrite(text, source_name):
    """Lightly rewrite a paragraph to make it unique while preserving meaning."""
    # Simple word-level rewrites
    rewrites = {
        "menurut": ["berdasarkan laporan", "sebagaimana dilaporkan", "menurut data"],
        "mengatakan": ["menyatakan", "menjelaskan", "ungkap"],
        "juga": ["turut", "selain itu", "pula"],
        "saat ini": ["kini", "belakangan ini", "di periode ini"],
        "terbaru": ["paling anyar", "terkini", "yang baru dirilis"],
        "menunjukkan": ["mengindikasikan", "memperlihatkan", "menyerlahkan"],
        "terjadi": ["berlangsung", "tercatat", "terekam"],
        "menguat": ["naik", "positive", "mengalami kenaikan"],
        "melemah": ["turun", "negative", "mengalami penurunan"],
    }
    
    result = text
    for word, alternatives in rewrites.items():
        if word in result.lower() and random.random() > 0.5:
            result = re.sub(re.escape(word), random.choice(alternatives), result, count=1, flags=re.IGNORECASE)
    
    return result


def detect_tags(text):
    """Detect tags based on content keywords."""
    text_lower = text.lower()
    tag_map = [
        (["ihsg", "saham", "idx", "bursa efek", "indeks"], "IHSG, Saham, Bursa Efek, Pasar Modal"),
        (["emas", "gold", "antam", "logam mulia"], "Emas, Logam Mulia, Gold, Investasi"),
        (["bitcoin", "crypto", "ethereum", "blockchain", "aset digital"], "Bitcoin, Crypto, Cryptocurrency, Blockchain"),
        (["rupiah", "dollar", "kurs", "nilai tukar", "forex"], "Forex, Rupiah, Dolar, Kurs, Nilai Tukar"),
        (["inflasi", "daya beli", "harga"], "Inflasi, Harga, Daya Beli, Ekonomi"),
        (["reksadana", "mutual fund", "nab"], "Reksadana, Mutual Fund, Investasi"),
        (["pajak", "spt", "pph", "ppn"], "Pajak, Perpajakan, SPT, PPh"),
        (["properti", "rumah", "kpr", "real estate"], "Properti, Real Estate, Rumah, KPR"),
        (["fintech", "digital", "paylater", "qris"], "Fintech, Keuangan Digital, QRIS"),
        (["ekonomi", "pdb", "pertumbuhan"], "Ekonomi, Indonesia, Pertumbuhan, PDB"),
    ]
    
    for keywords, tags in tag_map:
        if any(kw in text_lower for kw in keywords):
            return tags
    
    return "Keuangan, Ekonomi, Indonesia, Investasi"


def get_existing_slugs():
    """Get existing article slugs to avoid duplicates."""
    slugs = set()
    for d in [ID_DIR, EN_DIR]:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.endswith(".json"):
                    slugs.add(f.replace(".json", "").lower())
    return slugs


def save_article(article, directory, lang="id"):
    """Save article JSON."""
    slug = article.get("slug", slugify(article["judul"]))
    date_prefix = datetime.now().strftime('%Y-%m-%d')
    today_str = date.today().strftime('%Y-%m-%d')
    if date_prefix > today_str:
        date_prefix = today_str
    
    filename = f"{date_prefix}-{slug[:50]}.json"
    filepath = os.path.join(directory, filename)
    
    if os.path.exists(filepath):
        return None
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, indent=2)
    
    return filepath


# ============================================================
# ENGLISH TRANSLATOR
# ============================================================
def translate_to_english(article_id):
    """Translate an Indonesian article to English."""
    id_content = article_id["content_markdown"]
    id_title = article_id["judul"]
    
    # Simple translation patterns
    en_content = id_content
    translations = {
        "Berdasarkan data terbaru": "Based on the latest data",
        "pergerakan pasar": "market movements",
        "menunjukkan dinamika yang menarik": "showing interesting dynamics",
        "Analisis Pasar": "Market Analysis",
        "Update Keuangan": "Financial Update",
        "Laporan Pasar": "Market Report",
        "Berita Terkini": "Latest News",
        "Rangkuman Pasar": "Market Summary",
        "ANALISIS DAN PANDANGAN PASAR": "ANALYSIS & MARKET OUTLOOK",
        "STRATEGI INVESTASI": "INVESTMENT STRATEGY",
        "Pantau terus perkembangan pasar keuangan": "Stay updated on financial market developments",
        "di DailyMoney": "at DailyMoney",
        "untuk mendapatkan analisis": "for comprehensive analysis",
        "Informasi dalam artikel ini bersifat edukatif": "Information in this article is educational",
        "dan bukan merupakan ajakan": "and does not constitute a recommendation",
        "untuk membeli atau menjual aset keuangan": "to buy or sell financial assets",
    }
    
    for id_text, en_text in translations.items():
        en_content = en_content.replace(id_text, en_text)
    
    # Translate title
    en_title = id_title
    title_translations = {
        "Analisis Pasar": "Market Analysis",
        "Update Keuangan": "Financial Update",
        "Laporan Pasar": "Market Report",
        "Berita Terkini": "Latest News",
        "Rangkuman Pasar": "Market Summary",
    }
    for id_t, en_t in title_translations.items():
        en_title = en_title.replace(id_t, en_t)
    
    img_url, img_caption = get_unique_image()
    
    en_article = {
        "judul": en_title,
        "slug": slugify(en_title),
        "meta_desc": article_id.get("meta_desc", "")[:155],
        "date": article_id["date"],
        "source": article_id["source"],
        "source_url": article_id.get("source_url", ""),
        "tags": article_id["tags"].replace("IHSG", "JCI").replace("Saham", "Stocks").replace("Emas", "Gold").replace("Rupiah", "IDR"),
        "image_url": img_url,
        "image_caption": img_caption,
        "content_markdown": en_content,
    }
    
    return en_article


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"✍️  DailyMoney Smart Writer v1 @ {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}")
    
    # Step 1: Scrape from portals
    log_path = os.path.join(LOG_DIR, "smart-writer.log")
    def log(msg):
        ts = datetime.now().strftime('%H:%M:%S')
        print(f"[{ts}] {msg}")
        with open(log_path, "a") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    
    log("🔍 Step 1: Scraping portals...")
    from dailymoney_portal_scraper import scrape_portals
    scraped = scrape_portals(max_per_portal=2, max_total=12)
    
    if not scraped:
        log("❌ No articles scraped. Trying with lower threshold...")
        scraped = scrape_portals(max_per_portal=3, max_total=15)
    
    if not scraped:
        log("❌ Still no articles. Exiting.")
        sys.exit(1)
    
    # Step 2: Rewrite and save
    log(f"✍️  Step 2: Rewriting {len(scraped)} articles...")
    existing_slugs = get_existing_slugs()
    
    id_written = 0
    en_written = 0
    
    for s in scraped:
        # Check for title duplicate
        title_key = re.sub(r'[^a-z0-9]', '', s["title"].lower())[:30]
        is_dup = False
        for es in existing_slugs:
            if title_key and title_key[:20] in es:
                is_dup = True
                break
        
        if is_dup:
            log(f"  ⏭️ Skipping duplicate: {s['title'][:50]}")
            continue
        
        # Write Indonesian article
        id_article = rewrite_article(s, lang='id')
        id_path = save_article(id_article, ID_DIR, "id")
        if id_path:
            id_written += 1
            log(f"  ✅ ID: {id_article['judul'][:50]} ({len(id_article['content_markdown'])}c)")
            
            # Write English version
            en_article = translate_to_english(id_article)
            en_path = save_article(en_article, EN_DIR, "en")
            if en_path:
                en_written += 1
                log(f"  ✅ EN: {en_article['judul'][:50]}")
    
    # Step 3: Fix articles missing date/source
    log("🔧 Step 3: Fixing articles with missing date/source...")
    fixed = 0
    for d in [ID_DIR, EN_DIR]:
        if os.path.exists(d):
            for fname in os.listdir(d):
                if fname.endswith(".json"):
                    fpath = os.path.join(d, fname)
                    try:
                        with open(fpath) as f:
                            art = json.load(f)
                        changed = False
                        if not art.get("date"):
                            art["date"] = date.today().strftime('%d/%m/%Y')
                            changed = True
                        if not art.get("source"):
                            art["source"] = "DailyMoney Editorial"
                            changed = True
                        if changed:
                            with open(fpath, "w", encoding="utf-8") as f:
                                json.dump(art, f, ensure_ascii=False, indent=2)
                            fixed += 1
                    except:
                        pass
    log(f"  Fixed {fixed} articles with missing fields")
    
    # Summary
    log(f"\n{'='*60}")
    log(f"📊 SUMMARY")
    log(f"  Scraped: {len(scraped)} articles from portals")
    log(f"  Written ID: {id_written} new articles")
    log(f"  Written EN: {en_written} new articles")
    log(f"  Fixed: {fixed} articles with missing date/source")
    log(f"{'='*60}")
    
    # Generate site and push
    log("🏗️ Generating site...")
    import subprocess
    r = subprocess.run(["python3", "generate-site.py"], capture_output=True, text=True, timeout=120, cwd=BASE_DIR)
    if r.returncode == 0:
        log("✅ Site generated")
    else:
        log(f"⚠️ Generate issue: {r.stderr[:200]}")
    
    # Commit and push
    log("📤 Committing...")
    subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10, cwd=BASE_DIR)
    r2 = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True, timeout=10, cwd=BASE_DIR)
    if r2.returncode != 0:  # There are changes
        msg = f"feat: portal-sourced articles {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        subprocess.run(["git", "commit", "-m", msg], capture_output=True, timeout=10, cwd=BASE_DIR)
        r3 = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, timeout=30, cwd=BASE_DIR)
        if r3.returncode == 0:
            log("✅ Pushed to GitHub")
        else:
            log(f"⚠️ Push failed: {r3.stderr[:100]}")
    else:
        log("No changes to commit")
    
    log("🎉 Smart Writer complete!")

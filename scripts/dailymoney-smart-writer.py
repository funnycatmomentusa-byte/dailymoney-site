#!/usr/bin/env python3
"""DailyMoney — Smart Writer v2
Ambil artikel dari portal scraper, bersihkan, rewrite unik, output JSON artikel.
"""

import json, os, re, sys, hashlib, random
from datetime import datetime, date

BASE_DIR = "/root/workspace/dailymoney-site"
SCRAPED_FILE = os.path.join(BASE_DIR, "_scraped_articles.json")
ID_DIR = os.path.join(BASE_DIR, "_articles")
EN_DIR = os.path.join(ID_DIR, "en")
sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))

try:
    from dailymoney_image_pool import get_unique_image
    def get_article_images(_count=2):
        return [get_unique_image() for _ in range(_count)]
except ImportError:
    def get_article_images(_count=2):
        return [f"https://images.unsplash.com/photo-{random.randint(1600000000,1700000000)}?w=1080&q=80&auto=format" for _ in range(_count)]

# ============================================================
# CONTENT CLEANING
# ============================================================
def clean_content(text):
    """Remove noise from scraped content."""
    # Decode HTML entities first
    text = text.replace('&nbsp;', ' ').replace('&ndash;', '–').replace('&mdash;', '—')
    text = text.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&rsquo;', "'")
    text = text.replace('&lsquo;', "'").replace('&rdquo;', '"').replace('&ldquo;', '"')
    
    # Remove common noise patterns
    noise_patterns = [
        r'^(?:&nbsp;\s*)?[A-Z][a-z]+\s+Indonesia\s+\d{1,2}\s+\w+\s+\d{4}\s+\d{2}:\d{2}\s*',  # "CNBC Indonesia 10 July 2026 08:45"
        r'Foto:\s*[^\.]+\.\s*',
        r'\(Dok\.?\s*[^)]+\)\s*',
        r'Dok\.?\s+\w+\s*\.\s*',
        r'Jakarta,\s+\w+\s+\d{4}\s*[-–]\s*',
        r'^(?:&nbsp;\s*)*',
        r'Comment\s*SHARE\s*url\s*telah\s*tercopy[^,]*,?\s*',
        r'©\s*\d{4}\s+\w+\.\s*All rights reserved\.?\s*',
        r'ADVERTISEMENT\s*',
        r'Simak Juga\s*:.*?(?=\n\n|\Z)',
        r'Baca juga\s*:.*?(?=\n\n|\Z)',
        r'BACA JUGA\s*:.*?(?=\n\n|\Z)',
        r'Lihat juga\s*:.*?(?=\n\n|\Z)',
        r'Artikel Lainnya\s*:.*?(?=\n\n|\Z)',
        r'Read More\s*:?.*?(?=\n\n|\Z)',
        r'Share to\s*:?.*?(?=\n\n|\Z)',
        r'COPY LINK\s*',
        r'COPY\s*URL\s*',
        r'Ilustrasi\s*',
        r'Foto:\s*[^\.]+\.\s*',
        r'\(Dok\.?\s*[^)]*\)\s*',
        r'Dok\.?\s*\w*\s*\.?\s*',
        r'Sumber:\s*[^\.]+\.\s*',
        r'Liputan6\.com,?\s*(Jakarta|Indonesia)?\s*[-–]?\s*',
        r'KONTAN\.CO\.ID\s*[-–]\s*(Jakarta)?\.?\s*',
        r'CNBC\s+Indonesia\s+\d{1,2}\s+\w+\s+\d{4}\s+\d{2}:\d{2}\s*',
        r'Jakarta,?\s+CNBC\s+Indonesia\s*[-–—]?\s*',
        r'Jakarta,?\s+\d{1,2}\s+\w+\s+\d{4}\s*[-–—]\s*',
        r'Jakarta\s*[-–—,]+\s*',
    ]
    for pat in noise_patterns:
        text = re.sub(pat, '', text, flags=re.IGNORECASE)
    
    # Clean reporter/editor bylines
    text = re.sub(r'Reporter:\s*[^|]+\|\s*Editor:\s*[^\n]+', '', text)
    text = re.sub(r'Penulis:\s*[^\n]+', '', text)
    text = re.sub(r'Editor:\s*[^\n]+', '', text)
    
    # Clean multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'\s{2,}', ' ', text)
    
    # Clean leading bylines in paragraphs
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        # Skip lines that are just bylines/source citations
        if re.match(r'^(Reporter|Editor|Penulis|Kontributor)\s*:', line):
            continue
        if re.match(r'^\w+\s+Indonesia\s+\d{4}', line):
            continue
        cleaned_lines.append(line)
    text = '\n'.join(cleaned_lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text.strip()


def extract_key_sentences(text, max_sentences=5):
    """Extract the most important sentences from article."""
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # Filter short sentences and duplicates
    seen = set()
    important = []
    for s in sentences:
        s = s.strip()
        if len(s) < 20:
            continue
        key = s[:30].lower()
        if key in seen:
            continue
        seen.add(key)
        important.append(s)
        if len(important) >= max_sentences:
            break
    return important


# ============================================================
# SLUG GENERATION
# ============================================================
def generate_slug(title):
    """Generate URL-friendly slug from title."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = re.sub(r'-{2,}', '-', slug)
    slug = slug[:80].rstrip('-')
    return slug


# ============================================================
# TAG EXTRACTION
# ============================================================
def extract_tags(title, content):
    """Extract relevant tags from article."""
    tag_map = {
        "ihsg": ["IHSG", "Pasar Saham"],
        "saham": ["Saham", "Pasar Modal"],
        "emas": ["Emas", "Logam Mulia"],
        "gold": ["Emas", "Logam Mulia"],
        "antam": ["Antam", "Emas"],
        "rupiah": ["Rupiah", "Kurs"],
        "dollar": ["Dollar", "Kurs"],
        "kurs": ["Kurs", "Forex"],
        "crypto": ["Crypto", "Aset Digital"],
        "bitcoin": ["Bitcoin", "Crypto"],
        "ethereum": ["Ethereum", "Crypto"],
        "investasi": ["Investasi"],
        "reksadana": ["Reksadana", "Investasi"],
        "obligasi": ["Obligasi", "Investasi"],
        "inflasi": ["Inflasi", "Ekonomi"],
        "pdb": ["PDB", "Ekonomi"],
        "ekonomi": ["Ekonomi"],
        "pertumbuhan": ["Ekonomi", "Pertumbuhan"],
        "pajak": ["Pajak"],
        "properti": ["Properti", "Real Estate"],
        "rumah": ["Properti", "Rumah"],
        "fintech": ["Fintech", "Teknologi"],
        "bank indonesia": ["Bank Indonesia", "BI"],
        "suku bunga": ["Suku Bunga", "BI Rate"],
        "komoditas": ["Komoditas"],
        "minyak": ["Minyak", "Energi"],
        "nikel": ["Nikel", "Komoditas"],
        "cpo": ["CPO", "Komoditas"],
        "ekspor": ["Ekspor", "Perdagangan"],
        "impor": ["Impor", "Perdagangan"],
        "neraca perdagangan": ["Neraca Perdagangan"],
        "trading": ["Trading", "Investasi"],
        "rekomendasi": ["Rekomendasi Saham"],
        "bendungan": ["Infrastruktur", "Energi"],
        "listrik": ["Energi", "Infrastruktur"],
        "prabowo": ["Politik", "Ekonomi"],
        "presiden": ["Politik", "Ekonomi"],
    }
    
    text = (title + " " + content).lower()
    tags = set()
    for kw, tag_list in tag_map.items():
        if kw in text:
            for t in tag_list:
                tags.add(t)
    
    if not tags:
        tags = {"Ekonomi", "Keuangan"}
    
    return list(tags)[:6]


# ============================================================
# CATEGORY MAPPING
# ============================================================
def get_category(tags):
    """Map tags to article category."""
    tag_str = " ".join(tags).lower()
    if any(t in tag_str for t in ["saham", "ihsg", "pasar modal", "rekomendasi"]):
        return "saham"
    if any(t in tag_str for t in ["emas", "logam mulia", "antam"]):
        return "emas"
    if any(t in tag_str for t in ["kurs", "rupiah", "dollar", "forex"]):
        return "forex"
    if any(t in tag_str for t in ["crypto", "bitcoin", "ethereum", "aset digital"]):
        return "crypto"
    if any(t in tag_str for t in ["pajak"]):
        return "pajak"
    if any(t in tag_str for t in ["properti", "rumah", "real estate"]):
        return "properti"
    if any(t in tag_str for t in ["fintech", "teknologi"]):
        return "fintech"
    if any(t in tag_str for t in ["reksadana", "investasi", "obligasi"]):
        return "reksadana"
    return "ekonomi"


# ============================================================
# ARTICLE GENERATION
# ============================================================
def create_article(scraped, language="id"):
    """Create a clean article JSON from scraped content."""
    # Clean content
    cleaned = clean_content(scraped["content"])
    cleaned_paras = [clean_content(p) for p in scraped["paragraphs"]]
    cleaned_paras = [p for p in cleaned_paras if len(p) > 30]
    
    if not cleaned_paras:
        return None
    
    # Extract tags and category
    tags = extract_tags(scraped["title"], cleaned)
    category = get_category(tags)
    
    # Generate slug from title
    slug = generate_slug(scraped["title"])
    
    # Pick image based on tags
    try:
        images = get_article_images(2)
        if images and isinstance(images[0], tuple):
            image_url = images[0][0]  # (url, caption) tuple
        else:
            image_url = images[0] if images else ""
    except:
        image_url = ""
    
    # Get date
    article_date = scraped.get("date", date.today().isoformat())
    
    # Get source info
    source_name = scraped.get("source_name", "DailyMoney")
    source_url = scraped.get("source_url", "")
    
    # Content markdown — cleaned paragraphs
    content_md = "\n\n".join(cleaned_paras)
    
    # Ensure minimum content length
    if len(content_md) < 800:
        return None
    
    # Build article JSON
    article = {
        "judul": scraped["title"][:120],
        "slug": slug,
        "date": article_date,
        "category": category,
        "tags": ", ".join(tags),
        "source": source_name,
        "source_url": source_url,
        "image_url": image_url,
        "content_markdown": content_md,
    }
    
    return article


# ============================================================
# MAIN
# ============================================================
def run_writer():
    """Read scraped articles, create clean article JSONs."""
    # Read scraped articles
    if not os.path.exists(SCRAPED_FILE):
        print("❌ No scraped articles found. Run dailymoney-portal-scraper.py first.")
        return
    
    with open(SCRAPED_FILE) as f:
        scraped_list = json.load(f)
    
    print(f"📖 Processing {len(scraped_list)} scraped articles...")
    
    # Ensure directories exist
    os.makedirs(ID_DIR, exist_ok=True)
    os.makedirs(EN_DIR, exist_ok=True)
    
    today = date.today().isoformat()
    articles_created = 0
    articles_updated = 0
    
    for scraped in scraped_list:
        # Create article
        article = create_article(scraped, language="id")
        if not article:
            continue
        
        # Generate filename
        article_date = article["date"]
        cat_slug = article["category"]
        title_slug = article["slug"][:50]
        filename = f"{article_date}-{cat_slug}-{title_slug}.json"
        
        # Check if article already exists (by source_url hash)
        existing = False
        for existing_file in os.listdir(ID_DIR):
            if existing_file.endswith(".json"):
                try:
                    with open(os.path.join(ID_DIR, existing_file)) as ef:
                        existing_art = json.load(ef)
                    if existing_art.get("source_url") == article.get("source_url"):
                        existing = True
                        break
                except:
                    pass
        
        if existing:
            continue
        
        # Write article
        filepath = os.path.join(ID_DIR, filename)
        with open(filepath, "w") as f:
            json.dump(article, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ {article['judul'][:60]}")
        articles_created += 1
    
    print(f"\n📊 Created {articles_created} articles")


if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"✍️  DailyMoney Smart Writer v2 @ {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}")
    run_writer()

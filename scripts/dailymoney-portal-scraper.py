#!/usr/bin/env python3
"""DailyMoney — Portal Scraper v3
Scrape berita real dari portal keuangan Indonesia.
Approach: fetch portal pages → extract article links → fetch + extract content.
"""

import json, os, re, sys, time, hashlib, random
from datetime import datetime, date
from urllib.request import Request, urlopen

BASE_DIR = "/root/workspace/dailymoney-site"
ID_DIR = os.path.join(BASE_DIR, "_articles")
EN_DIR = os.path.join(ID_DIR, "en")
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)

# ============================================================
# PORTALS — name, feed URL, article link pattern, finance keywords
# ============================================================
PORTALS = [
    {
        "name": "CNBC Indonesia",
        "feed_url": "https://www.cnbcindonesia.com/market",
        "domain": "cnbcindonesia.com",
        "link_pattern": r'/market/\d{8}\d+-[^"]+',
    },
    {
        "name": "Kontan",
        "feed_url": "https://investasi.kontan.co.id/",
        "domain": "kontan.co.id",
        "link_pattern": r'/news/[a-z0-9-]+',
    },
    {
        "name": "Bisnis.com",
        "feed_url": "https://market.bisnis.com/",
        "domain": "bisnis.com",
        "link_pattern": r'/read/\d+/\d+/\d+/\d+/\d+',
    },
    {
        "name": "CNN Indonesia",
        "feed_url": "https://www.cnnindonesia.com/business",
        "domain": "cnnindonesia.com",
        "link_pattern": r'/business/\d{8}\d+-\d+-\d+',
    },
    {
        "name": "Detik Finance",
        "feed_url": "https://finance.detik.com/",
        "domain": "detik.com",
        "link_pattern": r'/berita-ekonomi-bisnis/d-\d+',
    },
    {
        "name": "Liputan6",
        "feed_url": "https://www.liputan6.com/bisnis",
        "domain": "liputan6.com",
        "link_pattern": r'/bisnis/read/\d+',
    },
    {
        "name": "Kompas",
        "feed_url": "https://money.kompas.com/",
        "domain": "kompas.com",
        "link_pattern": r'/read/\d{4}/\d{2}/\d{2}/\d+',
    },
    {
        "name": "Okezone",
        "feed_url": "https://www.okezone.com/bisnis",
        "domain": "okezone.com",
        "link_pattern": r'/read/\d{8}/\d+/\d+',
    },
    {
        "name": "Republika",
        "feed_url": "https://www.republika.co.id/ekonomi",
        "domain": "republika.co.id",
        "link_pattern": r'/ekonomi/\d{8}',
    },
    {
        "name": "Tribunnews",
        "feed_url": "https://www.tribunnews.com/bisnis",
        "domain": "tribunnews.com",
        "link_pattern": r'/bisnis/\d{8}',
    },
    {
        "name": "VIVA",
        "feed_url": "https://www.viva.co.id/bisnis",
        "domain": "viva.co.id",
        "link_pattern": r'/bisnis/\d+',
    },
]

FINANCIAL_KEYWORDS = [
    "saham", "ihsg", "idx", "bursa", "emas", "gold", "antam", "logam mulia",
    "rupiah", "dollar", "kurs", "forex", "nilai tukar",
    "bitcoin", "crypto", "ethereum", "blockchain", "aset digital",
    "investasi", "reksadana", "obligasi", "surat utang",
    "inflasi", "pdb", "ekonomi", "pertumbuhan",
    "pajak", "pph", "ppn", "spt",
    "properti", "kpr", "real estate", "harga rumah",
    "fintech", "pinjaman", "paylater",
    "bank indonesia", "bi rate", "suku bunga",
    "komoditas", "minyak", "nikel", "cpo",
    "neraca perdagangan", "ekspor", "impor",
    "pasar modal", "investor", "trading",
    "perdagangan", "transaksi", "volume",
    "harga", "naik", "turun", "menguat", "melemah",
]


def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(os.path.join(LOG_DIR, "portal-scraper.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")


def fetch_url(url, timeout=12):
    """Fetch URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
    }
    try:
        req = Request(url, headers=headers)
        resp = urlopen(req, timeout=timeout)
        return resp.read().decode("utf-8", errors="replace")
    except:
        return None


def extract_article_links(html, base_url, domain, link_pattern):
    """Extract article links from portal page."""
    links = set()
    # Find all href matching the pattern
    for m in re.finditer(r'href=["\']([^"\']+)["\']', html):
        href = m.group(1)
        # Make absolute
        if href.startswith("/"):
            # Determine scheme and domain from base_url
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            href = f"{parsed.scheme}://{parsed.netloc}{href}"
        elif not href.startswith("http"):
            continue
        
        # Check if matches pattern and domain
        if domain in href and re.search(link_pattern, href):
            # Clean URL (remove anchors, tracking params)
            href = href.split("#")[0].split("?")[0]
            links.add(href)
    
    # Also find links in <a> tags with text
    for m in re.finditer(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>\s*([^<]{10,})', html):
        href, text = m.group(1), m.group(2).strip()
        if href.startswith("/"):
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            href = f"{parsed.scheme}://{parsed.netloc}{href}"
        if domain in href and re.search(link_pattern, href):
            href = href.split("#")[0].split("?")[0]
            # Only keep if title looks financial
            if any(kw in text.lower() for kw in FINANCIAL_KEYWORDS):
                links.add(href)
    
    return list(links)


def extract_article_content(html, url=""):
    """Extract article content from HTML."""
    # Clean HTML
    html_clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html_clean = re.sub(r'<style[^>]*>.*?</style>', '', html_clean, flags=re.DOTALL|re.IGNORECASE)
    html_clean = re.sub(r'<nav[^>]*>.*?</nav>', '', html_clean, flags=re.DOTALL|re.IGNORECASE)
    html_clean = re.sub(r'<footer[^>]*>.*?</footer>', '', html_clean, flags=re.DOTALL|re.IGNORECASE)
    html_clean = re.sub(r'<header[^>]*>.*?</header>', '', html_clean, flags=re.DOTALL|re.IGNORECASE)
    html_clean = re.sub(r'<!--.*?-->', '', html_clean, flags=re.DOTALL)

    # Title
    title = ""
    h1 = re.search(r'<h1[^>]*>(.*?)</h1>', html_clean, re.DOTALL|re.IGNORECASE)
    if h1:
        title = re.sub(r'<[^>]+>', '', h1.group(1)).strip()
    if not title or len(title) < 10:
        t = re.search(r'<title[^>]*>(.*?)</title>', html_clean, re.DOTALL|re.IGNORECASE)
        if t:
            title = re.sub(r'<[^>]+>', '', t.group(1)).strip()

    # Date
    date_text = ""
    for pat in [
        r'"datePublished"\s*:\s*"([^"]+)"',
        r'<time[^>]*datetime="([^"]+)"',
        r'property="article:published_time"\s+content="([^"]+)"',
        r'(\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember|January|February|March|April|May|June|July|August|September|October|November|December)\w*\s+\d{4})',
        r'(\d{1,2}/\d{1,2}/\d{4})',
    ]:
        m = re.search(pat, html_clean, re.IGNORECASE)
        if m:
            date_text = m.group(1).strip()[:50]
            break

    # Paragraphs
    paragraphs = []
    article_match = re.search(r'<article[^>]*>(.*?)</article>', html_clean, re.DOTALL|re.IGNORECASE)
    content_html = article_match.group(1) if article_match else html_clean
    
    for m in re.finditer(r'<p[^>]*>(.*?)</p>', content_html, re.DOTALL|re.IGNORECASE):
        text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        text = re.sub(r'\s+', ' ', text)
        if len(text) > 40 and not any(skip in text for skip in ['ADVERTISEMENT', 'Baca juga', 'BACA JUGA', 'Lihat juga', 'Artikel Lainnya', 'Baca Juga']):
            paragraphs.append(text)

    return {"title": title[:200], "date_text": date_text, "paragraphs": paragraphs, "content": "\n\n".join(paragraphs)}


def parse_date(text):
    """Parse date to YYYY-MM-DD."""
    if not text:
        return date.today().isoformat()
    m = re.match(r'(\d{4}-\d{2}-\d{2})', text)
    if m: return m.group(1)
    
    id_months = {
        "januari":"01","februari":"02","maret":"03","april":"04","mei":"05","juni":"06",
        "juli":"07","agustus":"08","september":"09","oktober":"10","november":"11","desember":"12",
        "january":"01","february":"02","march":"03","may":"05","june":"06","july":"07",
        "august":"08","september":"09","october":"10","november":"11","december":"12",
    }
    m = re.search(r'(\d{1,2})\s+(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember|January|February|March|April|May|June|July|August|September|October|November|December)\w*\s+(\d{4})', text, re.IGNORECASE)
    if m:
        day, month_name, year = m.groups()
        return f"{year}-{id_months.get(month_name.lower(),'01')}-{day.zfill(2)}"
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', text)
    if m:
        return f"{m.group(3)}-{m.group(2).zfill(2)}-{m.group(1).zfill(2)}"
    return date.today().isoformat()


def get_existing_hashes():
    hashes = set()
    for d in [ID_DIR, EN_DIR]:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.endswith(".json"):
                    try:
                        with open(os.path.join(d, f)) as fh:
                            art = json.load(fh)
                        if art.get("source_url"):
                            hashes.add(hashlib.md5(art["source_url"].encode()).hexdigest()[:12])
                    except: pass
    return hashes


def scrape_portals(max_per_portal=2, max_total=10):
    """Scrape articles from all portals."""
    existing = get_existing_hashes()
    articles = []
    seen = set()
    
    for portal in PORTALS:
        if len(articles) >= max_total:
            break
            
        name = portal["name"]
        feed_url = portal["feed_url"]
        domain = portal["domain"]
        pattern = portal["link_pattern"]
        
        log(f"🔍 {name}...")
        html = fetch_url(feed_url)
        if not html:
            log(f"  ⚠️ Cannot fetch {name}")
            continue
        
        links = extract_article_links(html, feed_url, domain, pattern)
        log(f"  Found {len(links)} article links")
        
        count = 0
        for link in links:
            if count >= max_per_portal or len(articles) >= max_total:
                break
            
            url_hash = hashlib.md5(link.encode()).hexdigest()[:12]
            if url_hash in seen or url_hash in existing:
                continue
            
            # Fetch article
            art_html = fetch_url(link)
            if not art_html or len(art_html) < 2000:
                continue
            
            extracted = extract_article_content(art_html, link)
            
            if len(extracted["content"]) < 400 or len(extracted["paragraphs"]) < 2:
                continue
            if not extracted["title"] or len(extracted["title"]) < 10:
                continue
            
            # Financial filter
            if not any(kw in extracted["content"].lower() for kw in FINANCIAL_KEYWORDS):
                continue
            
            art_date = parse_date(extracted["date_text"])
            try:
                if (datetime.now() - datetime.strptime(art_date, "%Y-%m-%d")).days > 10:
                    continue
            except:
                art_date = date.today().isoformat()
            
            articles.append({
                "title": extracted["title"],
                "url": link,
                "date": art_date,
                "source_name": name,
                "source_url": link,
                "paragraphs": extracted["paragraphs"],
                "content": extracted["content"],
            })
            
            seen.add(url_hash)
            count += 1
            time.sleep(0.3)
    
    log(f"✅ Scraped {len(articles)} articles from {len(set(a['source_name'] for a in articles))} portals")
    return articles


if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"📰 DailyMoney Portal Scraper v3 @ {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}")
    
    articles = scrape_portals(max_per_portal=2, max_total=10)
    
    output_path = os.path.join(BASE_DIR, "_scraped_articles.json")
    with open(output_path, "w") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Saved {len(articles)} articles to {output_path}")
    for a in articles:
        print(f"  • [{a['source_name']}] {a['title'][:55]} ({a['date']})")

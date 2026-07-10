#!/usr/bin/env python3
"""DailyMoney — Portal Scraper v1
Scrape berita real dari 10+ portal berita keuangan Indonesia.
Setiap artikel diambil dari portal asli, lalu di-rewrite agar unik.
"""

import json, os, re, sys, time, hashlib, random
from datetime import datetime, date
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser

BASE_DIR = "/root/workspace/dailymoney-site"
ID_DIR = os.path.join(BASE_DIR, "_articles")
EN_DIR = os.path.join(ID_DIR, "en")
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(EN_DIR, exist_ok=True)

# ============================================================
# PORTAL SOURCES — 15 portal keuangan Indonesia
# ============================================================
# 15 portal — search by portal name, filter by URL domain
PORTALS = [
    {"name": "CNBC Indonesia",   "domain": "cnbcindonesia.com",    "query": "CNBC Indonesia saham IHSG emas hari ini"},
    {"name": "Kontan",           "domain": "kontan.co.id",         "query": "Kontan saham IHSG emas terbaru"},
    {"name": "Bisnis.com",       "domain": "bisnis.com",           "query": "Bisnis.com saham IHSG ekonomi"},
    {"name": "CNN Indonesia",    "domain": "cnnindonesia.com",     "query": "CNN Indonesia saham IHSG emas"},
    {"name": "Detik Finance",    "domain": "detik.com",            "query": "Detik finance saham IHSG emas rupiah"},
    {"name": "Liputan6",         "domain": "liputan6.com",         "query": "Liputan6 bisnis saham emas"},
    {"name": "TEMPO.CO",         "domain": "tempo.co",             "query": "Tempo bisnis saham ekonomi"},
    {"name": "Kompas",           "domain": "kompas.com",           "query": "Kompas money saham emas rupiah"},
    {"name": "IDX Channel",      "domain": "idx.co.id",            "query": "IDX Channel berita pasar modal"},
    {"name": "Okezone",          "domain": "okezone.com",          "query": "Okezone bisnis saham emas"},
    {"name": "Republika",        "domain": "republika.co.id",      "query": "Republika ekonomi indonesia"},
    {"name": "Suara.com",        "domain": "suara.com",            "query": "Suara money saham emas"},
    {"name": "Tribunnews",       "domain": "tribunnews.com",       "query": "Tribunnews bisnis saham emas"},
    {"name": "Katadata",         "domain": "katadata.co.id",       "query": "Katadata ekonomi saham investasi"},
    {"name": "VIVA",             "domain": "viva.co.id",           "query": "VIVA bisnis saham emas"},
]

# ============================================================
# HTML PARSER — Extract article content from HTML
# ============================================================
class ArticleExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_article = False
        self.in_script = False
        self.in_style = False
        self.in_nav = False
        self.in_footer = False
        self.skip_depth = 0
        self.paragraphs = []
        self.current_text = []
        self.title = ""
        self.in_title = False
        self.in_h1 = False
        self.in_date = False
        self.date_text = ""
        self.depth = 0
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")
        
        # Track skip zones
        if tag in ("script", "style", "noscript"):
            self.skip_depth += 1
        if tag in ("nav", "footer", "aside", "header"):
            self.skip_depth += 1
            
        # Title
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.in_h1 = True
            
        # Article content - look for article tags, div with article-like classes
        article_classes = ["article", "content", "entry-content", "post-content",
                          "detail-content", "text-detail", "article-content",
                          "detail_text", "body-text", "konten"]
        if tag == "article" or (tag == "div" and any(ac in cls.lower() for ac in article_classes)):
            self.in_article = True
            self.skip_depth = max(0, self.skip_depth - 1)
            
        # Date elements
        date_classes = ["date", "time", "published", "ago", "timestamp"]
        if tag in ("time", "span", "div") and any(dc in cls.lower() for dc in date_classes):
            self.in_date = True
            
        # Paragraphs
        if tag == "p" and self.in_article and self.skip_depth == 0:
            self.current_text = []
            
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self.skip_depth = max(0, self.skip_depth - 1)
        if tag in ("nav", "footer", "aside", "header"):
            self.skip_depth = max(0, self.skip_depth - 1)
        if tag == "title":
            self.in_title = False
        if tag == "h1":
            self.in_h1 = False
        if tag == "time":
            self.in_date = False
        if tag == "p" and self.current_text:
            text = " ".join(self.current_text).strip()
            if len(text) > 30:
                self.paragraphs.append(text)
            self.current_text = []
        if tag in ("div", "article") and self.in_article:
            # Check if we're still inside an article context
            pass
            
    def handle_data(self, data):
        text = data.strip()
        if not text:
            return
        if self.in_title:
            self.title += text
        if self.in_h1 and not self.title:
            self.title = text
        if self.in_date and not self.date_text:
            self.date_text = text
        if self.current_text is not None:
            self.current_text.append(text)

def extract_article_from_html(html, url=""):
    """Extract article text from raw HTML."""
    # Simple regex-based extraction as fallback
    # Remove scripts and styles
    html_clean = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html_clean = re.sub(r'<style[^>]*>.*?</style>', '', html_clean, flags=re.DOTALL|re.IGNORECASE)
    html_clean = re.sub(r'<nav[^>]*>.*?</nav>', '', html_clean, flags=re.DOTALL|re.IGNORECASE)
    html_clean = re.sub(r'<footer[^>]*>.*?</footer>', '', html_clean, flags=re.DOTALL|re.IGNORECASE)
    html_clean = re.sub(r'<header[^>]*>.*?</header>', '', html_clean, flags=re.DOTALL|re.IGNORECASE)
    html_clean = re.sub(r'<aside[^>]*>.*?</aside>', '', html_clean, flags=re.DOTALL|re.IGNORECASE)
    
    # Extract title
    title = ""
    title_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_clean, re.DOTALL|re.IGNORECASE)
    if title_match:
        title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
    if not title:
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_clean, re.DOTALL|re.IGNORECASE)
        if title_match:
            title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip()
    
    # Extract date
    date_text = ""
    date_patterns = [
        r'<time[^>]*datetime="([^"]+)"',
        r'<time[^>]*>(.*?)</time>',
        r'"datePublished"\s*:\s*"([^"]+)"',
        r'"date_published"\s*:\s*"([^"]+)"',
        r'property="article:published_time"\s+content="([^"]+)"',
        r'class="[^"]*date[^"]*"[^>]*>(.*?)<',
        r'class="[^"]*time[^"]*"[^>]*>(.*?)<',
        r'(\d{1,2}\s+(?:Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})',
        r'(\d{1,2}/\d{1,2}/\d{4})',
        r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})',
    ]
    for pat in date_patterns:
        m = re.search(pat, html_clean, re.IGNORECASE)
        if m:
            date_text = m.group(1).strip()
            break
    
    # Extract paragraphs
    paragraphs = []
    # Try article tag first
    article_match = re.search(r'<article[^>]*>(.*?)</article>', html_clean, re.DOTALL|re.IGNORECASE)
    content_html = article_match.group(1) if article_match else html_clean
    
    # Find all <p> tags
    for m in re.finditer(r'<p[^>]*>(.*?)</p>', content_html, re.DOTALL|re.IGNORECASE):
        text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        text = re.sub(r'\s+', ' ', text)
        if len(text) > 40 and not text.startswith(('ADVERTISEMENT', 'Baca juga:', 'BACA JUGA', 'Lihat juga')):
            paragraphs.append(text)
    
    return {
        "title": title[:200],
        "date_text": date_text[:50],
        "paragraphs": paragraphs,
        "url": url,
        "content": "\n\n".join(paragraphs)
    }


def fetch_url(url, timeout=15):
    """Fetch URL content."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
    }
    try:
        req = Request(url, headers=headers)
        resp = urlopen(req, timeout=timeout)
        return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        return None


def search_duckduckgo(query, max_results=5):
    """Search DuckDuckGo and return results."""
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results, region="id-id"))
            return [{"title": r.get("title",""), "url": r.get("href",""), "body": r.get("body","")} for r in results]
    except Exception as e:
        return []


def parse_date(date_text):
    """Parse various date formats to YYYY-MM-DD."""
    if not date_text:
        return date.today().isoformat()
    
    # Try ISO format
    m = re.match(r'(\d{4}-\d{2}-\d{2})', date_text)
    if m:
        return m.group(1)
    
    # Indonesian months
    id_months = {
        "januari": "01", "februari": "02", "maret": "03", "april": "04",
        "mei": "05", "juni": "06", "juli": "07", "agustus": "08",
        "september": "09", "oktober": "10", "november": "11", "desember": "12",
        "january": "01", "february": "02", "march": "03", "may": "05",
        "june": "06", "july": "07", "august": "08", "september": "09",
        "october": "10", "november": "11", "december": "12",
    }
    
    # "10 Juli 2026" or "10/07/2026"
    m = re.search(r'(\d{1,2})\s+(Januari|Februari|Maret|April|Mei|Juni|Juli|Agustus|September|Oktober|November|Desember|January|February|March|April|May|June|July|August|September|October|November|December)\w*\s+(\d{4})', date_text, re.IGNORECASE)
    if m:
        day, month_name, year = m.groups()
        month = id_months.get(month_name.lower(), "01")
        return f"{year}-{month}-{day.zfill(2)}"
    
    # "07/10/2026"
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', date_text)
    if m:
        day, month, year = m.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    
    # "X jam/hari/menit lalu" → compute relative date
    m = re.search(r'(\d+)\s*(jam|hour|hari|day|menit|minute|bulan|month|tahun|year)\w*\s*(yang lalu|lalu|ago)', date_text, re.IGNORECASE)
    if m:
        num = int(m.group(1))
        unit = m.group(2).lower()
        now = datetime.now()
        if unit in ("jam", "hour"):
            dt = now - __import__('datetime').timedelta(hours=num)
        elif unit in ("hari", "day"):
            dt = now - __import__('datetime').timedelta(days=num)
        elif unit in ("menit", "minute"):
            dt = now - __import__('datetime').timedelta(minutes=num)
        elif unit in ("bulan", "month"):
            dt = now - __import__('datetime').timedelta(days=num*30)
        elif unit in ("tahun", "year"):
            dt = now - __import__('datetime').timedelta(days=num*365)
        else:
            dt = now
        return dt.strftime('%Y-%m-%d')
    
    return date.today().isoformat()


def is_duplicate_url(url, existing_urls):
    """Check if URL already scraped."""
    url_hash = hashlib.md5(url.encode()).hexdigest()[:12]
    return url_hash in existing_urls


def log(msg):
    """Log to stdout and file."""
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(os.path.join(LOG_DIR, "portal-scraper.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")


# ============================================================
# MAIN SCRAPER
# ============================================================
def scrape_portals(max_per_portal=2, max_total=10):
    """Scrape articles from all portals, return unique articles."""
    
    # Load existing URLs to avoid duplicates
    existing_urls = set()
    existing_slugs = set()
    for d in [ID_DIR, EN_DIR]:
        if os.path.exists(d):
            for fname in os.listdir(d):
                if fname.endswith(".json"):
                    try:
                        with open(os.path.join(d, fname)) as f:
                            art = json.load(f)
                        if art.get("source_url"):
                            existing_urls.add(hashlib.md5(art["source_url"].encode()).hexdigest()[:12])
                        existing_slugs.add(fname.replace(".json", "")[:40].lower())
                    except:
                        pass
    
    articles = []
    seen_titles = set()
    
    for portal in PORTALS:
        if len(articles) >= max_total:
            break
            
        portal_name = portal["name"]
        query = portal["query"]
        log(f"🔍 Scraping {portal_name}...")
        portal_count = 0
        
        results = search_duckduckgo(query, max_results=3)
        
        for r in results:
            if portal_count >= max_per_portal:
                break
            if len(articles) >= max_total:
                break
                
            url = r["url"]
            title_from_search = r["title"]
            
            # Skip if already scraped
            if is_duplicate_url(url, existing_urls):
                continue
                
            # Skip if title too similar to existing
            title_key = re.sub(r'[^a-z0-9]', '', title_from_search.lower())[:30]
            if title_key in seen_titles:
                continue
                
            # Skip non-article URLs
            if any(skip in url for skip in ["/video/", "/gallery/", "#", ".jpg", ".png", ".pdf"]):
                continue
            
            # Fetch article
            log(f"  📰 {title_from_search[:60]}...")
            html = fetch_url(url)
            if not html:
                continue
                
            extracted = extract_article_from_html(html, url)
            
            # Validate quality
            if len(extracted["content"]) < 500:
                continue
            if len(extracted["paragraphs"]) < 3:
                continue
            if not extracted["title"]:
                extracted["title"] = title_from_search
                
            # Parse date
            article_date = parse_date(extracted["date_text"])
            
            # Skip if too old (>7 days)
            try:
                art_dt = datetime.strptime(article_date, "%Y-%m-%d")
                if (datetime.now() - art_dt).days > 7:
                    continue
            except:
                article_date = date.today().isoformat()
            
            articles.append({
                "title": extracted["title"],
                "url": url,
                "date": article_date,
                "source_name": portal_name,
                "source_url": url,
                "paragraphs": extracted["paragraphs"],
                "content": extracted["content"],
            })
            
            seen_titles.add(title_key)
            existing_urls.add(hashlib.md5(url.encode()).hexdigest()[:12])
            portal_count += 1
            
            # Be polite
            time.sleep(0.5)
    
    log(f"✅ Scraped {len(articles)} articles from {len(set(a['source_name'] for a in articles))} portals")
    return articles


if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"📰 DailyMoney Portal Scraper v1 @ {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}")
    
    articles = scrape_portals(max_per_portal=2, max_total=15)
    
    # Save results to temp file for the writer to use
    output_path = os.path.join(BASE_DIR, "_scraped_articles.json")
    with open(output_path, "w") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Saved {len(articles)} articles to {output_path}")
    for a in articles[:5]:
        print(f"  • [{a['source_name']}] {a['title'][:60]} ({a['date']})")

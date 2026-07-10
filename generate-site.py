#!/usr/bin/env python3
"""
DailyMoney Site Generator v3.0
- Multi-language (ID/EN)
- Dynamic sitemap.xml
- Table wrapper for mobile
- Thesis-style paragraph spacing
- Image support
"""
import json
import os
import re
import html
import glob
from datetime import datetime
import sys
import urllib.request
import urllib.parse


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ID_ARTICLES_DIR = os.path.join(BASE_DIR, '_articles')
EN_ARTICLES_DIR = os.path.join(BASE_DIR, '_articles', 'en')
OUTPUT_DIR = os.path.join(BASE_DIR, 'articles')
EN_OUTPUT_DIR = os.path.join(BASE_DIR, 'en', 'articles')
EN_ASSETS_JS_DIR = os.path.join(BASE_DIR, 'en', 'assets', 'js')

SITE_URL = "https://dailymoney.my.id"

# ─── Visitor counter (fetched from visitor-badge.laobi.icu) ───
def fetch_visitor_counts():
    """Fetch current visitor totals from visitor-badge.laobi.icu."""
    today = datetime.now().strftime("%Y-%m-%d")
    result = {"daily": 0, "total": 0}
    pages = {
        "total": "https://visitor-badge.laobi.icu/badge?page_id=dailymoneyid",
        "daily": f"https://visitor-badge.laobi.icu/badge?page_id=dmid-{today}",
    }
    for key, url in pages.items():
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'DailyMoney/1.0'})
            svg = urllib.request.urlopen(req, timeout=10).read().decode()
            nums = re.findall(r'<text[^>]*>(\d+)</text>', svg)
            if nums:
                result[key] = int(nums[0])
        except Exception:
            pass
    return result["daily"], result["total"]

LANG_CONFIG = {
    "id": {
        "html_lang": "id",
        "schema_lang": "id-ID",
        "nav_beranda": "Beranda",
        "nav_artikel": "Artikel",
        "nav_tentang": "Tentang",
        "nav_en": "English",
        "tentang_about": "DailyMoney menyajikan analisis mendalam seputar pasar modal, investasi, inflasi, dan ekonomi makro. Konten kami dirancang untuk membantu pembaca mengambil keputusan finansial yang lebih cerdas dan terinformasi.",
        "tentang_standards": "Setiap artikel ditulis dengan standar jurnalistik tinggi, mengutip data terbaru dari sumber terpercaya seperti BPS, Bank Indonesia, OJK, dan lembaga internasional.",
        "tentang_vision_title": "Visi Kami",
        "tentang_vision": "Menjadi sumber berita keuangan terpercaya nomor satu di Indonesia, dapat diakses oleh semua orang, gratis selamanya.",
        "tentang_contact_title": "Hubungi Kami",
        "tentang_contact": "X: @DailyMoneyID • Telegram: @EsterToobit",
        "breadcrumb_home": "Beranda",
        "breadcrumb_articles": "Artikel",
        "share_label": "Bagikan",
        "footer_desc": "Platform edukasi keuangan yang membantu masyarakat Indonesia mengambil keputusan finansial yang lebih cerdas dan terinformasi.",
        "footer_nav": "Navigasi",
        "footer_topics": "Topik",
        "footer_partner": "Kerja Sama",
        "footer_disclosure": "Disclosure",
        "footer_copyright": "© 2026 DailyMoney. Hak cipta dilindungi undang-undang.",
        "footer_made": "Dibuat dengan ❤️ untuk Indonesia",
        "breaking_text": "BERITA TERKINI",
        "hero_title": "Berita Keuangan Terpercaya",
        "hero_desc": "Analisis mendalam dan berita terkini seputar pasar modal, investasi, dan ekonomi makro untuk Indonesia yang lebih cerdas secara finansial.",
        "hero_stat1_num": "4+",
        "hero_stat1_label": "Artikel Hari Ini",
        "hero_stat2_num": "ID/EN",
        "hero_stat2_label": "Dua Bahasa",
        "hero_stat3_num": "Gratis",
        "hero_stat3_label": "Selamanya",
        "hero_stat4_num": "2026",
        "hero_stat4_label": "Terkini",
        "section_articles": "Artikel Terbaru",
        "section_tagline": "Analisis dan berita keuangan terkini untuk membantu keputusan investasi Anda",
        "empty_title": "Belum Ada Artikel",
        "empty_desc": "Artikel baru akan segera hadir. Pantau terus!",
        "cta_bookmark_text": "Simpan artikel ini untuk dibaca nanti.",
        "cta_share_text": "Bagikan artikel ini ke teman-teman Anda.",
        "tentang_title": "Tentang DailyMoney",
        "tentang_desc": "DailyMoney adalah platform berita dan edukasi keuangan yang didedikasikan untuk membantu masyarakat Indonesia mengambil keputusan finansial yang lebih cerdas.",
        "404_title": "Halaman Tidak Ditemukan",
        "404_desc": "Halaman yang Anda cari tidak tersedia atau telah dipindahkan.",
        "404_btn": "Kembali ke Beranda",
        "loading_text": "Memuat...",
        "sidebar_title": "Menu Utama",
        "sidebar_desc": "Portal berita & edukasi keuangan untuk Indonesia yang lebih cerdas secara finansial.",
        "sidebar_stat_articles": "Artikel/hari",
        "sidebar_stat_langs": "2 Bahasa",
        "sidebar_stat_free": "Gratis",
        "sidebar_stat_free_lbl": "Selamanya",
        "sidebar_lang_label": "Bahasa",
        "sidebar_font_label": "Ukuran Teks",
        "market_title": "Pasar Live",
        "market_update": "• Live Update (Real-time)",
        "trending_label": "TOPIK POPULER",
        "share_copy_aria": "Salin Tautan",
        "share_copied": "✔ Tersalin!",
        "share_copy_btn": " Salin Tautan",
    },
    "en": {
        "html_lang": "en",
        "schema_lang": "en-US",
        "nav_beranda": "Home",
        "nav_artikel": "Articles",
        "nav_tentang": "About",
        "nav_en": "Bahasa Indonesia",
        "breadcrumb_home": "Home",
        "breadcrumb_articles": "Articles",
        "share_label": "Share",
        "footer_desc": "A financial education platform that helps people make smarter, more informed financial decisions.",
        "footer_nav": "Navigation",
        "footer_topics": "Topics",
        "footer_partner": "Partner",
        "footer_disclosure": "Disclosure",
        "footer_copyright": "© 2026 DailyMoney. All rights reserved.",
        "footer_made": "Made with ❤️ for smart investors",
        "breaking_text": "BREAKING",
        "hero_title": "Trusted Financial News",
        "hero_desc": "In-depth analysis and latest news on capital markets, investing, and macroeconomics for smarter financial decisions.",
        "hero_stat1_num": "4+",
        "hero_stat1_label": "Today's Articles",
        "hero_stat2_num": "ID/EN",
        "hero_stat2_label": "Bilingual",
        "hero_stat3_num": "Free",
        "hero_stat3_label": "Forever",
        "hero_stat4_num": "2026",
        "hero_stat4_label": "Latest",
        "section_articles": "Latest Articles",
        "section_tagline": "Latest financial analysis and news to guide your investment decisions",
        "empty_title": "No Articles Yet",
        "empty_desc": "New articles coming soon. Stay tuned!",
        "cta_bookmark_text": "Save this article to read later.",
        "cta_share_text": "Share this article with your friends.",
        "tentang_title": "About DailyMoney",
        "tentang_desc": "DailyMoney is a financial news and education platform dedicated to helping people make smarter financial decisions.",
        "tentang_about": "DailyMoney provides in-depth analysis of capital markets, investments, inflation, and macroeconomics. Our content is designed to help readers make smarter and more informed financial decisions.",
        "tentang_standards": "Every article is written to high journalistic standards, citing the latest data from trusted sources such as BPS, Bank Indonesia, OJK, and international institutions.",
        "tentang_vision_title": "Our Vision",
        "tentang_vision": "To become the number one trusted financial news source in Indonesia, accessible to everyone, free forever.",
        "tentang_contact_title": "Contact Us",
        "tentang_contact": "X: @DailyMoneyID • Telegram: @EsterToobit",
        "404_title": "Page Not Found",
        "404_desc": "The page you are looking for is not available or has been moved.",
        "404_btn": "Back to Home",
        "loading_text": "Loading...",
        "sidebar_title": "Main Menu",
        "sidebar_desc": "Your trusted financial portal for smarter money decisions.",
        "sidebar_stat_articles": "Articles/day",
        "sidebar_stat_langs": "2 Languages",
        "sidebar_stat_free": "Free",
        "sidebar_stat_free_lbl": "Forever",
        "sidebar_lang_label": "Language",
        "sidebar_font_label": "Text Size",
        "market_title": "Market Live",
        "market_update": "• Live Update (Real-time)",
        "trending_label": "TRENDING TOPICS",
        "share_copy_aria": "Copy Link",
        "share_copied": "✔ Copied!",
        "share_copy_btn": " Copy Link",
    }
}


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    text = text.strip('-')
    return text[:80]


def markdown_to_html(md):
    # Fix literal \n (backslash-n) that should be actual newlines
    md = md.replace('\\n', '\n')
    lines = md.split('\n')
    html_lines = []
    in_list = False
    in_olist = False
    in_blockquote = False
    in_paragraph = False
    in_table = False

    def close_list():
        nonlocal in_list
        if in_list:
            html_lines.append('</ul>')
            in_list = False

    def close_olist():
        nonlocal in_olist
        if in_olist:
            html_lines.append('</ol>')
            in_olist = False

    def close_blockquote():
        nonlocal in_blockquote
        if in_blockquote:
            html_lines.append('</blockquote>')
            in_blockquote = False

    def close_paragraph():
        nonlocal in_paragraph
        if in_paragraph:
            html_lines[-1] += '</p>'
            in_paragraph = False

    def close_table():
        nonlocal in_table
        if in_table:
            html_lines.append('</tbody></table></div>')
            in_table = False

    def inline_cleanup(text):
        # Convert markdown links [text](url) first
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
        text = re.sub(r'(?<!\w)\*(.+?)\*(?!\w)', r'<em>\1</em>', text)
        text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<em>\1</em>', text)
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        text = re.sub(r'~~(.+?)~~', r'<del>\1</del>', text)
        return text

    def close_all():
        close_table(); close_olist(); close_list(); close_blockquote(); close_paragraph()

    for line in lines:
        stripped = line.strip()

        if stripped.startswith('### '):
            close_all()
            html_lines.append(f'<h3>{inline_cleanup(stripped[4:])}</h3>')
            continue
        if stripped.startswith('## '):
            close_all()
            html_lines.append(f'<h2>{inline_cleanup(stripped[3:])}</h2>')
            continue
        if stripped.startswith('# '):
            close_all()
            continue

        if stripped == '---':
            close_all()
            html_lines.append('<hr>')
            continue

        if stripped.startswith('> '):
            close_table(); close_olist(); close_list(); close_paragraph()
            if not in_blockquote:
                html_lines.append('<blockquote>')
                in_blockquote = True
            html_lines.append(f'  <p>{inline_cleanup(stripped[2:])}</p>')
            continue
        elif stripped.startswith('>'):
            close_table(); close_olist(); close_list(); close_paragraph()
            if not in_blockquote:
                html_lines.append('<blockquote>')
                in_blockquote = True
            html_lines.append(f'  <p>{inline_cleanup(stripped[1:])}</p>')
            continue
        else:
            close_blockquote()

        if '|' in stripped and stripped.startswith('|'):
            if re.match(r'^\|[-:\s|]+\|$', stripped):
                continue
            close_olist(); close_list(); close_paragraph()
            if not in_table:
                html_lines.append('<div class="table-wrapper"><table><thead><tr>')
                if stripped.startswith('|'):
                    cells = [c.strip() for c in stripped.split('|')[1:-1]]
                else:
                    cells = [c.strip() for c in stripped.split('|') if c.strip() != '']
                for cell in cells:
                    html_lines.append(f'  <th>{inline_cleanup(cell)}</th>')
                html_lines.append('</tr></thead><tbody>')
                in_table = True
            else:
                if stripped.startswith('|'):
                    cells = [c.strip() for c in stripped.split('|')[1:-1]]
                else:
                    cells = [c.strip() for c in stripped.split('|') if c.strip() != '']
                html_lines.append('<tr>')
                for cell in cells:
                    html_lines.append(f'  <td>{inline_cleanup(cell)}</td>')
                html_lines.append('</tr>')
            continue
        else:
            close_table()

        if stripped == '':
            close_all()
            html_lines.append('')
            continue

        # Ordered list: "1. item" or "1) item"
        ol_match = re.match(r'^(\d+)[\.\)] (.+)$', stripped)
        if ol_match:
            close_table(); close_list(); close_paragraph(); close_blockquote()
            if not in_olist:
                html_lines.append('<ol>')
                in_olist = True
            html_lines.append(f'  <li>{inline_cleanup(ol_match.group(2))}</li>')
            continue
        else:
            close_olist()

        if stripped.startswith('- ') or stripped.startswith('* '):
            close_table(); close_olist(); close_paragraph(); close_blockquote()
            if not in_list:
                html_lines.append('<ul>')
                in_list = True
            # Handle nested task lists
            item_text = inline_cleanup(stripped[2:])
            html_lines.append(f'  <li>{item_text}</li>')
            continue
        else:
            close_list()

        text = inline_cleanup(stripped)
        if not in_paragraph:
            html_lines.append(f'<p>{text}')
            in_paragraph = True
        else:
            html_lines.append(f' {text}')

    close_table(); close_olist(); close_list(); close_blockquote(); close_paragraph()
    return '\n'.join(html_lines)


def build_article_html(data, lang, lang_prefix="", lang_map=None):
    """Build a full article HTML page for a given language."""
    L = LANG_CONFIG[lang]
    # Load market prices for embedded ticker
    price_path = os.path.join(BASE_DIR, '_price_data.json')
    prices = {}
    if os.path.exists(price_path):
        try:
            with open(price_path) as f:
                prices = json.load(f).get('data', {})
        except: pass
    judul = data.get('judul', 'Untitled')
    meta_desc = data.get('meta_desc', '')
    content_md = data.get('content_markdown', '')
    tags = data.get('tags', '')
    date = data.get('date', '')
    image_url = data.get('image_url', '')
    image_caption = data.get('image_caption', '')

    slug = slugify(judul)
    judul_escaped = html.escape(judul)
    judul_title = html.escape(judul[:57].rstrip() + '...') if len(judul) > 60 else judul_escaped
    meta_desc_escaped = html.escape(meta_desc)

    # Prefix for relative paths
    p = lang_prefix  # "" for ID articles, "../" for EN articles
    if p:
        article_url_path = f"/en/articles/{slug}.html"
        canonical_url = f"{SITE_URL}/en/articles/{slug}.html"
        js_path = f"{p}assets/js/articles.js"
    else:
        article_url_path = f"/articles/{slug}.html"
        canonical_url = f"{SITE_URL}/articles/{slug}.html"
        js_path = f"../assets/js/articles.js"

    # Tags
    tag_list = [t.strip() for t in tags.split(',') if t.strip()]
    tags_html = '\n          '.join(
        f'<span class="tag">{html.escape(t)}</span>' for t in tag_list[:5]
    )

    # Home URL for relative navigation
    root_url = "/" if lang == "id" else "/en/"
    home_url = root_url
    partner_url = "/kerjasama/" if lang == "id" else "/en/kerjasama/"
    disclosure_url = "/disclosure/" if lang == "id" else "/en/disclosure/"
    tentang_url = "/tentang/" if lang == "id" else "/en/tentang/"
    main_js_url = f"/assets/js/main.js"    # Convert date to readable format
    try:
        parts = date.split('/')
        day_num = int(parts[0])
        month_num = int(parts[1])
        year_num = parts[2]
        if lang == "en":
            month_names = ["", "January", "February", "March", "April", "May", "June",
                          "July", "August", "September", "October", "November", "December"]
            day_names = ["", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            # Convert DD/MM/YYYY to date object for day of week
            from datetime import date as dt_date
            dt = dt_date(int(year_num), month_num, day_num)
            day_name = day_names[dt.weekday() + 1]
            date_formatted = f"{day_name}, {day_num} {month_names[month_num]} {year_num}"
        else:
            month_names = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni",
                          "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
            day_names = ["", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
            from datetime import date as dt_date
            dt = dt_date(int(year_num), month_num, day_num)
            day_name = day_names[dt.weekday() + 1]
            date_formatted = f"{day_name}, {day_num} {month_names[month_num]} {year_num}"
        source_name = data.get("source", "")
        author_str = source_name if source_name else "DailyMoney"
    except:
        date_formatted = date
        source_name = data.get("source", "")
        author_str = source_name if source_name else "DailyMoney"


    # Image

    date_html = f'<span class="article-date">{html.escape(date_formatted)}</span>' if date else ''

    # Convert markdown
    content_html = markdown_to_html(content_md)

    # CTA box — last <p> containing "DailyMoney" (per-paragraph, not cross-paragraph)
    para_matches = list(re.finditer(r'<p>(.*?)</p>', content_html, re.DOTALL))
    cta_paras = [m for m in para_matches if 'DailyMoney' in m.group(1)]
    if cta_paras:
        last = cta_paras[-1]
        inner = last.group(1)
        new_tag = f'<div class="cta-box"><p>{inner}</p></div>'
        content_html = content_html[:last.start()] + new_tag + content_html[last.end():]

    if image_url:
        # Sanitize image URL: remove double slashes
        clean_url = re.sub(r'([^:]/)/+', r'\1', image_url)
        cap_html = f'<div class="img-caption">{html.escape(image_caption)}</div>' if image_caption else ''
        image_html = f'<div class="article-featured-image"><img src="{html.escape(clean_url)}" alt="{judul_escaped}" loading="lazy">{cap_html}</div>'
    else:
        image_html = ''

    # Date ISO
    try:
        parts = date.split('/')
        article_date_iso = f"{parts[2]}-{parts[1]}-{parts[0]}"
    except:
        article_date_iso = "2026-01-01"

    cache_buster = int(datetime.now().timestamp())
    gen_ts = cache_buster

    # Language switcher link
    if lang == "id":
        if lang_map and data.get('pair_id') in lang_map:
            en_slug = lang_map[data['pair_id']]['en']
            id_slug = lang_map[data['pair_id']]['id']
            lang_switch_url = f"{SITE_URL}/en/articles/{en_slug}.html"
        else:
            en_slug = slug
            id_slug = slug
            lang_switch_url = f"{SITE_URL}/en/articles/{slug}.html"
        lang_switch_label = L["nav_en"]
        newsletter_title = "📬 Tetap Terupdate"
        newsletter_desc = "Dapatkan berita keuangan terbaru langsung di email Anda"
        newsletter_placeholder = "email@anda.com"
        newsletter_btn = "Langganan"
    else:
        if lang_map and data.get('pair_id') in lang_map:
            id_slug = lang_map[data['pair_id']]['id']
            en_slug = lang_map[data['pair_id']]['en']
            lang_switch_url = f"{SITE_URL}/articles/{id_slug}.html"
        else:
            id_slug = slug
            en_slug = slug
            lang_switch_url = f"{SITE_URL}/articles/{slug}.html"
        lang_switch_label = L["nav_en"]
        newsletter_title = "📬 Stay Updated"
        newsletter_desc = "Get the latest financial news delivered to your inbox"
        newsletter_placeholder = "your@email.com"
        newsletter_btn = "Subscribe"

    # Build
    html_out = f"""<!DOCTYPE html>
<html lang="{L["html_lang"]}" class="dm-smooth-scroll">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>{judul_title} - DailyMoney</title>
  <meta name="description" content="{meta_desc_escaped}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23DC2626'/><text x='16' y='23' text-anchor='middle' fill='white' font-size='18' font-weight='800' font-family='system-ui'>D</text></svg>">
  <link rel="manifest" href="/manifest.json">
  <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23DC2626'/><text x='16' y='23' text-anchor='middle' fill='white' font-size='18' font-weight='800' font-family='system-ui'>D</text></svg>">
  <meta name="theme-color" content="#DC2626">
  <meta http-equiv="Content-Security-Policy" content="default-src 'self' https:; script-src 'self' 'unsafe-inline' https:; style-src 'self' 'unsafe-inline'; img-src 'self' https://images.unsplash.com https://s3.tradingview.com data:; connect-src 'self' https://fonts.googleapis.com https://api.coingecko.com wss://ws.coincap.io https://s3.tradingview.com wss://ws.tradingview.com https://visitor-badge.laobi.icu; font-src 'self' https://fonts.gstatic.com; frame-ancestors 'none'; base-uri 'self'; object-src 'none'">
  <meta property="og:title" content="{judul_title}">
  <meta property="og:description" content="{meta_desc_escaped}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{canonical_url}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="alternate" hreflang="id" href="{SITE_URL}/articles/{id_slug}.html">
  <link rel="alternate" hreflang="en" href="{SITE_URL}/en/articles/{en_slug}.html">
  <link rel="canonical" href="{canonical_url}">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    "headline": "{judul_escaped}",
    "description": "{meta_desc_escaped}",
    "url": "{canonical_url}",
    "inLanguage": "{L["schema_lang"]}",
    "isAccessibleForFree": true,
    "datePublished": "{article_date_iso}",
    "author": {{
      "@type": "Organization",
      "name": "DailyMoney",
      "url": "{SITE_URL}/"
    }},
    "publisher": {{
      "@type": "Organization",
      "name": "DailyMoney"
    }}
  }}
  </script>
  <link rel="alternate" hreflang="id" href="https://dailymoney.my.id/" />
  <link rel="alternate" hreflang="en" href="https://dailymoney.my.id/en" />
</head>
<body>

  <!-- Navigation -->
    <!-- dm-header: New clean header -->
  <div class="dm-overlay" id="dmOverlay"></div>
  
  <header class="dm-header">
    <a href="{root_url}" class="dm-logo">
      <span class="dm-logo-icon">D</span>
      <span class="dm-logo-text">DailyMoney</span>
    </a>
    <button class="dm-hamburger" id="dmMenuBtn" aria-label="Menu">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
    </button>
  
    <nav class="dm-desktop-nav">
      <a href="{root_url}">{L["nav_beranda"]}</a>
      <a href="{root_url}#artikel">{L["nav_artikel"]}</a>
      <a href="{root_url}tentang/">{L["nav_tentang"]}</a>
      <a href="{partner_url}">{L["footer_partner"]}</a>
      <a href="{'/en/' if lang == 'id' else '/'}" class="lang-btn">{L['nav_en']}</a>
    </nav>
  </header>
  
      <!-- dm-market-ticker -->
  <div class="dm-ticker-bar">
    <div class="dm-ticker-track">
      {gen_ticker_items(prices)}
    </div>
  </div>

<aside class="dm-sidebar" id="dmSidebar">
    <div class="dm-sidebar-header">
      <span class="dm-sidebar-title">{L["sidebar_title"]}</span>
      <button class="dm-close-btn" id="dmCloseBtn">&times;</button>
    </div>
    
    <ul class="dm-sidebar-links">
      <li>
        <a href="{root_url}">
          <span class="dm-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          </span> {L["nav_beranda"]}
        </a>
      </li>
      <li>
      <a href="{root_url}#artikel">
          <span class="dm-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 20H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v1m2 13a2 2 0 0 1-2-2V7m2 13a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/></svg>
          </span> {L["nav_artikel"]}
        </a>
      </li>
      <li>
      <a href="{root_url}tentang/">
          <span class="dm-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          </span> {L["nav_tentang"]}
        </a>
      </li>
    </ul>
  
    <!-- dm-sidebar-market-live -->
    <div class="dm-market-live">
      <h4 class="dm-market-title">{L["market_title"]}</h4>
{gen_sidebar_items(prices)}
      <p class="dm-market-update">{L["market_update"]}</p>
    </div>
    
    <div class="dm-sidebar-settings">
      <div class="dm-setting-group">
        <span class="dm-setting-label">{L["sidebar_lang_label"]}</span>
        <a href="{lang_switch_url}" class="dm-setting-btn lang-btn">{lang_switch_label}</a>
      </div>
      <div class="dm-setting-group">
        <span class="dm-setting-label">{L["sidebar_font_label"]}</span>
        <div class="dm-text-controls">
          <button class="dm-size-btn" id="dmBtnMin">A-</button>
          <button class="dm-size-btn" id="dmBtnPlus">A+</button>
        </div>
      </div>
      <div class="dm-setting-group is-column">
        <span class="dm-setting-label">Kategori</span>
        <div class="dm-categories">
          <a href="{root_url}#artikel" class="dm-cat-tag">Saham</a>
          <a href="{root_url}#artikel" class="dm-cat-tag">Reksadana</a>
          <a href="{root_url}#artikel" class="dm-cat-tag">Inflasi</a>
          <a href="{root_url}#artikel" class="dm-cat-tag">Tips Hemat</a>
          <a href="{root_url}#artikel" class="dm-cat-tag">Ekonomi</a>
        </div>
      </div>
    </div>
  </aside>

  <!-- Article Content -->
  <article class="article-page">
    <nav class="breadcrumb">
      <a href="{home_url}">{L["breadcrumb_home"]}</a> / <a href="{home_url}#artikel">{L["breadcrumb_articles"]}</a> / {judul_escaped}
    </nav>

    <div class="article-inner">
    <header class="article-header">
      <h1>{judul_escaped}</h1>
      <div class="article-meta">
        {date_html}
        <span class="article-author">{author_str}</span>
        <div class="article-tags">
          {tags_html}
        </div>
      </div>
    </header>

    {image_html}

    <div class="article-content dm-break-words">
{content_html}
    </div>

    </div>

    <!-- Social Share -->
    <div class="share-bar">
      <div class="share-label">{L["share_label"]}</div>
      <button class="share-btn twitter" data-platform="twitter" aria-label="Twitter"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg></button>
      <button class="share-btn facebook" data-platform="facebook" aria-label="Facebook"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg></button>
      <button class="share-btn whatsapp" data-platform="whatsapp" aria-label="WhatsApp"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg></button>
      <button class="share-btn linkedin" data-platform="linkedin" aria-label="LinkedIn"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg></button>
      <button class="share-btn telegram" data-platform="telegram" aria-label="Telegram"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M11.944 0A12 12 0 000 12a12 12 0 0012 12 12 12 0 0012-12A12 12 0 0012 0a12 12 0 00-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 01.171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg></button>
      <button class="share-btn copy" data-platform="copy" aria-label="{L["share_copy_aria"]}" data-label="{L["share_copy_btn"]}" data-copied="{L["share_copied"]}"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M15 7.5a4.5 4.5 0 014.5 4.5V15a4.5 4.5 0 01-9 0v-3a.75.75 0 011.5 0v3a3 3 0 006 0v-3A3 3 0 0015 9H9a4.5 4.5 0 000 9h3a.75.75 0 010 1.5H9a6 6 0 010-12h6z"/></svg></button>
    </div>

    <!-- Newsletter -->
    <div class="newsletter-section">
      <h3>{newsletter_title}</h3>
      <p>{newsletter_desc}</p>
      <form class="newsletter-form" id="newsletterForm">
        <input type="email" placeholder="{newsletter_placeholder}" required>
        <button type="submit">{newsletter_btn}</button>
      </form>
    </div>
  </article>

  <footer>
    <div class="footer-inner">
      <div class="footer-brand">
        <a href="{root_url}" class="logo">
          <div class="logo-icon">D</div>
          <span>DailyMoney</span>
        </a>
        <p>{L["footer_desc"]}</p>
      </div>
      <div class="footer-col">
        <h4>{L["footer_nav"]}</h4>
        <ul>
          <li><a href="{root_url}">{L["nav_beranda"]}</a></li>
          <li><a href="#artikel">{L["nav_artikel"]}</a></li>
          <li><a href="{tentang_url}">{L["nav_tentang"]}</a></li>
          <li><a href="{partner_url}">{L["footer_partner"]}</a></li>
          <li><a href="{disclosure_url}">{L["footer_disclosure"]}</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>{L["footer_topics"]}</h4>
        <ul>
          <li><a href="{root_url}#artikel">Investasi</a></li>
          <li><a href="{root_url}#artikel">Inflasi</a></li>
          <li><a href="{root_url}#artikel">Reksadana</a></li>
          <li><a href="{root_url}#artikel">Saham</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>{L["footer_copyright"]}</span>
      <span>{L["footer_made"]}</span>
    </div>
  </footer>

  <button class="back-to-top" id="backToTop">↑</button>


  <script src="{main_js_url}?v={gen_ts}"></script>
  <script src="/assets/js/market-live.js?v={gen_ts}"></script>
  <script src="{js_path}?v={gen_ts}"></script>
<img src="https://visitor-badge.laobi.icu/badge?page_id=dmid" style="display:none" alt="" aria-hidden="true">
<script>
(function(){{var d=(new Date).toISOString().slice(0,10),k='dm_v_'+d;if(!localStorage.getItem(k)){{new Image().src='https://visitor-badge.laobi.icu/badge?page_id=dmid-'+d;localStorage.setItem(k,'1')}}}})();
</script>

</body>
</html>"""
    return html_out, slug


def generate_articles(lang, source_dir, output_dir, js_path, lang_prefix="", lang_map=None):
    """Generate all articles for a given language."""
    L = LANG_CONFIG[lang]
    article_files = sorted(glob.glob(os.path.join(source_dir, '*.json')))
    articles_data = []

    if not article_files:
        print(f"  ℹ️ No articles found in {source_dir}")
        return articles_data

    os.makedirs(output_dir, exist_ok=True)
    if lang == "en":
        os.makedirs(os.path.join(BASE_DIR, 'en', 'assets', 'js'), exist_ok=True)

    for filepath in article_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        article_html, slug = build_article_html(data, lang, lang_prefix, lang_map)

        article_path = os.path.join(output_dir, f'{slug}.html')
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(article_html)

        articles_data.append({
            'judul': data.get('judul', 'Untitled'),
            'meta_desc': data.get('meta_desc', ''),
            'slug': slug,
            'tags': data.get('tags', ''),
            'date': data.get('date', ''),
            'image_url': data.get('image_url', ''),
            'lang': lang,
        })
        print(f'  ✓ {slug}.html')

    # Generate JS feed — exclude archived articles
    fresh_articles = [a for a in articles_data if not a.get('_archived')]
    js_content = '/* Auto-generated by generate-site.py */\nwindow.__ARTICLES = '
    js_content += json.dumps(fresh_articles, ensure_ascii=False, indent=2)
    js_content += ';\n'

    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)

    print(f'  → articles.js ({len(js_content)} bytes)')
    return articles_data


def generate_homepage(lang, output_path, articles, lang_prefix="", prices=None, visitor_daily=0, visitor_total=0):
    """Generate homepage for a given language."""
    L = LANG_CONFIG[lang]
    if prices is None:
        prices = {}
    root_url = "/" if lang == "id" else "/en/"
    
    # Build stat cards with embedded prices
    stat_items = []
    symbols_order = ['BTC', 'ETH', 'IHSG', 'XAU', 'USDIDR']
    for sym in symbols_order:
        pdata = prices.get(sym, {})
        price = pdata.get('price')
        change = pdata.get('change')
        display_sym = 'USD/IDR' if sym == 'USDIDR' else sym
        sym_id = sym.lower() if sym != 'USDIDR' else 'usdidr'
        if price is not None:
            price_str = format_price(price, sym)
            change_class = 'up' if change and change >= 0 else 'down'
            change_str = f'{change:+.2f}%' if change is not None else ''
            stat_html = f'<div class="hero-market-stat" data-symbol="{display_sym}"><span class="stat-num {change_class}" id="price-{sym_id}">{price_str}</span><span class="stat-lbl {change_class}">{display_sym}</span></div>'
        else:
            stat_html = f'<div class="hero-market-stat" data-symbol="{display_sym}"><span class="stat-num">--</span><span class="stat-lbl">{display_sym}</span></div>'
        stat_items.append(stat_html)
    stats_grid_html = '\n'.join(stat_items)

    slider_articles = articles[:4]
    grid_items = ""

    for i, a in enumerate(slider_articles):
        featured_class = " featured" if i == 0 else ""
        if lang == "en":
            article_url = f"/en/articles/{a['slug']}.html"
        else:
            article_url = f"/articles/{a['slug']}.html"

        img_html = ""
        if a.get('image_url'):
            clean_url = re.sub(r'([^:]/)/+', r'\1', a["image_url"])
            img_html = f'<img src="{html.escape(clean_url)}" alt="{html.escape(a["judul"])}" loading="lazy">'

        grid_items += f"""
    <a href="{article_url}" class="article-card{featured_class}" data-index="{i}">
      <div class="article-card-visual">
        {img_html}
        <div class="article-card-gradient"></div>
      </div>
      <div class="article-card-body">
        <div class="article-card-top">
          <span class="tag">{html.escape(a["tags"].split(",")[0].strip()) if a["tags"] else "Finance"}<span class="ai-badge">⚙️ AI</span></span>
          <h3>{html.escape(a["judul"])}</h3>
          <p class="excerpt">{html.escape(a["meta_desc"][:120])}</p>
        </div>
        <div class="meta">
          <span>📅 {html.escape(a["date"])}</span>
        </div>
      </div>
    </a>"""

    if not grid_items:
        grid_items = f"""
    <div class="empty-state">
      <div class="icon">📰</div>
      <h3>{L["empty_title"]}</h3>
      <p>{L["empty_desc"]}</p>
    </div>"""

    if lang == "en":
        lang_switch_url = "/"
        lang_switch_label = L["nav_en"]
        tentang_url = "/en/tentang/"
        partner_url = "/en/kerjasama/"
        disclosure_url = "/en/disclosure/"
        js_url = "/en/assets/js/articles.js"
        canon_url = f"{SITE_URL}/en/"
        search_placeholder = "Search articles..."
        search_btn = "Search"
        rss_url = "/en/feed.xml"
    else:
        lang_switch_url = "/en/"
        lang_switch_label = L["nav_en"]
        tentang_url = "/tentang/"
        partner_url = "/kerjasama/"
        disclosure_url = "/disclosure/"
        js_url = "/assets/js/articles.js"
        canon_url = SITE_URL
        search_placeholder = "Cari artikel..."
        search_btn = "Cari"
        rss_url = "/feed.xml"

    # Build embedded market data JSON
    prices_clean = {}
    if prices:
        for k, v in prices.items():
            if v and v.get('price') is not None:
                prices_clean[k] = {'price': v['price'], 'change': v.get('change')}
    prices_json = json.dumps(prices_clean, ensure_ascii=False)

    # Build chart + stocks HTML (f-string safe — no backslash escaping needed)
    # Build combined market overview box (IHSG + Saham)
    ihsg_price = prices.get('IHSG', {}).get('price', '')
    ihsg_change = prices.get('IHSG', {}).get('change', 0)
    # IHSG card removed (insight only)
    # Compact market section (fills gap between insight and articles)
    ihsg_p = prices.get('IHSG', {}).get('price', 0)
    ihsg_c = prices.get('IHSG', {}).get('change', 0)
    ihsg_cls = 'up' if ihsg_c is not None and ihsg_c >= 0 else 'down'
    ihsg_change_str = f'{ihsg_c:+.2f}%' if ihsg_c is not None else ''
    compact_market = '<div class="compact-market"><div class="cmp-ihsg"><div class="cmp-top"><div class="cmp-label">IHSG</div><div class="cmp-prices"><span class="cmp-price ' + ihsg_cls + '" id="cmp-ihsg-price">' + str(ihsg_p) + '</span><span class="cmp-change ' + ihsg_cls + '" id="cmp-ihsg-change">' + ihsg_change_str + '</span></div></div><div class="cmp-stocks-wrap">'
    stocks = [('TLKM','Telkom'),('BBRI','BRI'),('BBCA','BCA'),('ASII','Astra'),('UNVR','Unilever'),('BMRI','Mandiri')]
    for s, n in stocks:
        sp = prices.get(s, {})
        sprice = sp.get('price')
        schange = sp.get('change')
        if sprice:
            sprice_str = 'Rp' + str(int(sprice))
            schange_str = f'{schange:+.2f}%' if schange is not None else ''
            schange_cls = 'cmp-neutral' if schange is None or schange == 0 else ('cmp-up' if schange > 0 else 'cmp-down')
            compact_market += '<div class="cmp-stock stock-card-clean" data-stock="' + s + '"><span class="cmp-ticker">' + s + '</span><span class="cmp-sprice" id="stock-' + s + '">' + sprice_str + '</span><span class="cmp-schange ' + schange_cls + '" id="change-' + s + '">' + schange_str + '</span></div>'
    compact_market += '</div></div></div>'
    chart_html = compact_market
    # Dynamic insight text
    ihsg_c = prices.get('IHSG', {}).get('change', 0)
    btc_c = prices.get('BTC', {}).get('change', 0)
    if ihsg_c is not None and ihsg_c >= 0: sen = 'zona hijau dengan sentimen positif'
    elif ihsg_c is not None: sen = 'tekanan jual'
    else: sen = 'konsolidasi'
    if btc_c is not None and btc_c >= 0: btc_sen = 'tren positif'
    else: btc_sen = 'tekanan jual'
    timestamp = datetime.now().strftime('%H:%M')
    insight_text = f'Pasar hari ini menunjukkan pergerakan di {sen}. Sentimen global mempengaruhi pergerakan IHSG, sementara kripto masih dalam {btc_sen}. Investor disarankan mencermati data ekonomi makro ke depan.'
    
    stocks_html = '<div class="saham-modern-panel"><div class="native-section-header"><h3 class="section-title">Pantauan Saham Lokal</h3></div><div class="stock-grid-clean" id="stocksGrid">'
    for s, n in stocks:
        sp = prices.get(s, {})
        sprice = sp.get('price')
        schange = sp.get('change')
        if sprice:
            sprice_str = f'Rp{int(sprice):,}'.replace(',', '.')
            schange_str = f'{schange:+.2f}%' if schange is not None else ''
            schange_cls = 'neutral' if schange is None or schange == 0 else ('up' if schange > 0 else 'down')
            stocks_html += f'<div class="stock-card-clean" data-stock="{s}"><div class="stock-title"><span class="ticker">{s}</span><span class="company">{n}</span></div><div class="stock-price" id="stock-{s}">{sprice_str}</div><div class="stock-change {schange_cls}" id="change-{s}">{schange_str}</div></div>'
        else:
            stocks_html += f'<div class="stock-card-clean" data-stock="{s}"><div class="stock-title"><span class="ticker">{s}</span><span class="company">{n}</span></div><div class="stock-price" id="stock-{s}">--</div><div class="stock-change" id="change-{s}"></div></div>'
    stocks_html += '</div><p class="stocks-note">* Harga saham diperbarui tiap 10 menit</p></div>'

    # Format visitor counts with thousand separator
    visitor_daily_fmt = f"{visitor_daily:,}".replace(",", ".")
    visitor_total_fmt = f"{visitor_total:,}".replace(",", ".")

    homepage = f"""<!DOCTYPE html>
<html lang="{L["html_lang"]}" class="dm-smooth-scroll">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>DailyMoney - Berita Finansial Terpercaya | Trusted Financial News</title>
  <meta name="description" content="Informasi terkini seputar saham, reksadana, dan tips hemat. | Latest updates on stocks, mutual funds, and saving tips.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23DC2626'/><text x='16' y='23' text-anchor='middle' fill='white' font-size='18' font-weight='800' font-family='system-ui'>D</text></svg>">
  <meta property="og:title" content="DailyMoney - {L["hero_title"]}">
  <meta property="og:description" content="{L["hero_desc"]}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canon_url}">
  <meta property="og:image" content="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="alternate" hreflang="id" href="{SITE_URL}/">
  <link rel="alternate" hreflang="en" href="{SITE_URL}/en/">
  <link rel="canonical" href="{canon_url}">
  <link rel="manifest" href="/manifest.json">
  <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23DC2626'/><text x='16' y='23' text-anchor='middle' fill='white' font-size='18' font-weight='800' font-family='system-ui'>D</text></svg>">
<meta http-equiv="Content-Security-Policy" content="default-src 'self' https:; script-src 'self' 'unsafe-inline' https:; style-src 'self' 'unsafe-inline'; img-src 'self' https://images.unsplash.com https://s3.tradingview.com data:; connect-src 'self' https://fonts.googleapis.com https://api.coingecko.com wss://ws.coincap.io https://s3.tradingview.com wss://ws.tradingview.com https://visitor-badge.laobi.icu; font-src 'self' https://fonts.gstatic.com; frame-ancestors 'none'; base-uri 'self'; object-src 'none'">
    <meta name="theme-color" content="#DC2626">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "DailyMoney",
    "url": "{SITE_URL}/",
    "description": "{L["hero_desc"]}",
    "inLanguage": "{L["schema_lang"]}",
    "isAccessibleForFree": true
  }}
  </script>
</head>
<body>


  <!-- Navigation -->
    <div class="dm-overlay" id="dmOverlay"></div>
  
  <header class="dm-header">
    <a href='{"/" if lang=="id" else "/en/"}' class="dm-logo">
      <span class="dm-logo-icon">D</span>
      <span class="dm-logo-text">DailyMoney</span>
    </a>
    <button class="dm-hamburger" id="dmMenuBtn" aria-label="Menu">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
    </button>
  
    <nav class="dm-desktop-nav">
      <a href='{"/" if lang=="id" else "/en/"}'>{L["nav_beranda"]}</a>
      <a href='{"/" if lang=="id" else "/en/"}#artikel'>{L["nav_artikel"]}</a>
      <a href="{tentang_url}">{L["nav_tentang"]}</a>
      <a href="{partner_url}">{L["footer_partner"]}</a>
      <a href='{"/en/" if lang=="id" else "/"}' class="lang-btn">{L["nav_en"]}</a>
    </nav>
  </header>
  
  <!-- dm-market-ticker -->
  <div class="dm-ticker-bar">
    <div class="dm-ticker-track">
      {gen_ticker_items(prices)}
    </div>
  </div>

  <aside class="dm-sidebar" id="dmSidebar">
    <div class="dm-sidebar-header">
      <span class="dm-sidebar-title">{L["sidebar_title"]}</span>
      <button class="dm-close-btn" id="dmCloseBtn">&times;</button>
    </div>
    <ul class="dm-sidebar-links">
      <li>
        <a href='{"/" if lang=="id" else "/en/"}'><span class="dm-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg></span> {L["nav_beranda"]}</a>
      </li>
      <li>
        <a href='{"/" if lang=="id" else "/en/"}#artikel'><span class="dm-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 20H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v1m2 13a2 2 0 0 1-2-2V7m2 13a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/></svg></span> {L["nav_artikel"]}</a>
      </li>
      <li>
        <a href="{tentang_url}"><span class="dm-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg></span> {L["nav_tentang"]}</a>
      </li>
    </ul>
    <!-- dm-sidebar-market-live -->
    <div class="dm-market-live">
      <h4 class="dm-market-title">{L["market_title"]}</h4>
{gen_sidebar_items(prices)}
      <p class="dm-market-update">{L["market_update"]}</p>
    </div>
    <div class="dm-sidebar-settings">
      <div class="dm-setting-group">
        <span class="dm-setting-label">{L["sidebar_lang_label"]}</span>
        <a href="{lang_switch_url}" class="dm-setting-btn lang-btn">{lang_switch_label}</a>
      </div>
      <div class="dm-setting-group">
        <span class="dm-setting-label">{L["sidebar_font_label"]}</span>
        <div class="dm-text-controls">
          <button class="dm-size-btn" id="dmBtnMin">A-</button>
          <button class="dm-size-btn" id="dmBtnPlus">A+</button>
        </div>
      </div>
      <div class="dm-setting-group is-column">
        <span class="dm-setting-label">Kategori</span>
        <div class="dm-categories">
          <a href="{root_url}#artikel" class="dm-cat-tag">Saham</a>
          <a href="{root_url}#artikel" class="dm-cat-tag">Reksadana</a>
          <a href="{root_url}#artikel" class="dm-cat-tag">Inflasi</a>
          <a href="{root_url}#artikel" class="dm-cat-tag">Tips Hemat</a>
          <a href="{root_url}#artikel" class="dm-cat-tag">Ekonomi</a>
        </div>
      </div>
    </div>
  </aside>

  <!-- dm-trending: Trending Topics Bar (SEO Optimized) -->
  <section class="hero">
    <div class="hero-inner">
      <div class="hero-content">
        <h1>{L["hero_title"]}</h1>
        <p class="hero-desc">{L["hero_desc"]}</p>
        <div class="hero-stats-grid">
          {stats_grid_html}
        </div>
      </div>
    </div>
  </section>

  {gen_crypto_section(prices)}

  <!-- dm-trending: Trending Topics Bar (SEO Optimized) -->
  <div class="dm-trending">
    <span class="dm-label">Trending:</span>
    <a href="#artikel" class="dm-tag">Saham (Stocks)</a>
    <a href="#artikel" class="dm-tag">Investasi (Investment)</a>
    <a href="#artikel" class="dm-tag">Inflasi (Inflation)</a>
    <a href="#artikel" class="dm-tag">Reksadana</a>
  </div>

  <!-- Catatan Kilat Agent Hermes -->
  <div class="hermes-insight-box">
    <div class="insight-header">
      <span class="insight-icon">🤖</span>
      <h4 class="insight-title">Catatan Kilat Agent Hermes</h4>
    </div>
    <p class="insight-body">"{insight_text}"</p>
  <div class="market-footer-bar"><span class="market-timestamp">⏱️ Data per <span id="marketTime">{timestamp}</span> WIB</span><span class="market-status" id="marketStatus"><span class="status-dot"></span> Pasar Dibuka</span></div>
  </div>
  {chart_html}
  <!-- Market Stats Strip -->
  <div class="market-strip">
    <div class="strip-item">
      <span class="strip-icon">👥</span>
      <span class="strip-label">Pengunjung Hari Ini</span>
      <span class="strip-value highlight">{visitor_daily_fmt}</span>
    </div>
    <div class="strip-item">
      <span class="strip-icon">👁️</span>
      <span class="strip-label">Total Dilihat</span>
      <span class="strip-value">{visitor_total_fmt}</span>
    </div>
    <div class="strip-item">
      <span class="strip-icon">⏱️</span>
      <span class="strip-label">Update Setiap</span>
      <span class="strip-value">10 menit</span>
    </div>
  </div>
  <!-- Articles Grid -->
  <section class="container dm-break-words" id="artikel">
    <div class="section-header">
      <h2>{L["section_articles"]}</h2>
      <p>{L["section_tagline"]}</p>
    </div>
    <div class="search-box">
      <input type="text" id="searchInput" placeholder="{search_placeholder}">
      <button id="searchBtn">{search_btn}</button>
    </div>
    <div class="article-grid" id="article-grid">
{grid_items}
    </div>
  </section>

  <!-- Footer -->
  <footer>
    <div class="footer-inner">
      <div class="footer-brand">
        <a href="{"/" if lang=="id" else "/en/"}" class="logo">
          <div class="logo-icon">D</div>
          <span>DailyMoney</span>
        </a>
        <p>{L["footer_desc"]}</p>
      </div>
      <div class="footer-col">
        <h4>{L["footer_nav"]}</h4>
        <ul>
          <li><a href="{root_url}">{L["nav_beranda"]}</a></li>
          <li><a href="{root_url}#artikel">{L["nav_artikel"]}</a></li>
          <li><a href="{tentang_url}">{L["nav_tentang"]}</a></li>
          <li><a href="{partner_url}">{L["footer_partner"]}</a></li>
          <li><a href="{disclosure_url}">{L["footer_disclosure"]}</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>{L["footer_topics"]}</h4>
        <ul>
          <li><a href="#artikel">Investasi</a></li>
          <li><a href="#artikel">Inflasi</a></li>
          <li><a href="#artikel">Reksadana</a></li>
          <li><a href="#artikel">Saham</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>RSS</h4>
        <ul>
          <li><a href="{rss_url}" target="_blank" rel="noopener">RSS Feed</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>{L["footer_copyright"]}</span>
      <span>{L["footer_made"]}</span>
    </div>
  </footer>

  <button class="back-to-top" id="backToTop">↑</button>

  <script>window.__INITIAL_DATA={{"prices":{prices_json}}};</script>
  <script src="{js_url}?v={int(datetime.now().timestamp())}"></script>
  <script src="/assets/js/main.js?v={int(datetime.now().timestamp())}"></script>
  <script src="/assets/js/market-live.js?v={int(datetime.now().timestamp())}"></script>
  <script>
    if ('serviceWorker' in navigator) {{
      navigator.serviceWorker.register('/sw.js').then(function(reg) {{
        // Force update check on every page load
        reg.update();
        // If waiting, activate immediately
        if (reg.waiting) {{
          reg.waiting.postMessage({{action: 'skipWaiting'}});
        }}
      }});
    }}
  </script>
<img src="https://visitor-badge.laobi.icu/badge?page_id=dmid" style="display:none" alt="" aria-hidden="true">
<script>
(function(){{var d=(new Date).toISOString().slice(0,10),k='dm_v_'+d;if(!localStorage.getItem(k)){{new Image().src='https://visitor-badge.laobi.icu/badge?page_id=dmid-'+d;localStorage.setItem(k,'1')}}}})();
</script>

</body>
</html>"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(homepage)
    print(f'  ✓ {output_path}')


def generate_tentang(lang, output_path, lang_prefix="", prices=None):
    """Generate about page for a given language."""
    L = LANG_CONFIG[lang]
    gen_ts = int(datetime.now().timestamp())
    root_url = "/" if lang == "id" else "/en/"

    if lang == "en":
        lang_switch_url = "/tentang/"
        tentang_url = "/en/tentang/"
        partner_url = "/en/kerjasama/"
        disclosure_url = "/en/disclosure/"
        canon_url = f"{SITE_URL}/en/tentang/"
    else:
        lang_switch_url = "/en/tentang/"
        tentang_url = "/tentang/"
        partner_url = "/kerjasama/"
        disclosure_url = "/disclosure/"
        canon_url = f"{SITE_URL}/tentang/"

    html_out = f"""<!DOCTYPE html>
<html lang="{L["html_lang"]}" class="dm-smooth-scroll">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>{L["tentang_title"]} - DailyMoney</title>
  <meta name="description" content="{L["tentang_desc"]}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css">
  <link rel="manifest" href="/manifest.json">
  <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23DC2626'/><text x='16' y='23' text-anchor='middle' fill='white' font-size='18' font-weight='800' font-family='system-ui'>D</text></svg>">
<meta http-equiv="Content-Security-Policy" content="default-src 'self' https:; script-src 'self' 'unsafe-inline' https:; style-src 'self' 'unsafe-inline'; img-src 'self' https://images.unsplash.com https://s3.tradingview.com data:; connect-src 'self' https://fonts.googleapis.com https://api.coingecko.com wss://ws.coincap.io https://s3.tradingview.com wss://ws.tradingview.com https://visitor-badge.laobi.icu; font-src 'self' https://fonts.gstatic.com; frame-ancestors 'none'; base-uri 'self'; object-src 'none'">
    <meta name="theme-color" content="#DC2626">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23DC2626'/><text x='16' y='23' text-anchor='middle' fill='white' font-size='18' font-weight='800' font-family='system-ui'>D</text></svg>">
  <meta property="og:title" content="{L["tentang_title"]} - DailyMoney">
  <meta property="og:description" content="{L["tentang_desc"]}">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canon_url}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="alternate" hreflang="id" href="{SITE_URL}/tentang/">
  <link rel="alternate" hreflang="en" href="{SITE_URL}/en/tentang/">
  <link rel="canonical" href="{canon_url}">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "AboutPage",
    "name": "{L["tentang_title"]}",
    "description": "{L["tentang_desc"]}",
    "url": "{canon_url}",
    "isAccessibleForFree": true
  }}
  </script>
</head>
<body>

    <!-- dm-header: New clean header -->
  <div class="dm-overlay" id="dmOverlay"></div>
  
  <header class="dm-header">
    <a href="{root_url}" class="dm-logo">
      <span class="dm-logo-icon">D</span>
      <span class="dm-logo-text">DailyMoney</span>
    </a>
    <button class="dm-hamburger" id="dmMenuBtn" aria-label="Menu">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
    </button>
  
    <nav class="dm-desktop-nav">
      <a href="{root_url}">{L["nav_beranda"]}</a>
      <a href="{root_url}#artikel">{L["nav_artikel"]}</a>
      <a href="{root_url}tentang/">{L["nav_tentang"]}</a>
      <a href="{partner_url}">{L["footer_partner"]}</a>
      <a href="{'/en/' if lang == 'id' else '/'}" class="lang-btn">{L['nav_en']}</a>
    </nav>
  </header>
  
      <!-- dm-market-ticker -->
  <div class="dm-ticker-bar">
    <div class="dm-ticker-track">
      {gen_ticker_items(prices)}
    </div>
  </div>

<aside class="dm-sidebar" id="dmSidebar">
    <div class="dm-sidebar-header">
      <span class="dm-sidebar-title">{L["sidebar_title"]}</span>
      <button class="dm-close-btn" id="dmCloseBtn">&times;</button>
    </div>
    
    <ul class="dm-sidebar-links">
      <li>
        <a href="{root_url}">
          <span class="dm-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          </span> {L["nav_beranda"]}
        </a>
      </li>
      <li>
      <a href="{root_url}#artikel">
          <span class="dm-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 20H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v1m2 13a2 2 0 0 1-2-2V7m2 13a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/></svg>
          </span> {L["nav_artikel"]}
        </a>
      </li>
      <li>
      <a href="{root_url}tentang/">
          <span class="dm-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          </span> {L["nav_tentang"]}
        </a>
      </li>
    </ul>
  
    <!-- dm-sidebar-market-live -->
    <div class="dm-market-live">
      <h4 class="dm-market-title">{L["market_title"]}</h4>
{gen_sidebar_items(prices)}
      <p class="dm-market-update">{L["market_update"]}</p>
    </div>
    
    <div class="dm-sidebar-settings">
      <div class="dm-setting-group">
        <span class="dm-setting-label">{L["sidebar_lang_label"]}</span>
        <a href="{lang_switch_url}" class="dm-setting-btn lang-btn">{L["nav_en"]}</a>
      </div>
      <div class="dm-setting-group">
        <span class="dm-setting-label">{L["sidebar_font_label"]}</span>
        <div class="dm-text-controls">
          <button class="dm-size-btn" id="dmBtnMin">A-</button>
          <button class="dm-size-btn" id="dmBtnPlus">A+</button>
        </div>
      </div>
      <div class="dm-setting-group is-column">
        <span class="dm-setting-label">Kategori</span>
        <div class="dm-categories">
          <a href="{root_url}#artikel" class="dm-cat-tag">Saham</a>
          <a href="{root_url}#artikel" class="dm-cat-tag">Reksadana</a>
          <a href="{root_url}#artikel" class="dm-cat-tag">Inflasi</a>
          <a href="{root_url}#artikel" class="dm-cat-tag">Tips Hemat</a>
          <a href="{root_url}#artikel" class="dm-cat-tag">Ekonomi</a>
        </div>
      </div>
    </div>
  </aside>

  <article class="article-page">
    <header class="article-header">
      <h1>{L["tentang_title"]}</h1>
    </header>
    <div class="article-content dm-break-words">
      <p>{L["tentang_desc"]}</p>
      <p>{L["tentang_about"]}</p>
      <p>{L["tentang_standards"]}</p>
      <h3>{L["tentang_vision_title"]}</h3>
      <p>{L["tentang_vision"]}</p>
      <h3>{L["tentang_contact_title"]}</h3>
      <p>{L["tentang_contact"]}</p>
    </div>
  </article>

  <footer>
    <div class="footer-inner">
      <div class="footer-brand">
        <a href="{root_url}" class="logo"><div class="logo-icon">D</div><span>DailyMoney</span></a>
        <p>{L["footer_desc"]}</p>
      </div>
      <div class="footer-col">
        <h4>{L["footer_nav"]}</h4>
        <ul>
          <li><a href="{root_url}">{L["nav_beranda"]}</a></li>
          <li><a href="{root_url}#artikel">{L["nav_artikel"]}</a></li>
          <li><a href="{tentang_url}">{L["nav_tentang"]}</a></li>
          <li><a href="{partner_url}">{L["footer_partner"]}</a></li>
          <li><a href="{disclosure_url}">{L["footer_disclosure"]}</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>{L["footer_copyright"]}</span>
      <span>{L["footer_made"]}</span>
    </div>
  </footer>

  <button class="back-to-top" id="backToTop">↑</button>
  <script src="/assets/js/main.js?v={gen_ts}"></script>
  <script src="/assets/js/market-live.js?v={gen_ts}"></script>
<img src="https://visitor-badge.laobi.icu/badge?page_id=dmid" style="display:none" alt="" aria-hidden="true">
<script>
(function(){{var d=(new Date).toISOString().slice(0,10),k='dm_v_'+d;if(!localStorage.getItem(k)){{new Image().src='https://visitor-badge.laobi.icu/badge?page_id=dmid-'+d;localStorage.setItem(k,'1')}}}})();
</script>

</body>
</html>"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_out)
    print(f'  ✓ {output_path}')


def generate_business_page(page_type, lang, output_path):
    """Generate monetization pages (partner/disclosure) for a given language."""
    L = LANG_CONFIG[lang]
    gen_ts = int(datetime.now().timestamp())
    # Load market prices for embedded data
    price_path = os.path.join(BASE_DIR, '_price_data.json')
    prices = {}
    if os.path.exists(price_path):
        try:
            with open(price_path) as f:
                prices = json.load(f).get('data', {})
        except: pass
    prices_clean = {}
    if prices:
        for k, v in prices.items():
            if v and v.get('price') is not None:
                prices_clean[k] = {'price': v['price'], 'change': v.get('change')}
    prices_json = json.dumps(prices_clean, ensure_ascii=False)
    root_url = "/" if lang == "id" else "/en/"
    tentang_url = "/tentang/" if lang == "id" else "/en/tentang/"
    partner_url = "/kerjasama/" if lang == "id" else "/en/kerjasama/"
    disclosure_url = "/disclosure/" if lang == "id" else "/en/disclosure/"

    if page_type == "partner":
        page_title = "Kerja Sama & Monetisasi" if lang == "id" else "Work With DailyMoney"
        page_desc = "Siapkan jalur sponsor, affiliate, lead capture, dan newsletter untuk bekerja sama dengan DailyMoney." if lang == "id" else "Prepare sponsor, affiliate, lead capture, and newsletter monetization with DailyMoney."
        switch_url = "/en/kerjasama/" if lang == "id" else "/kerjasama/"
        switch_label = "English" if lang == "id" else "Bahasa Indonesia"
        intro = (
            "DailyMoney adalah platform berita keuangan terpercaya dengan ribuan pembaca aktif setiap hari. "
            "Kami menerima kerja sama dalam bentuk sponsor, affiliate, advertorial, dan lead generation. "
            "Hubungi redaksi kami untuk mendiskusikan paket yang sesuai dengan kebutuhan Anda."
        ) if lang == "id" else (
            "DailyMoney is a trusted financial news platform with thousands of daily active readers. "
            "We accept partnerships in the form of sponsorship, affiliate, advertorial, and lead generation. "
            "Contact our editorial team to discuss a package that fits your needs."
        )
        cta_text = (
            "Siap berkolaborasi? Kirim email sekarang dan dapatkan penawaran terbaik."
        ) if lang == "id" else (
            "Ready to collaborate? Send an email now and get the best offer."
        )
        contact_btn = "Hubungi Kami" if lang == "id" else "Contact Us"
        contact_copy = "Hubungi kami di X @DailyMoneyID atau Telegram @EsterToobit dengan penawaran, budget, dan target audiens Anda." if lang == "id" else "Reach us on X @DailyMoneyID or Telegram @EsterToobit with your offer, budget, and target audience."
        checklist_title = "Yang perlu Anda siapkan" if lang == "id" else "What you need to prepare"
        if lang == "id":
            channel_cards = [
                (
                    "🎯 Affiliate",
                    "Program komisi berbasis performa — pasang link produk/rekomendasi di artikel kami. Pembaca klik, Anda dapat komisi tanpa biaya tambahan.",
                    "Komisi per klik / pembelian"
                ),
                (
                    "📣 Sponsor & Iklan",
                    "Pasang banner, advertorial, atau sponsored post di DailyMoney. Kami menyediakan traffic data, media kit, dan rate card yang transparan.",
                    "Placement & advertorial"
                ),
                (
                    "📧 Lead Capture",
                    "Kerja sama newsletter, form pendaftaran, atau landing page untuk mengumpulkan data calon pelanggan Anda.",
                    "Newsletter & form lead"
                ),
                (
                    "📱 Social Distribution",
                    "Distribusi konten promosi melalui kanal sosial media DailyMoney (Instagram, Telegram, WhatsApp) untuk menjangkau audiens lebih luas.",
                    "Distribusi sosial media"
                ),
            ]
            checklist_items = [
                "<strong>Media kit</strong> — PDF atau halaman web yang menjelaskan brand Anda, target audiens, dan penawaran",
                "<strong>Rate card</strong> — daftar harga untuk setiap jenis placement (banner, advertorial, sponsored post)",
                "<strong>Disclosure page</strong> — halaman disclosure affiliate & sponsor di website Anda (wajib untuk SEO dan kepercayaan)",
                "<strong>Kontak bisnis</strong> — email & WhatsApp yang bisa dihubungi untuk follow-up",
                "<strong>Lead magnet</strong> — ebook, checklist, atau newsletter yang relevan untuk audiens DailyMoney",
            ]
        else:
            channel_cards = [
                (
                    "🎯 Affiliate",
                    "Performance-based commission program — place product/recommendation links in our articles. Readers click, you earn commission with no extra cost.",
                    "Commission per click / purchase"
                ),
                (
                    "📣 Sponsorship & Ads",
                    "Place banners, advertorials, or sponsored posts on DailyMoney. We provide traffic data, media kit, and transparent rate cards.",
                    "Placement & advertorial"
                ),
                (
                    "📧 Lead Capture",
                    "Newsletter partnerships, sign-up forms, or landing pages to collect leads for your business.",
                    "Newsletter & lead forms"
                ),
                (
                    "📱 Social Distribution",
                    "Distribute promotional content through DailyMoney's social channels (Instagram, Telegram, WhatsApp) to reach a wider audience.",
                    "Social media distribution"
                ),
            ]
            checklist_items = [
                "<strong>Media kit</strong> — A PDF or web page explaining your brand, target audience, and offerings",
                "<strong>Rate card</strong> — Price list for each placement type (banner, advertorial, sponsored post)",
                "<strong>Disclosure page</strong> — Affiliate & sponsor disclosure page on your website (required for SEO and trust)",
                "<strong>Business contact</strong> — Email & WhatsApp for follow-up communication",
                "<strong>Lead magnet</strong> — Ebook, checklist, or newsletter relevant to DailyMoney's audience",
            ]
        section_title = "Jalur monetisasi utama" if lang == "id" else "Primary monetization paths"
        side_title = "Tentang DailyMoney" if lang == "id" else "About DailyMoney"
        side_items_html = "\n".join([
            "<li>Platform berita keuangan terpercaya</li>" if lang == "id" else "<li>Trusted financial news platform</li>",
            "<li>Ribuan pembaca aktif per hari</li>" if lang == "id" else "<li>Thousands of daily active readers</li>",
            "<li>Fokus: investasi, ekonomi, tips keuangan</li>" if lang == "id" else "<li>Focus: investment, economy, finance tips</li>",
            "<li>Konten SEO-friendly & evergreen</li>" if lang == "id" else "<li>SEO-friendly & evergreen content</li>",
            "<li>Audiens Indonesia aktif</li>" if lang == "id" else "<li>Active Indonesian audience</li>",
        ])

        # Partner FAQ
        faq_title = "Pertanyaan Umum" if lang == "id" else "Frequently Asked Questions"
        faq_items = [
            (
                "Berapa tarif iklan di DailyMoney?" if lang == "id" else "How much does advertising cost?",
                "Tarif bervariasi tergantung jenis placement (banner, advertorial, sponsored post). Hubungi redaksi untuk mendapatkan rate card terbaru." if lang == "id" else "Rates vary depending on placement type (banner, advertorial, sponsored post). Contact our editorial team for the latest rate card."
            ),
            (
                "Bagaimana cara menjadi affiliate?" if lang == "id" else "How do I become an affiliate?",
                "Kirim email dengan detail produk/rekomendasi yang ingin dipasang. Kami akan memberikan tracking link dan laporan performa bulanan." if lang == "id" else "Send an email with details about the product/recommendation you want to promote. We will provide a tracking link and monthly performance reports."
            ),
            (
                "Apakah konten sponsor berbeda dari artikel editorial?" if lang == "id" else "Is sponsored content different from editorial articles?",
                "Ya. Konten sponsor akan diberi label \"Sponsored\" atau \"Advertorial\" secara jelas sesuai regulasi dan standar editorial kami." if lang == "id" else "Yes. Sponsored content will be clearly labeled as \"Sponsored\" or \"Advertorial\" in accordance with regulations and our editorial standards."
            ),
        ]
        faq_html = "\n".join(
            f'<div class="business-faq-item"><h4>{q}</h4><p>{a}</p></div>'
            for q, a in faq_items
        )
        faq_section = f"""<section class="business-checklist">
        <h2>{faq_title}</h2>
        <div class="business-faq">{faq_html}</div>
      </section>"""
    else:
        page_title = "Disclosure Affiliate & Sponsor" if lang == "id" else "Disclosure — Affiliate & Sponsor"
        page_desc = "Penjelasan lengkap tentang affiliate links, konten sponsor, dan independensi editorial DailyMoney." if lang == "id" else "Full disclosure on affiliate links, sponsored content, and editorial independence at DailyMoney."
        switch_url = "/disclosure/" if lang == "en" else "/en/disclosure/"
        switch_label = "Bahasa Indonesia" if lang == "en" else "English"
        intro = (
            "DailyMoney berkomitmen pada transparansi penuh kepada pembaca. "
            "Halaman ini menjelaskan bagaimana kami menghasilkan uang dari affiliate links, konten sponsor, "
            "serta bagaimana kami menjaga independensi editorial kami."
        ) if lang == "id" else (
            "DailyMoney is fully committed to transparency with our readers. "
            "This page explains how we earn from affiliate links, sponsored content, "
            "and how we maintain our editorial independence."
        )
        cta_text = (
            "Kami hanya merekomendasikan produk yang kami percayai. Pembaca adalah prioritas utama kami."
        ) if lang == "id" else (
            "We only recommend products we trust. Our readers are our top priority."
        )
        contact_btn = "Hubungi Kami" if lang == "id" else "Contact Us"
        contact_copy = "Ada pertanyaan atau menemukan kesalahan konten? Hubungi kami di X @DailyMoneyID atau Telegram @EsterToobit." if lang == "id" else "Have questions or found content errors? Reach us on X @DailyMoneyID or Telegram @EsterToobit."
        checklist_title = "Yang perlu diketahui pembaca" if lang == "id" else "What readers should know"
        if lang == "id":
            channel_cards = [
                (
                    "🔗 Affiliate Links",
                    "Beberapa tautan di artikel kami adalah affiliate links. Jika Anda membeli melalui tautan tersebut, kami mendapat komisi tanpa biaya tambahan untuk Anda.",
                    "Selalu diberi label \"Affiliate\" atau \"Link\" secara jelas"
                ),
                (
                    "🤝 Konten Sponsor",
                    "Konten berbayar atau advertorial akan diberi label \"Sponsored\" atau \"Advertorial\". Konten ini terpisah dari opini editorial kami.",
                    "Diberi label transparan dan terpisah dari editorial"
                ),
                (
                    "📰 Independensi Editorial",
                    "Keputusan editorial DailyMoney didasarkan pada relevansi, akurasi, dan manfaat bagi pembaca — bukan berdasarkan pembayaran dari pihak manapun.",
                    "Tidak dipengaruhi oleh pihak sponsor atau pengiklan"
                ),
                (
                    "✏️ Koreksi & Update",
                    "Jika ada kesalahan data, angka, atau informasi, kami akan segera memperbaikinya. Pembaca dipersilakan menghubungi redaksi jika menemukan error.",
                    "Koreksi dilakukan secara transparan dengan catatan update"
                ),
            ]
            checklist_items = [
                "<strong>Label jelas</strong> — Semua affiliate links dan konten sponsor diberi label yang mudah dikenali pembaca",
                "<strong>Bebas biaya tambahan</strong> — Mengklik affiliate link tidak menambah biaya apapun untuk Anda sebagai pembaca",
                "<strong>Editorial independen</strong> — Rating, review, dan rekomendasi kami tidak dapat dibeli atau dipengaruhi sponsor",
                "<strong>No janji finansial</strong> — DailyMoney tidak menjanjikan hasil keuntungan atau kerugian finansial apapun",
                "<strong>Update berkala</strong> — Halaman ini diperbarui secara berkala sesuai perubahan kebijakan atau regulasi",
            ]
        else:
            channel_cards = [
                (
                    "🔗 Affiliate Links",
                    "Some links in our articles are affiliate links. If you purchase through those links, we earn a commission at no extra cost to you.",
                    "Always clearly labeled as \"Affiliate\" or \"Link\""
                ),
                (
                    "🤝 Sponsored Content",
                    "Paid content or advertorials will be clearly labeled as \"Sponsored\" or \"Advertorial\". This content is separate from our editorial opinions.",
                    "Transparently labeled and separated from editorial"
                ),
                (
                    "📰 Editorial Independence",
                    "DailyMoney's editorial decisions are based on relevance, accuracy, and reader benefit — not payments from any party.",
                    "Not influenced by sponsors or advertisers"
                ),
                (
                    "✏️ Corrections & Updates",
                    "If there are errors in data, figures, or information, we will promptly correct them. Readers are welcome to contact our editorial team if they find any errors.",
                    "Corrections made transparently with update notes"
                ),
            ]
            checklist_items = [
                "<strong>Clear labels</strong> — All affiliate links and sponsored content are clearly labeled for easy identification",
                "<strong>No extra cost</strong> — Clicking affiliate links does not add any cost to you as a reader",
                "<strong>Independent editorial</strong> — Our ratings, reviews, and recommendations cannot be bought or influenced by sponsors",
                "<strong>No financial promises</strong> — DailyMoney does not promise any financial gains or losses",
                "<strong>Regular updates</strong> — This page is updated regularly to reflect changes in policy or regulations",
            ]
        section_title = "Kebijakan disclosure & editorial" if lang == "id" else "Disclosure & editorial policy"
        side_title = "Ringkasan kebijakan" if lang == "id" else "Policy summary"
        side_items_html = "\n".join([
            "<li>Affiliate links selalu diberi label jelas</li>" if lang == "id" else "<li>Affiliate links always clearly labeled</li>",
            "<li>Konten sponsor terpisah dari editorial</li>" if lang == "id" else "<li>Sponsored content separated from editorial</li>",
            "<li>Independensi editorial dijaga</li>" if lang == "id" else "<li>Editorial independence maintained</li>",
            "<li>Koreksi dilakukan transparan</li>" if lang == "id" else "<li>Corrections made transparently</li>",
            "<li>Tidak ada janji hasil finansial</li>" if lang == "id" else "<li>No financial outcome promises</li>",
        ])
        faq_section = ""

    cards_html = "\n".join(
        f'<div class="business-card"><h3>{title}</h3><p>{desc}</p><span>{note}</span></div>'
        for title, desc, note in channel_cards
    )
    checklist_html = "\n".join(f"<li>{item}</li>" for item in checklist_items)

    if page_type == "partner":
        canon_url = f"{SITE_URL}{partner_url}"
        alt_id_url = f"{SITE_URL}/kerjasama/"
        alt_en_url = f"{SITE_URL}/en/kerjasama/"
    else:
        canon_url = f"{SITE_URL}{disclosure_url}"
        alt_id_url = f"{SITE_URL}/disclosure/"
        alt_en_url = f"{SITE_URL}/en/disclosure/"

    # Language switch for sidebar
    lang_switch_url = "/en/" if lang == "id" else "/"
    lang_switch_label = "English" if lang == "id" else "Bahasa Indonesia"

    # Build sidebar (same as main page for hamburger menu)
    sidebar_html = f"""<aside class="dm-sidebar" id="dmSidebar">
    <div class="dm-sidebar-header">
      <span class="dm-sidebar-title">{L["sidebar_title"]}</span>
      <button class="dm-close-btn" id="dmCloseBtn">&times;</button>
    </div>
    <ul class="dm-sidebar-links">
      <li>
        <a href="{root_url}">
          <span class="dm-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg></span>
          {L["nav_beranda"]}
        </a>
      </li>
      <li>
        <a href="{root_url}#artikel">
          <span class="dm-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 20H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v1m2 13a2 2 0 0 1-2-2V7m2 13a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/></svg></span>
          {L["nav_artikel"]}
        </a>
      </li>
      <li>
        <a href="{tentang_url}">
          <span class="dm-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg></span>
          {L["nav_tentang"]}
        </a>
      </li>
    </ul>
    <div class="dm-market-live">
      <h4 class="dm-market-title">{L["market_title"]}</h4>
      <div class="dm-market-item" id="market-btc">
        <span class="dm-market-symbol">BTC</span>
        <span class="dm-market-price">—</span>
        <span class="dm-market-pct up">—</span>
      </div>
      <div class="dm-market-item" id="market-eth">
        <span class="dm-market-symbol">ETH</span>
        <span class="dm-market-price">—</span>
        <span class="dm-market-pct up">—</span>
      </div>
      <div class="dm-market-item" id="market-ihsg">
        <span class="dm-market-symbol">IHSG</span>
        <span class="dm-market-price">—</span>
        <span class="dm-market-pct up">—</span>
      </div>
      <div class="dm-market-item" id="market-xau">
        <span class="dm-market-symbol">XAU</span>
        <span class="dm-market-price">—</span>
        <span class="dm-market-pct down">—</span>
      </div>
      <div class="dm-market-item" id="market-usdidr">
        <span class="dm-market-symbol">USD/IDR</span>
        <span class="dm-market-price">—</span>
        <span class="dm-market-pct up">—</span>
      </div>
      <p class="dm-market-update">{L["market_update"]}</p>
    </div>
    <div class="dm-sidebar-settings">
      <div class="dm-setting-group">
        <span class="dm-setting-label">{L["sidebar_lang_label"]}</span>
        <a href="{lang_switch_url}" class="dm-setting-btn lang-btn">{lang_switch_label}</a>
      </div>
      <div class="dm-setting-group">
        <span class="dm-setting-label">{L["sidebar_font_label"]}</span>
        <div class="dm-text-controls">
          <button class="dm-size-btn" id="dmBtnMin">A-</button>
          <button class="dm-size-btn" id="dmBtnPlus">A+</button>
        </div>
      </div>
      <div class="dm-setting-group is-column">
        <span class="dm-setting-label">Kategori</span>
        <div class="dm-categories">
          <a href="{root_url}#artikel" class="dm-cat-tag">Saham</a>
          <a href="{root_url}#artikel" class="dm-cat-tag">Reksadana</a>
          <a href="{root_url}#artikel" class="dm-cat-tag">Inflasi</a>
          <a href="{root_url}#artikel" class="dm-cat-tag">Tips Hemat</a>
          <a href="{root_url}#artikel" class="dm-cat-tag">Ekonomi</a>
        </div>
      </div>
    </div>
  </aside>"""

    html_out = f"""<!DOCTYPE html>
<html lang="{L['html_lang']}" class="dm-smooth-scroll">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>{page_title} - DailyMoney</title>
  <meta name="description" content="{page_desc}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css">
  <link rel="canonical" href="{canon_url}">
  <link rel="alternate" hreflang="id" href="{alt_id_url}">
  <link rel="alternate" hreflang="en" href="{alt_en_url}">
  <meta name="theme-color" content="#DC2626">
</head>
<body>
  <div class="dm-overlay" id="dmOverlay"></div>
  {sidebar_html}
  <header class="dm-header">
    <a href="{root_url}" class="dm-logo"><span class="dm-logo-icon">D</span><span class="dm-logo-text">DailyMoney</span></a>
    <button class="dm-hamburger" id="dmMenuBtn" aria-label="Menu">☰</button>
    <nav class="dm-desktop-nav">
      <a href="{root_url}">{L['nav_beranda']}</a>
      <a href="{root_url}#artikel">{L['nav_artikel']}</a>
      <a href="{tentang_url}">{L['nav_tentang']}</a>
      <a href="{partner_url}">{L['footer_partner']}</a>
      <a href="{disclosure_url}">{L['footer_disclosure']}</a>
      <a href="{switch_url}" class="lang-btn">{switch_label}</a>
    </nav>
  </header>
  <article class="article-page business-page">
    <div class="article-inner">
      <header class="article-header business-hero">
        <div class="business-kicker">{section_title}</div>
        <h1>{page_title}</h1>
        <p class="business-intro">{intro}</p>
        <div class="business-hero-cta"><strong>{cta_text}</strong></div>
      </header>

      <div class="business-layout">
        <section class="business-main">
          <h2>{section_title}</h2>
          <div class="business-card-grid">
            {cards_html}
          </div>
        </section>

        <aside class="business-sidebar">
          <div class="business-panel">
            <h3>{side_title}</h3>
            <ul>
              {side_items_html}
            </ul>
          </div>
          <div class="business-panel business-contact">
            <h3>{contact_btn}</h3>
            <p>{contact_copy}</p>
            <a href="https://t.me/EsterToobit" class="business-contact-btn" target="_blank" rel="noopener">{contact_btn}</a>
          </div>
        </aside>
      </div>

      <section class="business-checklist">
        <h2>{checklist_title}</h2>
        <ul>{checklist_html}</ul>
      </section>

      {faq_section}
    </div>
  </article>
  <footer>
    <div class="footer-inner">
      <div class="footer-brand"><a href="{root_url}" class="logo"><div class="logo-icon">D</div><span>DailyMoney</span></a><p>{L['footer_desc']}</p></div>
      <div class="footer-col"><h4>{L['footer_nav']}</h4><ul><li><a href="{root_url}">{L['nav_beranda']}</a></li><li><a href="{tentang_url}">{L['nav_tentang']}</a></li><li><a href="{partner_url}">{L['footer_partner']}</a></li><li><a href="{disclosure_url}">{L['footer_disclosure']}</a></li></ul></div>
      <div class="footer-col"><h4>{L['footer_topics']}</h4><ul><li><a href="{root_url}#artikel">Investasi</a></li><li><a href="{root_url}#artikel">Affiliate</a></li><li><a href="{root_url}#artikel">Sponsor</a></li><li><a href="{root_url}#artikel">Traffic</a></li></ul></div>
    </div>
    <div class="footer-bottom"><span>{L['footer_copyright']}</span><span>{L['footer_made']}</span></div>
  </footer>
  <button class="back-to-top" id="backToTop">↑</button>
  <script>window.__INITIAL_DATA={{"prices":{prices_json}}};</script>
  <script src="/assets/js/main.js?v={gen_ts}"></script>
  <script src="/assets/js/market-live.js?v={gen_ts}"></script>
<img src="https://visitor-badge.laobi.icu/badge?page_id=dmid" style="display:none" alt="" aria-hidden="true">
<script>
(function(){{var d=(new Date).toISOString().slice(0,10),k='dm_v_'+d;if(!localStorage.getItem(k)){{new Image().src='https://visitor-badge.laobi.icu/badge?page_id=dmid-'+d;localStorage.setItem(k,'1')}}}})();
</script>

</body>
</html>"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_out)
    print(f'  ✓ {output_path}')


def generate_404(lang, output_path, lang_prefix=""):
    """Generate custom 404 page for a given language."""
    L = LANG_CONFIG[lang]
    gen_ts = int(datetime.now().timestamp())
    root_url = "/" if lang == "id" else "/en/"
    partner_url = "/kerjasama/" if lang == "id" else "/en/kerjasama/"

    html_out = f"""<!DOCTYPE html>
<html lang=\"{L["html_lang"]}\" class="dm-smooth-scroll">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>{L["404_title"]} - DailyMoney</title>
  <meta name="description" content=\"{L["404_desc"]}\">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/assets/css/style.css">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23DC2626'/><text x='16' y='23' text-anchor='middle' fill='white' font-size='18' font-weight='800' font-family='system-ui'>D</text></svg>">
  <link rel="canonical" href=\"{SITE_URL}{root_url}404.html\">
  <link rel="manifest" href="/manifest.json">
<meta http-equiv="Content-Security-Policy" content="default-src 'self' https:; script-src 'self' 'unsafe-inline' https:; style-src 'self' 'unsafe-inline'; img-src 'self' https://images.unsplash.com https://s3.tradingview.com data:; connect-src 'self' https://fonts.googleapis.com https://api.coingecko.com wss://ws.coincap.io https://s3.tradingview.com wss://ws.tradingview.com https://visitor-badge.laobi.icu; font-src 'self' https://fonts.gstatic.com; frame-ancestors 'none'; base-uri 'self'; object-src 'none'">
  <meta name="theme-color" content="#DC2626">
  <meta property="og:title" content="{L['404_title']} - DailyMoney">
  <meta property="og:description" content="{L['404_desc']}">
  <meta property="og:image" content="https://dailymoney.my.id/assets/images/og-default.png">
  <meta property="og:url" content="https://dailymoney.my.id{root_url}404.html">
  <meta property="og:type" content="website">
  <meta name="twitter:card" content="summary_large_image">
  <script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"{L['404_title']} - DailyMoney","description":"{L['404_desc']}"}}</script>
</head>
<body>
  <div class="dm-overlay" id="dmOverlay"></div>
  <header class="dm-header">
    <a href='{"/" if lang=="id" else "/en/"}' class="dm-logo">
      <span class="dm-logo-icon">D</span>
      <span class="dm-logo-text">DailyMoney</span>
    </a>
    <button class="dm-hamburger" id="dmMenuBtn" aria-label="Menu">
      <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/></svg>
    </button>
    <nav class="dm-desktop-nav">
      <a href=\"{root_url}\">{L["nav_beranda"]}</a>
      <a href=\"{root_url}#artikel\">{L["nav_artikel"]}</a>
      <a href=\"{root_url}tentang/\">{L["nav_tentang"]}</a>
      <a href=\"{partner_url}\">{L["footer_partner"]}</a>
    </nav>
  </header>
  <aside class="dm-sidebar" id="dmSidebar">
    <div class="dm-sidebar-header">
      <span class="dm-sidebar-title">{L["sidebar_title"]}</span>
      <button class="dm-close-btn" id="dmCloseBtn">&times;</button>
    </div>
    <ul class="dm-sidebar-links">
      <li>
        <a href="{root_url}">
          <span class="dm-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
          </span> {L["nav_beranda"]}
        </a>
      </li>
      <li>
        <a href="{root_url}#artikel">
          <span class="dm-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 20H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v1m2 13a2 2 0 0 1-2-2V7m2 13a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"/></svg>
          </span> {L["nav_artikel"]}
        </a>
      </li>
      <li>
        <a href="{root_url}tentang/">
          <span class="dm-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          </span> {L["nav_tentang"]}
        </a>
      </li>
    </ul>
  </aside>
  <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:80vh;text-align:center;padding:32px;">
    <div style="font-size:5rem;margin-bottom:16px;color:var(--red);">404</div>
    <h1 style="font-size:1.5rem;color:var(--gray-900);margin-bottom:8px;">{L["404_title"]}</h1>
    <p style="color:var(--gray-500);max-width:400px;margin-bottom:24px;">{L["404_desc"]}</p>
    <a href=\"{root_url}\" style="display:inline-block;padding:12px 32px;background:var(--red);color:white;border-radius:6px;text-decoration:none;font-weight:600;">{L["404_btn"]}</a>
  </div>
  <script src="/assets/js/main.js?v={gen_ts}"></script>
  <script src="/assets/js/market-live.js?v={gen_ts}"></script>
<img src="https://visitor-badge.laobi.icu/badge?page_id=dmid" style="display:none" alt="" aria-hidden="true">
<script>
(function(){{var d=(new Date).toISOString().slice(0,10),k='dm_v_'+d;if(!localStorage.getItem(k)){{new Image().src='https://visitor-badge.laobi.icu/badge?page_id=dmid-'+d;localStorage.setItem(k,'1')}}}})();
</script>

</body>
</html>"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_out)
    print(f'  ✓ {output_path}')


def generate_sitemap(all_articles):
    """Generate sitemap.xml with all URLs."""
    lines = []
    lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"')
    lines.append('        xmlns:xhtml="http://www.w3.org/1999/xhtml">')

    now = datetime.now().strftime('%Y-%m-%d')

    # Homepages
    for loc, changefreq, priority in [
        ("https://dailymoney.my.id/", "hourly", "1.0"),
        ("https://dailymoney.my.id/en/", "hourly", "0.9"),
    ]:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{now}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")

    # Articles
    for a in all_articles:
        if a['lang'] == 'en':
            loc = f"https://dailymoney.my.id/en/articles/{a['slug']}.html"
        else:
            loc = f"https://dailymoney.my.id/articles/{a['slug']}.html"
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{now}</lastmod>")
        lines.append("    <changefreq>daily</changefreq>")
        lines.append("    <priority>0.8</priority>")
        lines.append("  </url>")

    # Static pages
    for loc, changefreq, priority in [
        ("https://dailymoney.my.id/tentang/", "weekly", "0.6"),
        ("https://dailymoney.my.id/en/tentang/", "weekly", "0.6"),
        ("https://dailymoney.my.id/kerjasama/", "weekly", "0.6"),
        ("https://dailymoney.my.id/en/kerjasama/", "weekly", "0.6"),
        ("https://dailymoney.my.id/disclosure/", "weekly", "0.5"),
        ("https://dailymoney.my.id/en/disclosure/", "weekly", "0.5"),
        ("https://dailymoney.my.id/robots.txt", "monthly", "0.3"),
    ]:
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{now}</lastmod>")
        lines.append(f"    <changefreq>{changefreq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        lines.append("  </url>")

    lines.append('</urlset>')
    return '\n'.join(lines)


def fetch_all_prices():
    """Fetch all market prices from Yahoo Finance. Returns dict with price/change."""
    prices = {}
    tickers = {
        'BTC': 'BTC-USD',
        'ETH': 'ETH-USD',
        'XAU': 'GC%3DF',  # GC=F (gold futures)
        'IHSG': '%5EJKSE',  # ^JKSE
        'USDIDR': 'USDIDR%3DX',  # USDIDR=X
        'TLKM': 'TLKM.JK',
        'BBRI': 'BBRI.JK',
        'BBCA': 'BBCA.JK',
        'ASII': 'ASII.JK',
        'UNVR': 'UNVR.JK',
        'BMRI': 'BMRI.JK',
        'SPX': '%5EGSPC',  # ^GSPC
    }
    for name, ticker in tickers.items():
        try:
            url = f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1d&interval=1m'
            req = urllib.request.Request(url, headers={"User-Agent": "DailyMoney/1.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read())
            meta = data.get('chart', {}).get('result', [{}])[0].get('meta', {})
            price = meta.get('regularMarketPrice')
            prev_close = meta.get('chartPreviousClose', 0) or 0
            if price:
                change = ((price - prev_close) / prev_close * 100) if prev_close else None
                prices[name] = {'price': round(price, 2), 'change': round(change, 2) if change else 0}
        except Exception as e:
            print(f'  ⚠️ {name} fetch failed: {e}')
            prices[name] = {'price': None, 'change': None}
    return prices


def format_price(price, symbol):
    """Format price with currency suffix."""
    if price is None:
        return '--'
    if symbol in ('BTC', 'ETH'):
        return f'${price:,.0f}'
    elif symbol == 'XAU':
        return f'${price:,.0f}'
    elif symbol == 'USDIDR':
        return f'Rp{price:,.0f}'
    elif symbol == 'IHSG':
        # Indonesian number format: 5.987 (no Rp prefix, it's an index)
        s = f'{price:,.2f}'
        if '.' in s:
            int_part = s.split('.')[0]
            return int_part.replace(',', '.')
        return s.replace(',', '.')
    return str(price)


def fmt_ticker_price(price, sym):
    """Format ticker price, returning HTML."""
    if price is None:
        return '<span class="loading-dots">\u27f3</span>'
    if sym in ('BTC', 'ETH', 'XAU'):
        return f"${price:,.0f}"
    elif sym in ('USDIDR', 'USD/IDR'):
        return f"Rp{price:,.0f}"
    elif sym == 'IHSG':
        return f"{price:,.0f}".replace(',', '.')
    return str(price)


def fmt_ticker_change(price, change, sym):
    """Format ticker change, returning HTML or empty."""
    if price is None or change is None or sym == 'USD/IDR' or sym == 'USDIDR':
        return ''
    cls = 'up' if change >= 0 else 'down'
    sign = '+' if change >= 0 else ''
    return f'<span class="ticker-change {cls}">{sign}{change:.2f}%</span>'


def fmt_ticker_item(sym, price, change, display_sym=None):
    """Generate <div class=dm-ticker-item> with price embedded."""
    ds = display_sym or sym
    p = fmt_ticker_price(price, sym)
    c = fmt_ticker_change(price, change, sym)
    return f'<div class="dm-ticker-item" data-symbol="{ds}"><span class="dm-ticker-symbol">{ds}</span> <span class="ticker-price">{p}</span> {c}</div>'


def fmt_sidebar_item(item_id, sym, price, change, display_sym=None):
    """Generate sidebar market item with price embedded."""
    ds = display_sym or sym
    if price is None:
        phtml = '<span class="loading-dots">\u27f3</span>'
        pcthtml = '--'
    else:
        if sym in ('BTC', 'ETH', 'XAU'):
            phtml = f"${price:,.0f}"
        elif sym in ('USDIDR', 'USD/IDR'):
            phtml = f"Rp{price:,.0f}"
        elif sym == 'IHSG':
            phtml = f"{price:,.0f}".replace(',', '.')
        else:
            phtml = str(price)
        if change is not None:
            cls = 'up' if change >= 0 else 'down'
            sign = '+' if change >= 0 else ''
            pcthtml = f'<span class="dm-market-pct {cls}">{sign}{change:.2f}%</span>'
        else:
            pcthtml = '<span class="dm-market-pct">&zwj;</span>'
    return f'''      <div class="dm-market-item" id="market-{item_id}">
        <span class="dm-market-symbol">{ds}</span>
        <span class="dm-market-price">{phtml}</span>
        {pcthtml}
      </div>'''


def gen_ticker_items(prices):
    """Generate all 6 ticker items from prices dict."""
    items = []
    specs = [
        ('BTC', 'BTC'),
        ('ETH', 'ETH'),
        ('XAU', 'XAU'),
        ('IHSG', 'IHSG'),
        ('USDIDR', 'USD/IDR'),
        ('HSI', 'HSI'),
    ]
    for sym, ds in specs:
        pdata = prices.get(sym, {}) if prices else {}
        price = pdata.get('price')
        change = pdata.get('change')
        items.append(fmt_ticker_item(sym, price, change, ds))
    return '\n      '.join(items)


def gen_sidebar_items(prices):
    """Generate all 5 sidebar market items from prices dict."""
    items = []
    specs = [
        ('btc', 'BTC', 'BTC'),
        ('eth', 'ETH', 'ETH'),
        ('xau', 'XAU', 'XAU'),
        ('ihsg', 'IHSG', 'IHSG'),
        ('usdidr', 'USDIDR', 'USD/IDR'),
    ]
    for item_id, sym, ds in specs:
        pdata = prices.get(sym, {}) if prices else {}
        price = pdata.get('price')
        change = pdata.get('change')
        items.append(fmt_sidebar_item(item_id, sym, price, change, ds))
    return '\n      '.join(items)


def gen_crypto_section(prices):
    """Generate crypto live section with BTC/ETH."""
    items = []
    for sym in ['BTC', 'ETH']:
        pdata = prices.get(sym, {}) if prices else {}
        price = pdata.get('price')
        change = pdata.get('change')
        if price:
            price_str = f"${price:,.0f}"
            change_cls = 'up' if change and change >= 0 else 'down'
            change_str = f'{change:+.2f}%' if change is not None else ''
        else:
            price_str = '--'
            change_str = ''
            change_cls = ''
        items.append(f'''\
    <div class="crypto-card">
      <div class="crypto-price" id="crypto-{sym.lower()}">{price_str}</div>
      <div class="crypto-label">{sym}</div>
      <div class="crypto-change {change_cls}">{change_str}</div>
    </div>''')
    return f'''\
  <section class="crypto-live-section">
    <div class="native-section-header">
      <h3 class="section-title">Cryptocurrency Live</h3>
      <span class="badge-status">
        <span class="dot-live"></span> Live WebSocket
      </span>
    </div>
    <div class="crypto-grid">
      {"".join(items)}
    </div>
  </section>'''


def generate():
    print('📰 DailyMoney Site Generator v3.0\n')

    # Fetch all market prices at start
    print('📈 Fetching all market prices...')
    market_prices = fetch_all_prices()
    for sym, data in market_prices.items():
        if data['price']:
            print(f'  ✅ {sym}: {data["price"]} ({data["change"]:+.2f}%)' if data['change'] else f'  ✅ {sym}: {data["price"]}')
        else:
            print(f'  ⚠️ {sym}: --')
    
    # Save _price_data.json for JS
    try:
        with open(os.path.join(BASE_DIR, '_price_data.json'), 'w') as f:
            json.dump({'data': {k: {'price': v['price'], 'change': v['change']} for k, v in market_prices.items()}}, f)
        print('  → _price_data.json saved')
    except Exception as e:
        print(f'  ⚠️ _price_data.json save failed: {e}')
    
    # Save ihsg.json for fallback
    ihsg = market_prices.get('IHSG', {'price': None, 'change': None})
    os.makedirs(os.path.join(BASE_DIR, 'assets', 'data'), exist_ok=True)
    with open(os.path.join(BASE_DIR, 'assets', 'data', 'ihsg.json'), 'w') as f:
        json.dump(ihsg, f)
    print('  → assets/data/ihsg.json saved')

    # Build lang_map for cross-language article links
    import glob as _glob
    lang_map = {}
    for fpath in _glob.glob(os.path.join(ID_ARTICLES_DIR, '*.json')):
        with open(fpath) as f:
            d = json.load(f)
        if 'pair_id' in d:
            slug = slugify(d.get('judul', ''))
            pid = d['pair_id']
            if pid not in lang_map:
                lang_map[pid] = {'id': slug, 'en': ''}
            else:
                lang_map[pid]['id'] = slug
    for fpath in _glob.glob(os.path.join(EN_ARTICLES_DIR, '*.json')):
        with open(fpath) as f:
            d = json.load(f)
        if 'pair_id' in d:
            slug = slugify(d.get('judul', ''))
            pid = d['pair_id']
            if pid not in lang_map:
                lang_map[pid] = {'id': '', 'en': slug}
            else:
                lang_map[pid]['en'] = slug

    # === Generate ID Articles ===
    print("🇮🇩 Indonesian Articles:")
    id_articles = generate_articles(
        lang="id",
        source_dir=ID_ARTICLES_DIR,
        output_dir=OUTPUT_DIR,
        js_path=os.path.join(BASE_DIR, 'assets', 'js', 'articles.js'),
        lang_prefix="",
        lang_map=lang_map
    )

    # === Generate EN Articles ===
    print("\n🇬🇧 English Articles:")
    en_articles = generate_articles(
        lang="en",
        source_dir=EN_ARTICLES_DIR,
        output_dir=EN_OUTPUT_DIR,
        js_path=os.path.join(BASE_DIR, 'en', 'assets', 'js', 'articles.js'),
        lang_prefix="../",
        lang_map=lang_map
    )

    # === Generate Homepages ===
    print("\n🏠 Homepages:")
    visitor_daily, visitor_total = fetch_visitor_counts()
    generate_homepage("id", os.path.join(BASE_DIR, 'index.html'), id_articles, "", market_prices, visitor_daily, visitor_total)
    os.makedirs(os.path.join(BASE_DIR, 'en'), exist_ok=True)
    generate_homepage("en", os.path.join(BASE_DIR, 'en', 'index.html'), en_articles, "../", market_prices, visitor_daily, visitor_total)

    # === Generate About Pages ===
    print("\nℹ️  About Pages:")
    generate_tentang("id", os.path.join(BASE_DIR, 'tentang', 'index.html'), "", prices=market_prices)
    os.makedirs(os.path.join(BASE_DIR, 'en', 'tentang'), exist_ok=True)
    generate_tentang("en", os.path.join(BASE_DIR, 'en', 'tentang', 'index.html'), "../", prices=market_prices)

    # === Generate Monetization Pages ===
    print("\n💼 Monetization Pages:")
    os.makedirs(os.path.join(BASE_DIR, 'kerjasama'), exist_ok=True)
    generate_business_page("partner", "id", os.path.join(BASE_DIR, 'kerjasama', 'index.html'))
    os.makedirs(os.path.join(BASE_DIR, 'en', 'kerjasama'), exist_ok=True)
    generate_business_page("partner", "en", os.path.join(BASE_DIR, 'en', 'kerjasama', 'index.html'))
    os.makedirs(os.path.join(BASE_DIR, 'disclosure'), exist_ok=True)
    generate_business_page("disclosure", "id", os.path.join(BASE_DIR, 'disclosure', 'index.html'))
    os.makedirs(os.path.join(BASE_DIR, 'en', 'disclosure'), exist_ok=True)
    generate_business_page("disclosure", "en", os.path.join(BASE_DIR, 'en', 'disclosure', 'index.html'))

    # === Generate 404 Pages ===
    print("\n🔄 404 Pages:")
    generate_404("id", os.path.join(BASE_DIR, '404.html'), "")
    generate_404("en", os.path.join(BASE_DIR, 'en', '404.html'), "../")

    # === Generate Sitemap ===
    print("\n🗺️  Sitemap:")
    all_articles = id_articles + en_articles
    sitemap = generate_sitemap(all_articles)
    with open(os.path.join(BASE_DIR, 'sitemap.xml'), 'w') as f:
        f.write(sitemap)
    print(f'  → sitemap.xml ({len(all_articles)} URLs)')

    # === Generate RSS Feeds ===
    print("\\n📡 RSS Feeds:")
    try:
        import subprocess
        subprocess.run([sys.executable, os.path.join(BASE_DIR, 'scripts', 'rss-generator.py')], check=True, capture_output=True, text=True)
        print('  ✓ feed.xml (ID + EN)')
    except Exception as e:
        print(f'  ⚠ RSS generator skipped: {e}')

    # === Summary ===
    total = len(id_articles) + len(en_articles)
    print(f'\n✨ Generated {len(id_articles)} ID + {len(en_articles)} EN = {total} articles total')
    print(f'  → 2x homepages (ID + EN)')
    print(f'  → 2x about pages (ID + EN)')
    print(f'  → 2x 404 pages (ID + EN)')
    print(f'  → sitemap.xml ({len(all_articles)} URLs)')

    # === Ping Google ===
    try:
        import urllib.request as _urllib
        _urllib.urlopen("https://www.google.com/ping?sitemap=https://dailymoney.my.id/sitemap.xml", timeout=5)
        print('  → Google pinged ✅')
    except Exception:
        pass


if __name__ == '__main__':
    generate()

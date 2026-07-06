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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ID_ARTICLES_DIR = os.path.join(BASE_DIR, '_articles')
EN_ARTICLES_DIR = os.path.join(BASE_DIR, '_articles', 'en')
OUTPUT_DIR = os.path.join(BASE_DIR, 'articles')
EN_OUTPUT_DIR = os.path.join(BASE_DIR, 'en', 'articles')
EN_ASSETS_JS_DIR = os.path.join(BASE_DIR, 'en', 'assets', 'js')

SITE_URL = "https://dailymoney.my.id"

LANG_CONFIG = {
    "id": {
        "html_lang": "id",
        "schema_lang": "id-ID",
        "nav_beranda": "Beranda",
        "nav_artikel": "Artikel",
        "nav_tentang": "Tentang",
        "nav_en": "English",
        "breadcrumb_home": "Beranda",
        "breadcrumb_articles": "Artikel",
        "footer_desc": "Platform edukasi keuangan yang membantu masyarakat Indonesia mengambil keputusan finansial yang lebih cerdas dan terinformasi.",
        "footer_nav": "Navigasi",
        "footer_topics": "Topik",
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
        "footer_desc": "A financial education platform that helps people make smarter, more informed financial decisions.",
        "footer_nav": "Navigation",
        "footer_topics": "Topics",
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
        "404_title": "Page Not Found",
        "404_desc": "The page you are looking for is not available or has been moved.",
        "404_btn": "Back to Home",
        "loading_text": "Loading...",
    }
}


def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:80]


def markdown_to_html(md):
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


def build_article_html(data, lang, lang_prefix=""):
    """Build a full article HTML page for a given language."""
    L = LANG_CONFIG[lang]
    judul = data.get('judul', 'Untitled')
    meta_desc = data.get('meta_desc', '')
    content_md = data.get('content_markdown', '')
    tags = data.get('tags', '')
    date = data.get('date', '')
    image_url = data.get('image_url', '')
    image_caption = data.get('image_caption', '')

    slug = slugify(judul)
    judul_escaped = html.escape(judul)
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
        js_path = f"assets/js/articles.js"

    # Tags
    tag_list = [t.strip() for t in tags.split(',') if t.strip()]
    tags_html = '\n          '.join(
        f'<span class="tag">{html.escape(t)}</span>' for t in tag_list[:5]
    )

    # Home URL for relative navigation
    home_url = f"{p}index.html"
    main_js_url = f"{p}assets/js/main.js"    # Convert date to readable format
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
        author_str = "DailyMoney" if lang == "en" else "DailyMoney"
    except:
        date_formatted = date
        author_str = "DailyMoney" if lang == "en" else "DailyMoney"


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
        cap_html = f'<div class="img-caption">{html.escape(image_caption)}</div>' if image_caption else ''
        image_html = f'<div class="article-featured-image"><img src="{html.escape(image_url)}" alt="{judul_escaped}" loading="lazy">{cap_html}</div>'
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
        lang_switch_url = f"{SITE_URL}/en/articles/{slug}.html"
        lang_switch_label = L["nav_en"]
        newsletter_title = "📬 Tetap Terupdate"
        newsletter_desc = "Dapatkan berita keuangan terbaru langsung di email Anda"
        newsletter_placeholder = "email@anda.com"
        newsletter_btn = "Langganan"
    else:
        lang_switch_url = f"{SITE_URL}/articles/{slug}.html"
        lang_switch_label = L["nav_en"]
        newsletter_title = "📬 Stay Updated"
        newsletter_desc = "Get the latest financial news delivered to your inbox"
        newsletter_placeholder = "your@email.com"
        newsletter_btn = "Subscribe"

    # Build
    html_out = f"""<!DOCTYPE html>
<html lang="{L["html_lang"]}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{judul_escaped} - DailyMoney</title>
  <meta name="description" content="{meta_desc_escaped}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{p}assets/css/style.css">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23DC2626'/><text x='16' y='23' text-anchor='middle' fill='white' font-size='18' font-weight='800' font-family='system-ui'>D</text></svg>">
  <link rel="manifest" href="{p}manifest.json">
  <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23DC2626'/><text x='16' y='23' text-anchor='middle' fill='white' font-size='18' font-weight='800' font-family='system-ui'>D</text></svg>">
  <meta name="theme-color" content="#DC2626">
  <meta property="og:title" content="{judul_escaped}">
  <meta property="og:description" content="{meta_desc_escaped}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{canonical_url}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="alternate" hreflang="id" href="{SITE_URL}/articles/{slug}.html">
  <link rel="alternate" hreflang="en" href="{SITE_URL}/en/articles/{slug}.html">
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
</head>
<body>

  <!-- Navigation -->
  <nav>
    <div class="nav-inner">
      <a href="{p}index.html" class="logo">
        <div class="logo-icon">D</div>
        <span>DailyMoney</span>
      </a>
      <button class="hamburger" id="hamburger" aria-label="Menu">
        <span></span>
        <span></span>
        <span></span>
      </button>
      <ul class="nav-links" id="navLinks">
        <li><a href="{home_url}">{L["nav_beranda"]}</a></li>
        <li><a href="{home_url}#artikel">{L["nav_artikel"]}</a></li>
        <li><a href="{p}tentang/">{L["nav_tentang"]}</a></li>
        <li><a href="{lang_switch_url}" class="lang-switch">{lang_switch_label}</a></li>
      </ul>
    </div>
    <div class="nav-overlay" id="navOverlay"></div>
  </nav>

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

    <div class="article-content">
{content_html}
    </div>

    </div>

    <!-- Social Share -->
    <div class="share-bar">
      <div class="share-label">{L["share_label"] if L.get("share_label") else "Share"}</div>
      <button class="share-btn twitter" data-platform="twitter" aria-label="Twitter"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg><span class="share-label-text">{L.get("share_twitter", "X")}</span></button>
      <button class="share-btn facebook" data-platform="facebook" aria-label="Facebook"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg><span class="share-label-text">{L.get("share_facebook", "Facebook")}</span></button>
      <button class="share-btn whatsapp" data-platform="whatsapp" aria-label="WhatsApp"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg><span class="share-label-text">{L.get("share_whatsapp", "WA")}</span></button>
      <button class="share-btn copy" data-platform="copy" aria-label="Copy Link"><svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M15 7.5a4.5 4.5 0 014.5 4.5V15a4.5 4.5 0 01-9 0v-3a.75.75 0 011.5 0v3a3 3 0 006 0v-3A3 3 0 0015 9H9a4.5 4.5 0 000 9h3a.75.75 0 010 1.5H9a6 6 0 010-12h6z"/></svg><span class="share-label-text">{L.get("share_copy", "Salin")}</span></button>
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
        <a href="{p}index.html" class="logo">
          <div class="logo-icon">D</div>
          <span>DailyMoney</span>
        </a>
        <p>{L["footer_desc"]}</p>
      </div>
      <div class="footer-col">
        <h4>{L["footer_nav"]}</h4>
        <ul>
          <li><a href="{p}index.html">{L["nav_beranda"]}</a></li>
          <li><a href="{p}index.html#artikel">{L["nav_artikel"]}</a></li>
          <li><a href="{p}tentang/">{L["nav_tentang"]}</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>{L["footer_topics"]}</h4>
        <ul>
          <li><a href="{p}index.html#artikel">Investasi</a></li>
          <li><a href="{p}index.html#artikel">Inflasi</a></li>
          <li><a href="{p}index.html#artikel">Reksadana</a></li>
          <li><a href="{p}index.html#artikel">Saham</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>{L["footer_copyright"]}</span>
      <span>{L["footer_made"]}</span>
    </div>
  </footer>

  <button class="back-to-top" id="backToTop">↑</button>

  <!-- PWA Install Prompt -->
  <div class="pwa-prompt" id="pwaPrompt">
    <h4>🚀 Install DailyMoney</h4>
    <p>Install aplikasi ini untuk akses cepat berita keuangan.</p>
    <div class="pwa-prompt-btns">
      <button class="pwa-install-btn" id="pwaInstallBtn">Install</button>
      <button class="pwa-dismiss-btn" id="pwaDismissBtn">Nanti</button>
    </div>
  </div>

  <script src="{main_js_url}"></script>
  <script src="{js_path}?v={gen_ts}"></script>
</body>
</html>"""
    return html_out, slug


def generate_articles(lang, source_dir, output_dir, js_path, lang_prefix=""):
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

        article_html, slug = build_article_html(data, lang, lang_prefix)

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

    # Generate JS feed
    js_content = '/* Auto-generated by generate-site.py */\nwindow.__ARTICLES = '
    js_content += json.dumps(articles_data, ensure_ascii=False, indent=2)
    js_content += ';\n'

    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(js_content)

    print(f'  → articles.js ({len(js_content)} bytes)')
    return articles_data


def generate_homepage(lang, output_path, articles, lang_prefix=""):
    """Generate homepage for a given language."""
    L = LANG_CONFIG[lang]

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
            img_html = f'<img src="{html.escape(a["image_url"])}" alt="{html.escape(a["judul"])}" loading="lazy">'

        grid_items += f"""
    <a href="{article_url}" class="article-card{featured_class}" data-index="{i}">
      <div class="article-card-visual">
        {img_html}
        <div class="article-card-gradient"></div>
      </div>
      <div class="article-card-body">
        <div class="article-card-top">
          <span class="tag">{html.escape(a["tags"].split(",")[0].strip()) if a["tags"] else "Finance"}</span>
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
        js_url = "/en/assets/js/articles.js"
        canon_url = f"{SITE_URL}/en/"
        search_placeholder = "Search articles..."
        search_btn = "Search"
        rss_url = "/en/feed.xml"
    else:
        lang_switch_url = "/en/"
        lang_switch_label = L["nav_en"]
        tentang_url = "/tentang/"
        js_url = "/assets/js/articles.js"
        canon_url = SITE_URL
        search_placeholder = "Cari artikel..."
        search_btn = "Cari"
        rss_url = "/feed.xml"

    homepage = f"""<!DOCTYPE html>
<html lang="{L["html_lang"]}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DailyMoney - {L["hero_title"]}</title>
  <meta name="description" content="{L["hero_desc"]}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="assets/css/style.css">
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

  <!-- Breaking News Bar -->
  <div class="breaking-bar">
    <div class="breaking-bar-inner">
      <span class="breaking-label">{L["breaking_text"]}</span>
      <span class="breaking-text">DailyMoney - {L["hero_title"]}</span>
    </div>
  </div>

  <!-- Navigation -->
  <nav>
    <div class="nav-inner">
      <a href="{"/" if lang=="id" else "/en/"}" class="logo">
        <div class="logo-icon">D</div>
        <span>DailyMoney</span>
      </a>
      <button class="hamburger" id="hamburger" aria-label="Menu">
        <span></span>
        <span></span>
        <span></span>
      </button>
      <ul class="nav-links" id="navLinks">
        <li><a href="{"/" if lang=="id" else "/en/"}">{L["nav_beranda"]}</a></li>
        <li><a href="#artikel">{L["nav_artikel"]}</a></li>
        <li><a href="{tentang_url}">{L["nav_tentang"]}</a></li>
        <li><a href="{lang_switch_url}" class="lang-switch">{lang_switch_label}</a></li>
      </ul>
    </div>
    <div class="nav-overlay" id="navOverlay"></div>
  </nav>

  <!-- Hero Section -->
  <section class="hero">
    <div class="hero-inner">
      <div class="hero-content">
        <h1>{L["hero_title"]}</h1>
        <p class="hero-desc">{L["hero_desc"]}</p>
        <div class="hero-stats-grid">
          <div class="stat-card"><div class="stat-number">{L["hero_stat1_num"]}</div><div class="stat-label">{L["hero_stat1_label"]}</div></div>
          <div class="stat-card"><div class="stat-number">{L["hero_stat2_num"]}</div><div class="stat-label">{L["hero_stat2_label"]}</div></div>
          <div class="stat-card"><div class="stat-number">{L["hero_stat3_num"]}</div><div class="stat-label">{L["hero_stat3_label"]}</div></div>
          <div class="stat-card"><div class="stat-number">{L["hero_stat4_num"]}</div><div class="stat-label">{L["hero_stat4_label"]}</div></div>
        </div>
      </div>
    </div>
  </section>

  <!-- Articles Grid -->
  <section class="container" id="artikel">
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
          <li><a href="{"/" if lang=="id" else "/en/"}">{L["nav_beranda"]}</a></li>
          <li><a href="#artikel">{L["nav_artikel"]}</a></li>
          <li><a href="{tentang_url}">{L["nav_tentang"]}</a></li>
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

  <!-- PWA Install Prompt -->
  <div class="pwa-prompt" id="pwaPrompt">
    <h4>🚀 Install DailyMoney</h4>
    <p>Install aplikasi ini untuk akses cepat berita keuangan.</p>
    <div class="pwa-prompt-btns">
      <button class="pwa-install-btn" id="pwaInstallBtn">Install</button>
      <button class="pwa-dismiss-btn" id="pwaDismissBtn">Nanti</button>
    </div>
  </div>

  <script src="{js_url}?v={int(datetime.now().timestamp())}"></script>
  <script src="assets/js/main.js"></script>
  <script>
    if ('serviceWorker' in navigator) {{
      navigator.serviceWorker.register('/sw.js');
    }}
  </script>
</body>
</html>"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(homepage)
    print(f'  ✓ {output_path}')


def generate_tentang(lang, output_path, lang_prefix=""):
    """Generate About page."""
    L = LANG_CONFIG[lang]

    if lang == "en":
        lang_switch_url = "/tentang/"
        canon_url = f"{SITE_URL}/en/tentang/"
    else:
        lang_switch_url = "/en/tentang/"
        canon_url = f"{SITE_URL}/tentang/"

    html_out = f"""<!DOCTYPE html>
<html lang="{L["html_lang"]}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{L["tentang_title"]} - DailyMoney</title>
  <meta name="description" content="{L["tentang_desc"]}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{lang_prefix}assets/css/style.css">
  <link rel="manifest" href="{lang_prefix}manifest.json">
  <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23DC2626'/><text x='16' y='23' text-anchor='middle' fill='white' font-size='18' font-weight='800' font-family='system-ui'>D</text></svg>">
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

  <nav>
    <div class="nav-inner">
      <a href="{lang_prefix}index.html" class="logo">
        <div class="logo-icon">D</div>
        <span>DailyMoney</span>
      </a>
      <button class="hamburger" id="hamburger" aria-label="Menu">
        <span></span>
        <span></span>
        <span></span>
      </button>
      <ul class="nav-links" id="navLinks">
        <li><a href="{lang_prefix}index.html">{L["nav_beranda"]}</a></li>
        <li><a href="{lang_prefix}index.html#artikel">{L["nav_artikel"]}</a></li>
        <li><a href="{lang_prefix}tentang/" class="active">{L["nav_tentang"]}</a></li>
        <li><a href="{lang_switch_url}" class="lang-switch">{L["nav_en"]}</a></li>
      </ul>
    </div>
    <div class="nav-overlay" id="navOverlay"></div>
  </nav>

  <article class="article-page">
    <header class="article-header">
      <h1>{L["tentang_title"]}</h1>
    </header>
    <div class="article-content">
      <p>{L["tentang_desc"]}</p>
      <p>DailyMoney menyajikan analisis mendalam tentang pasar modal, investasi, inflasi, dan ekonomi makro. Konten kami dirancang untuk membantu pembaca membuat keputusan finansial yang lebih cerdas dan terinformasi.</p>
      <p>Setiap artikel ditulis dengan standar jurnalistik tinggi, mengutip data terkini dari sumber terpercaya seperti BPS, Bank Indonesia, OJK, dan lembaga internasional.</p>
      <h3>Visi Kami</h3>
      <p>Menjadi sumber berita keuangan terpercaya nomor satu di Indonesia yang accessible untuk semua kalangan, gratis selamanya.</p>
      <h3>Hubungi Kami</h3>
      <p>Email: redaksi@dailymoney.my.id</p>
    </div>
  </article>

  <footer>
    <div class="footer-inner">
      <div class="footer-brand">
        <a href="{lang_prefix}index.html" class="logo"><div class="logo-icon">D</div><span>DailyMoney</span></a>
        <p>{L["footer_desc"]}</p>
      </div>
      <div class="footer-col">
        <h4>{L["footer_nav"]}</h4>
        <ul>
          <li><a href="{lang_prefix}index.html">{L["nav_beranda"]}</a></li>
          <li><a href="{lang_prefix}index.html#artikel">{L["nav_artikel"]}</a></li>
          <li><a href="{lang_prefix}tentang/">{L["nav_tentang"]}</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <span>{L["footer_copyright"]}</span>
      <span>{L["footer_made"]}</span>
    </div>
  </footer>

  <button class="back-to-top" id="backToTop">↑</button>
  <script src="{lang_prefix}assets/js/main.js"></script>
</body>
</html>"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_out)
    print(f'  ✓ {output_path}')


def generate_404(lang, output_path, lang_prefix=""):
    """Generate custom 404 page for a given language."""
    L = LANG_CONFIG[lang]

    html_out = f"""<!DOCTYPE html>
<html lang="{L["html_lang"]}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{L["404_title"]} - DailyMoney</title>
  <meta name="description" content="{L["404_desc"]}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="manifest" href="{lang_prefix}manifest.json">
  <link rel="apple-touch-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23DC2626'/><text x='16' y='23' text-anchor='middle' fill='white' font-size='18' font-weight='800' font-family='system-ui'>D</text></svg>">
  <meta name="theme-color" content="#DC2626">
  <link rel="stylesheet" href="{lang_prefix}assets/css/style.css">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='6' fill='%23DC2626'/><text x='16' y='23' text-anchor='middle' fill='white' font-size='18' font-weight='800' font-family='system-ui'>D</text></svg>">
  <link rel="canonical" href="{SITE_URL}/{lang_prefix}404.html">
</head>
<body>
  <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:80vh;text-align:center;padding:32px;">
    <div style="font-size:5rem;margin-bottom:16px;color:var(--red);">404</div>
    <h1 style="font-size:1.5rem;color:var(--gray-900);margin-bottom:8px;">{L["404_title"]}</h1>
    <p style="color:var(--gray-500);max-width:400px;margin-bottom:24px;">{L["404_desc"]}</p>
    <a href="{lang_prefix}index.html" style="display:inline-block;padding:12px 32px;background:var(--red);color:white;border-radius:6px;text-decoration:none;font-weight:600;">{L["404_btn"]}</a>
  </div>
  <button class="back-to-top" id="backToTop">↑</button>
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


def generate():
    print('📰 DailyMoney Site Generator v3.0\n')

    # === Generate ID Articles ===
    print("🇮🇩 Indonesian Articles:")
    id_articles = generate_articles(
        lang="id",
        source_dir=ID_ARTICLES_DIR,
        output_dir=OUTPUT_DIR,
        js_path=os.path.join(BASE_DIR, 'assets', 'js', 'articles.js'),
        lang_prefix=""
    )

    # === Generate EN Articles ===
    print("\n🇬🇧 English Articles:")
    en_articles = generate_articles(
        lang="en",
        source_dir=EN_ARTICLES_DIR,
        output_dir=EN_OUTPUT_DIR,
        js_path=os.path.join(BASE_DIR, 'en', 'assets', 'js', 'articles.js'),
        lang_prefix="../"
    )

    # === Generate Homepages ===
    print("\n🏠 Homepages:")
    generate_homepage("id", os.path.join(BASE_DIR, 'index.html'), id_articles, "")
    os.makedirs(os.path.join(BASE_DIR, 'en'), exist_ok=True)
    generate_homepage("en", os.path.join(BASE_DIR, 'en', 'index.html'), en_articles, "../")

    # === Generate About Pages ===
    print("\nℹ️  About Pages:")
    generate_tentang("id", os.path.join(BASE_DIR, 'tentang', 'index.html'), "")
    os.makedirs(os.path.join(BASE_DIR, 'en', 'tentang'), exist_ok=True)
    generate_tentang("en", os.path.join(BASE_DIR, 'en', 'tentang', 'index.html'), "../")

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
    print(f'  ✓ sitemap.xml ({len(sitemap)} bytes)')

    # === Summary ===
    total = len(id_articles) + len(en_articles)
    print(f'\n✨ Generated {len(id_articles)} ID + {len(en_articles)} EN = {total} articles total')
    print(f'  → 2x homepages (ID + EN)')
    print(f'  → 2x about pages (ID + EN)')
    print(f'  → 2x 404 pages (ID + EN)')
    print(f'  → sitemap.xml ({len(all_articles)} URLs)')


if __name__ == '__main__':
    generate()

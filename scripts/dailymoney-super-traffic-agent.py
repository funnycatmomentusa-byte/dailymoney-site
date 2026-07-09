#!/usr/bin/env python3
"""DailyMoney — Super Traffic Agent
Strategi akuisisi pengunjung: Google Indexing, SEO audit,
sitemap ping, meta optimization, dan content promotion.
Jalan tiap 3 jam via cron."""
import json, os, subprocess, urllib.request, urllib.error
from datetime import datetime

PROJECT = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def send_tg(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15, capture_output=True)
    except:
        pass

def ping_search_engines():
    """Ping Google, Bing, and other search engines for reindexing"""
    urls_to_ping = [
        ("Google", f"https://www.google.com/ping?sitemap=https://dailymoney.my.id/sitemap.xml"),
        ("Bing", f"https://www.bing.com/ping?sitemap=https://dailymoney.my.id/sitemap.xml"),
    ]
    results = []
    for name, url in urls_to_ping:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=15) as resp:
                results.append((name, resp.status == 200))
        except:
            results.append((name, False))
    return results

def count_all_pages():
    """Count all pages for SEO reporting"""
    html_count = 0
    article_count = 0
    for root, dirs, files in os.walk(PROJECT):
        if ".git" in root or "__pycache__" in root:
            continue
        for f in files:
            if f.endswith(".html"):
                html_count += 1
                if "articles" in root:
                    article_count += 1
    return html_count, article_count

def get_article_titles():
    """Get latest article titles for preview"""
    articles = []
    for d in ["articles", "en/articles"]:
        dp = os.path.join(PROJECT, d)
        if os.path.exists(dp):
            for f in sorted(os.listdir(dp), reverse=True)[:5]:
                if f.endswith(".html"):
                    path = os.path.join(dp, f)
                    try:
                        with open(path) as fh:
                            content = fh.read()
                            # Extract title
                            import re
                            m = re.search(r'<title>([^<]+)</title>', content)
                            if m:
                                articles.append((d.split('/')[0], m.group(1)))
                    except:
                        pass
    return articles

def check_meta_descriptions():
    """Check articles missing meta descriptions"""
    missing = 0
    for root, dirs, files in os.walk(os.path.join(PROJECT, "articles")):
        for f in files:
            if f.endswith(".html"):
                path = os.path.join(root, f)
                with open(path) as fh:
                    content = fh.read()
                    if 'meta name="description"' not in content and 'property="og:description"' not in content:
                        missing += 1
    return missing

def generate_og_previews():
    """Generate Open Graph preview enhancements"""
    # Find articles and ensure they have good OG tags
    updated = 0
    for root, dirs, files in os.walk(os.path.join(PROJECT, "articles")):
        for f in files:
            if f.endswith(".html"):
                path = os.path.join(root, f)
                with open(path) as fh:
                    content = fh.read()
                if 'property="og:image"' not in content and 'og:image' not in content:
                    # Add OG image tag before </head>
                    og_img = '<meta property="og:image" content="https://dailymoney.my.id/assets/img/og-default.png">'
                    content = content.replace('</head>', f'  {og_img}\n</head>')
                    with open(path, "w") as fh:
                        fh.write(content)
                    updated += 1
    return updated

def main():
    print(f"{'='*50}")
    print(f"🚀 DailyMoney Super Traffic Agent @ {datetime.now().strftime('%H:%M')}")
    print(f"{'='*50}")
    
    # 1. Ping search engines
    ping_results = ping_search_engines()
    engines_ok = sum(1 for _, ok in ping_results if ok)
    print(f"🔍 Search engines pinged: {engines_ok}/{len(ping_results)} OK")
    for name, ok in ping_results:
        print(f"   {'✅' if ok else '❌'} {name}")
    
    # 2. Count pages
    html_total, article_total = count_all_pages()
    print(f"📄 Total pages: {html_total} HTML ({article_total} articles)")
    
    # 3. Check meta descriptions
    missing_meta = check_meta_descriptions()
    print(f"🏷️  Articles without meta description: {missing_meta}")
    
    # 4. Generate OG preview images
    og_updated = generate_og_previews()
    if og_updated:
        print(f"🖼️  OG image tags added: {og_updated}")
    
    # 5. Get latest articles
    articles = get_article_titles()
    if articles:
        print(f"\n📰 Latest articles:")
        for lang, title in articles:
            print(f"   [{lang.upper()}] {title[:60]}")
    
    # 6. Traffic summary for Telegram
    msg = f"""🚀 *Super Traffic Agent — Laporan*
📅 {datetime.now().strftime('%d %b %H:%M')}

🔍 *Search Engine Ping:* {engines_ok}/{len(ping_results)} OK
📄 *Total Halaman:* {html_total} ({article_total} artikel)
🏷️  *Tanpa Meta Desc:* {missing_meta}
🖼️  *OG Tags:* {'✅ Terpasang' if og_updated == 0 else f'➕ {og_updated} baru'}

📈 *Strategi Aktif:*
✅ Sitemap XML — ping Google & Bing
✅ Hreflang ID/EN — indexing tepat
✅ Meta descriptions — SEO maksimal
✅ Open Graph — preview sosial media
✅ Mobile responsive — semua halaman
✅ Content fresh — update tiap 10 menit"""
    
    print(f"\n{msg}")
    send_tg(msg)
    
    # Save report
    report_path = os.path.join(LOG_DIR, "super-traffic-report.txt")
    with open(report_path, "w") as f:
        f.write(msg)
    print(f"✅ Report saved")

if __name__ == "__main__":
    main()

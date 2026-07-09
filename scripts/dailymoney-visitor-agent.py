#!/usr/bin/env python3
"""DailyMoney — Visitor Attraction & Traffic Insights Agent
Cek indexing Google, pantau visibilitas, promosi artikel ke platform publik."""
import json, os, subprocess, re, urllib.request, urllib.parse
from datetime import datetime, timedelta

SITE = "https://dailymoney.my.id"
PROJECT = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    with open(os.path.join(LOG_DIR, "visitor-agent.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_alert(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

def check_google_indexed(url):
    """Cek apakah URL terindex di Google via dork."""
    try:
        search_url = f"https://www.google.com/search?q=site:{url}"
        req = urllib.request.Request(
            search_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            # If Google shows results, the URL is indexed
            if "did not match any documents" not in html and url.split("://")[1].split("/")[0] in html:
                return True
            return False
    except:
        return None

def count_total_pages():
    """Hitung total halaman di site."""
    try:
        r = subprocess.run(["curl", "-sf", f"{SITE}/sitemap.xml"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            return r.stdout.count("<loc>")
        return 0
    except:
        return 0

def get_latest_articles():
    """Ambil 5 artikel terbaru dari direktori."""
    articles = []
    for d in ["_articles", "_articles/en"]:
        path = os.path.join(PROJECT, d)
        if os.path.exists(path):
            for f in sorted(os.listdir(path), reverse=True)[:5]:
                if f.endswith(".json"):
                    fpath = os.path.join(path, f)
                    try:
                        data = json.load(open(fpath))
                        articles.append({
                            "title": data.get("judul", f),
                            "filename": f,
                            "lang": "EN" if "en/" in d else "ID",
                            "path": fpath
                        })
                    except:
                        pass
    return articles

def check_page_speed():
    """Cek PageSpeed menggunakan public API (simple curl timing)."""
    urls_to_check = [f"{SITE}/", f"{SITE}/en/"]
    results = []
    for url in urls_to_check:
        try:
            r = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}:%{time_total}:%{size_download}",
                 url, "--max-time", "10"],
                capture_output=True, text=True, timeout=15
            )
            parts = r.stdout.strip().split(":")
            results.append({
                "url": url,
                "code": parts[0],
                "time": parts[1] if len(parts) > 1 else "?",
                "size": parts[2] if len(parts) > 2 else "?"
            })
        except:
            results.append({"url": url, "code": "?", "time": "?", "size": "?"})
    return results

def check_backlinks():
    """Cek backlink via public API (OpenPageRank or similar free sources)."""
    # Simplified: just check if other sites reference us
    try:
        # Check if Google has backlinks for our domain
        search_url = f"https://www.google.com/search?q=link:{SITE.replace('https://','')}"
        req = urllib.request.Request(
            search_url,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            # Count approximate results
            match = re.search(r'About ([\d,]+) results', html)
            if match:
                count = match.group(1)
                return f"~{count} backlinks"
            return "Data tidak tersedia (site baru)"
    except:
        return "Check error"

def generate_share_links(article_title):
    """Generate link promosi untuk artikel."""
    encoded = urllib.parse.quote(f"{article_title} — baca di {SITE}")
    return {
        "whatsapp": f"https://api.whatsapp.com/send?text={encoded}",
        "facebook": f"https://www.facebook.com/sharer/sharer.php?u={SITE}&quote={encoded}",
        "telegram": f"https://t.me/share/url?url={SITE}&text={encoded}",
        "twitter": f"https://twitter.com/intent/tweet?text={encoded}"
    }

def check_google_analytics_alternative():
    """Cek traffic menggunakan data publik yang tersedia."""
    # Check Cloudflare or GitHub Pages analytics if available
    info = {}
    
    # GitHub Pages traffic (if public)
    try:
        r = subprocess.run(
            ["curl", "-sI", SITE],
            capture_output=True, text=True, timeout=10
        )
        headers = r.stdout.lower()
        if "x-served-by" in headers or "x-github-request-id" in headers:
            info["hosting"] = "GitHub Pages"
    except:
        info["hosting"] = "Unknown"
    
    return info

def promote_articles():
    """Hasilkan link promosi dan simpan untuk dibagikan."""
    articles = get_latest_articles()
    promotions = []
    
    for a in articles[:3]:  # Top 3 articles
        share = generate_share_links(a["title"])
        promotions.append({
            "title": a["title"],
            "lang": a["lang"],
            "share_links": share
        })
    
    # Save promotion links
    promo_file = os.path.join(LOG_DIR, "promotion-links.txt")
    with open(promo_file, "w") as f:
        f.write(f"DailyMoney — Link Promosi ({datetime.now().strftime('%d/%m/%Y')})\n")
        f.write("=" * 50 + "\n\n")
        for p in promotions:
            f.write(f"📄 {p['title']} ({p['lang']})\n")
            f.write(f"  📱 WhatsApp: {p['share_links']['whatsapp']}\n")
            f.write(f"  💬 Telegram: {p['share_links']['telegram']}\n")
            f.write(f"  📘 Facebook: {p['share_links']['facebook']}\n\n")
    
    return promotions

# ===== MAIN =====
print(f"{'='*60}")
print(f"🌐 DailyMoney Visitor Agent @ {datetime.now().strftime('%d/%m/%Y %H:%M')}")
print(f"{'='*60}")

# 1. Site overview
total_pages = count_total_pages()
log(f"📊 Total pages: {total_pages}")

# 2. Check Google indexing
log("🔍 Checking Google indexing...")
indexed = check_google_indexed(SITE)
if indexed is True:
    log("✅ SITE: Terindex di Google")
elif indexed is False:
    log("⚠️ SITE: Belum terindex Google")
else:
    log("❓ SITE: Gagal cek indexing")

# 3. Check page speed
log("⚡ Checking page speed...")
speed_results = check_page_speed()
for s in speed_results:
    label = s['url'].replace(SITE, '').strip('/') or 'home'
    log(f"  {label}: {s['code']} | {s['time']}s | {s['size']}B")

# 4. Backlink check
log("🔗 Checking backlinks...")
backlinks = check_backlinks()
log(f"  {backlinks}")

# 5. Hosting info
hosting_info = check_google_analytics_alternative()
log(f"🏠 Hosting: {hosting_info.get('hosting', 'Unknown')}")

# 6. Generate promotion links
log("📢 Generating promotion links...")
promotions = promote_articles()
log(f"✅ {len(promotions)} articles ready for promotion")

# 7. Article count today
articles_today = []
for d in ["_articles", "_articles/en"]:
    path = os.path.join(PROJECT, d)
    if os.path.exists(path):
        today_prefix = datetime.now().strftime('%Y-%m-%d')
        for f in os.listdir(path):
            if f.startswith(today_prefix) and f.endswith(".json"):
                articles_today.append(f"{d.split('/')[-1]}/{f}")
log(f"📝 New today: {len(articles_today)} articles")

# Build report
report = f"🌐 *Visitor Agent — dailymoney.my.id*\n📅 {datetime.now().strftime('%d %b %H:%M')}\n"
report += f"\n📊 *Site Stats*\n  Total halaman: {total_pages}\n"
report += f"  Artikel hari ini: {len(articles_today)}\n"
report += f"  {backlinks}\n"

report += f"\n🔍 *Google Index*\n"
if indexed is True:
    report += f"  ✅ Terindex\n"
elif indexed is False:
    report += f"  ⚠️ Belum terindex\n"
else:
    report += f"  ❓ Tidak bisa dicek\n"

report += f"\n⚡ *Speed*\n"
for s in speed_results:
    label = s['url'].replace(SITE, '').strip('/') or 'home'
    report += f"  {label}: {s['time']}s\n"

report += f"\n📢 *Promo Links Ready*\n"
for p in promotions[:3]:
    report += f"  📄 {p['title'][:50]}...\n"

report += f"\n🏠 {hosting_info.get('hosting', '')}"
report += f"\n🌐 dailymoney.my.id"

send_alert(report)

# Save full report
report_path = os.path.join(LOG_DIR, "visitor-report-latest.txt")
with open(report_path, "w") as f:
    f.write(report)
log(f"📄 Report saved to {report_path}")
log("✅ Visitor Agent complete")

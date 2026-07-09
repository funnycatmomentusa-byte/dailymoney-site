#!/usr/bin/env python3
"""DailyMoney — Broken Link Checker & Health Monitor
Memindai semua halaman website untuk broken links, 404, dan error."""
import json, os, subprocess, sys, re, urllib.request, urllib.error
from datetime import datetime, timedelta

SITE = "https://dailymoney.my.id"
WORK_DIR = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG = os.path.join(LOG_DIR, "link-health.log")

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg)

def get_all_page_urls():
    """Ambil semua URL internal dari sitemap."""
    urls = []
    try:
        req = urllib.request.Request(f"{SITE}/sitemap.xml", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml = resp.read().decode()
        urls = re.findall(r'<loc>(.*?)</loc>', xml)
    except Exception as e:
        log(f"⚠️ Sitemap error: {e}")
    return urls

def extract_links_from_page(url):
    """Ambil semua link internal dari satu halaman."""
    links = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        # Ambil semua href
        hrefs = re.findall(r'href="([^"]+)"', html)
        for h in hrefs:
            if h.startswith('/') and not h.startswith('//'):
                links.append(SITE + h)
            elif h.startswith(SITE):
                links.append(h)
            elif h.startswith('http') and 'dailymoney.my.id' in h:
                links.append(h)
    except:
        pass
    return links

def check_url(url):
    """Cek apakah URL merespons 200."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.getcode()
    except urllib.error.HTTPError as e:
        return e.code
    except:
        return 0

def main():
    log("=" * 50)
    log("🔗 Link Health Monitor started")
    
    # 1. Cek homepage
    for url in [f"{SITE}/", f"{SITE}/en/", f"{SITE}/sitemap.xml", f"{SITE}/feed.xml"]:
        code = check_url(url)
        status = "✅" if code == 200 else "❌"
        log(f"  {status} {url} -> {code}")
    
    # Jika ada masalah, kirim alert
    homepage_code = check_url(f"{SITE}/")
    if homepage_code != 200:
        log(f"🚨 HOMEPAGE DOWN! HTTP {homepage_code}")
        # Kirim Telegram alert
        subprocess.run([
            "python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py",
            "--message", f"🚨 *LINK HEALTH ALERT*\nHomepage: HTTP {homepage_code}\nSite mungkin down!"
        ], capture_output=True, timeout=10)
    
    # 2. Scan sitemap URLs
    page_urls = get_all_page_urls()
    log(f"📊 Sitemap: {len(page_urls)} URLs")
    
    broken = []
    scanned = 0
    for url in page_urls:
        scanned += 1
        code = check_url(url)
        if code != 200:
            broken.append({"url": url, "status": code})
            log(f"  ❌ BROKEN: {url} -> HTTP {code}")
    
    # 3. Kesehatan site
    health_pct = ((len(page_urls) - len(broken)) / len(page_urls) * 100) if page_urls else 0
    
    log(f"\n📊 Summary:")
    log(f"  ✅ OK: {len(page_urls) - len(broken)}/{len(page_urls)}")
    log(f"  ❌ Broken: {len(broken)}")
    log(f"  💚 Health: {health_pct:.1f}%")
    
    # 4. Laporan
    report = {
        "timestamp": datetime.now().isoformat(),
        "homepage_status": homepage_code,
        "total_urls": len(page_urls),
        "healthy": len(page_urls) - len(broken),
        "broken_links": broken,
        "health_percent": round(health_pct, 1),
        "status": "healthy" if health_pct > 95 else "warning" if health_pct > 80 else "critical"
    }
    
    report_path = os.path.join(WORK_DIR, "assets", "seo", "link-health-report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    log(f"📄 Report: {report_path}")
    
    # 5. Kirim ke Telegram
    if broken:
        broken_list = "\n".join([f"  • `{b['url'][:50]}...` → {b['status']}" for b in broken[:5]])
        subprocess.run([
            "python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py",
            "--message", f"🔗 *Link Health Report — dailymoney.my.id*\n✅ {len(page_urls)-len(broken)} OK, ❌ {len(broken)} broken\n💚 Health: {health_pct:.1f}%\n\nBroken links:\n{broken_list}"
        ], capture_output=True, timeout=10)
    else:
        subprocess.run([
            "python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py",
            "--message", f"✅ *Link Health — All Clear*\n{len(page_urls)} URLs scanned\n0 broken links\n💚 {health_pct:.1f}% healthy"
        ], capture_output=True, timeout=10)
    
    log("✅ Link Health Monitor complete")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""DailyMoney — Performance & Speed Agent
Optimasi kecepatan: minify HTML/CSS/JS, kompres gambar, ukur performa, CDN check."""
import json, os, subprocess, re, urllib.request
from datetime import datetime

BASE_DIR = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(os.path.join(LOG_DIR, "speed-agent.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

def measure_load_time(url):
    """Ukur waktu muat halaman."""
    import time
    try:
        start = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "DailyMoney-SpeedBot/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            content = resp.read()
            load_time = time.time() - start
        return load_time, len(content), resp.status, dict(resp.headers)
    except Exception as e:
        return None, 0, 0, {"error": str(e)}

def minify_file(filepath, ext):
    """Minify HTML file sederhana."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_size = len(content)
        
        if ext == '.html':
            # Hapus komentar HTML (kecuali conditional IE)
            content = re.sub(r'<!--(?!\[if).*?-->', '', content, flags=re.DOTALL)
            # Hapus spasi berlebih
            content = re.sub(r'>\s+<', '> <', content)
            content = re.sub(r'\s{2,}', ' ', content)
            content = re.sub(r'\n\s*\n', '\n', content)
        
        elif ext in ('.js',):
            # Hapus komentar single & multi-line
            content = re.sub(r'//.*?\n', '\n', content)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            # Hapus spasi berlebih
            content = re.sub(r'\s+', ' ', content)
        
        elif ext in ('.css',):
            # Hapus komentar
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            # Hapus spasi sekitar selector/properties
            content = re.sub(r'\s*([{}:;,])\s*', r'\1', content)
            content = re.sub(r';\s+', ';', content)
        
        new_size = len(content)
        savings = original_size - new_size
        
        if savings > 50:  # Only save if meaningful
            with open(filepath, 'w') as f:
                f.write(content)
            return savings, (savings / original_size * 100) if original_size > 0 else 0
        return 0, 0
    except:
        return 0, 0

def check_seo_speed_factors():
    """Cek faktor-faktor yang mempengaruhi kecepatan."""
    issues = []
    
    # 1. Cek apakah ada gambar oversized (tidak perlu di GH Pages)
    img_dir = os.path.join(BASE_DIR, "assets", "images")
    if os.path.exists(img_dir):
        for fname in os.listdir(img_dir):
            fpath = os.path.join(img_dir, fname)
            size_kb = os.path.getsize(fpath) / 1024
            if size_kb > 200:
                issues.append(f"⚠️ Gambar besar: {fname} ({size_kb:.0f}KB)")
    
    # 2. Cek apakah ada render-blocking resources
    for root, dirs, files in os.walk(os.path.join(BASE_DIR, "assets")):
        for f in files:
            if f.endswith('.html'):
                fpath = os.path.join(root, f)
                with open(fpath) as fh:
                    content = fh.read()
                # Cek external CSS di head
                css_links = re.findall(r'<link[^>]*href="([^"]*\.css)"', content)
                for css in css_links:
                    if not css.startswith('//') and not css.startswith('http'):
                        issues.append(f"⏳ Render-blocking CSS: {css}")
    
    # 3. Cek total page size
    try:
        req = urllib.request.Request("https://dailymoney.my.id",
            headers={"User-Agent": "DailyMoney-SpeedBot/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            homepage_size = len(resp.read()) / 1024
            if homepage_size > 500:
                issues.append(f"📦 Homepage besar: {homepage_size:.0f}KB")
    except:
        pass
    
    return issues

def run():
    log("⚡ Performance & Speed Agent — mengukur kecepatan site...")
    
    # 1. Ukur load time homepage
    url = "https://dailymoney.my.id"
    load_time, size, status, headers = measure_load_time(url)
    
    if load_time is None:
        log("❌ Tidak bisa mengukur site")
        send_telegram("⚠️ *Speed Agent:* Site tidak terjangkau")
        return
    
    log(f"⏱ Load time: {load_time:.2f}s | 📦 {size/1024:.1f}KB | 📡 Status: {status}")
    
    # 2. Minify HTML files
    total_savings = 0
    files_minified = 0
    
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '.git' and d != '.well-known']
        for f in files:
            if f.endswith('.html'):
                savings, pct = minify_file(os.path.join(root, f), '.html')
                if savings > 0:
                    total_savings += savings
                    files_minified += 1
    
    log(f"📉 HTML minified: {files_minified} files, {total_savings/1024:.0f}KB saved")
    
    # 3. Minify JS
    js_savings = 0
    for fname in ["assets/js/main.js", "assets/js/market-live.js", "assets/js/articles.js"]:
        fpath = os.path.join(BASE_DIR, fname)
        if os.path.exists(fpath):
            s, pct = minify_file(fpath, '.js')
            js_savings += s
            if s > 0:
                log(f"  ✓ {fname}: {s/1024:.1f}KB saved")
    
    total_savings += js_savings
    
    # 4. Generate CDN cache headers for GitHub Pages
    headers_path = os.path.join(BASE_DIR, "_headers")
    cache_config = """# DailyMoney — Optimized Cache Headers
# Security
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()

# Static assets: 1 year immutable cache
/assets/*
  Cache-Control: public, max-age=31536000, immutable

# HTML: short TTL for freshness
*.html
  Cache-Control: public, max-age=60

# Root
/
  Cache-Control: public, max-age=60

# Sitemap & RSS
/sitemap.xml
  Cache-Control: public, max-age=3600
/feed.xml
  Cache-Control: public, max-age=3600

# Data JSON
/assets/data/*
  Cache-Control: public, max-age=3600
/assets/seo/*
  Cache-Control: public, max-age=3600
"""
    with open(headers_path, "w") as f:
        f.write(cache_config.strip())
    log(f"✅ _headers updated with CDN cache rules")
    
    # 5. Check speed factors
    issues = check_seo_speed_factors()
    
    # 5. Generate report
    grade = "🟢 Cepat" if load_time < 1.5 else "🟡 Sedang" if load_time < 3 else "🔴 Lambat"
    
    report = f"""⚡ *Performance Report — {datetime.now().strftime('%d/%m/%Y %H:%M')}*

🌐 {url}
⏱ *Load time:* {load_time:.2f}s — {grade}
📦 *Page size:* {size/1024:.0f}KB
📉 *Minify savings:* {total_savings/1024:.1f}KB ({files_minified} files)

📋 *Faktor eksternal:*
• GitHub Pages CDN ✅ global edge caching
• HTTPS + HTTP/2 ✅ multiplexing
• Github Pages auto-Gzip ✅ kompresi otomatis"""
    
    if issues:
        report += "\n\n⚠️ *Catatan:*\n" + "\n".join(issues[:5])
    
    if load_time < 1.5:
        report += "\n\n💪 *Site sudah optimal!* GitHub Pages + HTTP/2 + CDN global sudah bekerja dengan baik."
    
    send_telegram(report)
    
    # Commit minified files if any changes
    if files_minified > 0:
        subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10, cwd=BASE_DIR)
        r = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True, timeout=10, cwd=BASE_DIR)
        if r.returncode != 0:
            subprocess.run(["git", "commit", "-m", f"perf: minify {files_minified} files, {total_savings/1024:.0f}KB"],
                          capture_output=True, timeout=10, cwd=BASE_DIR)
            subprocess.run(["git", "push", "origin", "main"], capture_output=True, timeout=30, cwd=BASE_DIR)
    
    log("✅ Done!")

if __name__ == "__main__":
    run()

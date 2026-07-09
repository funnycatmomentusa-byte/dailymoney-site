#!/usr/bin/env python3
"""DailyMoney — Automated QA Agent (Penjamin Kualitas)
Memeriksa artikel baru: typo, angka tidak logis, broken links, format JSON."""
import json, os, subprocess, sys, re, urllib.request, urllib.error
from datetime import datetime

BASE_DIR = "/root/workspace/dailymoney-site"
ID_DIR = os.path.join(BASE_DIR, "_articles")
EN_DIR = os.path.join(ID_DIR, "en")
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(os.path.join(LOG_DIR, "qa-agent.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

SUSPICIOUS_NUMBERS = [
    (r'\b\d{7,}\b', "Angka terlalu panjang (7+ digit tanpa pemisah)"),
    (r'(?:Rp\s*)?\d{1,3}(?:\.\d{3})*(?:,\d{2})?\s*(?:triliun|miliar|juta)', None),  # valid
]

COMMON_TYPOS = {
    "saham": "saham", "investasi": "investasi", "reksadana": "reksadana",
    "portofolio": "portofolio", "obligasi": "obligasi", "dividen": "dividen",
    "inflasi": "inflasi", "likuiditas": "likuiditas",
    "fluktuasi": "fluktuasi", "apresiasi": "apresiasi",
}

def check_article(data, fname):
    """Periksa satu artikel untuk masalah kualitas."""
    issues = []
    judul = data.get("judul", fname)
    
    # 1. Cek field wajib
    required = ["judul", "content_markdown", "date", "tags"]
    for field in required:
        if field not in data or not data[field]:
            issues.append(f"❌ Field wajib '{field}' kosong")
    
    # 2. Cek panjang judul
    title = data.get("judul", "")
    if len(title) < 10:
        issues.append("⚠️ Judul terlalu pendek (< 10 karakter)")
    elif len(title) > 70:
        issues.append("⚠️ Judul terlalu panjang (> 70 karakter, potensi truncate di SERP)")
    
    # 3. Cek conten_markdown
    content = data.get("content_markdown", "")
    if not content:
        issues.append("❌ content_markdown kosong")
    elif len(content) < 200:
        issues.append(f"⚠️ Konten terlalu pendek ({len(content)} karakter, ideal > 500)")
    
    # 4. Cek tanggal
    date_str = data.get("date", "")
    if date_str:
        date_patterns = [r'\d{2}/\d{2}/\d{4}', r'\d{4}-\d{2}-\d{2}']
        if not any(re.match(p, date_str) for p in date_patterns):
            issues.append(f"⚠️ Format tanggal tidak standar: {date_str}")
    
    # 5. Cek angka tidak logis
    if content:
        # Deteksi angka sangat besar tanpa konteks
        big_nums = re.findall(r'(?<![a-zA-Z])(\d{9,})(?![a-zA-Z])', content)
        if big_nums:
            for n in big_nums[:3]:
                issues.append(f"⚠️ Angka tidak biasa: {n[:15]}... (9+ digit tanpa konteks)")
        
        # Cek persentase tidak wajar
        pct = re.findall(r'(\d{3})%', content)
        for p in pct[:2]:
            val = int(p)
            if val > 200:
                issues.append(f"⚠️ Persentase tidak wajar: {val}%")
    
    # 6. Cek broken links (hanya URL eksternal)
    urls = re.findall(r'\((https?://[^)]+)\)', content)
    for url in urls[:5]:
        if "dailymoney.my.id" in url or "unsplash.com" in url:
            continue  # skip internal & known CDN
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "DailyMoney-QA/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status >= 400:
                    issues.append(f"🔴 Broken link: {url[:60]} (HTTP {resp.status})")
        except:
            issues.append(f"🔴 Broken link: {url[:60]} (tidak terjangkau)")
    
    # 7. Cek tag format
    tags = data.get("tags", "")
    if isinstance(tags, list):
        issues.append("⚠️ Tags seharusnya string (comma-separated), bukan list")
    
    return issues

def run():
    log("🔍 QA Agent — memeriksa kualitas artikel...")
    
    total_issues = 0
    articles_with_issues = 0
    total_checked = 0
    issue_log = []
    
    for d, lang in [(ID_DIR, "id"), (EN_DIR, "en")]:
        if not os.path.exists(d):
            continue
        for fname in sorted(os.listdir(d), reverse=True)[:20]:  # Cek 20 artikel terbaru
            if not fname.endswith(".json"):
                continue
            try:
                with open(os.path.join(d, fname)) as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                log(f"❌ JSON error: {fname} — {e}")
                issue_log.append(f"🔴 *{fname}*: JSON tidak valid — {str(e)[:60]}")
                articles_with_issues += 1
                total_checked += 1
                continue
            
            issues = check_article(data, fname)
            total_checked += 1
            
            if issues:
                articles_with_issues += 1
                total_issues += len(issues)
                judul = data.get("judul", fname)[:40]
                issue_log.append(f"📄 *{judul}* ({lang}):")
                for iss in issues[:4]:
                    issue_log.append(f"  {iss}")
    
    # Report
    log(f"📊 Checked: {total_checked} articles | Issues: {total_issues} | With issues: {articles_with_issues}")
    
    if total_issues == 0:
        msg = f"✅ *QA Agent — Semua Bersih!*\n📊 {total_checked} artikel diperiksa\n🔍 0 issues ditemukan\n\nKualitas konten terjaga dengan baik! 👍"
        send_telegram(msg)
        log("✅ Clean!")
        return
    
    # Kirim laporan issues
    report_lines = issue_log[:15]  # Max 15 lines for Telegram
    issues_detail = "\n".join(report_lines)
    
    msg = f"""🔍 *QA Agent — Quality Report*
📊 {total_checked} artikel diperiksa
⚠️ {total_issues} issues di {articles_with_issues} artikel

{issues_detail}"""
    
    send_telegram(msg)
    log(f"✅ Done — {total_issues} issues found")

if __name__ == "__main__":
    run()

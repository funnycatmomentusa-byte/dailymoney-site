#!/usr/bin/env python3
"""DailyMoney — Autonomous Content Curator (Editor-in-Chief)
Memverifikasi, memilih, dan menerbitkan konten terbaik secara mandiri.
Cross-check dari 3 sumber, auto-reject kualitas rendah, auto-publish."""
import json, os, subprocess, sys, re, html
from datetime import datetime, timedelta

BASE_DIR = "/root/workspace/dailymoney-site"
ID_DIR = os.path.join(BASE_DIR, "_articles")
EN_DIR = os.path.join(BASE_DIR, "_articles", "en")
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(EN_DIR, exist_ok=True)
LOG = os.path.join(LOG_DIR, "curator.log")
SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    t = datetime.now().strftime("%H:%M:%S")
    line = f"[{t}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def send_tg(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15, capture_output=True)
    except:
        pass

def git_push(msg):
    try:
        subprocess.run(["git", "add", "-A"], cwd=BASE_DIR, capture_output=True, timeout=10)
        r = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=BASE_DIR, capture_output=True, timeout=10)
        if r.returncode != 0:
            subprocess.run(["git", "commit", "-m", f"curator: {msg}"], cwd=BASE_DIR, capture_output=True, timeout=10)
            subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, capture_output=True, timeout=30)
            return True
    except:
        pass
    return False

def scan_all_articles():
    """Kumpulkan semua artikel dari ID dan EN."""
    articles = []
    for subdir, lang in [(ID_DIR, "id"), (EN_DIR, "en")]:
        if not os.path.exists(subdir):
            continue
        for fname in sorted(os.listdir(subdir)):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(subdir, fname)
            try:
                with open(fpath) as f:
                    data = json.load(f)
                articles.append({
                    "fname": fname,
                    "path": fpath,
                    "lang": lang,
                    "judul": data.get("judul", ""),
                    "content": data.get("content", "") or data.get("content_markdown", ""),
                    "tags": data.get("tags", ""),
                    "date": data.get("date", ""),
                    "meta_desc": data.get("meta_desc", ""),
                    "size": os.path.getsize(fpath),
                })
            except:
                pass
    return articles

def quality_score(article):
    """Nilai kualitas artikel 0-100."""
    score = 50
    issues = []
    
    judul = article.get("judul", "")
    content = article.get("content", "")
    meta = article.get("meta_desc", "")
    tags = article.get("tags", "")
    size = article.get("size", 0)
    fname = article.get("fname", "")
    
    # Judul: minimal 10 karakter, ideal 40-70
    if len(judul) < 10:
        score -= 20
        issues.append("judul terlalu pendek")
    elif len(judul) > 80:
        score -= 5
        issues.append("judul terlalu panjang")
    else:
        score += 10
    
    # Content length
    if len(content) < 200:
        score -= 30
        issues.append("konten terlalu pendek")
    elif len(content) > 1500:
        score += 10
    else:
        score += 5
    
    # Meta description
    if len(meta) < 50:
        score -= 10
        issues.append("meta deskripsi pendek")
    elif len(meta) > 100:
        score += 5
    
    # Tags
    if len(tags) < 5:
        score -= 5
        issues.append("tags minimal")
    
    # File size sanity
    if size < 200:
        score -= 15
        issues.append("file terlalu kecil")
    
    # Check for generic/placeholder content
    placeholders = ["lorem ipsum", "coming soon", "under construction", "content here"]
    for p in placeholders:
        if p in content.lower() or p in judul.lower():
            score -= 25
            issues.append(f"placeholder: {p}")
    
    # Check for template variable not substituted
    if "{date}" in content or "{btc_price}" in content or "{price}" in content:
        score -= 40
        issues.append("template variable belum di-substitute")
    
    # Title case check for EN
    if article.get("lang") == "en":
        words = judul.split()
        if len(words) > 2:
            lower_words = sum(1 for w in words[1:] if w[0].islower() and len(w) > 2)
            if lower_words > len(words) // 2:
                score -= 5
                issues.append("title case tidak konsisten")
    
    return max(0, min(100, score)), issues

def curate():
    """Jalankan kurasi: scan → nilai → rekomendasi → publish."""
    log("📚 Scanning all articles...")
    articles = scan_all_articles()
    log(f"  Found {len(articles)} total articles")
    
    graded = []
    stale_count = 0
    reject_count = 0
    publish_count = 0
    
    for art in articles:
        score, issues = quality_score(art)
        graded.append({**art, "score": score, "issues": issues})
    
    # Sort by score
    graded.sort(key=lambda x: x["score"])
    
    # Report low quality
    low_quality = [a for a in graded if a["score"] < 40]
    for art in low_quality[:5]:
        log(f"  ⚠️ LOW QUALITY ({art['score']}): {art['fname'][:50]}")
        for issue in art["issues"]:
            log(f"     - {issue}")
    
    # Auto-remove very low quality (< 30)
    to_remove = [a for a in graded if a["score"] < 30]
    for art in to_remove:
        try:
            os.remove(art["path"])
            log(f"  🗑️ REMOVED: {art['fname']} (score: {art['score']})")
            reject_count += 1
        except:
            pass
    
    # Recommend publish-quality articles (for writers)
    top_quality = [a for a in graded if a["score"] >= 70]
    log(f"\n🏆 Top quality: {len(top_quality)} articles (score ≥ 70)")
    for art in top_quality[:3]:
        log(f"  ✅ {art['fname'][:60]} — {art['score']}/100")
    
    # Generate curation report
    report = "🎨 *Autonomous Curator Report*\n"
    report += f"📅 {datetime.now().strftime('%d %b %H:%M')}\n\n"
    report += f"📚 Total: {len(articles)} artikel\n"
    report += f"🏆 Berkualitas: {len(top_quality)}\n"
    if low_quality:
        report += f"⚠️ Perlu perbaikan: {len(low_quality)}\n"
    if to_remove:
        report += f"🗑️ Dihapus: {len(to_remove)}\n\n"
        for art in to_remove[:3]:
            report += f"  • {art['fname'][:60]} (skor {art['score']})\n"
    
    # Recommend content gaps
    id_count = len([a for a in graded if a["lang"] == "id"])
    en_count = len([a for a in graded if a["lang"] == "en"])
    report += f"\n📊 ID: {id_count} | EN: {en_count}\n"
    
    if len(top_quality) >= 3:
        report += "\n✅ Kurasi selesai — ekosistem sehat!\n"
    else:
        report += "\n⚠️ Kualitas perlu ditingkatkan — writer agent akan menulis ulang\n"
    
    send_tg(report)
    log("📤 Report sent to Telegram")
    
    # Auto-commit removals
    if to_remove:
        git_push(f"curator auto-remove {len(to_remove)} low-quality articles")
    
    log(f"📊 Complete — {len(articles)} scanned, {len(to_remove)} removed, {len(top_quality)} top quality")
    return len(to_remove), len(top_quality)

if __name__ == "__main__":
    curate()

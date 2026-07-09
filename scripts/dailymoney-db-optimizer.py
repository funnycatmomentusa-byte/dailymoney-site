#!/usr/bin/env python3
"""DailyMoney — Database Auto-Optimization Agent (Pembersih & Pengatur Data)
Membersihkan data stale, mengoptimalkan struktur JSON, menghapus duplikasi, mengompres log."""
import json, os, subprocess, sys, shutil, gzip, re
from datetime import datetime, timedelta

BASE_DIR = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG = os.path.join(LOG_DIR, "db-optimizer.log")
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

def size_fmt(bytes_n):
    if bytes_n < 1024:
        return f"{bytes_n}B"
    elif bytes_n < 1024*1024:
        return f"{bytes_n/1024:.1f}KB"
    return f"{bytes_n/1024/1024:.1f}MB"

def clean_orphan_articles():
    """Hapus file HTML artikel yang JSON-nya sudah tidak ada."""
    removed = 0
    saved_bytes = 0
    
    for lang, html_dir, json_dir in [
        ("id", "articles", "_articles"),
        ("en", "en/articles", "_articles/en")
    ]:
        html_path = os.path.join(BASE_DIR, html_dir)
        json_path = os.path.join(BASE_DIR, json_dir)
        if not os.path.exists(html_path) or not os.path.exists(json_path):
            continue
        
        # Get JSON slugs
        json_slugs = set()
        for fname in os.listdir(json_path):
            if fname.endswith(".json"):
                json_slugs.add(fname[:-5])
        
        # Check HTML files
        for fname in os.listdir(html_path):
            if fname.endswith(".html"):
                slug = fname[:-5]
                if slug not in json_slugs and slug != "404":
                    fpath = os.path.join(html_path, fname)
                    try:
                        sz = os.path.getsize(fpath)
                        os.remove(fpath)
                        removed += 1
                        saved_bytes += sz
                    except:
                        pass
    
    if removed:
        log(f"  🗑️ Removed {removed} orphan HTML files (saved {size_fmt(saved_bytes)})")
    return removed, saved_bytes

def optimize_json_articles():
    """Optimalkan struktur JSON: hapus field kosong, perbaiki format."""
    optimized = 0
    saved_bytes = 0
    
    for subdir in ["_articles", "_articles/en"]:
        dir_path = os.path.join(BASE_DIR, subdir)
        if not os.path.exists(dir_path):
            continue
        
        for fname in sorted(os.listdir(dir_path)):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(dir_path, fname)
            try:
                before = os.path.getsize(fpath)
                with open(fpath) as f:
                    data = json.load(f)
                
                changed = False
                # Remove empty fields
                for field in ["image_caption", "image_url", "alt_text"]:
                    if field in data and not data[field]:
                        del data[field]
                        changed = True
                
                # Ensure tags is string
                if "tags" in data and isinstance(data["tags"], list):
                    data["tags"] = ", ".join(data["tags"])
                    changed = True
                
                # Ensure lang exists
                if "lang" not in data:
                    data["lang"] = "id" if "en" not in fpath else "en"
                    changed = True
                
                if changed:
                    with open(fpath, "w") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    after = os.path.getsize(fpath)
                    saved_bytes += (before - after) if before > after else 0
                    optimized += 1
            except:
                pass
    
    if optimized:
        log(f"  📝 Optimized {optimized} JSON files (saved {size_fmt(saved_bytes)})")
    return optimized, saved_bytes

def compress_old_logs():
    """Kompres log yang lebih dari 3 hari."""
    compressed = 0
    saved_bytes = 0
    cutoff = datetime.now() - timedelta(days=3)
    
    if not os.path.exists(LOG_DIR):
        return 0, 0
    
    for fname in os.listdir(LOG_DIR):
        if not fname.endswith(".log"):
            continue
        fpath = os.path.join(LOG_DIR, fname)
        mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
        
        if mtime < cutoff and os.path.getsize(fpath) > 1024:
            # Compress
            gz_path = fpath + ".gz"
            try:
                with open(fpath, "rb") as f_in:
                    with gzip.open(gz_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                before = os.path.getsize(fpath)
                after = os.path.getsize(gz_path)
                os.remove(fpath)
                compressed += 1
                saved_bytes += (before - after)
                log(f"  🗜️ Compressed {fname}: {size_fmt(before)} → {size_fmt(after)}")
            except:
                pass
    
    if compressed:
        log(f"  🗜️ Compressed {compressed} old logs (saved {size_fmt(saved_bytes)})")
    return compressed, saved_bytes

def clean_generated_backups():
    """Hapus backup lama yang menumpuk."""
    removed = 0
    saved_bytes = 0
    
    # Check for old backup files
    backup_dir = os.path.join(BASE_DIR, "backups")
    if os.path.exists(backup_dir):
        for fname in os.listdir(backup_dir):
            fpath = os.path.join(backup_dir, fname)
            mtime = os.path.getmtime(fpath)
            age_days = (datetime.now() - datetime.fromtimestamp(mtime)).days
            if age_days > 14:
                sz = os.path.getsize(fpath)
                os.remove(fpath)
                removed += 1
                saved_bytes += sz
                log(f"  🗑️ Removed old backup: {fname} ({age_days}d old)")
    
    return removed, saved_bytes

def consolidate_duplicate_json():
    """Cari dan hapus artikel JSON duplikat (judul mirip)."""
    removed = 0
    saved_bytes = 0
    
    for subdir in ["_articles", "_articles/en"]:
        dir_path = os.path.join(BASE_DIR, subdir)
        if not os.path.exists(dir_path):
            continue
        
        articles = []
        for fname in os.listdir(dir_path):
            if fname.endswith(".json"):
                fpath = os.path.join(dir_path, fname)
                try:
                    with open(fpath) as f:
                        data = json.load(f)
                    articles.append({
                        "fname": fname,
                        "path": fpath,
                        "judul": data.get("judul", "").lower().strip(),
                        "size": os.path.getsize(fpath),
                    })
                except:
                    pass
        
        # Find duplicates by similar title
        seen_titles = {}
        for art in sorted(articles, key=lambda x: -x["size"]):
            # Normalize title - take first 30 chars
            key = art["judul"][:40]
            if key in seen_titles and len(art["judul"]) > 10:
                # Duplicate! Remove shorter one
                try:
                    sz = art["size"]
                    os.remove(art["path"])
                    removed += 1
                    saved_bytes += sz
                    log(f"  🗑️ Duplicate: {art['fname']} (same as {seen_titles[key]})")
                except:
                    pass
            else:
                seen_titles[key] = art["fname"]
    
    return removed, saved_bytes

# ════════════════════════════════════════
def main():
    log("=" * 60)
    log("🗄️ DailyMoney DB Optimization Agent — started")
    
    total_saved = 0
    report_items = []
    
    # 1. Orphan HTML
    log("\n📋 1. Orphan HTML cleanup...")
    n, sz = clean_orphan_articles()
    if n:
        report_items.append(f"🗑️ Orphan HTML: {n} files ({size_fmt(sz)})")
        total_saved += sz
    
    # 2. JSON optimization
    log("\n📋 2. JSON optimization...")
    n, sz = optimize_json_articles()
    total_saved += sz
    
    # 3. Compress old logs
    log("\n📋 3. Log compression...")
    n, sz = compress_old_logs()
    if n:
        report_items.append(f"🗜️ Logs compressed: {n} files ({size_fmt(sz)})")
        total_saved += sz
    
    # 4. Old backups
    log("\n📋 4. Old backup cleanup...")
    n, sz = clean_generated_backups()
    if n:
        report_items.append(f"🗑️ Old backups: {n} files ({size_fmt(sz)})")
        total_saved += sz
    
    # 5. Duplicate articles
    log("\n📋 5. Duplicate detection...")
    n, sz = consolidate_duplicate_json()
    if n:
        report_items.append(f"🗑️ Duplicate articles: {n} ({size_fmt(sz)})")
        total_saved += sz
    
    # Report
    log("\n" + "=" * 60)
    report = "🗄️ *DB Optimization Report*\n"
    report += f"📅 {datetime.now().strftime('%d %b %H:%M')}\n\n"
    
    if total_saved > 0:
        report += f"💾 Total space saved: **{size_fmt(total_saved)}**\n\n"
    for item in report_items:
        report += f"  • {item}\n"
    
    if not report_items:
        report += "✅ Semua sudah optimal — tidak ada yang perlu dibersihkan.\n"
        log("✅ All clean — no optimization needed")
    
    send_tg(report)
    log(f"📤 Report sent to Telegram")
    log(f"📊 Complete — saved {size_fmt(total_saved)}")

if __name__ == "__main__":
    main()

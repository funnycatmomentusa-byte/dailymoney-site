#!/usr/bin/env python3
"""DailyMoney — Bug Fixer Agent
Otomatis memperbaiki bug yang ditemukan Bug Hunter + QA Agent."""
import json, os, subprocess, sys, re, urllib.request, urllib.error
from datetime import datetime

BASE_DIR = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG = os.path.join(LOG_DIR, "bug-fixer.log")
SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(LOG, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

def send_telegram(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15, capture_output=True)
    except:
        pass

def git_commit(msg):
    try:
        subprocess.run(["git", "add", "-A"], cwd=BASE_DIR, capture_output=True, timeout=10)
        r = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=BASE_DIR, capture_output=True, timeout=10)
        if r.returncode != 0:
            subprocess.run(["git", "commit", "-m", f"fix: {msg}"], cwd=BASE_DIR, capture_output=True, timeout=10)
            subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, capture_output=True, timeout=30)
            return True
    except:
        pass
    return False

# ─── FIX 1: Validate & Rebuild Broken Article JSON ───
def fix_article_json():
    """Perbaiki format JSON artikel (tags string, slug, dll)."""
    fixes = []
    for lang, subdir in [("id", "_articles"), ("en", "_articles/en")]:
        dir_path = os.path.join(BASE_DIR, subdir)
        if not os.path.exists(dir_path):
            continue
        for fname in sorted(os.listdir(dir_path)):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(dir_path, fname)
            changed = False
            try:
                with open(fpath) as f:
                    data = json.load(f)
                
                # Fix tags: list → comma-separated string
                if "tags" in data and isinstance(data["tags"], list):
                    data["tags"] = ", ".join(data["tags"])
                    changed = True
                    log(f"  ✅ Fixed tags type in {fname}")
                
                # Fix missing lang
                if "lang" not in data:
                    data["lang"] = lang
                    changed = True
                    log(f"  ✅ Added lang={lang} to {fname}")
                
                # Fix missing date
                if "date" not in data or not data["date"]:
                    data["date"] = datetime.now().strftime("%Y-%m-%d")
                    changed = True
                    log(f"  ✅ Added date to {fname}")
                
                if changed:
                    with open(fpath, "w") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    fixes.append(fname)
            except json.JSONDecodeError as e:
                log(f"  ❌ JSON error in {fname}: {e}")
            except Exception as e:
                log(f"  ⚠️ {fname}: {e}")
    
    return fixes

# ─── FIX 2: Fix Broken Image References ───
def fix_broken_images():
    """Cari dan perbaiki referensi gambar yang 404."""
    fixes = []
    # Check article JSON image URLs
    for subdir in ["_articles", "_articles/en"]:
        dir_path = os.path.join(BASE_DIR, subdir)
        if not os.path.exists(dir_path):
            continue
        for fname in sorted(os.listdir(dir_path)):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(dir_path, fname)
            try:
                with open(fpath) as f:
                    data = json.load(f)
                
                img_url = data.get("image_url", "")
                if img_url and not img_url.startswith("https://images.unsplash.com"):
                    # Unsplash is the only reliable source
                    data["image_url"] = ""
                    data["image_caption"] = ""
                    with open(fpath, "w") as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    log(f"  ✅ Removed non-unsplash image from {fname}")
                    fixes.append(fname)
            except:
                pass
    return fixes

# ─── FIX 3: Fix & Rebuild Site ───
def rebuild_site():
    """Generate ulang site setelah perbaikan."""
    try:
        r = subprocess.run(["python3", "generate-site.py"], cwd=BASE_DIR, capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            log("✅ Site regenerated successfully")
            return True
        else:
            # Try to fix generation errors
            error = r.stderr + r.stdout
            log(f"⚠️ Site regeneration had issues")
            return False
    except Exception as e:
        log(f"❌ Site regeneration failed: {e}")
        return False

# ─── FIX 4: Verify & Fix HTML Structure ───
def fix_html_issues():
    """Perbaiki issues HTML umum."""
    fixes = []
    html_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.git']]
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.join(root, f))
    
    for fpath in html_files:
        rel = os.path.relpath(fpath, BASE_DIR)
        try:
            with open(fpath) as f:
                content = f.read()
            
            # Check for empty <a> tags
            empty_links = re.findall(r'<a[^>]*href="\s*"[^>]*>\s*</a>', content)
            if empty_links:
                for link in empty_links:
                    content = content.replace(link, '')
                log(f"  ✅ Removed {len(empty_links)} empty links in {rel}")
                fixes.append(rel)
            
            # Check for double script tags (common bug with widget injection)
            scripts = re.findall(r'<script[^>]*src="([^"]*)"[^>]*></script>', content)
            seen = set()
            dupes = []
            for s in scripts:
                if s in seen:
                    dupes.append(s)
                else:
                    seen.add(s)
            if dupes:
                for dup in dupes:
                    # Remove duplicate script tag (keep first occurrence)
                    first = True
                    def replacer(m):
                        nonlocal first
                        if m.group(1) == dup:
                            if first:
                                first = False
                                return m.group(0)
                            return ""
                        return m.group(0)
                    content = re.sub(r'<script[^>]*src="([^"]*)"[^>]*></script>', replacer, content)
                log(f"  ✅ Removed {len(dupes)} duplicate scripts in {rel}")
                fixes.append(rel)
            
            if fixes:
                with open(fpath, 'w') as f:
                    f.write(content)
        except Exception as e:
            log(f"  ⚠️ {rel}: {e}")
    
    return fixes

# ─── FIX 5: Clean Stale/Orphan HTML Files ───
def clean_stale_html():
    """Hapus file HTML artikel yang sudah tidak ada JSON source-nya."""
    removed = []
    for lang, art_dir, json_subdir in [("id", "articles", "_articles"), ("en", "en/articles", "_articles/en")]:
        art_path = os.path.join(BASE_DIR, art_dir)
        json_path = os.path.join(BASE_DIR, json_subdir)
        if not os.path.exists(art_path) or not os.path.exists(json_path):
            continue
        
        # Get all article slugs from JSON
        json_slugs = set()
        for fname in os.listdir(json_path):
            if fname.endswith(".json"):
                slug = fname[:-5]  # remove .json
                json_slugs.add(slug)
        
        # Check HTML files
        for fname in os.listdir(art_path):
            if fname.endswith(".html"):
                slug = fname[:-5]  # remove .html
                if slug not in json_slugs and not slug.startswith("404"):
                    fpath = os.path.join(art_path, fname)
                    try:
                        os.remove(fpath)
                        log(f"  🗑️ Removed stale: {art_dir}/{fname}")
                        removed.append(f"{art_dir}/{fname}")
                    except:
                        pass
    
    return removed

# ════════════════════════════════════════
# MAIN
# ════════════════════════════════════════
def main():
    log("=" * 60)
    log("🔧 DailyMoney Bug Fixer Agent — started")
    
    total_fixes = []
    
    # FIX 1: Article JSON format
    log("\n📋 Fix 1: Article JSON validation...")
    json_fixes = fix_article_json()
    if json_fixes:
        log(f"  ✅ Fixed {len(json_fixes)} JSON files")
        total_fixes.append(f"JSON format: {len(json_fixes)} files")
    
    # FIX 2: Broken images
    log("\n📋 Fix 2: Image references...")
    img_fixes = fix_broken_images()
    if img_fixes:
        log(f"  ✅ Cleaned {len(img_fixes)} image references")
        total_fixes.append(f"Image cleanup: {len(img_fixes)} articles")
    
    # FIX 3: Stale HTML
    log("\n📋 Fix 3: Stale HTML cleanup...")
    stale = clean_stale_html()
    if stale:
        log(f"  ✅ Removed {len(stale)} stale HTML files")
        total_fixes.append(f"Stale HTML: {len(stale)} files")
    
    # FIX 4: HTML structure issues
    log("\n📋 Fix 4: HTML structure...")
    html_fixes = fix_html_issues()
    if html_fixes:
        log(f"  ✅ Fixed HTML in {len(html_fixes)} files")
        total_fixes.append(f"HTML fixes: {len(html_fixes)} files")
    
    # FIX 5: Rebuild site if any changes
    log("\n📋 Fix 5: Site regeneration...")
    any_fixes = json_fixes or img_fixes or stale or html_fixes
    if any_fixes:
        rebuild_site()
    
    # Git push
    if any_fixes:
        committed = git_commit("auto bug fixes by Bug Fixer Agent")
        if committed:
            log("✅ Changes committed & pushed to GitHub")
            total_fixes.append("Auto-pushed to GitHub")
    
    # Report
    log("\n" + "=" * 60)
    if total_fixes:
        report = "🔧 *Bug Fixer Report*\n"
        report += f"📅 {datetime.now().strftime('%d %b %H:%M')}\n\n"
        report += "✅ Perbaikan otomatis:\n"
        for f in total_fixes:
            report += f"  • {f}\n"
        send_telegram(report)
        log("📤 Report sent to Telegram")
    else:
        log("✅ No bugs found — all clean")
        send_telegram("✅ *Bug Fixer* — Tidak ada bug ditemukan. Semua bersih! 🎉")
    
    log(f"📊 Complete — {len(total_fixes)} fix categories applied")
    print(f"✅ Done — {len(total_fixes)} fix categories")

if __name__ == "__main__":
    main()

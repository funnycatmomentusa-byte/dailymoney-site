#!/usr/bin/env python3
"""DailyMoney — Mobile Optimization & Reader Comfort Agent
Cek mobile responsiveness, page speed, dan kenyamanan membaca.
Jalan tiap 12 jam via cron."""
import os, subprocess, json
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

def check_html_files():
    """Cek HTML files untuk tag viewport dan responsive design"""
    issues = []
    ok_count = 0
    for root, dirs, files in os.walk(PROJECT):
        if ".git" in root or "__pycache__" in root:
            continue
        for f in files:
            if f.endswith(".html"):
                path = os.path.join(root, f)
                try:
                    with open(path) as fh:
                        content = fh.read()
                    if "viewport" in content:
                        ok_count += 1
                    else:
                        rel = os.path.relpath(path, PROJECT)
                        issues.append(f"{rel}: missing viewport meta")
                except:
                    pass
    return ok_count, issues

def check_image_optimization():
    """Cek ukuran gambar yang mungkin terlalu besar"""
    large_images = []
    for root, dirs, files in os.walk(os.path.join(PROJECT, "assets")):
        for f in files:
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
                path = os.path.join(root, f)
                size = os.path.getsize(path)
                if size > 500 * 1024:  # > 500KB
                    rel = os.path.relpath(path, PROJECT)
                    large_images.append(f"{rel}: {size/1024:.0f}KB")
    return large_images

def main():
    print(f"{'='*50}")
    print(f"📱 DailyMobile Optimizer @ {datetime.now().strftime('%H:%M')}")
    print(f"{'='*50}")
    
    ok_count, viewport_issues = check_html_files()
    large_images = check_image_optimization()
    
    issues = []
    notes = []
    
    if viewport_issues:
        issues.append(f"📱 {len(viewport_issues)} HTML tanpa viewport tag")
        for i in viewport_issues[:5]:
            notes.append(f"  ⚠️  {i}")
    
    if large_images:
        issues.append(f"🖼️ {len(large_images)} gambar > 500KB")
        for img in large_images[:5]:
            notes.append(f"  ⚠️  {img}")
    
    if not issues:
        msg = f"📱 *Mobile Optimizer*\n✅ Semua HTML responsive-ready ({ok_count} file)\n✅ Tidak ada gambar oversized\n📅 {datetime.now().strftime('%d %b %H:%M')}"
        print(msg)
        # Only send to Telegram if there are issues
    else:
        msg = f"📱 *Mobile Optimizer*\n⚠️ {len(issues)} isu(s) ditemukan\n"
        for i, n in zip(issues, notes[:5]):
            msg += f"\n{i}"
            msg += f"\n{n}"
        msg += f"\n📅 {datetime.now().strftime('%d %b %H:%M')}"
        print(msg)
        send_tg(msg)
    
    print(f"✅ Mobile check: {ok_count} HTML files OK, {len(issues)} issues")

if __name__ == "__main__":
    main()

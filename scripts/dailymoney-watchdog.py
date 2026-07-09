#!/usr/bin/env python3
"""DailyMoney — Watchdog Agent
Pantau semua cron job, deteksi yang gagal, restart otomatis."""
import json, os, subprocess, sys, urllib.request
from datetime import datetime, timezone

LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG = os.path.join(LOG_DIR, "watchdog.log")
SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    t = datetime.now().strftime("%H:%M:%S")
    line = f"[{t}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def send_alert(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

def check_site():
    """Cek apakah site masih hidup."""
    try:
        req = urllib.request.Request("https://dailymoney.my.id/")
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.status == 200, resp.status
    except Exception as e:
        return False, str(e)

def check_price_file():
    """Cek apakah _price_data.json masih fresh (< 15 menit)."""
    path = "/root/workspace/dailymoney-site/_price_data.json"
    if not os.path.exists(path):
        return False, "File not found"
    mtime = os.path.getmtime(path)
    age_min = (datetime.now().timestamp() - mtime) / 60
    if age_min > 15:
        return False, f"File too old ({age_min:.0f} min)"
    return True, f"Fresh ({age_min:.0f} min old)"

def check_latest_commit():
    """Cek kapan terakhir commit ke GitHub."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct:%s"],
            capture_output=True, text=True, timeout=10,
            cwd="/root/workspace/dailymoney-site"
        )
        parts = result.stdout.strip().split(":", 1)
        if len(parts) == 2:
            ts = int(parts[0])
            age_min = (datetime.now().timestamp() - ts) / 60
            return True, f"{age_min:.0f} min ago: {parts[1][:60]}"
        return False, "Could not parse"
    except Exception as e:
        return False, str(e)

def restart_price_updater():
    """Trigger Price Updater script langsung."""
    try:
        subprocess.run(
            ["bash", os.path.expanduser("~/.hermes/scripts/dailymoney-update.sh")],
            capture_output=True, text=True, timeout=120
        )
        return True
    except:
        return False

def run_bug_hunter():
    """Jalankan bug hunter untuk deteksi & perbaikan."""
    try:
        result = subprocess.run(
            [sys.executable, os.path.expanduser("~/.hermes/scripts/dailymoney-bug-hunter.py")],
            capture_output=True, text=True, timeout=120
        )
        return result.returncode == 0, result.stdout
    except:
        return False, ""

# ===== MAIN CHECK =====
log(f"{'='*50}")
log(f"🛡️ Watchdog Check @ {datetime.now().strftime('%d/%m/%Y %H:%M')}")

issues = []
fixes = []

# 1. Check site
site_ok, site_detail = check_site()
if not site_ok:
    issues.append(f"❌ Site DOWN: {site_detail}")
else:
    log(f"✅ Site: {site_detail}")

# 2. Check price file freshness
price_ok, price_detail = check_price_file()
if not price_ok:
    issues.append(f"❌ Price file stale: {price_detail}")
    log(f"❌ {price_detail} — attempting auto-restart...")
    if restart_price_updater():
        fixes.append("✅ Price Updater restarted")
        log("✅ Auto-restart triggered")
    else:
        fixes.append("❌ Price Updater restart FAILED")
else:
    log(f"✅ Price: {price_detail}")

# 3. Check latest commit
commit_ok, commit_detail = check_latest_commit()
if not commit_ok:
    issues.append(f"❌ Commit check: {commit_detail}")
    # Try to run update
    log("⚠️ No recent commit — running update...")
    if restart_price_updater():
        fixes.append("✅ Update triggered (no recent commit)")
else:
    log(f"✅ Git: {commit_detail}")

# 4. Run bug hunter periodically (skip if ran recently)
log("🔍 Running Bug Hunter scan...")
bh_ok, bh_output = run_bug_hunter()
if bh_ok:
    log("✅ Bug Hunter completed")
    # Extract key info from output
    for line in bh_output.split('\n'):
        if 'error' in line.lower() and '❌' in line:
            issues.append(line.strip())
        elif 'fix' in line.lower() and '✅' in line:
            fixes.append(line.strip())
else:
    issues.append("⚠️ Bug Hunter failed")

# Report
if issues:
    msg_lines = ["🛡️ *Watchdog Alert — dailymoney.my.id*",
                 f"📅 {datetime.now().strftime('%d %b %H:%M')}",
                 "",
                 "🚨 *Issues Found:*"]
    for i in issues[:5]:
        msg_lines.append(i)
    if fixes:
        msg_lines.append("")
        msg_lines.append("🔧 *Auto-Fixes:*")
        for f in fixes[:5]:
            msg_lines.append(f)
    msg = "\n".join(msg_lines)
    send_alert(msg)
    log("🚨 Alert sent to Telegram")
else:
    log("✅ All systems healthy — no alert needed")

log(f"📊 Watchdog complete: {len(issues)} issues, {len(fixes)} fixes")

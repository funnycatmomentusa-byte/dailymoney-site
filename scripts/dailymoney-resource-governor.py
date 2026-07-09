#!/usr/bin/env python3
"""DailyMoney — Smart Resource Governor (Hermes System Manager)
Memantau resource Hermes (disk, memory, cron health) dan auto-recovery."""
import json, os, subprocess, sys, shutil
from datetime import datetime

BASE_DIR = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG = os.path.join(LOG_DIR, "resource-governor.log")
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

def size_fmt(b):
    if b < 1024: return f"{b}B"
    if b < 1024*1024: return f"{b/1024:.1f}KB"
    return f"{b/1024/1024:.1f}MB"

def check_disk():
    """Cek disk usage dari direktori kritis."""
    issues = []
    targets = {
        "📁 Logs": LOG_DIR,
        "📁 Scripts": os.path.expanduser("~/.hermes/scripts"),
        "📁 Articles": os.path.join(BASE_DIR, "_articles"),
        "📁 Site": BASE_DIR,
    }
    report = {}
    for name, path in targets.items():
        if os.path.exists(path):
            total = 0
            for root, dirs, files in os.walk(path):
                for f in files:
                    try:
                        total += os.path.getsize(os.path.join(root, f))
                    except:
                        pass
            report[name] = total
            if total > 10 * 1024 * 1024:  # > 10MB
                issues.append(f"⚠️ {name}: {size_fmt(total)}")
                log(f"  ⚠️ {name}: {size_fmt(total)} — large, consider cleanup")
    
    return report, issues

def check_memory():
    """Cek memory Android/Hermes."""
    issues = []
    try:
        result = subprocess.run(["free", "-m"], capture_output=True, text=True, timeout=5)
        lines = result.stdout.strip().split("\n")
        if len(lines) > 1:
            parts = lines[1].split()
            total = int(parts[1])
            used = int(parts[2])
            avail = int(parts[-1])
            pct = (used / total) * 100
            log(f"  💾 RAM: {used}/{total}MB ({pct:.0f}% used, {avail}MB free)")
            if pct > 90:
                issues.append(f"🔴 RAM kritis: {pct:.0f}%")
            elif pct > 75:
                issues.append(f"⚠️ RAM tinggi: {pct:.0f}%")
    except:
        log("  ⚠️ Could not check memory")
    
    return issues

def check_disk_space():
    """Cek disk space keseluruhan."""
    issues = []
    try:
        result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
        lines = result.stdout.strip().split("\n")
        if len(lines) > 1:
            parts = lines[1].split()
            total = parts[1]
            used = parts[2]
            avail = parts[3]
            pct = parts[4].replace("%", "")
            log(f"  💽 Disk: {used}/{total} ({pct}% used, {avail} free)")
            if int(pct) > 90:
                issues.append(f"🔴 Disk kritis: {pct}%")
            elif int(pct) > 80:
                issues.append(f"⚠️ Disk: {pct}%")
    except:
        pass
    return issues

def check_python_packages():
    """Cek apakah package kritis terinstall."""
    issues = []
    critical = ["ddgs", "requests", "lxml"]
    for pkg in critical:
        try:
            subprocess.run([sys.executable, "-c", f"import {pkg}"], capture_output=True, timeout=5)
        except:
            issues.append(f"⚠️ Package missing: {pkg}")
            log(f"  ⚠️ Package {pkg} not installed")
    return issues

def check_git_repo():
    """Cek kesehatan git repo."""
    issues = []
    try:
        # Check if repo is clean
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=BASE_DIR, capture_output=True, text=True, timeout=5
        )
        dirty = [l for l in result.stdout.strip().split("\n") if l]
        if len(dirty) > 10:
            issues.append(f"⚠️ {len(dirty)} uncommitted files")
            log(f"  ⚠️ {len(dirty)} uncommitted files in repo")
        
        # Check if behind remote
        subprocess.run(["git", "fetch"], cwd=BASE_DIR, capture_output=True, timeout=10)
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD..origin/main"],
            cwd=BASE_DIR, capture_output=True, text=True, timeout=5
        )
        behind = int(result.stdout.strip() or "0")
        if behind > 0:
            issues.append(f"⚠️ Repo {behind} commit behind origin")
    except:
        pass
    return issues

def check_hermes_cron_health():
    """Cek cron jobs yang error."""
    issues = []
    try:
        result = subprocess.run(
            ["hermes", "cron", "list", "--json"],
            capture_output=True, text=True, timeout=10
        )
        data = json.loads(result.stdout)
        jobs = data if isinstance(data, list) else data.get("jobs", [])
        
        error_jobs = [j for j in jobs if j.get("last_status") == "error"]
        for job in error_jobs[:5]:
            issues.append(f"🔴 Cron error: {job.get('name', 'unknown')}")
            log(f"  🔴 Cron error: {job.get('name')}")
        
        running = len(jobs)
        errors = len(error_jobs)
        log(f"  ⏰ Cron: {running} jobs, {errors} errors")
    except:
        pass
    return issues

def auto_recovery(issues):
    """Auto-fix untuk isu yang bisa diperbaiki."""
    actions = []
    
    # 1. Clean logs if too many errors
    for issue in issues:
        if "uncommitted" in issue:
            try:
                subprocess.run(["git", "add", "-A"], cwd=BASE_DIR, capture_output=True, timeout=10)
                subprocess.run(["git", "commit", "-m", "gov: auto-commit stray changes"], 
                    cwd=BASE_DIR, capture_output=True, timeout=10)
                subprocess.run(["git", "push", "origin", "main"], 
                    cwd=BASE_DIR, capture_output=True, timeout=30)
                actions.append("✅ Auto-commit & push stray changes")
                log("  ✅ Auto-committed stray changes")
            except:
                pass
        
        if "Logs" in issue and "large" in issue:
            # Compress old logs
            try:
                import gzip
                cutoff = datetime.now().timestamp() - (7 * 86400)
                for f in os.listdir(LOG_DIR):
                    fpath = os.path.join(LOG_DIR, f)
                    if f.endswith(".log") and os.path.getsize(fpath) > 50000:
                        mtime = os.path.getmtime(fpath)
                        if mtime < cutoff:
                            gz_path = fpath + ".gz"
                            if not os.path.exists(gz_path):
                                with open(fpath, "rb") as f_in:
                                    with gzip.open(gz_path, "wb") as f_out:
                                        f_out.write(f_in.read())
                                os.remove(fpath)
                                actions.append(f"🗜️ Compressed {f}")
                                log(f"  🗜️ Compressed old log: {f}")
            except:
                pass
    
    return actions

# ════════════════════════════════════════
def main():
    log("=" * 60)
    log("⚙️ DailyMoney Resource Governor — started")
    
    all_issues = []
    
    # 1. Disk usage
    log("\n📋 1. Disk usage analysis...")
    report, issues = check_disk()
    all_issues.extend(issues)
    for name, size in report.items():
        log(f"  {name}: {size_fmt(size)}")
    
    # 2. Memory
    log("\n📋 2. Memory check...")
    issues = check_memory()
    all_issues.extend(issues)
    
    # 3. Disk space
    log("\n📋 3. Disk space...")
    issues = check_disk_space()
    all_issues.extend(issues)
    
    # 4. Python packages
    log("\n📋 4. Python dependencies...")
    issues = check_python_packages()
    all_issues.extend(issues)
    
    # 5. Git health
    log("\n📋 5. Git repository...")
    issues = check_git_repo()
    all_issues.extend(issues)
    
    # 6. Cron health
    log("\n📋 6. Hermes cron health...")
    issues = check_hermes_cron_health()
    all_issues.extend(issues)
    
    # Auto-recovery
    log("\n📋 7. Auto-recovery...")
    actions = auto_recovery(all_issues)
    
    # Report
    log("\n" + "=" * 60)
    report_msg = "⚙️ *Resource Governor Report*\n"
    report_msg += f"📅 {datetime.now().strftime('%d %b %H:%M')}\n\n"
    
    if not all_issues:
        report_msg += "✅ Semua resource sehat — sistem stabil!\n"
    else:
        report_msg += f"⚠️ {len(all_issues)} issue(s) ditemukan:\n"
        for iss in all_issues[:8]:
            report_msg += f"  {iss}\n"
    
    if actions:
        report_msg += "\n*Auto-Recovery:*\n"
        for a in actions:
            report_msg += f"  {a}\n"
    
    send_tg(report_msg)
    log("📤 Report sent to Telegram")
    log(f"📊 Complete — {len(all_issues)} issues, {len(actions)} auto-recovery actions")

if __name__ == "__main__":
    main()

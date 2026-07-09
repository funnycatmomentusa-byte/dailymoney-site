#!/usr/bin/env python3
"""DailyMoney — Automated Backup & Disaster Recovery Agent
Backup repo ke archive lokal + laporan integritas."""
import json, os, subprocess, sys, tarfile, shutil
from datetime import datetime

WORK_DIR = "/root/workspace/dailymoney-site"
BACKUP_DIR = os.path.expanduser("~/.hermes/backups/dailymoney")
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
LOG = os.path.join(LOG_DIR, "backup-agent.log")
MAX_BACKUPS = 14  # Simpan 14 hari terakhir

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(msg)

def verify_repo():
    """Cek integritas git repo sebelum backup."""
    try:
        # Cek git status
        r = subprocess.run(["git", "status", "--porcelain"], cwd=WORK_DIR, capture_output=True, text=True, timeout=10)
        dirty_files = r.stdout.strip().split('\n') if r.stdout.strip() else []
        clean = len([f for f in dirty_files if f]) == 0
        
        # Cek last commit
        r2 = subprocess.run(["git", "log", "-1", "--format=%H %s"], cwd=WORK_DIR, capture_output=True, text=True, timeout=10)
        last_commit = r2.stdout.strip()
        
        return {
            "clean": clean,
            "dirty_count": len([f for f in dirty_files if f]),
            "last_commit": last_commit,
            "dirty_mtime": datetime.fromtimestamp(os.path.getmtime(WORK_DIR)).isoformat() if clean else "dirty"
        }
    except Exception as e:
        log(f"⚠️ Git verify error: {e}")
        return {"clean": False, "error": str(e)}

def create_backup():
    """Buat tar.gz backup dari repo."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"dailymoney-backup-{ts}.tar.gz"
    backup_path = os.path.join(BACKUP_DIR, backup_name)
    
    # Get commit hash for filename
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=WORK_DIR, capture_output=True, text=True, timeout=10)
        commit_hash = r.stdout.strip()
        backup_name = f"dailymoney-backup-{ts}-{commit_hash}.tar.gz"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
    except:
        pass
    
    # Buat tar.gz, exclude _site dan node_modules
    try:
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(WORK_DIR, arcname="dailymoney-site",
                    filter=lambda x: None if x.name.endswith(('.pyc', '__pycache__')) or 
                    '.git' in x.name.split('/') else x)
        
        size_kb = round(os.path.getsize(backup_path) / 1024, 1)
        log(f"✅ Backup created: {backup_name} ({size_kb} KB)")
        return {"name": backup_name, "path": backup_path, "size_kb": size_kb}
    except Exception as e:
        log(f"❌ Backup failed: {e}")
        return None

def cleanup_old_backups():
    """Hapus backup lebih dari MAX_BACKUPS hari."""
    backups = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith('dailymoney-backup-') and f.endswith('.tar.gz')])
    removed = 0
    while len(backups) > MAX_BACKUPS:
        old = backups.pop(0)
        os.remove(os.path.join(BACKUP_DIR, old))
        removed += 1
        log(f"🗑️ Removed old backup: {old}")
    return removed

def check_disk_space():
    """Cek sisa disk space."""
    try:
        stat = os.statvfs(BACKUP_DIR)
        free_gb = round(stat.f_frsize * stat.f_bavail / (1024**3), 1)
        return free_gb
    except:
        return 0

def main():
    log("=" * 50)
    log("💾 Backup Agent started")
    
    # 1. Verify repo integrity
    repo_status = verify_repo()
    log(f"📋 Repo: {'Clean' if repo_status['clean'] else '⚠️ Uncommitted changes'}")
    if repo_status.get('dirty_count', 0) > 0:
        log(f"  ⚠️ {repo_status['dirty_count']} files uncommitted")
        
        # Auto commit uncommitted files before backup
        try:
            subprocess.run(["git", "add", "-A"], cwd=WORK_DIR, capture_output=True, timeout=10)
            subprocess.run(["git", "commit", "-m", "chore: auto backup commit", "--allow-empty"], cwd=WORK_DIR, capture_output=True, timeout=10)
            log("  ✅ Auto-committed changes")
            repo_status['clean'] = True
        except Exception as e:
            log(f"  ⚠️ Auto-commit failed: {e}")
    
    # 2. Create backup
    backup = create_backup()
    if not backup:
        log("❌ Backup failed — check disk space")
        return
    
    # 3. Cleanup old backups
    removed = cleanup_old_backups()
    if removed > 0:
        log(f"🧹 Removed {removed} old backup(s)")
    
    # 4. Check disk
    free_gb = check_disk_space()
    log(f"💽 Free disk: {free_gb} GB")
    
    # 5. Report
    report = {
        "timestamp": datetime.now().isoformat(),
        "repo_status": repo_status,
        "backup": backup,
        "disk_free_gb": free_gb,
        "backups_count": len([f for f in os.listdir(BACKUP_DIR) if f.endswith('.tar.gz')]),
        "max_backups": MAX_BACKUPS
    }
    
    report_path = os.path.join(WORK_DIR, "assets", "seo", "backup-report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    log(f"📄 Report: {report_path}")
    log("✅ Backup Agent complete")

if __name__ == "__main__":
    main()

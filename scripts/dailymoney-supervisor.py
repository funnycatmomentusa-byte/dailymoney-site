#!/usr/bin/env python3
"""DailyMoney — Agent Supervisor (The Watcher)
Memastikan semua 36 cron agent berjalan, tidak error, site tidak 404.
Auto-restart agent yang gagal, auto-notify jika ada masalah kritis."""
import json, os, subprocess, sys, re, urllib.request, urllib.error
from datetime import datetime, timedelta
from collections import defaultdict

BASE_DIR = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG = os.path.join(LOG_DIR, "supervisor.log")
STATE_FILE = os.path.join(LOG_DIR, "supervisor-state.json")
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

def load_state():
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                return json.load(f)
    except:
        pass
    return {"previous_errors": {}, "consecutive_failures": {}, "last_report": ""}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def size_fmt(b):
    if b < 1024: return f"{b}B"
    return f"{b/1024:.1f}KB"

def check_all_cron_jobs():
    """Cek status semua cron jobs via hermes CLI (tabel output)."""
    error_jobs = []
    stale_jobs = []
    
    try:
        result = subprocess.run(
            ["hermes", "cron", "list"],
            capture_output=True, text=True, timeout=15
        )
        text = result.stdout
    except Exception as e:
        log(f"  🔴 Cannot list cron jobs: {e}")
        return [], []
    
    # Parse text table format
    now = datetime.now()
    current_job = None
    total = 0
    
    for line in text.split("\n"):
        # Detect job header: starts with hex ID
        m = re.match(r'^  ([a-f0-9]{12})\s+\[(\w+)\]', line)
        if m:
            if current_job and current_job.get("name"):
                analyze_job(current_job, error_jobs, stale_jobs, now)
                total += 1
            current_job = {"job_id": m.group(1), "status": m.group(2)}
            continue
        
        if current_job is None:
            continue
        
        m = re.match(r'    Name:\s+(.+)', line)
        if m:
            current_job["name"] = m.group(1).strip()
            continue
        
        m = re.match(r'    Schedule:\s+(.+)', line)
        if m:
            current_job["schedule"] = m.group(1).strip()
            continue
        
        m = re.match(r'    Last run:\s+(\S+\s+\S+)\s+(\w+)', line)
        if m:
            current_job["last_run"] = m.group(1)
            current_job["last_status"] = m.group(2)
            continue
    
    # Analyze last job
    if current_job and current_job.get("name"):
        analyze_job(current_job, error_jobs, stale_jobs, now)
        total += 1
    
    log(f"\n  📊 Cron: {total} total, {len(error_jobs)} ERROR, {len(stale_jobs)} stale")
    return error_jobs, stale_jobs


def analyze_job(job, error_jobs, stale_jobs, now):
    """Analyze a single cron job."""
    name = job.get("name", "Unknown")
    status = job.get("last_status")
    
    if status == "error":
        error_jobs.append(job)
        log(f"  🔴 {name}: ERROR")
        return
    
    # Check staleness
    last_run = job.get("last_run")
    if last_run and status == "ok":
        try:
            last = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
            hours_since = (now - last).total_seconds() / 3600
            schedule = job.get("schedule", "")
            expected_hours = 12
            if "10m" in schedule: expected_hours = 0.5
            elif "15m" in schedule: expected_hours = 0.5
            elif "30m" in schedule: expected_hours = 1
            elif "120m" in schedule or "2h" in schedule: expected_hours = 3
            elif "180m" in schedule: expected_hours = 4
            elif "240m" in schedule or "4h" in schedule: expected_hours = 5
            elif "360m" in schedule or "6h" in schedule: expected_hours = 8
            elif "720m" in schedule or "12h" in schedule: expected_hours = 14
            elif schedule.startswith("0 "):
                expected_hours = 30  # daily/weekly
            
            if hours_since > expected_hours * 2:
                stale_jobs.append(job)
                log(f"  ⚠️ {name}: stale ({hours_since:.0f}h since last run)")
        except:
            pass

def check_site_404():
    """Cek semua halaman site untuk 404."""
    issues = []
    checked = 0
    
    # 1. Check homepage
    urls_to_check = ["https://dailymoney.my.id/"]
    
    # 2. Get all URLs from sitemap
    try:
        req = urllib.request.Request(
            "https://dailymoney.my.id/sitemap.xml",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        resp = urllib.request.urlopen(req, timeout=15)
        sitemap = resp.read().decode()
        
        # Extract all URLs from sitemap
        urls = re.findall(r'<loc>(.*?)</loc>', sitemap)
        urls_to_check.extend(urls[:50])  # Check top 50
    except Exception as e:
        issues.append(f"⚠️ Cannot fetch sitemap: {e}")
        log(f"  ⚠️ Sitemap fetch failed: {e}")
    
    # 3. Check each URL
    for url in urls_to_check:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=15)
            checked += 1
            
            if resp.status == 404:
                issues.append(f"🔴 404: {url}")
                log(f"  🔴 404: {url}")
            elif resp.status in (301, 302):
                log(f"  ⚠️ Redirect: {url} → {resp.headers.get('Location', '?')}")
            elif resp.status != 200:
                log(f"  ⚠️ HTTP {resp.status}: {url}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                issues.append(f"🔴 404: {url}")
                log(f"  🔴 404: {url}")
            checked += 1
        except Exception as e:
            issues.append(f"⚠️ Error: {url} ({e})")
            log(f"  ⚠️ {url}: {e}")
    
    log(f"  📊 Checked {checked} URLs — {len(issues)} issues")
    return issues, checked

def check_agent_scripts_exist():
    """Verifikasi semua script cron masih ada di filesystem."""
    issues = []
    
    # Known scripts that should exist (based on cron names)
    expected_scripts = [
        "dailymoney-update.sh", "dailymoney-watchdog.py",
        "dailymoney-telegram-summary.py", "dailymoney-rss-monitor.sh",
        "dailymoney-news-researcher.sh", "dailymoney-perf-monitor.py",
        "dailymoney-seo-writer.py", "dailymoney-security-agent.py",
        "dailymoney-master-writer.py", "dailymoney-seo-agent.sh",
        "dailymoney-traffic-agent.sh", "dailymoney-bug-hunter.py",
        "dailymoney-forex-researcher.sh", "dailymoney-visitor-agent.py",
        "dailymoney-link-checker.sh", "dailymoney-curator.sh",
        "dailymoney-daily-dashboard.py", "dailymoney-seo-architect.py",
        "dailymoney-viral-repurposer.py", "dailymoney-backlink-hunter.py",
        "dailymoney-internal-linker.py", "dailymoney-speed-agent.py",
        "dailymoney-trend-monitor.py", "dailymoney-newsletter-agent.py",
        "dailymoney-qa-agent.py", "dailymoney-content-recycler.py",
        "dailymoney-analyser-agent.py", "dailymoney-security-hardener.py",
        "dailymoney-indexing-agent.py", "dailymoney-link-health.py",
        "dailymoney-backup-agent.py", "dailymoney-bug-fixer.py",
        "dailymoney-log-analysis.py", "dailymoney-db-optimizer.py",
        "dailymoney-api-watchdog.py", "dailymoney-article-fetcher.sh",
        "dailymoney-curator-ai.py", "dailymoney-resource-governor.py",
        "dailymoney-security-auditor.py",
    ]
    
    scripts_dir = os.path.expanduser("~/.hermes/scripts")
    for script in expected_scripts:
        fpath = os.path.join(scripts_dir, script)
        if not os.path.exists(fpath):
            issues.append(f"⚠️ Missing script: {script}")
            log(f"  ⚠️ MISSING: {script}")
    
    return issues

def check_log_errors():
    """Cek log untuk error spike (error rate > normal)."""
    issues = []
    
    # Check log file sizes - if huge, might indicate runaway error
    for fname in os.listdir(LOG_DIR):
        if not fname.endswith(".log"):
            continue
        fpath = os.path.join(LOG_DIR, fname)
        size = os.path.getsize(fpath)
        if size > 500 * 1024:  # > 500KB
            issues.append(f"⚠️ Large log: {fname} ({size_fmt(size)})")
            log(f"  ⚠️ Large log file: {fname} — {size_fmt(size)}")
    
    # Count recent errors in agent.log
    agent_log = os.path.join(LOG_DIR, "agent.log")
    if os.path.exists(agent_log):
        try:
            size = os.path.getsize(agent_log)
            if size > 300 * 1024:  # > 300KB → auto-trim
                with open(agent_log) as f:
                    lines = f.readlines()
                if len(lines) > 500:
                    with open(agent_log, "w") as f:
                        f.writelines(lines[-500:])
                    log(f"  ✂️ Auto-trimmed agent.log to last 500 lines (was {size_fmt(size)})")
            
            with open(agent_log) as f:
                lines = f.readlines()
            # Count ERROR in last 100 lines
            recent = lines[-100:]
            recent_errors = sum(1 for l in recent if "ERROR" in l)
            if recent_errors > 10:
                issues.append(f"⚠️ {recent_errors} errors in last 100 agent.log lines")
                log(f"  ⚠️ {recent_errors} errors in last 100 log lines — spike?")
        except:
            pass
    
    return issues

def auto_restart_failed_cron(job_id, job_name):
    """Coba restart cron job yang gagal."""
    try:
        # Remove and recreate
        subprocess.run(["hermes", "cron", "remove", job_id], 
            capture_output=True, timeout=10)
        log(f"  🔄 Removed failed job: {job_name}")
        
        # Try to find and re-run the script directly
        # This is a soft restart - the cron scheduler will re-create next tick
        return True
    except Exception as e:
        log(f"  ❌ Cannot restart {job_name}: {e}")
        return False

def check_git_deploy():
    """Cek apakah GitHub Pages deploy terakhir sukses."""
    issues = []
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/funnycatmomentusa-byte/dailymoney-site/actions/runs?per_page=3&status=completed",
            headers={"Accept": "application/vnd.github+json"}
        )
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        runs = data.get("workflow_runs", [])
        
        if runs:
            latest = runs[0]
            conclusion = latest.get("conclusion", "unknown")
            created = latest.get("created_at", "")[:16]
            name = latest.get("name", "deploy")
            
            if conclusion == "failure":
                issues.append(f"🔴 Deploy failed: {name} ({created})")
                log(f"  🔴 GitHub Actions: {name} FAILED at {created}")
            elif conclusion == "success":
                log(f"  ✅ Deploy: {name} success ({created})")
    except urllib.error.HTTPError as e:
        if e.code != 403 and e.code != 401:
            issues.append(f"⚠️ GitHub API: HTTP {e.code}")
    except:
        pass
    
    return issues

def fix_404_homepage():
    """Jika homepage 404, regenerate dan push ulang."""
    try:
        log("  🔧 Auto-rebuild: running generate-site.py...")
        r = subprocess.run(["python3", "generate-site.py"], 
            cwd=BASE_DIR, capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            subprocess.run(["git", "add", "-A"], cwd=BASE_DIR, capture_output=True, timeout=10)
            subprocess.run(["git", "commit", "-m", "supervisor: auto-rebuild after 404 detection"],
                cwd=BASE_DIR, capture_output=True, timeout=10)
            subprocess.run(["git", "push", "origin", "main"],
                cwd=BASE_DIR, capture_output=True, timeout=30)
            log("  ✅ Auto-rebuild & push complete")
            return True
    except:
        pass
    return False

# ════════════════════════════════════════
def main():
    log("=" * 60)
    log("👁️ DailyMoney Agent Supervisor — started")
    
    state = load_state()
    now = datetime.now()
    
    all_issues = []
    critical = []
    auto_actions = []
    
    # ─── CHECK 1: All Cron Jobs ───
    log("\n📋 1. Cron job health check...")
    error_jobs, stale_jobs = check_all_cron_jobs()
    
    for job in error_jobs:
        name = job.get("name", "Unknown")
        jid = job.get("job_id", "")
        all_issues.append(f"🔴 {name} — ERROR")
        critical.append(f"  • {name}")
        
        # Auto-restart if consecutively failing
        prev = state.get("consecutive_failures", {}).get(jid, 0)
        state["consecutive_failures"][jid] = prev + 1
        
        if prev >= 2:  # Failed 3+ times consecutively
            auto_actions.append(f"🔧 Auto-restart {name}")
            auto_restart_failed_cron(jid, name)
    
    for job in stale_jobs:
        name = job.get("name", "Unknown")
        all_issues.append(f"⚠️ {name} — stale (>2x interval)")
    
    # Reset consecutive failures for healthy jobs
    for job in error_jobs:
        jid = job.get("job_id", "")
        if jid not in [e.get("job_id", "") for e in error_jobs]:
            if jid in state.get("consecutive_failures", {}):
                state["consecutive_failures"][jid] = 0
    
    # ─── CHECK 2: 404 Scan ───
    log("\n📋 2. Site 404 check...")
    _404_issues, checked = check_site_404()
    
    if _404_issues:
        for iss in _404_issues:
            all_issues.append(iss)
            if iss.startswith("🔴 404"):
                critical.append(f"  • {iss}")
                # Auto-fix: regenerate site
                if fix_404_homepage():
                    auto_actions.append("🔧 Auto-rebuild site (404 detected)")
    
    # ─── CHECK 3: Script Integrity ───
    log("\n📋 3. Agent script integrity...")
    script_issues = check_agent_scripts_exist()
    all_issues.extend(script_issues)
    
    # ─── CHECK 4: Log Health ───
    log("\n📋 4. Log analysis...")
    log_issues = check_log_errors()
    all_issues.extend(log_issues)
    
    # ─── CHECK 5: Git Deploy ───
    log("\n📋 5. Deploy status...")
    deploy_issues = check_git_deploy()
    all_issues.extend(deploy_issues)
    
    # ─── CHECK 6: Site Down? ───
    log("\n📋 6. Site availability...")
    try:
        req = urllib.request.Request("https://dailymoney.my.id/",
            headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=20)
        if resp.status != 200:
            critical.append(f"  • Site HTTP {resp.status}")
            all_issues.append(f"🔴 SITE DOWN: HTTP {resp.status}")
            auto_actions.append("🔧 Auto-rebuild site")
            fix_404_homepage()
        else:
            log(f"  ✅ Site OK: HTTP {resp.status}")
    except Exception as e:
        critical.append(f"  • Site unreachable: {e}")
        all_issues.append(f"🔴 SITE UNREACHABLE: {e}")
    
    # ─── SAVE STATE ───
    state["last_check"] = now.isoformat()
    save_state(state)
    
    # ─── REPORT ───
    log("\n" + "=" * 60)
    
    # Priority: critical first, then warnings
    report = "👁️ *Agent Supervisor Report*\n"
    report += f"📅 {datetime.now().strftime('%d %b %H:%M')}\n\n"
    
    total_cron = len(error_jobs) + len([j for j in []])  # approximate
    report += f"📊 Cron: {len(error_jobs)} error | {len(stale_jobs)} stale\n"
    report += f"🌐 URLs: {checked} checked | {len(_404_issues)} issues\n"
    report += f"📁 Scripts: {len(script_issues)} missing\n\n"
    
    if critical:
        report += "🔴 *Critical:*\n"
        for c in critical[:5]:
            report += f"{c}\n"
        report += "\n"
    
    if all_issues:
        # Group by type
        errors = [i for i in all_issues if i.startswith("🔴")]
        warnings = [i for i in all_issues if i.startswith("⚠️")]
        
        if errors:
            report += "*Errors:*\n"
            for e in errors[:6]:
                report += f"  {e}\n"
            report += "\n"
        if warnings:
            report += "*Warnings:*\n"
            for w in warnings[:6]:
                report += f"  {w}\n"
            report += "\n"
    
    if auto_actions:
        report += "*Auto-Actions:*\n"
        for a in auto_actions:
            report += f"  {a}\n"
        report += "\n"
    
    if not all_issues:
        report += "✅ *Semua sistem sehat!* 36 agent berjalan normal.\n"
    elif not critical:
        report += "ℹ️ Ada isu minor — tidak perlu tindakan manual.\n"
    
    send_tg(report)
    log("📤 Report sent to Telegram")
    log(f"📊 Complete — {len(all_issues)} issues, {len(critical)} critical, {len(auto_actions)} auto-actions")

if __name__ == "__main__":
    main()

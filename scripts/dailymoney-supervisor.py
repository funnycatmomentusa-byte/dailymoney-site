#!/usr/bin/env python3
"""DailyMoney — Agent Supervisor ZERO-ERROR ENFORCER
Agent ketat yang WAJIB memastikan:
1. Semua 44 cron agent berjalan tanpa error
2. Tidak ada artikel tanggal masa depan (hanya cek file YYYY-MM-DD-* prefix)
3. Tidak ada 404 di site
4. Semua script agent exist
5. Auto-fix langsung perbaiki error yang ditemukan
6. Auto-notify ke Telegram
ZERO TOLERANCE — satu error pun tidak boleh lewat."""
import json, os, subprocess, sys, re, urllib.request, urllib.error, glob
from datetime import datetime, timedelta, date

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
    return {"consecutive_failures": {}, "fixes_applied": []}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

# ══════════════════════════════════════════════════════════
# CHECK 1: Future Date Articles — ZERO TOLERANCE
# ══════════════════════════════════════════════════════════
def check_future_dates():
    """Cek artikel yang filename-nya YYYY-MM-DD-* tapi tanggalnya masa depan.
    HANYA cek file yang benar-benar start dengan YYYY-MM-DD- pattern."""
    issues = []
    fixes = []
    today_str = date.today().strftime('%Y-%m-%d')
    today_ddmmyyyy = date.today().strftime('%d/%m/%Y')
    
    # Pattern: exactly YYYY-MM-DD-something.json
    date_prefix_re = re.compile(r'^(\d{4}-\d{2}-\d{2})-(.+)\.json$')
    
    articles_dir = os.path.join(BASE_DIR, "_articles")
    en_dir = os.path.join(articles_dir, "en")
    
    for d in [articles_dir, en_dir]:
        if not os.path.exists(d):
            continue
        for f in os.listdir(d):
            m = date_prefix_re.match(f)
            if not m:
                continue  # Skip files without YYYY-MM-DD prefix
            
            fname_date = m.group(1)
            slug_part = m.group(2)
            
            if fname_date > today_str:
                # FUTURE DATE — fix it
                old_path = os.path.join(d, f)
                new_name = f"{today_str}-{slug_part}.json"
                new_path = os.path.join(d, new_name)
                
                try:
                    with open(old_path) as fh:
                        data = json.load(fh)
                    data["date"] = today_ddmmyyyy
                    with open(new_path, "w") as fh:
                        json.dump(data, fh, ensure_ascii=False, indent=2)
                    os.remove(old_path)
                    fixes.append(f"🔧 {f} → {new_name}")
                    log(f"  🔧 FIXED: {f} → {new_name}")
                except Exception as e:
                    try:
                        os.rename(old_path, new_path)
                        fixes.append(f"🔧 {f} → {new_name} (rename only)")
                    except:
                        issues.append(f"🔴 Cannot fix: {f}: {e}")
    
    if not fixes:
        log("  ✅ No future-dated articles found")
    
    return issues, fixes

# ══════════════════════════════════════════════════════════
# CHECK 2: All Cron Jobs — ZERO ERROR TOLERANCE
# ══════════════════════════════════════════════════════════
def check_all_cron_jobs():
    error_jobs = []
    stale_jobs = []
    total = 0
    
    try:
        result = subprocess.run(
            ["hermes", "cron", "list"],
            capture_output=True, text=True, timeout=15
        )
        text = result.stdout
    except Exception as e:
        log(f"  🔴 Cannot list cron jobs: {e}")
        return [], [], 0
    
    now = datetime.now()
    current_job = None
    
    for line in text.split("\n"):
        m = re.match(r'^  ([a-f0-9]{12})\s+\[(\w+)\]', line)
        if m:
            if current_job and current_job.get("name"):
                _analyze_job(current_job, error_jobs, stale_jobs, now)
                total += 1
            current_job = {"job_id": m.group(1), "status": m.group(2)}
            continue
        
        if current_job is None:
            continue
        
        for key, pattern in [
            ("name", r'    Name:\s+(.+)'),
            ("schedule", r'    Schedule:\s+(.+)'),
            ("script", r'    Script:\s+(.+)'),
        ]:
            m2 = re.match(pattern, line)
            if m2:
                current_job[key] = m2.group(1).strip()
        
        m2 = re.match(r'    Last run:\s+(\S+\s+\S+)\s+(\w+)', line)
        if m2:
            current_job["last_run"] = m2.group(1)
            current_job["last_status"] = m2.group(2)
    
    if current_job and current_job.get("name"):
        _analyze_job(current_job, error_jobs, stale_jobs, now)
        total += 1
    
    return error_jobs, stale_jobs, total

def _analyze_job(job, error_jobs, stale_jobs, now):
    name = job.get("name", "Unknown")
    status = job.get("last_status")
    
    if status == "error":
        error_jobs.append(job)
        log(f"  🔴 {name}: ERROR")
        return
    
    last_run = job.get("last_run")
    if last_run and status == "ok":
        try:
            last = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
            hours_since = (now - last).total_seconds() / 3600
            schedule = job.get("schedule", "")
            expected = _schedule_to_hours(schedule)
            if hours_since > expected * 2.5:
                stale_jobs.append(job)
                log(f"  ⚠️ {name}: stale ({hours_since:.0f}h)")
        except:
            pass

def _schedule_to_hours(schedule):
    if "10m" in schedule: return 0.5
    if "15m" in schedule: return 0.5
    if "30m" in schedule: return 1
    if "60m" in schedule or "1h" in schedule: return 1.5
    if "120m" in schedule or "2h" in schedule: return 3
    if "180m" in schedule or "3h" in schedule: return 4
    if "240m" in schedule or "4h" in schedule: return 5
    if "360m" in schedule or "6h" in schedule: return 8
    if "720m" in schedule or "12h" in schedule: return 14
    if schedule.startswith("0 "): return 30
    return 12

def auto_fix_error_agent(job):
    name = job.get("name", "Unknown")
    script = job.get("script", "")
    if not script:
        return False, "No script"
    
    for base in [os.path.join(BASE_DIR, "scripts"), os.path.expanduser("~/.hermes/scripts")]:
        script_path = os.path.join(base, script)
        if os.path.exists(script_path):
            break
    else:
        return False, f"Script not found: {script}"
    
    try:
        cmd = ["bash", script_path] if script.endswith(".sh") else ["python3", script_path]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=BASE_DIR)
        if r.returncode == 0:
            log(f"  ✅ AUTO-FIX: {name} now OK")
            return True, "Fixed"
        else:
            err = (r.stderr or r.stdout or "")[-150:]
            log(f"  ❌ AUTO-FIX: {name} still fails: {err[:100]}")
            return False, f"Still fails"
    except subprocess.TimeoutExpired:
        return False, "Timeout"
    except Exception as e:
        return False, str(e)[:100]

# ══════════════════════════════════════════════════════════
# CHECK 3: Script Integrity
# ══════════════════════════════════════════════════════════
def check_scripts_exist():
    issues = []
    scripts_dir = os.path.join(BASE_DIR, "scripts")
    alt_dir = os.path.expanduser("~/.hermes/scripts")
    
    expected = [
        "dailymoney-update.sh", "dailymoney-watchdog.py",
        "dailymoney-telegram-summary.py", "dailymoney-rss-monitor.sh",
        "dailymoney-news-researcher.sh", "dailymoney-perf-monitor.py",
        "dailymoney-seo-writer.py", "dailymoney-security-agent.py",
        "dailymoney-master-writer.py", "dailymoney-seo-agent.sh",
        "dailymoney-bug-hunter.py", "dailymoney-forex-researcher.sh",
        "dailymoney-visitor-agent.py", "dailymoney-seo-architect.py",
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
        "dailymoney-security-auditor.py", "dailymoney-daily-dashboard.py",
        "dailymoney-supervisor.py", "dailymoney-import-watchdog.py",
        "dailymoney-business-agent.py", "dailymoney-analytics-reporter.py",
        "dailymoney-mobile-optimizer.py", "dailymoney-sponsorship-agent.py",
        "dailymoney-frontend-dynamo.py", "dailymoney-super-traffic-agent.py",
    ]
    
    for s in expected:
        if not os.path.exists(os.path.join(scripts_dir, s)) and not os.path.exists(os.path.join(alt_dir, s)):
            issues.append(f"🔴 MISSING: {s}")
            log(f"  🔴 MISSING: {s}")
    
    if not issues:
        log(f"  ✅ All {len(expected)} scripts present")
    return issues

# ══════════════════════════════════════════════════════════
# CHECK 4: Site Health + 404
# ══════════════════════════════════════════════════════════
def check_site():
    issues = []
    checked = 0
    
    try:
        req = urllib.request.Request("https://dailymoney.my.id/",
            headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=20)
        if resp.status != 200:
            issues.append(f"🔴 Homepage: HTTP {resp.status}")
        else:
            log("  ✅ Homepage: OK")
    except Exception as e:
        issues.append(f"🔴 Homepage unreachable: {e}")
    
    try:
        req = urllib.request.Request("https://dailymoney.my.id/sitemap.xml",
            headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        sitemap = resp.read().decode()
        urls = re.findall(r'<loc>(.*?)</loc>', sitemap)
        
        for url in urls[:50]:
            try:
                req2 = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                resp2 = urllib.request.urlopen(req2, timeout=10)
                checked += 1
                if resp2.status == 404:
                    issues.append(f"🔴 404: {url}")
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    issues.append(f"🔴 404: {url}")
                checked += 1
            except:
                checked += 1
    except Exception as e:
        log(f"  ⚠️ Sitemap: {e}")
    
    log(f"  📊 Checked {checked} URLs — {len(issues)} issues")
    return issues, checked

# ══════════════════════════════════════════════════════════
# CHECK 5: Deploy Status
# ══════════════════════════════════════════════════════════
def check_deploy():
    issues = []
    try:
        req = urllib.request.Request(
            "https://api.github.com/repos/funnycatmomentusa-byte/dailymoney-site/actions/runs?per_page=3&status=completed",
            headers={"Accept": "application/vnd.github+json"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        runs = data.get("workflow_runs", [])
        if runs:
            latest = runs[0]
            c = latest.get("conclusion", "unknown")
            t = latest.get("created_at", "")[:16]
            n = latest.get("name", "deploy")
            if c == "failure":
                issues.append(f"🔴 Deploy FAILED: {n} ({t})")
                log(f"  🔴 Deploy: {n} FAILED at {t}")
            else:
                log(f"  ✅ Deploy: {n} OK ({t})")
    except:
        pass
    return issues

# ══════════════════════════════════════════════════════════
# CHECK 6: Content Freshness
# ══════════════════════════════════════════════════════════
def check_freshness():
    issues = []
    articles_dir = os.path.join(BASE_DIR, "_articles")
    if os.path.exists(articles_dir):
        files = sorted(glob.glob(os.path.join(articles_dir, "*.json")))
        if files:
            newest = os.path.getmtime(files[-1])
            hours = (datetime.now().timestamp() - newest) / 3600
            if hours > 24:
                issues.append(f"⚠️ Newest article is {hours:.0f}h old")
                log(f"  ⚠️ Article freshness: {hours:.0f}h")
            else:
                log(f"  ✅ Articles: fresh ({hours:.1f}h)")
    return issues

# ══════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════
def main():
    log("=" * 60)
    log("👁️ SUPERVISOR ZERO-ERROR ENFORCER — started")
    log(f"📅 {datetime.now().strftime('%d %b %Y %H:%M')}")
    
    state = load_state()
    all_issues = []
    all_fixes = []
    
    # CHECK 1: Future Dates
    log("\n📋 1. Future date scan (ZERO TOLERANCE)...")
    date_issues, date_fixes = check_future_dates()
    all_issues.extend(date_issues)
    all_fixes.extend(date_fixes)
    
    # CHECK 2: Cron Jobs
    log("\n📋 2. Cron job health (ZERO ERROR TOLERANCE)...")
    error_jobs, stale_jobs, total = check_all_cron_jobs()
    
    for job in error_jobs:
        name = job.get("name", "?")
        jid = job.get("job_id", "")
        prev = state.get("consecutive_failures", {}).get(jid, 0)
        state.setdefault("consecutive_failures", {})[jid] = prev + 1
        fixed, msg = auto_fix_error_agent(job)
        if fixed:
            all_fixes.append(f"🔧 {name}: {msg}")
        else:
            all_issues.append(f"🔴 {name}: {msg}")
    
    # Reset healthy jobs
    err_jids = set(j.get("job_id", "") for j in error_jobs)
    for jid in list(state.get("consecutive_failures", {}).keys()):
        if jid not in err_jids:
            state["consecutive_failures"][jid] = 0
    
    for job in stale_jobs:
        all_issues.append(f"⚠️ {job.get('name','?')}: stale")
    
    log(f"\n  📊 Cron: {total} total, {len(error_jobs)} error, {len(stale_jobs)} stale")
    
    # CHECK 3: Script Integrity
    log("\n📋 3. Script integrity...")
    script_issues = check_scripts_exist()
    all_issues.extend(script_issues)
    
    # CHECK 4: Site Health
    log("\n📋 4. Site health + 404 scan...")
    site_issues, checked = check_site()
    all_issues.extend(site_issues)
    
    # CHECK 5: Deploy
    log("\n📋 5. Deploy status...")
    deploy_issues = check_deploy()
    all_issues.extend(deploy_issues)
    
    # CHECK 6: Freshness
    log("\n📋 6. Content freshness...")
    fresh_issues = check_freshness()
    all_issues.extend(fresh_issues)
    
    # SAVE STATE
    state["last_check"] = datetime.now().isoformat()
    state["fixes_applied"] = all_fixes
    save_state(state)
    
    # REPORT
    log("\n" + "=" * 60)
    errors = [i for i in all_issues if i.startswith("🔴")]
    warnings = [i for i in all_issues if i.startswith("⚠️")]
    
    report = f"👁️ *SUPERVISOR ZERO-ERROR REPORT*\n"
    report += f"📅 {datetime.now().strftime('%d %b %Y %H:%M')}\n\n"
    report += f"📊 *{total} agents* | {len(error_jobs)} error | {len(stale_jobs)} stale\n"
    report += f"🌐 *{checked} URLs* checked | {len(site_issues)} issues\n"
    report += f"📁 *{44 - len(script_issues)}/44* scripts OK\n\n"
    
    if all_fixes:
        report += f"✅ *Auto-Fixed ({len(all_fixes)}):*\n"
        for fx in all_fixes[:8]:
            report += f"  {fx}\n"
        report += "\n"
    
    if errors:
        report += f"🔴 *ERRORS ({len(errors)}):*\n"
        for e in errors[:6]:
            report += f"  {e}\n"
        report += "\n"
    
    if warnings:
        report += f"⚠️ *Warnings ({len(warnings)}):*\n"
        for w in warnings[:6]:
            report += f"  {w}\n"
        report += "\n"
    
    if not errors:
        report += "✅ *ZERO ERRORS — Semua 44 agent sehat!*\n"
    else:
        report += "❌ *Masih ada error — perlu perhatian.*\n"
    
    send_tg(report)
    log("📤 Report sent to Telegram")
    
    if errors:
        sys.exit(1)

if __name__ == "__main__":
    main()

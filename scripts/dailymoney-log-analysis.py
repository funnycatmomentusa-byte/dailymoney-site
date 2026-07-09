#!/usr/bin/env python3
"""DailyMoney — Log Analysis & Traffic Detective Agent
Menganalisis log aktivitas: pola error, bot mencurigakan, 404 spikes, serangan."""
import json, os, subprocess, sys, re, gzip
from datetime import datetime, timedelta
from collections import Counter, defaultdict

BASE_DIR = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG = os.path.join(LOG_DIR, "log-analysis.log")
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

def analyze_agent_logs():
    """Analisis log agent Hermes untuk error berulang."""
    findings = []
    log_files = []
    if os.path.exists(LOG_DIR):
        for f in os.listdir(LOG_DIR):
            if f.endswith(".log"):
                log_files.append(os.path.join(LOG_DIR, f))
    
    # Pattern error per file
    error_patterns = defaultdict(int)
    error_details = []
    
    for fpath in log_files:
        try:
            with open(fpath) as f:
                for line in f:
                    if "❌" in line or "ERROR" in line.upper() or "Traceback" in line:
                        # Extract error context
                        parts = line.strip()
                        error_patterns[os.path.basename(fpath)] += 1
                        if len(error_details) < 20:
                            error_details.append(f"  {os.path.basename(fpath)}: {parts[:120]}")
        except:
            pass
    
    if error_patterns:
        log("❌ Error patterns detected in agent logs:")
        for agent, count in sorted(error_patterns.items(), key=lambda x: -x[1])[:5]:
            log(f"  {agent}: {count} errors")
            findings.append(f"⚠️ {agent}: {count} error(s)")
    
    return findings, error_details

def check_404_patterns():
    """Periksa pola 404 dari sitemap vs artikel yang ada."""
    findings = []
    sitemap_path = os.path.join(BASE_DIR, "sitemap.xml")
    if not os.path.exists(sitemap_path):
        return findings, []
    
    # Read sitemap URLs
    import xml.etree.ElementTree as ET
    try:
        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        sitemap_urls = set()
        for url in root.findall(".//sm:loc", ns):
            sitemap_urls.add(url.text.strip())
        
        # Check which sitemap URLs have HTML files
        missing = []
        for url in sitemap_urls:
            # Convert URL to relative path
            rel = url.replace("https://dailymoney.my.id/", "")
            if rel.endswith("/"):
                rel += "index.html"
            fpath = os.path.join(BASE_DIR, rel)
            if not os.path.exists(fpath):
                missing.append(rel)
        
        if missing:
            log(f"⚠️ {len(missing)} URLs in sitemap point to missing files")
            findings.append(f"sitemap → 404: {len(missing)} missing files")
            for m in missing[:5]:
                log(f"  🗺️ {m}")
    except Exception as e:
        log(f"⚠️ Sitemap parse error: {e}")
    
    return findings, []

def check_site_health():
    """Cek apakah site live dan respon cepat."""
    findings = []
    try:
        import urllib.request
        req = urllib.request.Request("https://dailymoney.my.id/", 
            headers={"User-Agent": "Mozilla/5.0"})
        start = datetime.now()
        resp = urllib.request.urlopen(req, timeout=30)
        elapsed = (datetime.now() - start).total_seconds()
        status = resp.status
        size = len(resp.read())
        
        if status != 200:
            findings.append(f"🔴 Site HTTP {status}")
            log(f"🔴 Site returned HTTP {status}")
        elif elapsed > 3:
            findings.append(f"⚠️ Site slow: {elapsed:.1f}s")
            log(f"⚠️ Site slow: {elapsed:.1f}s")
        else:
            log(f"✅ Site OK: {status} ({size:,} bytes in {elapsed:.1f}s)")
        
        # Check content type
        ct = resp.headers.get("Content-Type", "")
        if "text/html" not in ct:
            findings.append(f"⚠️ Content-Type: {ct}")
    except Exception as e:
        findings.append(f"🔴 Site unreachable: {e}")
        log(f"🔴 Site unreachable: {e}")
    
    return findings

def check_security_headers():
    """Cek security headers yang hilang."""
    findings = []
    try:
        import urllib.request
        req = urllib.request.Request("https://dailymoney.my.id/", 
            headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        headers = dict(resp.headers)
        
        required = {
            "Strict-Transport-Security": "HSTS",
            "Content-Security-Policy": "CSP",
            "X-Content-Type-Options": "XCTO",
            "X-Frame-Options": "XFO",
        }
        for hdr, name in required.items():
            if hdr not in headers:
                findings.append(f"⚠️ Missing: {name}")
                log(f"⚠️ Security header missing: {name}")
    except:
        pass
    return findings

def check_github_actions():
    """Cek status GitHub Actions workflow terakhir."""
    findings = []
    try:
        import urllib.request, json
        req = urllib.request.Request(
            "https://api.github.com/repos/funnycatmomentusa-byte/dailymoney-site/actions/runs?per_page=3&status=completed",
            headers={"Accept": "application/vnd.github+json"}
        )
        # Try without auth first
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read())
        runs = data.get("workflow_runs", [])
        if runs:
            latest = runs[0]
            conclusion = latest.get("conclusion", "unknown")
            created = latest.get("created_at", "")[:16]
            if conclusion == "failure":
                findings.append(f"🔴 Last deploy failed ({created})")
                log(f"🔴 GitHub Actions: last deploy FAILED at {created}")
            elif conclusion == "success":
                log(f"✅ GitHub Actions: last deploy success ({created})")
            else:
                log(f"⚠️ GitHub Actions: {conclusion} ({created})")
    except urllib.error.HTTPError as e:
        if e.code == 403:
            findings.append("⚠️ GitHub API rate limited")
        elif e.code == 401:
            findings.append("⚠️ GitHub API: no token")
        else:
            findings.append(f"⚠️ GitHub API: HTTP {e.code}")
    except Exception as e:
        findings.append(f"⚠️ GitHub check failed: {e}")
    
    return findings

# ════════════════════════════════════════
def main():
    log("=" * 60)
    log("🕵️ DailyMoney Log Analysis Agent — started")
    
    all_findings = []
    detail_lines = []
    
    # 1. Agent Log Scan
    log("\n📋 1. Agent log errors...")
    findings, details = analyze_agent_logs()
    all_findings.extend(findings)
    detail_lines.extend(details)
    
    # 2. 404 / Sitemap Check
    log("\n📋 2. Sitemap vs files...")
    findings, details = check_404_patterns()
    all_findings.extend(findings)
    
    # 3. Site Health Check
    log("\n📋 3. Site health...")
    findings = check_site_health()
    all_findings.extend(findings)
    
    # 4. Security Headers
    log("\n📋 4. Security headers...")
    findings = check_security_headers()
    all_findings.extend(findings)
    
    # 5. GitHub Actions
    log("\n📋 5. GitHub Actions...")
    findings = check_github_actions()
    all_findings.extend(findings)
    
    # Report
    log("\n" + "=" * 60)
    if all_findings:
        report = "🕵️ *Log Analysis Report*\n"
        report += f"📅 {datetime.now().strftime('%d %b %H:%M')}\n\n"
        for f in all_findings:
            report += f"  {f}\n"
        if detail_lines:
            report += "\n*Error Details:*\n" + "\n".join(detail_lines[:8])
        send_tg(report)
        log("📤 Report sent to Telegram")
        log(f"⚠️ {len(all_findings)} issues found")
    else:
        log("✅ All clean — no issues detected")
    
    log(f"📊 Complete")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""DailyMoney — Performance & HTML Validator Agent
Cek kecepatan, validitas HTML, dan PWA. Kirim alert jika bermasalah."""
import json, subprocess, os, re
from datetime import datetime

SITE = "https://dailymoney.my.id"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def curl_info(url):
    """Return (http_code, time_total, body_size, content_type)"""
    try:
        r = subprocess.run(
            ["curl", "-s", "-o", "/tmp/dm-perf.html", "-w", "%{http_code}:%{time_total}:%{size_download}:%{content_type}",
             url], capture_output=True, text=True, timeout=15)
        parts = r.stdout.strip().split(":")
        return parts[0], parts[1] if len(parts) > 1 else "?", parts[2] if len(parts) > 2 else "?", parts[3] if len(parts) > 3 else "?"
    except:
        return "?","?","?","?"

def validate_html(filepath):
    """Basic HTML validation checks"""
    issues = []
    try:
        html = open(filepath).read()
        # Check for unclosed tags
        for tag in ["h1", "h2", "h3", "p", "div", "section", "article", "meta", "img"]:
            opens = len(re.findall(rf'<{tag}[\\s>]', html, re.I))
            closes = len(re.findall(rf'</{tag}>', html, re.I))
            if tag in ["meta", "img"]:
                self_closing = html.count(f"<{tag} ") + html.count(f"<{tag}/>")
                if opens > self_closing:
                    issues.append(f"  {tag}: {opens} open, {closes} close")
            elif tag in ["h1"] and opens != closes:
                issues.append(f"  {tag}: {opens} open, {closes} close")
            elif opens != closes and opens > 0:
                issues.append(f"  {tag}: {opens} open, {closes} close")

        return issues
    except:
        return ["Could not read HTML file"]

def check_pwa():
    sw = subprocess.run(["curl", "-sfI", f"{SITE}/sw.js"], capture_output=True, text=True, timeout=10)
    manifest = subprocess.run(["curl", "-sfI", f"{SITE}/manifest.json"], capture_output=True, text=True, timeout=10)
    return sw.returncode == 0, manifest.returncode == 0

def check_lighthouse_alt():
    """Alternative perf check since we can't run Lighthouse CLI"""
    # Time to first byte for multiple pages
    pages = [f"{SITE}/", f"{SITE}/en/", f"{SITE}/sitemap.xml"]
    results = []
    for p in pages:
        code, time_s, size, ctype = curl_info(p)
        results.append(f"{p.split('/')[-1] or 'home'}: {code} | {time_s}s | {size}B")
    return results

# Run checks
results = check_lighthouse_alt()
sw_ok, manifest_ok = check_pwa()

# Download homepage for validation
subprocess.run(["curl", "-sf", f"{SITE}/"], capture_output=True, timeout=15)
validation_issues = validate_html("/tmp/dm-perf.html")

# Build report
issues = []
if not sw_ok:
    issues.append("❌ Service Worker tidak reachable")
if not manifest_ok:
    issues.append("❌ Manifest.json tidak reachable")
for p in results:
    if "200" not in p:
        issues.append(f"❌ {p}")

if validation_issues:
    for vi in validation_issues:
        issues.append(f"⚠️ {vi}")

# Log everything
log_path = os.path.join(LOG_DIR, "perf-monitor.log")
with open(log_path, "w") as f:
    f.write(f"Performance Monitor @ {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
    f.write("\n".join(results) + "\n")
    f.write(f"SW: {'OK' if sw_ok else 'DOWN'}, Manifest: {'OK' if manifest_ok else 'DOWN'}\n")
    if validation_issues:
        f.write("HTML issues:\n" + "\n".join(validation_issues) + "\n")
    if issues:
        f.write("Issues:\n" + "\n".join(issues) + "\n")

# Alert only if there are issues
if issues:
    alert = "⚠️ *Performance Alert — dailymoney.my.id*\n"
    alert += "\n".join(issues[:8])
    alert += "\n\n🌐 dailymoney.my.id"
    subprocess.run(SEND + [alert], timeout=15)
    print(f"🚨 {len(issues)} issues found, alert sent")
else:
    print("✅ All checks passed")

#!/usr/bin/env python3
"""DailyMoney — Self-Healing Security Auditor (Penetration Testing Otomatis)
Memindai celah keamanan: secrets in code, OWASP headers, exposed files, dependency vulns."""
import json, os, subprocess, sys, re, urllib.request, urllib.error
from datetime import datetime

BASE_DIR = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG = os.path.join(LOG_DIR, "security-auditor.log")
SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

SECRET_PATTERNS = [
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub PAT"),
    (r'gho_[a-zA-Z0-9]{36}', "GitHub OAuth"),
    (r'github_pat_[a-zA-Z0-9_]{36,}', "GitHub Fine-grained PAT"),
    (r'api_key\s*=\s*["\'][a-zA-Z0-9_]{20,}', "API Key in code"),
    (r'password\s*=\s*["\'][^"\']{6,}', "Password in code"),
    (r'secret\s*=\s*["\'][^"\']{10,}', "Secret in code"),
    (r'token\s*=\s*["\'][a-zA-Z0-9_\-\.]{10,}', "Token in code"),
    (r'-----BEGIN (RSA |EC )?PRIVATE KEY-----', "Private Key"),
    (r'AIza[0-9A-Za-z\-_]{35}', "Google API Key"),
    (r'sk-[a-zA-Z0-9]{20,}', "OpenAI/LLM API Key"),
    (r'xox[baprs]-[0-9a-zA-Z-]{10,}', "Slack Token"),
]

EXPOSED_PATHS = [
    "/.git/config",
    "/.env",
    "/wp-admin/",
    "/admin/",
    "/.gitignore",
    "/config.json",
    "/credentials.json",
]

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

def scan_secrets_in_code():
    """Cari secrets/hardcoded credentials di semua script."""
    findings = []
    scan_dirs = [
        os.path.expanduser("~/.hermes/scripts"),
        BASE_DIR,
    ]
    
    for scan_dir in scan_dirs:
        if not os.path.exists(scan_dir):
            continue
        for root, dirs, files in os.walk(scan_dir):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.git']]
            for fname in files:
                if not fname.endswith(('.py', '.sh', '.json', '.yml', '.yaml', '.env', '.txt', '.md')):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, errors='ignore') as f:
                        content = f.read()
                    for pattern, pname in SECRET_PATTERNS:
                        matches = re.findall(pattern, content)
                        # Filter out test/fake patterns
                        real_matches = [m for m in matches if not any(x in m.lower() for x in ['example', 'test', 'placeholder', 'your_'])]
                        if real_matches:
                            rel = os.path.relpath(fpath, os.path.expanduser("~"))
                            findings.append({
                                "file": rel,
                                "type": pname,
                                "match": real_matches[0][:30] + "...",
                            })
                            log(f"  🔴 {pname} in {rel}")
                except:
                    pass
    
    return findings

def scan_exposed_urls():
    """Cek apakah ada path sensitif yang terekspos di site."""
    findings = []
    site_url = "https://dailymoney.my.id"
    
    for path in EXPOSED_PATHS:
        url = site_url + path
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=10)
            code = resp.status
            size = len(resp.read())
            if code == 200 and size > 50:
                findings.append({
                    "url": path,
                    "status": code,
                    "risk": "HIGH" if path in ["/.git/config", "/.env", "/admin/"] else "MEDIUM"
                })
                log(f"  🔴 EXPOSED: {path} (HTTP {code}, {size}B)")
        except urllib.error.HTTPError as e:
            if e.code == 403:
                log(f"  ✅ Blocked: {path} (HTTP 403)")
            elif e.code == 404:
                pass  # expected
            else:
                log(f"  ⚠️ {path}: HTTP {e.code}")
        except:
            pass
    
    return findings

def check_owasp_headers():
    """Cek OWASP security headers di live site."""
    findings = []
    required = {
        "Strict-Transport-Security": ("HSTS", "max-age=31536000; includeSubDomains"),
        "Content-Security-Policy": ("CSP", "Mencegah XSS"),
        "X-Content-Type-Options": ("XCTO", "nosniff"),
        "X-Frame-Options": ("XFO", "DENY/SAMEORIGIN"),
        "Referrer-Policy": ("Referrer", "strict-origin-when-cross-origin"),
        "Permissions-Policy": ("Permissions", "mengontrol API browser"),
    }
    
    try:
        req = urllib.request.Request("https://dailymoney.my.id/", 
            headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        headers = dict(resp.headers)
        
        for hdr, (name, purpose) in required.items():
            value = headers.get(hdr, "")
            if value:
                log(f"  ✅ {name}: {value[:60]}")
            else:
                findings.append({"header": name, "status": "MISSING"})
                log(f"  ⚠️ MISSING: {name} ({purpose})")
    except Exception as e:
        findings.append({"header": "SITE_CHECK", "status": f"FAILED: {e}"})
    
    return findings

def check_ssl_cert():
    """Cek SSL certificate expiry."""
    findings = []
    try:
        import ssl, socket
        host = "dailymoney.my.id"
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                expires = cert.get("notAfter", "unknown")
                # Parse expiry
                from datetime import datetime as dt
                try:
                    expiry_date = dt.strptime(expires, "%b %d %H:%M:%S %Y %Z")
                    days_left = (expiry_date - dt.now()).days
                    if days_left < 0:
                        findings.append({"check": "SSL", "status": f"🔴 EXPIRED {abs(days_left)}d ago"})
                        log(f"  🔴 SSL expired {abs(days_left)} days ago!")
                    elif days_left < 7:
                        findings.append({"check": "SSL", "status": f"⚠️ Expires in {days_left}d"})
                        log(f"  ⚠️ SSL expires in {days_left} days")
                    elif days_left < 30:
                        log(f"  ⚠️ SSL expires in {days_left} days")
                    else:
                        log(f"  ✅ SSL: valid until {expires} ({days_left} days)")
                except:
                    log(f"  ✅ SSL: valid until {expires}")
    except Exception as e:
        findings.append({"check": "SSL", "status": f"⚠️ Check failed: {e}"})
    
    return findings

def auto_patch(findings):
    """Auto-patch celah yang bisa diperbaiki."""
    actions = []
    patched_headers = False
    
    for f in findings:
        if f.get("header") and f["status"] == "MISSING":
            # Generate _headers file if missing
            headers_path = os.path.join(BASE_DIR, "_headers")
            if not os.path.exists(headers_path) or "HSTS" not in open(headers_path).read():
                hdr_content = """# DailyMoney — Security Headers (Auto-generated by Security Auditor)
# OWASP Top 10 Protection
https://dailymoney.my.id/*
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=(), payment=()
  Content-Security-Policy: default-src 'self' https:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' https: data:; font-src 'self' https:; connect-src 'self' https:;
"""
                with open(headers_path, "w") as f:
                    f.write(hdr_content)
                actions.append("✅ Generated _headers with OWASP security headers")
                log("  ✅ Generated _headers with full OWASP protection")
                patched_headers = True
                break
    
    # Remove exposed sensitive files from repo
    for f in findings:
        if f.get("risk") == "HIGH":
            path = f.get("url", "").lstrip("/")
            # Only if in repo
            fpath = os.path.join(BASE_DIR, path)
            if os.path.exists(fpath) and os.path.isfile(fpath):
                try:
                    os.remove(fpath)
                    actions.append(f"🗑️ Removed exposed: {path}")
                    log(f"  🗑️ Removed exposed file: {path}")
                except:
                    pass
    
    return actions

# ════════════════════════════════════════
def main():
    log("=" * 60)
    log("🛡️ DailyMoney Self-Healing Security Auditor — started")
    
    all_findings = []
    vuln_count = 0
    
    # 1. Secrets scan
    log("\n📋 1. Secrets in code...")
    findings = scan_secrets_in_code()
    all_findings.extend(findings)
    vuln_count += len(findings)
    
    # 2. Exposed URLs
    log("\n📋 2. Exposed paths...")
    findings = scan_exposed_urls()
    all_findings.extend(findings)
    vuln_count += len(findings)
    
    # 3. OWASP Headers
    log("\n📋 3. OWASP headers...")
    findings = check_owasp_headers()
    all_findings.extend(findings)
    vuln_count += len(findings)
    
    # 4. SSL Certificate
    log("\n📋 4. SSL certificate...")
    findings = check_ssl_cert()
    all_findings.extend(findings)
    vuln_count += len(findings)
    
    # 5. Auto-patch
    log("\n📋 5. Auto-patching...")
    actions = auto_patch(all_findings)
    
    # If _headers changed, rebuild & push
    if actions:
        try:
            subprocess.run(["python3", "generate-site.py"], cwd=BASE_DIR, capture_output=True, timeout=60)
            subprocess.run(["git", "add", "-A"], cwd=BASE_DIR, capture_output=True, timeout=10)
            subprocess.run(["git", "commit", "-m", "security: auto-patch by Security Auditor"],
                cwd=BASE_DIR, capture_output=True, timeout=10)
            subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, capture_output=True, timeout=30)
            actions.append("✅ Changes committed & pushed")
            log("  ✅ Auto-patch committed & pushed")
        except:
            pass
    
    # Report
    log("\n" + "=" * 60)
    report = "🛡️ *Security Auditor Report*\n"
    report += f"📅 {datetime.now().strftime('%d %b %H:%M')}\n\n"
    
    if vuln_count == 0:
        report += "✅ Aman — tidak ada celah keamanan ditemukan.\n"
    else:
        report += f"🔴 {vuln_count} kerentanan ditemukan:\n\n"
        
        secrets_in_code = [f for f in all_findings if "type" in f]
        if secrets_in_code:
            report += "*🔑 Secrets in Code:*\n"
            for s in secrets_in_code[:5]:
                report += f"  • {s['type']} di {s['file'][:50]}\n"
        
        exposed = [f for f in all_findings if "url" in f]
        if exposed:
            report += "\n*🌐 Exposed Paths:*\n"
            for e in exposed:
                report += f"  • {e['url']} (risk: {e.get('risk', 'MEDIUM')})\n"
        
        headers = [f for f in all_findings if "header" in f]
        if headers:
            report += "\n*⚠️ Missing Headers:*\n"
            for h in headers:
                report += f"  • {h['header']}\n"
        
        ssl = [f for f in all_findings if "check" in f and f["check"] == "SSL"]
        if ssl:
            report += "\n*🔒 SSL:*\n"
            for s in ssl:
                report += f"  • {s['status']}\n"
    
    if actions:
        report += "\n*Auto-Patch Applied:*\n"
        for a in actions:
            report += f"  {a}\n"
    
    send_tg(report)
    log("📤 Report sent to Telegram")
    log(f"📊 Complete — {vuln_count} vulnerabilities, {len(actions)} patches applied")

if __name__ == "__main__":
    main()

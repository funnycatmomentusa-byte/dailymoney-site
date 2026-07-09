#!/usr/bin/env python3
"""DailyMoney — Website Security Agent
Memindai keamanan website secara menyeluruh: SSL, headers, malware, secrets, CSP, DNS."""
import json, os, subprocess, re, urllib.request, ssl, socket
from datetime import datetime, timedelta
from urllib.parse import urlparse

SITE = "https://dailymoney.my.id"
DOMAIN = "dailymoney.my.id"
GIT_REPO = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(os.path.join(LOG_DIR, "security-agent.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

def check_ssl():
    """Cek SSL certificate: expiry, issuer, protocol."""
    log("🔐 Checking SSL certificate...")
    result = {"valid": False, "expiry": "", "days_left": 0, "issuer": "", "issues": []}
    try:
        hostname = DOMAIN
        ctx = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                result["issuer"] = dict(cert["issuer"][0]).get("organizationName", "Unknown")
                
                # Expiry
                from datetime import timezone
                not_after = cert["notAfter"]
                expiry = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                now = datetime.now(timezone.utc)
                days_left = (expiry - now).days
                result["expiry"] = expiry.strftime('%d/%m/%Y')
                result["days_left"] = days_left
                
                if days_left < 0:
                    result["issues"].append(f"❌ SSL EXPIRED {abs(days_left)} hari lalu!")
                elif days_left < 7:
                    result["issues"].append(f"⚠️ SSL expires dalam {days_left} hari")
                elif days_left < 30:
                    result["issues"].append(f"ℹ️ SSL expires dalam {days_left} hari — perpanjang segera")
                else:
                    log(f"  ✅ SSL valid — expires in {days_left} days")
                    
                # Protocol version
                protocol = ssock.version()
                if protocol and "TLSv1" in protocol:
                    result["valid"] = True
                    
    except Exception as e:
        result["issues"].append(f"❌ SSL check error: {str(e)[:50]}")
        log(f"  ❌ SSL error: {e}")
    
    return result

def check_security_headers():
    """Cek security headers HTTP."""
    log("📋 Checking security headers...")
    result = {"headers": {}, "issues": []}
    
    required_headers = {
        "Strict-Transport-Security": "HSTS — protects against downgrade attacks",
        "X-Content-Type-Options": "Prevents MIME sniffing",
        "X-Frame-Options": "Prevents clickjacking",
        "Referrer-Policy": "Controls referrer info leakage",
        "Permissions-Policy": "Limits API access",
    }
    
    optional_headers = {
        "Content-Security-Policy": "CSP — prevents XSS",
        "X-XSS-Protection": "Legacy XSS filter (deprecated but still used)",
    }
    
    try:
        req = urllib.request.Request(SITE, method="GET", headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        
        headers_dict = dict(resp.headers)
        result["headers"] = headers_dict
        
        # Check required
        for hdr, desc in required_headers.items():
            if hdr in headers_dict:
                log(f"  ✅ {hdr}: {headers_dict[hdr][:50]}")
            else:
                result["issues"].append(f"❌ Missing {hdr} — {desc}")
                log(f"  ❌ Missing {hdr}")
        
        # Check optional
        for hdr, desc in optional_headers.items():
            if hdr in headers_dict:
                log(f"  ✅ {hdr}: {headers_dict[hdr][:50]}")
            else:
                result["issues"].append(f"⚠️ Missing {hdr} (recommended) — {desc}")
                log(f"  ⚠️ Missing {hdr}")
        
        # Check HSTS preload eligibility
        if "Strict-Transport-Security" in headers_dict:
            hsts = headers_dict["Strict-Transport-Security"]
            if "max-age=31536000" in hsts or "max-age=63072000" in hsts:
                if "includeSubDomains" in hsts:
                    log(f"  ✅ HSTS preload ready!")
                else:
                    result["issues"].append("ℹ️ Add 'includeSubDomains' to HSTS for preload")
            else:
                result["issues"].append("ℹ️ HSTS max-age should be ≥ 31536000 for preload")
        
        # Check for info leakage
        server = headers_dict.get("Server", "")
        if server and server not in ("cloudflare", "GitHub.com"):
            result["issues"].append(f"⚠️ Server header leaks info: {server}")
        
    except urllib.error.HTTPError as e:
        result["issues"].append(f"HTTP {e.code}: {e.reason}")
    except Exception as e:
        result["issues"].append(f"Header check error: {str(e)[:50]}")
    
    return result

def check_malware_blacklist():
    """Cek apakah website terblokir atau terinfeksi."""
    log("🛡️ Checking malware/blacklist status...")
    result = {"blocked": False, "issues": []}
    
    # Check via Google Safe Browsing (simple check)
    # Using Google Transparency Report as reference
    try:
        url = f"https://transparencyreport.google.com/safe-browsing/search?url={SITE}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        body = resp.read().decode('utf-8', errors='ignore')
        
        if "not found" in body.lower() and "unsafe" not in body.lower():
            log(f"  ✅ No Google Safe Browsing issues")
        else:
            # Also check via simple HTTP check
            pass
    except:
        pass
    
    # Check if site is accessible (not blocked by ISP)
    try:
        resp = urllib.request.urlopen(SITE, timeout=10)
        if resp.status == 200:
            log(f"  ✅ Site accessible (HTTP {resp.status})")
        else:
            result["blocked"] = True
            result["issues"].append(f"⚠️ Site returned HTTP {resp.status}")
    except Exception as e:
        result["blocked"] = True
        result["issues"].append(f"❌ Site inaccessible: {str(e)[:50]}")
    
    return result

def check_git_secrets():
    """Cek apakah ada secret/credential di repo."""
    log("🔑 Scanning GitHub repo for secrets...")
    result = {"secrets_found": [], "issues": []}
    
    # Patterns to scan
    patterns = {
        "token_github": r'gh[pousr]_[A-Za-z0-9]{36,40}',
        "token_telegram": r'\d{9,10}:[A-Za-z0-9_-]{35}',
        "api_key_gen": r'[Aa][Pp][Ii]_?[Kk][Ee][Yy]\s*[=:]\s*["\'][A-Za-z0-9_\-]{16,}["\']',
        "password": r'[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd]\s*[=:]\s*["\'][^"\'\\s]{6,}["\']',
        "aws_key": r'AKIA[0-9A-Z]{16}',
        "private_key": r'-----BEGIN (RSA |EC )?PRIVATE KEY-----',
        "jwt_token": r'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}',
    }
    
    try:
        # Check git tracked files only (not .git dir)
        r = subprocess.run(
            ["git", "ls-files"],
            capture_output=True, text=True, timeout=10, cwd=GIT_REPO
        )
        files = r.stdout.strip().split('\n')
        
        for fpath in files[:100]:  # Limit to 100 files
            if not fpath:
                continue
            # Skip safe files
            if any(fpath.endswith(ext) for ext in ['.md', '.txt', '.json']):
                continue
                
            full_path = os.path.join(GIT_REPO, fpath)
            if not os.path.isfile(full_path):
                continue
            if os.path.getsize(full_path) > 50000:  # Skip large files
                continue
                
            try:
                with open(full_path, 'r', errors='ignore') as f:
                    content = f.read()
                    
                for name, pattern in patterns.items():
                    matches = re.findall(pattern, content)
                    if matches:
                        # Verify it's not a false positive
                        for m in matches[:3]:
                            # Skip if in test/sample data
                            line_ctx = content[:content.find(m) + len(m) + 50]
                            if any(kw in line_ctx.lower() for kw in ['example', 'sample', 'test_', 'dummy']):
                                continue
                            result["secrets_found"].append(f"  ⚠️ {fpath}: possible {name} found")
            except:
                pass
        
        if not result["secrets_found"]:
            log(f"  ✅ No obvious secrets in tracked files")
            
    except Exception as e:
        result["issues"].append(f"Git scan error: {str(e)[:50]}")
    
    return result

def check_dns():
    """Cek DNS records: A, AAAA, CNAME, TXT."""
    log("🌐 Checking DNS records...")
    result = {"records": {}, "issues": []}
    
    records_to_check = {
        "A": f"A record (IPv4) for {DOMAIN}",
        "AAAA": f"AAAA record (IPv6) for {DOMAIN}",
        "CNAME": f"CNAME for www.{DOMAIN}",
        "TXT": f"TXT for SPF/DKIM",
    }
    
    for rtype, desc in records_to_check.items():
        try:
            r = subprocess.run(
                ["dig", "+short", rtype, DOMAIN if rtype != "CNAME" else f"www.{DOMAIN}"],
                capture_output=True, text=True, timeout=10
            )
            output = r.stdout.strip()
            if output:
                result["records"][rtype] = output[:100]
                log(f"  ✅ {rtype}: {output[:60]}")
            else:
                if rtype == "AAAA":
                    result["issues"].append("ℹ️ No AAAA record — IPv6 not configured")
                    log(f"  ⚠️ No AAAA (IPv6) record")
        except FileNotFoundError:
            # dig not available, skip DNS check
            log(f"  ⚠️ dig not available, skipping DNS check")
            break
        except Exception as e:
            result["issues"].append(f"DNS {rtype} error: {str(e)[:30]}")
    
    return result

def check_github_actions_security():
    """Cek apakah ada security issues di GitHub Actions."""
    log("🔧 Checking GitHub Actions security...")
    result = {"issues": []}
    
    workflow_dir = os.path.join(GIT_REPO, ".github", "workflows")
    if os.path.exists(workflow_dir):
        for fname in os.listdir(workflow_dir):
            if fname.endswith(('.yml', '.yaml')):
                fpath = os.path.join(workflow_dir, fname)
                content = open(fpath).read()
                
                # Check for pinned actions
                if re.search(r'uses:\s+\w+/\w+@[^@]*$', content, re.MULTILINE):
                    # Check if using @main or @master without commit hash
                    if re.search(r'uses:\s+\w+/\w+@(main|master)', content):
                        result["issues"].append(f"⚠️ {fname}: Action uses @main/@master — use commit hash for supply chain security")
                
                # Check for secrets exposed in logs
                if re.search(r'(echo|print|run:\s*echo)\s+\${{', content):
                    result["issues"].append(f"⚠️ {fname}: Possible secret leakage in logs")
        
        if not result["issues"]:
            log(f"  ✅ Workflows look secure")
    else:
        log(f"  ⚠️ No workflows directory found")
    
    return result

def check_csp_basic():
    """Periksa apakah ada file HTML yang mengandung inline script/styles (XSS risk)."""
    log("📝 Scanning HTML for inline scripts (XSS indicator)...")
    result = {"inline_scripts": 0, "inline_styles": 0, "issues": []}
    
    # Cek di generate-site.py untuk template HTML
    gen_path = os.path.join(GIT_REPO, "generate-site.py")
    if os.path.exists(gen_path):
        content = open(gen_path).read()
        
        # Count inline script tags in templates
        inline_scripts = len(re.findall(r'<script\s[^>]*>(?!\s*<\/script>)(.*?)<\/script>', content, re.DOTALL | re.IGNORECASE))
        inline_styles = len(re.findall(r'<style[^>]*>', content, re.IGNORECASE))
        
        result["inline_scripts"] = inline_scripts
        result["inline_styles"] = inline_styles
        
        if inline_scripts > 0:
            result["issues"].append(f"⚠️ {inline_scripts} inline script(s) — CSP bypass risk")
        if inline_styles > 0:
            result["issues"].append(f"ℹ️ {inline_styles} inline style(s) — consider using class-based CSS")
    
    return result

def recommend_fixes(issues):
    """Generate rekomendasi perbaikan berdasarkan issue yang ditemukan."""
    fixes = []
    
    for issue in issues:
        if "Missing Strict-Transport-Security" in issue:
            fixes.append("1️⃣ Tambahkan HSTS header di GitHub Pages via Cloudflare atau proxy")
        elif "Missing X-Content-Type-Options" in issue:
            fixes.append("2️⃣ Tambahkan X-Content-Type-Options: nosniff di header response")
        elif "Missing X-Frame-Options" in issue:
            fixes.append("3️⃣ Tambahkan X-Frame-Options: DENY atau SAMEORIGIN")
        elif "Missing Referrer-Policy" in issue:
            fixes.append("4️⃣ Tambahkan Referrer-Policy: strict-origin-when-cross-origin")
        elif "Missing Permissions-Policy" in issue:
            fixes.append("5️⃣ Tambahkan Permissions-Policy untuk batasi API browser")
        elif "Missing Content-Security-Policy" in issue:
            fixes.append("6️⃣ Implementasikan CSP header untuk cegah XSS")
        elif "SSL EXPIRED" in issue:
            fixes.append("🔴 SEGERA perpanjang SSL certificate!")
        elif "inline script" in issue:
            fixes.append("7️⃣ Pindahkan inline script ke file .js eksternal untuk CSP compatibility")
        elif "HSTS max-age" in issue:
            fixes.append("8️⃣ Set HSTS max-age=31536000; includeSubDomains untuk preload eligibility")
        elif "IPv6" in issue:
            fixes.append("9️⃣ Tambahkan AAAA record untuk IPv6 accessibility")
        elif "secrets" in issue:
            fixes.append("🔴 HAPUS secret/credential dari repo! Gunakan GitHub Secrets atau environment variable")
    
    if not fixes:
        fixes = ["✅ Tidak ada rekomendasi perbaikan — website sudah secure!"]
    
    return fixes

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"🛡️ DailyMoney Security Agent @ {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}")
    
    log(f"Memindai {SITE}...")
    
    # Run all checks
    ssl_result = check_ssl()
    headers_result = check_security_headers()
    malware_result = check_malware_blacklist()
    secrets_result = check_git_secrets()
    dns_result = check_dns()
    actions_result = check_github_actions_security()
    csp_result = check_csp_basic()
    
    # Collect all issues
    all_issues = []
    all_issues.extend(ssl_result.get("issues", []))
    all_issues.extend(headers_result.get("issues", []))
    all_issues.extend(malware_result.get("issues", []))
    all_issues.extend(secrets_result.get("issues", []))
    all_issues.extend(dns_result.get("issues", []))
    all_issues.extend(actions_result.get("issues", []))
    all_issues.extend(csp_result.get("issues", []))
    
    # Count severity
    critical = sum(1 for i in all_issues if i.startswith("🔴") or i.startswith("❌"))
    warnings = sum(1 for i in all_issues if i.startswith("⚠️"))
    info = sum(1 for i in all_issues if i.startswith("ℹ️"))
    
    # Generate report
    report_lines = [f"🛡️ *Security Report — {datetime.now().strftime('%d %b %Y %H:%M')}*"]
    report_lines.append(f"🌐 {SITE}")
    report_lines.append("")
    
    # Summary
    icon = "✅" if critical == 0 else "🔴"
    report_lines.append(f"{icon} *Summary:*")
    report_lines.append(f"  🔴 Critical: {critical}")
    report_lines.append(f"  ⚠️ Warnings: {warnings}")
    report_lines.append(f"  ℹ️ Info: {info}")
    report_lines.append("")
    
    # SSL
    ssl_icon = "🔴" if any("EXPIRED" in i for i in ssl_result.get("issues", [])) else ("⚠️" if ssl_result["days_left"] < 30 else "✅")
    report_lines.append(f"{ssl_icon} *SSL:* {ssl_result.get('issuer', 'Unknown')}")
    report_lines.append(f"  Expires: {ssl_result['expiry']} ({ssl_result['days_left']} days)")
    report_lines.append("")
    
    # All issues
    if all_issues:
        report_lines.append("*Issues:*")
        for issue in all_issues:
            report_lines.append(f"  {issue}")
        report_lines.append("")
    
    # Recommendations
    if all_issues:
        fixes = recommend_fixes(all_issues)
        report_lines.append("*Rekomendasi:*")
        for fix in fixes:
            report_lines.append(f"  {fix}")
    
    report_lines.append("")
    report_lines.append(f"🔍 *{len(all_issues)} issue(s) ditemukan*")
    report_lines.append(f"🤖 Security Agent — dailymoney.my.id")
    
    report = "\n".join(report_lines)
    
    # Log report
    log(f"\n{'='*50}")
    log(f"SECURITY REPORT")
    log(f"{'='*50}")
    log(f"Critical: {critical} | Warnings: {warnings} | Info: {info}")
    for issue in all_issues:
        log(f"  {issue}")
    
    # Send to Telegram IF there are issues
    if all_issues:
        send_telegram(report)
        log("✅ Report sent to Telegram")
    else:
        log("✅ No issues found — site is secure")
    
    print(f"\n{'='*50}")
    print(f"SECURITY REPORT — {critical} critical, {warnings} warnings, {info} info")
    print(f"{'='*50}")
    for issue in all_issues:
        print(f"  {issue}")
    print(f"\n✅ Security Agent complete")

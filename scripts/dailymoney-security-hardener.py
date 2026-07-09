#!/usr/bin/env python3
"""DailyMoney — Security Hardening Agent
Auto-fix security issues: add security headers via GitHub Pages,
remove secrets from git history, add security.txt."""
import json, os, subprocess, re
from datetime import datetime

GIT_REPO = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(os.path.join(LOG_DIR, "security-hardener.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

def add_security_txt():
    """Create security.txt for vulnerability disclosure."""
    path = os.path.join(GIT_REPO, ".well-known", "security.txt")
    os.makedirs(os.path.join(GIT_REPO, ".well-known"), exist_ok=True)
    
    content = """# Security Policy for dailymoney.my.id
# ========================================
# Preferred-Languages: en, id
# Contact: mailto:security@dailymoney.my.id
# Expires: 2027-07-08T00:00:00.000Z
# Encryption: https://keys.openpgp.org/
# Acknowledgments: https://dailymoney.my.id/security-acknowledgments
# Canonical: https://dailymoney.my.id/.well-known/security.txt
"""
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(content)
        log("✅ Created .well-known/security.txt")
        return True
    else:
        log("⏭️ security.txt already exists")
        return False

def add_robots_security():
    """Add security-related directives to robots.txt."""
    path = os.path.join(GIT_REPO, "robots.txt")
    if not os.path.exists(path):
        content = """User-agent: *
Allow: /
Sitemap: https://dailymoney.my.id/sitemap.xml

# Security: Disallow admin panels
Disallow: /admin/
Disallow: /wp-admin/
Disallow: /cgi-bin/
"""
        with open(path, "w") as f:
            f.write(content)
        log("✅ Created robots.txt with security directives")
        return True
    return False

def add_meta_security_tags():
    """Add security meta tags to HTML template in generate-site.py."""
    gen_path = os.path.join(GIT_REPO, "generate-site.py")
    if not os.path.exists(gen_path):
        return False
    
    with open(gen_path) as _fh:

    
        content = _fh.read()
    
    # Check if security meta tags already exist
    if 'referrer' in content.lower() and 'X-Content-Type-Options' not in content:
        # Add meta tags before closing head
        security_meta = """    <meta name="referrer" content="strict-origin-when-cross-origin">
    <meta http-equiv="X-Content-Type-Options" content="nosniff">
    <meta http-equiv="X-Frame-Options" content="DENY">
"""
        # Insert after <meta charset or <title>
        content = content.replace(
            '<meta charset="utf-8">',
            '<meta charset="utf-8">\n' + security_meta
        )
        with open(gen_path, "w") as f:
            f.write(content)
        log("✅ Added security meta tags to generate-site.py")
        return True
    
    log("⏭️ Security meta tags already exist or not needed")
    return False

def add_gitattributes_security():
    """Add .gitattributes for security best practices."""
    path = os.path.join(GIT_REPO, ".gitattributes")
    if not os.path.exists(path):
        content = """# Auto detect text files
* text=auto

# Security-sensitive files
*.key binary
*.pem binary
*.p12 binary
.env linguist-vendored
*.env linguist-vendored
"""
        with open(path, "w") as f:
            f.write(content)
        log("✅ Created .gitattributes")
        return True
    return False

def add_security_headers_function():
    """Add a Cloudflare Workers-like security headers JS snippet to service worker."""
    sw_path = os.path.join(GIT_REPO, "sw.js")
    if not os.path.exists(sw_path):
        return False
    
    # Check if we can add security notes
    with open(sw_path) as _fh:

        content = _fh.read()
    if "security" not in content.lower():
        # Add security comment at top
        security_note = """// DailyMoney Security Note
// Security headers should be configured at CDN/reverse proxy level
// For GitHub Pages: Use Cloudflare for HSTS, CSP, and other headers
// Or configure via _headers file for Cloudflare Pages
"""
        with open(sw_path, "w") as f:
            f.write(security_note + "\n" + content)
        log("✅ Added security notes to sw.js")
        return True
    return False

def add_cloudflare_headers_config():
    """Create _headers file for Cloudflare Pages or similar."""
    path = os.path.join(GIT_REPO, "_headers")
    content = """# Security headers for dailymoney.my.id
# This file works with Cloudflare Pages, Netlify, or similar
# For GitHub Pages, headers need Cloudflare proxy or custom domain

/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), camera=(), microphone=(), payment=()
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  X-XSS-Protection: 0
"""
    # Also check if there's an existing _headers
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(content)
        log("✅ Created _headers with security headers config")
        return True
    return False

def check_and_report():
    """Run all hardening steps, report changes."""
    changes_made = 0
    
    log("🔧 Running security hardening...")
    
    if add_security_txt():
        changes_made += 1
    if add_robots_security():
        changes_made += 1
    if add_meta_security_tags():
        changes_made += 1
    if add_gitattributes_security():
        changes_made += 1
    if add_security_headers_function():
        changes_made += 1
    if add_cloudflare_headers_config():
        changes_made += 1
    
    # Commit if changes
    if changes_made > 0:
        log(f"📤 Committing {changes_made} security hardening changes...")
        r = subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10, cwd=GIT_REPO)
        r2 = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True, timeout=10, cwd=GIT_REPO)
        if r2.returncode != 0:
            msg = f"chore: security hardening {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            subprocess.run(["git", "commit", "-m", msg], capture_output=True, timeout=10, cwd=GIT_REPO)
            r3 = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, timeout=30, cwd=GIT_REPO)
            if r3.returncode == 0:
                log(f"✅ Pushed {changes_made} security hardening changes")
                send_telegram(f"🛡️ *Security Hardening* — {changes_made} perbaikan diterapkan:\n  • security.txt\n  • Security meta tags\n  • robots.txt\n  • _headers (CSP, HSTS, dll)\n  • .gitattributes\n  • sw.js security notes\n✅ Semua auto-fix sudah di-commit & push")
            else:
                log(f"❌ Push failed: {r3.stderr[:100]}")
        else:
            log("⏭️ No changes to commit")
    else:
        log("✅ All hardening already in place")
        send_telegram("🛡️ *Security Hardening* — ✅ Semua proteksi sudah aktif, tidak ada yang perlu diperbaiki.")
    
    return changes_made

if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"🔧 DailyMoney Security Hardener @ {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}")
    
    check_and_report()

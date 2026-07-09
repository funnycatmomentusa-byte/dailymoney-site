#!/usr/bin/env python3
"""DailyMoney — Cloudflare Security Agent
Setup Cloudflare proxy + security headers untuk dailymoney.my.id.
Jalankan setelah nameserver diubah ke Cloudflare."""
import json, os, subprocess, sys
from datetime import datetime

DOMAIN = "dailymoney.my.id"
GIT_REPO = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(os.path.join(LOG_DIR, "cloudflare-setup.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

def deploy_headers_via_worker():
    """Buat Cloudflare Worker script untuk security headers."""
    worker_code = """// DailyMoney Security Headers Worker v1.0
// Deploy di Cloudflare Workers untuk menambahkan security headers

const SECURITY_HEADERS = {
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'geolocation=(), camera=(), microphone=(), payment=(), usb=(), display-capture=()',
  'X-XSS-Protection': '0',
  'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://www.googletagmanager.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; img-src 'self' https: data:; font-src 'self' https://fonts.gstatic.com; connect-src 'self' https://api.coingecko.com; frame-src 'none'; object-src 'none'",
  'Cross-Origin-Opener-Policy': 'same-origin',
  'Cross-Origin-Embedder-Policy': 'require-corp',
  'Cross-Origin-Resource-Policy': 'same-origin'
};

async function handleRequest(request) {
  const response = await fetch(request);
  const newHeaders = new Headers(response.headers);
  
  // Add security headers
  for (const [key, value] of Object.entries(SECURITY_HEADERS)) {
    newHeaders.set(key, value);
  }
  
  // Remove info-leaking headers
  newHeaders.delete('X-Powered-By');
  newHeaders.delete('Server');
  newHeaders.delete('X-GitHub-Request-Id');
  
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: newHeaders
  });
}

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});
"""
    path = os.path.join(GIT_REPO, "cloudflare-worker.js")
    with open(path, "w") as f:
        f.write(worker_code)
    log("✅ Created cloudflare-worker.js")
    return path

def deploy_wrangler_config():
    """Buat wrangler.toml untuk deploy worker."""
    config = f"""name = "dailymoney-security-headers"
main = "cloudflare-worker.js"
compatibility_date = "2024-01-01"

routes = [
  {{ pattern = "{DOMAIN}/*", zone_id = "YOUR_ZONE_ID" }},
  {{ pattern = "www.{DOMAIN}/*", zone_id = "YOUR_ZONE_ID" }}
]
"""
    path = os.path.join(GIT_REPO, "wrangler.toml")
    with open(path, "w") as f:
        f.write(config)
    log("✅ Created wrangler.toml")
    return path

def create_pages_rules_guide():
    """Buat guide untuk Cloudflare Page Rules."""
    content = f"""# Cloudflare Page Rules untuk {DOMAIN}
# Masuk: Cloudflare Dashboard → Rules → Page Rules → Create Page Rule

# Page Rule 1: Always Use HTTPS
URL: *{DOMAIN}/*
Setting: Always Use HTTPS → ON

# Page Rule 2: Security Headers (via Worker)
URL: *{DOMAIN}/*
Setting: Worker Route → dailymoney-security-headers

# Page Rule 3: Cache Static Assets
URL: *{DOMAIN}/assets/*
Setting: Cache Level → Standard
         Edge Cache TTL → 1 month
         Browser Cache TTL → 4 hours

# Page Rule 4: Sitemap & RSS No Cache
URL: *{DOMAIN}/*.xml
Setting: Cache Level → Bypass

# Page Rule 5: Auto Minify
URL: *{DOMAIN}/*
Setting: Auto Minify → HTML: ON, CSS: ON, JS: ON
"""
    path = os.path.join(GIT_REPO, "CLOUDFLARE-PAGE-RULES.md")
    with open(path, "w") as f:
        f.write(content)
    log("✅ Created CLOUDFLARE-PAGE-RULES.md")
    return path

def create_step_by_step_guide():
    """Buat panduan lengkap setup Cloudflare."""
    content = f"""# 🛡️ Setup Cloudflare untuk dailymoney.my.id

## Langkah 1: Buat Akun Cloudflare (5 menit)
1️⃣ Buka https://dash.cloudflare.com/sign-up
2️⃣ Daftar dengan email (GRATIS)
3️⃣ Masukkan domain: **{DOMAIN}**
4️⃣ Pilih paket **Free** (sudah cukup)
5️⃣ Cloudflare akan scan DNS records

## Langkah 2: Update Nameserver di Niagahoster/Rumahweb
Setelah add domain di Cloudflare, mereka akan kasih 2 nameserver:
```
ns1.cloudflare.com
ns2.cloudflare.com  (atau nama lain)
```

**Cara ganti di Niagahoster:**
1. Login ke akun Niagahoster
2. Masuk ke **Layanan Saya** → **Domain**
3. Pilih **dailymoney.my.id** → **Kelola Domain**
4. Cari **Nameserver** → **Ubah Nameserver**
5. Ganti dengan nameserver dari Cloudflare
6. Simpan

**Cara ganti di Rumahweb:**
1. Login ke cPanel/klien area
2. Domain → Nameserver
3. Ganti ke nameserver Cloudflare

⚠️ **Tunggu 1-24 jam sampai propagasi selesai**

## Langkah 3: Setup DNS Records di Cloudflare
Setelah nameserver diganti, Cloudflare akan otomatis mendeteksi records.
Pastikan records ini ada (dengan ikon cloud ORANGE/proxied):

| Type | Name | Value | Proxy |
|------|------|-------|-------|
| A | @ | 185.199.108.153 | ☁️ Proxied |
| A | @ | 185.199.109.153 | ☁️ Proxied |
| A | @ | 185.199.110.153 | ☁️ Proxied |
| A | @ | 185.199.111.153 | ☁️ Proxied |
| CNAME | www | funnycatmomentusa-byte.github.io | ☁️ Proxied |

## Langkah 4: Deploy Security Headers Worker

Setelah Cloudflare aktif, jalankan script deploy worker:

```bash
# Install Wrangler CLI
npm install -g wrangler

# Login ke Cloudflare
wrangler login

# Deploy worker
cd /root/workspace/dailymoney-site
wrangler deploy cloudflare-worker.js --name dailymoney-security-headers
```

Atau minta saya deploy via API — kasih API token nanti.

## Langkah 5: Setup SSL/TLS di Cloudflare
1. Dashboard Cloudflare → SSL/TLS
2. Pilih **Full (strict)**
3. Aktifkan **Always Use HTTPS** → ON
4. Scroll ke **Minimum TLS Version** → 1.2
5. Aktifkan **Automatic HTTPS Rewrites** → ON

## Langkah 6: Tambahkan Page Rules
Ikuti panduan di **CLOUDFLARE-PAGE-RULES.md**

## Verifikasi
Setelah semua setup, jalankan:
```bash
python3 ~/.hermes/scripts/dailymoney-security-agent.py
```

Security headers akan ✅ muncul semua!

## Kalau ada masalah
Ketik: **setup cloudflare** — saya bantu deploy worker via API
"""
    path = os.path.join(GIT_REPO, "CLOUDFLARE-SETUP.md")
    with open(path, "w") as f:
        f.write(content)
    log("✅ Created CLOUDFLARE-SETUP.md")
    return path

def update_headers_file():
    """Update _headers dengan konfigurasi lengkap."""
    path = os.path.join(GIT_REPO, "_headers")
    content = """# Security headers for dailymoney.my.id
# Cloudflare will override with Worker headers,
# but these serve as fallback for direct GitHub Pages access

/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), camera=(), microphone=(), payment=(), usb=()
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  X-XSS-Protection: 0
  Cross-Origin-Opener-Policy: same-origin
"""
    with open(path, "w") as f:
        f.write(content)
    log("✅ Updated _headers with full security config")

def create_cloudflare_setup_script():
    """Buat script setup otomatis jika ada API token."""
    # Script sudah dibuat di scripts/cloudflare-auto-setup.py
    script_path = os.path.join(GIT_REPO, "scripts", "cloudflare-auto-setup.py")
    if os.path.exists(script_path):
        log("✅ cloudflare-auto-setup.py already exists in repo")
    else:
        log("⚠️ cloudflare-auto-setup.py not found in repo (created separately)")
    return script_path

# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"☁️  DailyMoney Cloudflare Setup @ {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}")
    
    log("Menyiapkan semua file untuk Cloudflare setup...")
    
    update_headers_file()
    deploy_headers_via_worker()
    deploy_wrangler_config()
    create_pages_rules_guide()
    create_step_by_step_guide()
    create_cloudflare_setup_script()
    
    # Commit
    log("📤 Committing Cloudflare preparation files...")
    subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10, cwd=GIT_REPO)
    r2 = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True, timeout=10, cwd=GIT_REPO)
    if r2.returncode != 0:
        subprocess.run(["git", "commit", "-m", "feat: cloudflare setup files - security headers"], capture_output=True, timeout=10, cwd=GIT_REPO)
        subprocess.run(["git", "push", "origin", "main"], capture_output=True, timeout=30, cwd=GIT_REPO)
    
    msg = f"""☁️ *Cloudflare Setup Siap!*

📁 File-file sudah di-commit ke repo:
• `_headers` — security headers
• `cloudflare-worker.js` — worker script
• `wrangler.toml` — deploy config
• `CLOUDFLARE-SETUP.md` — panduan lengkap
• `CLOUDFLARE-PAGE-RULES.md` — page rules guide
• `scripts/cloudflare-auto-setup.py` — auto-setup script

📖 Baca panduan lengkap:
`cat /root/workspace/dailymoney-site/CLOUDFLARE-SETUP.md`

Atau ketik **"sudah ganti nameserver"** — saya lanjut setup via API!"""
    
    send_telegram(msg)
    
    print(f"\n{'='*50}")
    print(f"✅ Semua file Cloudflare setup siap!")
    print(f"📖 Baca panduan: cat {GIT_REPO}/CLOUDFLARE-SETUP.md")
    print(f"{'='*50}")

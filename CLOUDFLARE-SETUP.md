# 🛡️ Setup Cloudflare untuk dailymoney.my.id

## Langkah 1: Buat Akun Cloudflare (5 menit)
1️⃣ Buka https://dash.cloudflare.com/sign-up
2️⃣ Daftar dengan email (GRATIS)
3️⃣ Masukkan domain: **dailymoney.my.id**
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

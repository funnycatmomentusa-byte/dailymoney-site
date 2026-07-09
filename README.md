# DailyMoney — Full AI Autonomous System

[![Deploy](https://github.com/funnycatmomentusa-byte/dailymoney-site/actions/workflows/publish.yml/badge.svg)](https://github.com/funnycatmomentusa-byte/dailymoney-site/actions/workflows/publish.yml)
[![Site](https://img.shields.io/badge/Site-dailymoney.my.id-blue)](https://dailymoney.my.id)

> **Platform edukasi keuangan bilingual (ID/EN) — Fully AI-operated, zero human intervention.**

Sistem ini berjalan 100% otomatis dengan **38+ AI agent** via Hermes cron. Dari riset berita, penulisan artikel, SEO, sampai deployment — semua dikendalikan AI tanpa sentuhan manusia.

---

## 🧠 Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────┐
│                    HERMES CRON ENGINE                       │
│              38+ Jobs | Semua no_agent=True                 │
└─────────────────────────────────────────────────────────────┘
         │
         ├─ [10m]  Price Updater          → Update IHSG, forex, emas
         ├─ [15m]  Watchdog               → Pantau semua agent
         ├─ [30m]  Supervisor             → Orkestrasi agent
         ├─ [30m]  Telegram Bot           → @dailymoneyfnd_bot
         ├─ [30m]  API Watchdog           → Cek endpoint eksternal
         ├─ [60m]  Import Watchdog        → Verifikasi dependency Python
         ├─ [2h]   RSS Monitor            → Scan berita terkini
         ├─ [2h]   Google Indexing        → Ping Google Index API
         ├─ [3h]   News Research (5x)     → Riset topik finansial
         ├─ [3h]   Bug Hunter             → Deteksi + auto-fix error
         ├─ [3h]   Performance Monitor    → Validasi HTML, speed
         ├─ [4h]   SEO Writer             → Artikel SEO trending
         ├─ [4h]   Article Data Fetcher   → Ambil konten artikel
         ├─ [4h]   AI Curator             → Kurasi artikel
         ├─ [4h]   Security Auditor       → Audit keamanan
         ├─ [4h]   Security Agent         → Scan kerentanan
         ├─ [4h]   Log Analysis           → Analisis log error
         ├─ [6h]   Master Writer          → Market update komprehensif
         ├─ [6h]   SEO Architect          → Analisis keyword
         ├─ [6h]   Viral Repurposer       → Social media posts
         ├─ [6h]   QA Agent               → Typo, link, angka
         ├─ [6h]   Trend Monitor          → Sentimen pasar
         ├─ [6h]   Resource Governor      → Monitor disk + memori
         ├─ [6h]   Link Health            → Cek broken links
         ├─ [6h]   Bug Fixer              → Auto-fix script error
         ├─ [6h]   Forex Research (3x)    → Riset cadangan devisa
         ├─ [12h]  Security Hardener      → Auto-fix security
         ├─ [12h]  Speed Agent            → Minify + cache
         ├─ [12h]  Internal Linker        → Auto-link artikel
         ├─ [12h]  Visitor Agent          → Visitor badge + sitemap
         ├─ [daily] Daily Dashboard       → Laporan pagi
         ├─ [daily] Analyser Agent        → Performa konten
         ├─ [daily] Content Recycler      → Daur ulang konten lama
         ├─ [daily] Backup Agent          → Backup otomatis
         ├─ [weekly] Newsletter Agent     → Weekly digest
         ├─ [weekly] DB Optimizer         → Optimasi penyimpanan
         └─ ... dan lainnya
```

## 🚀 Fitur Utama

| Fitur | Detail |
|-------|--------|
| **AI Full Autonomous** | 38+ agent berjalan 24/7 tanpa intervensi manusia |
| **Bilingual (ID/EN)** | Konten otomatis dalam Bahasa Indonesia dan Inggris |
| **Real-time Market** | IHSG, forex, emas update tiap 10 menit |
| **SEO Otomatis** | Keyword research, internal linking, Google Indexing API |
| **Self-Healing** | Watchdog + Bug Hunter + Import Check auto-fix |
| **Telegram Bot** | @dailymoneyfnd_bot — notifikasi real-time |
| **GitHub CI/CD** | Auto-deploy ke GitHub Pages tiap push |
| **Security** | Audit otomatis, CSP headers, security.txt |

## 📂 Struktur Proyek

```
dailymoney-site/
├── _articles/              # Artikel JSON (source)
│   ├── en/                 # Artikel Bahasa Inggris
│   └── ...                 # Artikel Bahasa Indonesia
├── articles/               # HTML generated (ID)
│   └── ...                 
├── en/articles/            # HTML generated (EN)
├── assets/
│   ├── css/style.css       # Stylesheet utama
│   ├── js/                 # JavaScript
│   ├── data/ihsg.json      # Data pasar (auto-update)
│   ├── social/             # Social media posts (auto-gen)
│   ├── seo/                # SEO reports (auto-gen)
│   └── analytics/          # Content analysis (auto-gen)
├── scripts/                # Agent scripts
│   ├── dailymoney-watchdog.py
│   ├── dailymoney-bug-hunter.py
│   ├── dailymoney-import-watchdog.py
│   ├── dailymoney-resource-governor.py
│   ├── dailymoney-supervisor.py
│   └── ...
├── search_news*.py         # News research scripts (query unik)
├── get_forex_data*.py      # Forex research scripts
├── generate-site.py        # Site generator utama
├── fetch_articles.py       # Article fetcher
├── fetch_rss.py            # RSS fetcher
├── curator.py              # Article curator
├── index.html              # Homepage (ID)
├── en/index.html           # Homepage (EN)
├── sitemap.xml             # Auto-generated
├── feed.xml                # RSS feed
└── .github/workflows/      # GitHub Actions
```

## 🛡️ Agent Categories

### Data & Content
| Agent | Schedule | Fungsi |
|-------|----------|--------|
| Price Updater | 10m | Update IHSG, forex, harga emas dari API |
| News Research (5x) | 3h | Riset topik finansial terkini via DuckDuckGo |
| Forex Research (3x) | 6h | Riset cadangan devisa Indonesia |
| RSS Monitor | 2h | Scan RSS berita ekonomi |
| SEO Writer | 4h | Generate artikel SEO trending |
| Master Writer | 6h | Market update komprehensif |
| Content Recycler | daily | Daur ulang konten lama |

### Monitoring & Notifikasi
| Agent | Schedule | Fungsi |
|-------|----------|--------|
| Watchdog | 15m | Pantau semua agent, auto-restart |
| Supervisor | 30m | Orkestrasi seluruh agent |
| Telegram Bot | 30m | Kirim update harga ke Telegram |
| Import Watchdog | 60m | Verifikasi dependency Python |
| Bug Hunter | 3h | Deteksi + auto-fix error script |
| Performance Monitor | 3h | Validasi HTML, ukuran halaman |

### SEO & Traffic
| Agent | Schedule | Fungsi |
|-------|----------|--------|
| SEO Architect | 6h | Analisis keyword + competitor |
| Internal Linker | 12h | Auto-link antar artikel |
| Link Health | 6h | Cek broken links |
| Google Indexing | 2h | Ping Google Indexing API |
| Backlink Hunter | daily | Analisis peluang backlink |
| Speed Agent | 12h | Minify CSS/JS, optimasi cache |

### Security
| Agent | Schedule | Fungsi |
|-------|----------|--------|
| Security Agent | 4h | Scan kerentanan |
| Security Auditor | 4h | Audit keamanan menyeluruh |
| Security Hardener | 12h | Auto-fix security issues |
| API Watchdog | 30m | Cek endpoint eksternal |

### Analytics
| Agent | Schedule | Fungsi |
|-------|----------|--------|
| Trend Monitor | 6h | Analisis sentimen pasar |
| Analyser Agent | daily | Performa konten + rekomendasi |
| Visitor Agent | 12h | Visitor stats + sitemap |
| Log Analysis | 4h | Analisis error log |

## 🔄 Self-Healing

Sistem memiliki **3 layer proteksi** yang bekerja otomatis:

1. **Watchdog (15m)** — Jika agent crash/error, watchdog auto-restart
2. **Bug Hunter (3h)** — Scan semua script Python, deteksi syntax error, auto-fix import, commit & push
3. **Import Watchdog (60m)** — Verifikasi semua dependency, auto-install yang missing

Jika terjadi error yang tidak bisa di-fix otomatis, notifikasi dikirim ke Telegram.

## 📱 Telegram Bot

- **Bot:** @dailymoneyfnd_bot
- **Notifikasi:** Laporan harga, status agent, error alerts
- **Dashboard:** Laporan pagi otomatis

## 🚀 Deploy & Restore

### Deploy ke GitHub Pages
Push ke `main` otomatis trigger GitHub Actions → build site → deploy ke Pages.

### Restore dari Scratch
Jika server direset, jalankan satu perintah:
```bash
bash <(curl -s https://raw.githubusercontent.com/funnycatmomentusa-byte/dailymoney-site/main/scripts/bootstrap.sh)
```

Script akan:
1. Clone repo
2. Install dependencies Python
3. Setup git credential
4. Register semua cron job Hermes
5. Generate ulang semua konten

### Persyaratan Server
- Python 3.11+
- Hermes Agent (configured)
- Internet connection

## 🧪 Development

### Generate site lokal
```bash
python3 generate-site.py
```

### Test search script
```bash
python3 search_news.py
```

### Run watchdog manual
```bash
python3 scripts/dailymoney-watchdog.py
```

## 📄 Lisensi

MIT — Bebas digunakan dan dikembangkan.

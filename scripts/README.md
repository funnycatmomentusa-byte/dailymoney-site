# DailyMoney AI Agents 🤖

Seluruh agent AI yang menjalankan **dailymoney.my.id** secara otomatis.

## 🏗️ Arsitektur

```
┌─────────────────────────────────────────────────────┐
│                   CRON SCHEDULER                     │
│  (Hermes Agent — 42 jobs berjalan otomatis 24/7)    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  🛠️ DATA & CONTENT LAYER                             │
│  ├── dailymoney-update.sh            (10m)           │
│  ├── dailymoney-news-researcher.sh   (3j)            │
│  ├── dailymoney-forex-researcher.sh  (6j)            │
│  ├── dailymoney-article-fetcher.sh   (4j)            │
│  ├── dailymoney-rss-monitor.sh       (2j)            │
│  ├── dailymoney-master-writer.py     (6j)            │
│  ├── dailymoney-seo-writer.py        (4j)            │
│  └── dailymoney-internal-linker.py   (12j)           │
│                                                      │
│  📢 PROMOTION & MONITORING LAYER                     │
│  ├── dailymoney-telegram-summary.py  (30m)           │
│  ├── dailymoney-api-watchdog.py      (30m)           │
│  ├── dailymoney-daily-dashboard.py   (pagi)          │
│  ├── dailymoney-newsletter-agent.py  (mingguan)      │
│  ├── dailymoney-traffic-agent.sh     (12j)           │
│  └── dailymoney-indexing-agent.py    (2j)            │
│                                                      │
│  🔧 INFRASTRUCTURE LAYER                             │
│  ├── dailymoney-watchdog.py          (15m)           │
│  ├── dailymoney-supervisor.py        (30m)           │
│  ├── dailymoney-import-watchdog.py   (60m)           │
│  ├── dailymoney-bug-hunter.py        (3j)            │
│  ├── dailymoney-bug-fixer.py         (6j)            │
│  ├── dailymoney-perf-monitor.py      (3j)            │
│  ├── dailymoney-resource-governor.py (6j)            │
│  ├── dailymoney-security-agent.py    (4j)            │
│  ├── dailymoney-security-hardener.py (12j)           │
│  └── dailymoney-security-auditor.py  (4j)            │
│                                                      │
│  🤖 AUTONOMOUS LOOPS                                 │
│  ├── dailymoney-curator-ai.py        (4j)            │
│  ├── dailymoney-trend-monitor.py     (6j)            │
│  ├── dailymoney-viral-repurposer.py  (6j)            │
│  ├── dailymoney-content-recycler.py  (harian)        │
│  ├── dailymoney-backlink-hunter.py   (pagi)          │
│  ├── dailymoney-seo-architect.py     (6j)            │
│  ├── dailymoney-qa-agent.py          (6j)            │
│  ├── dailymoney-log-analysis.py      (4j)            │
│  └── dailymoney-analyser-agent.py    (pagi)          │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## ⚙️ Cara Kerja

Semua agent berjalan sebagai **Hermes cron jobs** dengan mode `no_agent=True` (script-only, tanpa LLM). Setiap agent:

1. **Terjadwal otomatis** — interval tertentu (10m s/d mingguan)
2. **Script-only** — langsung eksekusi Python/bash, tanpa konsumsi token LLM
3. **Push ke GitHub** — hasil perubahan langsung di-commit & push
4. **Telegram alert** — hanya kalau ada error

## 📋 Daftar Lengkap Agent

| Agent | Interval | File | Fungsi |
|-------|----------|------|--------|
| 🏠 Price Updater | 10m | `dailymoney-update.sh` | Update harga, generate site, push |
| 📨 Telegram | 30m | `dailymoney-telegram-summary.py` | Kirim ringkasan ke Telegram |
| 👁️ API Watchdog | 30m | `dailymoney-api-watchdog.py` | Cek API prices hidup/mati |
| 🏃 Supervisor | 30m | `dailymoney-supervisor.py` | Monitor semua agent, auto-trim log |
| 👁️ Import Watchdog | 60m | `dailymoney-import-watchdog.py` | Cek dependency Python |
| 📡 RSS Monitor | 2j | `dailymoney-rss-monitor.sh` | Pantau RSS feed berita |
| 🌐 Indexing | 2j | `dailymoney-indexing-agent.py` | Google Indexing API |
| 🐛 Bug Hunter | 3j | `dailymoney-bug-hunter.py` | Scan error, auto-fix, push |
| 📊 News Research | 3j | `dailymoney-news-researcher.sh` | Riset berita terbaru |
| 📈 Performance | 3j | `dailymoney-perf-monitor.py` | Cek performa site |
| 📚 Article Data | 4j | `dailymoney-article-fetcher.sh` | Fetch artikel dari source |
| ✍️ SEO Writer | 4j | `dailymoney-seo-writer.py` | Tulis artikel SEO |
| 🛡️ Security Agent | 4j | `dailymoney-security-agent.py` | Scan keamanan |
| 🔒 Security Auditor | 4j | `dailymoney-security-auditor.py` | Audit keamanan menyeluruh |
| 🎯 AI Curator | 4j | `dailymoney-curator-ai.py` | Kurasi artikel terbaik |
| 📊 Log Analysis | 4j | `dailymoney-log-analysis.py` | Analisis log error |
| 🔄 Content Recycler | harian | `dailymoney-content-recycler.py` | Repurpose konten lama |
| 📧 Newsletter | mingguan | `dailymoney-newsletter-agent.py` | Kirim newsletter |
| 💰 Forex Research | 6j | `dailymoney-forex-researcher.sh` | Riset forex |
| ✍️ Master Writer | 6j | `dailymoney-master-writer.py` | Tulis artikel utama |
| 🐛 Bug Fixer | 6j | `dailymoney-bug-fixer.py` | Fix error otomatis |
| ⚙️ Resource Gov | 6j | `dailymoney-resource-governor.py` | Bersihkan resource |
| 📈 SEO Architect | 6j | `dailymoney-seo-architect.py` | Strategi SEO |
| 📊 Trend Monitor | 6j | `dailymoney-trend-monitor.py` | Pantau tren |
| 📱 Viral Repurpose | 6j | `dailymoney-viral-repurposer.py` | Buat konten viral |
| 🔍 QA Agent | 6j | `dailymoney-qa-agent.py` | Quality assurance |
| 🔗 Internal Linker | 12j | `dailymoney-internal-linker.py` | Internal linking |
| 🚀 Speed Agent | 12j | `dailymoney-speed-agent.py` | Optimasi kecepatan |
| 🛡️ Security Hardener | 12j | `dailymoney-security-hardener.py` | Hardening keamanan |
| 📊 Traffic Agent | 12j | `dailymoney-traffic-agent.sh` | Analisis traffic |
| 💼 Daily Dashboard | pagi | `dailymoney-daily-dashboard.py` | Dashboard harian |
| 🔗 Backlink Hunter | pagi | `dailymoney-backlink-hunter.py` | Cari backlink |
| 📊 Analyser Agent | pagi | `dailymoney-analyser-agent.py` | Analisis mendalam |
| 💾 Backup Agent | malam | `dailymoney-backup-agent.py` | Backup otomatis |

## 🚀 Deployment

Script di folder ini otomatis disinkronkan dari `~/.hermes/scripts/` tiap ada perubahan. Cron job Hermes reference langsung ke folder `~/.hermes/scripts/`.

Untuk menambah agent baru:
1. Buat script di `~/.hermes/scripts/`
2. Copy ke folder ini
3. Daftarkan cron job dengan `cronjob action=create`

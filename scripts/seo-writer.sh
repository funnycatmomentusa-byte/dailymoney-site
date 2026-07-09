#!/usr/bin/env bash
# DailyMoney — SEO & Master Writer Agent System
# Sistem penulisan konten otomatis untuk dailymoney.my.id
# Berjalan via Hermes cron:
#   SEO Writer  → every 4h  → dailymoney-seo-writer.py
#   Master Writer → every 6h  → dailymoney-master-writer.py
#
# SEO Writer: Cari topik trending dari DuckDuckGo, tulis artikel ID/EN
# Master Writer: Market update + Artikel edukasi + Evergreen content
echo "Writer agents run via cron — see ~/.hermes/scripts/dailymoney-{seo-writer,master-writer}.py"

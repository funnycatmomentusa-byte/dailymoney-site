#!/usr/bin/env python3
"""DailyMoney — Backlink Hunter Agent
Mengidentifikasi peluang backlink: direktori, forum, site kolaborasi, guest post, broken link building.
"""
import json, os, subprocess, sys, re, urllib.request
from datetime import datetime

BASE_DIR = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "assets", "backlinks")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(os.path.join(LOG_DIR, "backlink-hunter.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

def get_site_articles():
    """Ambil daftar judul artikel yang sudah ada."""
    articles = []
    for d in [os.path.join(BASE_DIR, "_articles"), os.path.join(BASE_DIR, "_articles", "en")]:
        if os.path.exists(d):
            for fname in sorted(os.listdir(d), reverse=True)[:10]:
                try:
                    with open(os.path.join(d, fname)) as f:
                        data = json.load(f)
                    articles.append({
                        "judul": data.get("judul", ""),
                        "slug": data.get("slug", ""),
                        "tags": data.get("tags", []),
                        "date": data.get("date", "")
                    })
                except:
                    pass
    return articles

def search_backlink_opportunities():
    """Cari peluang backlink via pencarian DuckDuckGo."""
    opportunities = []
    
    queries = [
        "daftar direktori bisnis Indonesia gratis submit 2026",
        "guest post keuangan Indonesia terima artikel",
        "forum finansial Indonesia komunitas investasi",
        "submit website keuangan ke direktori",
        "link exchange site keuangan Indonesia",
    ]
    
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            for query in queries:
                try:
                    results = list(ddgs.text(query, max_results=3, region='id-id'))
                    for r in results:
                        url = r.get("href", "")
                        title = r.get("title", "")
                        body = r.get("body", "")
                        if url and title:
                            opportunities.append({
                                "url": url,
                                "title": title,
                                "snippet": body[:150] if body else "",
                                "query": query,
                                "type": classify_opportunity(query, url, body)
                            })
                except:
                    pass
    except ImportError:
        log("⚠️ ddgs not installed, using static list")
        opportunities = get_static_opportunities()
    
    return opportunities

def classify_opportunity(query, url, body=""):
    """Klasifikasi tipe peluang backlink."""
    if "direktori" in query.lower() or "direktori" in url.lower():
        return "direktori"
    elif "guest post" in query.lower():
        return "guest_post"
    elif "forum" in query.lower():
        return "forum"
    elif "submit" in query.lower():
        return "submit"
    elif "link exchange" in query.lower():
        return "link_exchange"
    else:
        return "lainnya"

def get_static_opportunities():
    """Fallback static list of Indonesian financial directories/networks."""
    return [
        {"url": "https://www.google.com/business/", "title": "Google Business Profile", "snippet": "Daftar gratis — website financial news muncul di Google Maps & Search", "query": "direktori", "type": "direktori"},
        {"url": "https://id.techinasia.com/", "title": "Tech in Asia Indonesia", "snippet": "Platform startup & financial news Indonesia — bisa submit press release", "query": "direktori", "type": "submit"},
        {"url": "https://www.liputan6.com/", "title": "Liputan6", "snippet": "Portal berita besar Indonesia — punya kanal ekonomi", "query": "forum", "type": "guest_post"},
        {"url": "https://www.finansialku.com/", "title": "Finansialku", "snippet": "Portal edukasi keuangan Indonesia — komunitas aktif", "query": "forum", "type": "forum"},
        {"url": "https://www.seputarforex.com/", "title": "Seputar Forex", "snippet": "Komunitas trader & investor Indonesia — forum diskusi", "query": "forum", "type": "forum"},
        {"url": "https://www.indonesia-investments.com/", "title": "Indonesia Investments", "snippet": "Portal investasi Indonesia — konten kolaborasi", "query": "guest_post", "type": "guest_post"},
        {"url": "https://www.hotcourses.co.id/", "title": "Hotcourses Indonesia", "snippet": "Pendidikan & karir finansial", "query": "direktori", "type": "direktori"},
        {"url": "https://kaskus.co.id/category/finansial", "title": "Kaskus Finansial", "snippet": "Forum diskusi finansial terbesar Indonesia", "query": "forum", "type": "forum"},
        {"url": "https://www.kompasiana.com/", "title": "Kompasiana", "snippet": "Blog platform — bisa posting artikel dengan backlink", "query": "guest_post", "type": "guest_post"},
        {"url": "https://www.dmoz-odp.org/", "title": "DMOZ Indonesia", "snippet": "Direktori web global — submit site financial news", "query": "direktori", "type": "direktori"},
        {"url": "https://www.pajak.go.id/", "title": "Direktorat Jenderal Pajak", "snippet": "Portal pajak Indonesia — resource untuk konten pajak", "query": "direktori", "type": "direktori"},
        {"url": "https://www.bi.go.id/", "title": "Bank Indonesia", "snippet": "Referensi otoritatif — bisa jadi sumber konten & link ke BI", "query": "guest_post", "type": "guest_post"},
    ]

def analyze_competitor_backlinks():
    """Analisis website keuangan lain untuk ide backlink."""
    competitors = [
        {"name": "Bareksa", "url": "bareksa.com", "niche": "reksadana"},
        {"name": "Stockbit", "url": "stockbit.com", "niche": "saham"},
        {"name": "Kontan", "url": "kontan.co.id", "niche": "berita"},
        {"name": "Investor Daily", "url": "investor.id", "niche": "berita"},
    ]
    
    insights = []
    for c in competitors:
        insights.append({
            "competitor": c["name"],
            "url": c["url"],
            "niche": c["niche"],
            "strategy": f"Analisis backlink {c['name']} via Ahrefs/SEMrush untuk lihat dari mana mereka dapat link. Targetkan site serupa untuk dailymoney.my.id.",
            "action": f"Cari guest post atau komentar di {c['url']} yang terima kontributor eksternal"
        })
    
    return insights

def generate_backlink_report(opportunities, articles, insights):
    """Generate laporan peluang backlink."""
    now = datetime.now()
    
    # Group by type
    by_type = {}
    for opp in opportunities:
        t = opp.get("type", "lainnya")
        if t not in by_type:
            by_type[t] = []
        by_type[t].append(opp)
    
    report = f"""# Backlink Hunter Report
**Generated:** {now.strftime('%d/%m/%Y %H:%M')}
**Site:** dailymoney.my.id
**Articles total:** {len(articles)}

---

## 📊 Opportunities Found: {len(opportunities)}
"""
    
    for opp_type, items in by_type.items():
        icon = {"direktori": "📂", "guest_post": "✍️", "forum": "💬", "submit": "📝", "link_exchange": "🔗", "lainnya": "📌"}
        report += f"\n### {icon.get(opp_type, '📌')} {opp_type.replace('_', ' ').title()} ({len(items)})\n"
        for item in items[:5]:
            report += f"- [{item['title']}]({item['url']})\n  {item['snippet'][:80]}...\n"
    
    # Priority actions
    report += """
---

## 🎯 Priority Actions (This Week)

### 1. Google Business Profile
Daftarkan dailymoney.my.id di Google Business — GRATIS, meningkatkan visibilitas lokal.

### 2. Submit ke Direktori
Kirim site ke DMOZ, Yell Indonesia, dan direktori bisnis lokal — backlink berkualitas.

### 3. Kompasiana Guest Post
Tulis 1 artikel keuangan di Kompasiana dengan link ke dailymoney.my.id — DA tinggi.

### 4. Forum Engagement
Bergabung di Kaskus Finansial & Seputar Forex — jawab pertanyaan + link ke artikel relevan.

### 5. Broken Link Building
Cari broken link di site finansial → tawarkan artikel kita sebagai pengganti.
"""
    
    # Competitor insights
    if insights:
        report += "\n## 🏆 Competitor Analysis\n"
        for ins in insights:
            report += f"\n**{ins['competitor']}** ({ins['niche']})\n- {ins['strategy']}\n- {ins['action']}\n"
    
    # Save report
    report_path = os.path.join(OUTPUT_DIR, f"backlink-report-{now.strftime('%Y-%m-%d')}.md")
    with open(report_path, "w") as f:
        f.write(report)
    
    # Save JSON
    json_path = os.path.join(OUTPUT_DIR, f"backlink-opportunities-{now.strftime('%Y-%m-%d')}.json")
    with open(json_path, "w") as f:
        json.dump({"opportunities": opportunities, "insights": insights, "articles_count": len(articles)}, f, indent=2, ensure_ascii=False)
    
    return report_path

def run():
    log("🔗 Backlink Hunter — mencari peluang backlink...")
    
    articles = get_site_articles()
    log(f"📚 {len(articles)} artikel terindeks")
    
    opportunities = search_backlink_opportunities()
    log(f"🎯 {len(opportunities)} peluang ditemukan")
    
    insights = analyze_competitor_backlinks()
    
    report_path = generate_backlink_report(opportunities, articles, insights)
    log(f"✅ Report saved: {report_path}")
    
    # Commit report
    subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10, cwd=BASE_DIR)
    r = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True, timeout=10, cwd=BASE_DIR)
    if r.returncode != 0:
        subprocess.run(["git", "commit", "-m", f"seo: backlink hunter {datetime.now().strftime('%d/%m')}"],
                      capture_output=True, timeout=10, cwd=BASE_DIR)
        subprocess.run(["git", "push", "origin", "main"], capture_output=True, timeout=30, cwd=BASE_DIR)
        log("📤 Report committed & pushed")
    
    # Send Telegram summary
    by_type = {}
    for opp in opportunities:
        t = opp.get("type", "lainnya")
        by_type[t] = by_type.get(t, 0) + 1
    
    types_summary = " | ".join([f"{t}: {c}" for t, c in by_type.items()])
    
    msg = f"""🔗 *Backlink Hunter — Report Baru!*

🎯 *{len(opportunities)} peluang ditemukan*
{types_summary}

📂 *Priority (minggu ini):*
1️⃣ Google Business Profile
2️⃣ Submit ke direktori web
3️⃣ Guest post di Kompasiana
4️⃣ Forum Kaskus/Finansialku
5️⃣ Broken link building

📄 Lihat report lengkap: assets/backlinks/"""
    
    send_telegram(msg)
    log("✅ Done!")

if __name__ == "__main__":
    run()

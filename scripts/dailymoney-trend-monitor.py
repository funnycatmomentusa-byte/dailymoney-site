#!/usr/bin/env python3
"""DailyMoney — Sentiment & Trend Monitor Agent
Memantau tren finansial, sentimen pasar, dan rekomendasi topik tulisan."""
import json, os, subprocess, sys, re, urllib.request
from datetime import datetime, timedelta

LOG_DIR = os.path.expanduser("~/.hermes/logs")
TREND_DIR = os.path.expanduser("~/.hermes/trends")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(TREND_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(os.path.join(LOG_DIR, "trend-monitor.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

def search_trends():
    """Cari trending topics finansial via DuckDuckGo."""
    trends = []
    queries = [
        ("IHSG saham Indonesia terbaru 2026", "pasar"),
        ("investasi reksadana emas crypto 2026", "investasi"),
        ("ekonomi Indonesia berita terkini 2026", "ekonomi"),
        ("inflasi suku bunga BI 2026", "makro"),
        ("fintech bank digital Indonesia 2026", "fintech"),
        ("pajak pelaporan SPT 2026", "pajak"),
    ]
    
    try:
        from ddgs import DDGS
        with DDGS() as ddgs:
            for query, kategori in queries:
                results = list(ddgs.text(query, max_results=4, region='id-id'))
                for r in results:
                    title = r.get("title", "")
                    body = r.get("body", "")
                    url = r.get("href", "")
                    if title and body:
                        trends.append({
                            "title": title,
                            "body": body[:200],
                            "url": url,
                            "kategori": kategori,
                            "source": "ddgs"
                        })
    except ImportError:
        log("⚠️ ddgs not installed")
    
    return trends

def analyze_sentiment(texts):
    """Analisa sentimen sederhana berdasarkan kata kunci."""
    positive_words = set(["naik", "bangkit", "untung", "tumbuh", "cerah", "positif", "baik",
                          "surplus", "optimis", "stabil", "kuat", "menguat", "kenaikan", "gain",
                          "growth", "positive", "strong", "rally", "surge", "recovery"])
    negative_words = set(["turun", "anjlok", "rugi", "krisis", "inflasi", "resesi", "negatif",
                          "lesu", "melemah", "terpuruk", "buruk", "ancaman", "kekhawatiran",
                          "drop", "fall", "crisis", "recession", "decline", "loss", "bearish"])
    
    sentiment_scores = []
    for text in texts:
        text_lower = text.lower()
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        score = pos_count - neg_count
        sentiment_scores.append(score)
    
    avg_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
    
    if avg_score > 2:
        return "🟢 Bullish (Positif)", avg_score
    elif avg_score < -1:
        return "🔴 Bearish (Negatif)", avg_score
    else:
        return "🟡 Netral", avg_score

def generate_topic_recommendations(trends, sentiment_label):
    """Generate rekomendasi topik tulisan berdasarkan tren."""
    topics_by_cat = {}
    for t in trends:
        cat = t["kategori"]
        if cat not in topics_by_cat:
            topics_by_cat[cat] = []
        topics_by_cat[cat].append(t["title"])
    
    recommendations = []
    
    for cat, titles in topics_by_cat.items():
        if cat == "pasar":
            recommendations.append(f"📈 Update IHSG: {' vs '.join(titles[:2][:30]) if titles else 'Analisis Pergerakan'}")
        elif cat == "investasi":
            recommendations.append(f"💡 {titles[0][:50] if titles else 'Panduan Investasi 2026'}")
        elif cat == "ekonomi":
            recommendations.append(f"🏦 {' vs '.join(titles[:2][:30]) if titles else 'Ekonomi Indonesia Terkini'}")
        elif cat == "makro":
            recommendations.append(f"📊 {' '.join(titles[:2][:30]) if titles else 'Update Kebijakan Makro'}")
        elif cat == "fintech":
            recommendations.append(f"📱 {' '.join(titles[:2][:30]) if titles else 'Fintech Digital 2026'}")
        elif cat == "pajak":
            recommendations.append(f"🧾 {' '.join(titles[:2][:30]) if titles else 'Panduan Pajak 2026'}")
    
    return recommendations[:6]

def run():
    log("📊 Trend Monitor Agent — memantau tren finansial...")
    
    # 1. Cari trending topics
    trends = search_trends()
    log(f"🔍 {len(trends)} topik ditemukan")
    
    if not trends:
        send_telegram("📊 *Trend Monitor:* Tidak ada tren terdeteksi saat ini")
        return
    
    # 2. Analisa sentimen
    texts = [t["title"] + " " + t["body"] for t in trends]
    sentiment_label, sentiment_score = analyze_sentiment(texts)
    log(f"📈 Sentimen: {sentiment_label} (score: {sentiment_score})")
    
    # 3. Group by category
    by_cat = {}
    for t in trends:
        cat = t["kategori"]
        if cat not in by_cat:
            by_cat[cat] = []
        by_cat[cat].append(t)
    
    # 4. Generate topic recommendations
    recommendations = generate_topic_recommendations(trends, sentiment_label)
    
    # 5. Save trend report
    report = {
        "generated_at": datetime.now().isoformat(),
        "total_trends": len(trends),
        "sentiment": sentiment_label,
        "sentiment_score": sentiment_score,
        "categories": {cat: len(items) for cat, items in by_cat.items()},
        "top_trends": [{"title": t["title"][:60], "kategori": t["kategori"]} for t in trends[:10]],
        "recommendations": recommendations
    }
    
    report_path = os.path.join(TREND_DIR, f"trends-{datetime.now().strftime('%Y-%m-%d')}.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    log(f"✅ Report: {report_path}")
    
    # 6. Send Telegram
    hot_topics = "\n".join([f"• {t['title'][:45]}" for t in trends[:6]])
    
    msg = f"""📊 *Trend Monitor — {datetime.now().strftime('%d/%m/%Y')}*

{sum(len(v) for v in by_cat.values())} topik terpantau
Sentimen: {sentiment_label}

📌 *Topik Terhangat:*
{hot_topics}

📝 *Rekomendasi Tulisan Minggu Ini:*
"""
    for i, rec in enumerate(recommendations[:4], 1):
        msg += f"{i}. {rec}\n"
    
    msg += f"\n📈 Sentimen score: {sentiment_score:.1f}"
    
    send_telegram(msg)
    log(f"📤 Report dikirim ke Telegram")
    log("✅ Done!")

if __name__ == "__main__":
    run()

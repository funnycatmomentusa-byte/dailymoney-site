#!/usr/bin/env python3
"""DailyMoney — Viral Content Repurposer Agent
Mengubah artikel panjang jadi konten viral untuk Threads, Twitter/X, LinkedIn, Telegram.
"""
import json, os, subprocess, sys, re
from datetime import datetime

BASE_DIR = "/root/workspace/dailymoney-site"
ID_DIR = os.path.join(BASE_DIR, "_articles")
EN_DIR = os.path.join(ID_DIR, "en")
LOG_DIR = os.path.expanduser("~/.hermes/logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "assets", "social")
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(os.path.join(LOG_DIR, "viral-repurposer.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

def get_latest_articles(count=5):
    """Ambil artikel terbaru dari JSON."""
    articles = []
    for d in [ID_DIR, EN_DIR]:
        if os.path.exists(d):
            for fname in sorted(os.listdir(d), reverse=True)[:count]:
                try:
                    with open(os.path.join(d, fname)) as f:
                        data = json.load(f)
                    articles.append({"data": data, "lang": "id" if "en" not in d else "en"})
                except:
                    pass
    return articles

def extract_key_points(content_md, max_points=5):
    """Ekstrak poin penting dari konten markdown."""
    lines = content_md.split('\n')
    points = []
    current_point = ""
    
    for line in lines:
        line = line.strip()
        # Skip headers and empty lines
        if not line or line.startswith('#'):
            continue
        # Bold text often contains key info
        bold = re.findall(r'\*\*(.*?)\*\*', line)
        if bold:
            current_point = " ".join(bold)[:100]
            if current_point:
                points.append(current_point)
        
        # Numbered list items
        if re.match(r'^\d+[.)]', line):
            clean = re.sub(r'^\d+[.)]\s*', '', line)
            if len(clean) > 20:
                points.append(clean[:120])
    
    # Fallback: ambil kalimat pertama dari paragraf
    if len(points) < 3:
        for line in lines:
            line = line.strip()
            if len(line) > 40 and not line.startswith('#') and not line.startswith('*'):
                points.append(line[:120])
    
    return points[:max_points]

def create_threads_post(article, points):
    """Buat Threads/Thread untuk Twitter."""
    title = article.get("judul", "")
    date = article.get("date", "")
    
    thread = []
    
    # Tweet 1: Hook
    thread.append(f"🧵 {title}\n\n{date} — by @dailymoney.my.id\n\n👇 Baca selengkapnya di website")
    
    # Tweet 2-5: Key points
    for i, point in enumerate(points, 1):
        thread.append(f"{i}. {point}")
    
    # Last tweet: CTA
    thread.append(f"\n📖 Baca artikel lengkap → https://dailymoney.my.id")
    thread.append(f"\n#DailyMoney #Keuangan #Investasi #Indonesia #Finansial")
    
    return thread

def create_twitter_thread(article, points):
    """Buat Twitter/X thread."""
    title = article.get("judul", "")
    
    tweets = []
    tweets.append(f"💡 {title}\n\n{points[0] if points else ''}\n\n👇")
    
    for i, p in enumerate(points[1:4], 1):
        tweets.append(f"{i}. {p}")
    
    tweets.append(f"Baca lengkap di → dailymoney.my.id")
    return tweets

def create_linkedin_post(article, points):
    """Buat LinkedIn post."""
    title = article.get("judul", "")
    
    post = f"""📊 **{title}**

{points[0] if points else ''}

**Key takeaways:"""
    for p in points[:4]:
        post += f"\n• {p}"
    
    post += f"""

👉 Baca artikel lengkap: dailymoney.my.id

#FinancialLiteracy #Investasi #Indonesia #DailyMoney"""
    return post

def create_telegram_summary(article, points):
    """Buat Telegram post."""
    title = article.get("judul", "")
    medal = "📈" if any(k in title.lower() for k in ["naik", "bangkit", "untung"]) else "📊"
    post = f"{medal} *{title}*\n\n"
    for p in points[:3]:
        post += f"• {p}\n"
    post += f"\n🔗 dailymoney.my.id"
    return post

def run():
    log("📱 Viral Content Repurposer — membuat konten distribusi...")
    
    articles = get_latest_articles(5)
    if not articles:
        log("❌ No articles found")
        return
    
    posts_generated = 0
    
    for art in articles:
        data = art["data"]
        content = data.get("content_markdown", "")
        if not content:
            continue
        
        points = extract_key_points(content)
        if len(points) < 2:
            continue
        
        title_slug = re.sub(r'[^\w\s-]', '', data.get("judul", "article").lower())
        title_slug = re.sub(r'[\s_]+', '-', title_slug).strip('-')[:30]
        ts = datetime.now().strftime('%H%M')
        
        # Threads
        threads = create_threads_post(data, points)
        threads_path = os.path.join(OUTPUT_DIR, f"threads-{title_slug}-{ts}.md")
        with open(threads_path, "w") as f:
            f.write("---\n" + "\n---\n".join(threads) + "\n")
        log(f"  ✅ Threads: {threads_path}")
        
        # Twitter
        tweets = create_twitter_thread(data, points)
        tweets_path = os.path.join(OUTPUT_DIR, f"twitter-{title_slug}-{ts}.md")
        with open(tweets_path, "w") as f:
            f.write("\n\n".join(tweets) + "\n")
        log(f"  ✅ Twitter: {tweets_path}")
        
        # LinkedIn
        linkedin = create_linkedin_post(data, points)
        linkedin_path = os.path.join(OUTPUT_DIR, f"linkedin-{title_slug}-{ts}.md")
        with open(linkedin_path, "w") as f:
            f.write(linkedin + "\n")
        log(f"  ✅ LinkedIn: {linkedin_path}")
        
        # Telegram
        telegram = create_telegram_summary(data, points)
        telegram_path = os.path.join(OUTPUT_DIR, f"telegram-{title_slug}-{ts}.md")
        with open(telegram_path, "w") as f:
            f.write(telegram + "\n")
        log(f"  ✅ Telegram post: {telegram_path}")
        
        posts_generated += 1
    
    # Save index of social assets
    index = {
        "generated_at": datetime.now().isoformat(),
        "total_posts": posts_generated * 4,
        "articles_used": len(articles),
        "formats": ["threads", "twitter", "linkedin", "telegram"]
    }
    with open(os.path.join(OUTPUT_DIR, "index.json"), "w") as f:
        json.dump(index, f, indent=2)
    
    # Commit social assets to repo
    subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10, cwd=BASE_DIR)
    r = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True, timeout=10, cwd=BASE_DIR)
    if r.returncode != 0:
        subprocess.run(["git", "commit", "-m", f"social: viral content {datetime.now().strftime('%H:%M')}"],
                      capture_output=True, timeout=10, cwd=BASE_DIR)
        subprocess.run(["git", "push", "origin", "main"], capture_output=True, timeout=30, cwd=BASE_DIR)
    
    msg = f"📱 *Viral Repurposer:* {posts_generated} artikel → {posts_generated * 4} post sosial\n📋 Threads, Twitter, LinkedIn, Telegram — siap pakai"
    send_telegram(msg)
    log(f"✅ Done — {posts_generated * 4} post sosial dibuat!")

if __name__ == "__main__":
    run()

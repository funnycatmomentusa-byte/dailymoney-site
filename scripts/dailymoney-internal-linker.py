#!/usr/bin/env python3
"""DailyMoney — Internal Linking Agent v2
Menganalisis artikel existing & baru, lalu auto-inject link ke artikel terkait secara cerdas."""
import json, os, subprocess, sys, re
from datetime import datetime

BASE_DIR = "/root/workspace/dailymoney-site"
ID_DIR = os.path.join(BASE_DIR, "_articles")
EN_DIR = os.path.join(ID_DIR, "en")
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(os.path.join(LOG_DIR, "internal-linker.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

def load_all_articles():
    """Load semua artikel ID dan EN."""
    articles = []
    for d, lang in [(ID_DIR, "id"), (EN_DIR, "en")]:
        if os.path.exists(d):
            for fname in os.listdir(d):
                if fname.endswith(".json"):
                    try:
                        with open(os.path.join(d, fname)) as f:
                            data = json.load(f)
                        data["_file"] = os.path.join(d, fname)
                        data["_lang"] = lang
                        # Generate slug matching generate-site.py: slugify(judul)
                        judul = data.get("judul", "")
                        s = judul.lower().strip()
                        s = re.sub(r'[^a-z0-9\s-]', '', s)
                        s = re.sub(r'[\s_]+', '-', s)
                        s = re.sub(r'-+', '-', s).strip('-')
                        data["_slug"] = s
                        articles.append(data)
                    except:
                        pass
    return articles

def build_keyword_index(articles):
    """Bangun indeks keyword → artikel untuk internal linking."""
    index = {}
    stopwords = set(["dan", "di", "ke", "dari", "yang", "ini", "itu", "adalah", "akan", "tidak",
                     "dengan", "untuk", "pada", "dalam", "serta", "atau", "juga", "sudah", "bisa",
                     "the", "and", "for", "that", "this", "with", "from", "have", "been", "are",
                     "has", "had", "but", "its", "not", "than", "was", "were", "been", "being"])
    
    for art in articles:
        title = art.get("judul", "").lower()
        tags = art.get("tags", "")
        if isinstance(tags, str):
            tags = tags.split(",")
        tags = [t.strip().lower() for t in tags if isinstance(t, str)]
        
        # Keywords dari judul (bigrams)
        words = re.findall(r'\b[a-z]{4,}\b', title)
        for i in range(len(words)-1):
            phrase = f"{words[i]} {words[i+1]}"
            if phrase and len(phrase) > 8:
                if phrase not in index:
                    index[phrase] = []
                index[phrase].append({
                    "judul": art.get("judul", ""),
                    "slug": art.get("_slug", ""),
                    "lang": art.get("_lang", "id"),
                    "tags": tags
                })
        
        # Keywords dari tags
        for tag in tags:
            if tag and tag not in stopwords and len(tag) > 3:
                if tag not in index:
                    index[tag] = []
                index[tag].append({
                    "judul": art.get("judul", ""),
                    "slug": art.get("_slug", ""),
                    "lang": art.get("_lang", "id"),
                    "tags": tags
                })
    
    return index

def find_related_articles(article, all_articles, keyword_index, max_links=3):
    """Cari artikel terkait untuk internal linking."""
    content = article.get("content_markdown", "").lower()
    title = article.get("judul", "").lower()
    tags = article.get("tags", "")
    if isinstance(tags, str):
        tags = tags.split(",")
    tags = [t.strip().lower() for t in tags if isinstance(t, str)]
    lang = article.get("_lang", "id")
    slug = article.get("_slug", "")
    
    candidates = set()
    scores = {}
    
    # 1. Cari berdasarkan keyword match di content
    for phrase, refs in keyword_index.items():
        if phrase in content or phrase in title:
            for ref in refs:
                if ref["slug"] != slug and ref["lang"] == lang:
                    candidates.add(ref["slug"])
                    if ref["slug"] not in scores:
                        scores[ref["slug"]] = {"score": 0, "ref": ref}
                    # Hitung berapa kali muncul
                    count = content.count(phrase)
                    scores[ref["slug"]]["score"] += count
    
    # 2. Cari berdasarkan tag overlap
    for other in all_articles:
        other_slug = other.get("_slug", "")
        if other_slug == slug or other.get("_lang") != lang:
            continue
        other_tags = other.get("tags", "")
        if isinstance(other_tags, str):
            other_tags = other_tags.split(",")
        other_tags = [t.strip().lower() for t in other_tags if isinstance(t, str)]
        
        tag_overlap = set(tags) & set(other_tags)
        if tag_overlap:
            candidates.add(other_slug)
            if other_slug not in scores:
                scores[other_slug] = {"score": 0, "ref": other}
            scores[other_slug]["score"] += len(tag_overlap) * 2
    
    # Sort by score
    sorted_refs = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    
    links = []
    added = set()
    for slug_id, info in sorted_refs:
        ref = info["ref"]
        judul = ref.get("judul", ref.get("judul", ""))
        ref_slug = ref.get("slug", ref.get("_slug", slug_id))
        ref_tags = ref.get("tags", [])
        if isinstance(ref_tags, str):
            ref_tags = ref_tags.split(",")
        
        # Avoid self-link and duplicates
        if ref_slug == slug or ref_slug in added:
            continue
        added.add(ref_slug)
        
        link_url = f"/articles/{ref_slug}.html" if ref.get("_lang") == "id" else f"/en/articles/{ref_slug}.html"
        links.append({
            "url": link_url,
            "judul": judul[:60],
            "score": info["score"]
        })
        
        if len(links) >= max_links:
            break
    
    return links

def inject_links(article, links):
    """Inject internal links ke content_markdown."""
    content = article.get("content_markdown", "")
    if not content or not links:
        return content, 0
    
    # Inject di bagian akhir, sebelum disclaimer/footer
    link_section = "\n\n### 📖 Baca Juga\n\n"
    for link in links:
        link_section += f"- [{link['judul']}]({link['url']})\n"
    
    # Cari posisi disclaimer atau akhir paragraf terakhir
    disclaimer_pos = content.find("*DailyMoney — Platform")
    if disclaimer_pos > 100:
        content = content[:disclaimer_pos].rstrip() + "\n\n" + link_section + "\n" + content[disclaimer_pos:]
    else:
        # Inject sebelum paragraf terakhir yang panjang
        content = content.rstrip() + "\n\n" + link_section
    
    return content, len(links)

def run():
    log("🔗 Internal Linking Agent — menganalisis koneksi antar artikel...")
    
    all_articles = load_all_articles()
    log(f"📚 {len(all_articles)} artikel dimuat")
    
    if len(all_articles) < 3:
        log("⚠️ Terlalu sedikit artikel untuk linking")
        send_telegram("⚠️ *Internal Linker:* Hanya {len(all_articles)} artikel — minimal 3")
        return
    
    keyword_index = build_keyword_index(all_articles)
    log(f"📊 {len(keyword_index)} keyword phrase terindeks")
    
    total_links = 0
    articles_updated = 0
    
    for art in all_articles:
        old_content = art.get("content_markdown", "")
        if not old_content or len(old_content) < 200:
            continue
        
        # Skip if already has internal links section
        if "### 📖 Baca Juga" in old_content:
            continue
        
        links = find_related_articles(art, all_articles, keyword_index)
        if not links:
            continue
        
        new_content, n = inject_links(art, links)
        if n > 0:
            art["content_markdown"] = new_content
            total_links += n
            articles_updated += 1
    
    if articles_updated == 0:
        log("✅ Semua artikel sudah punya internal links — tidak ada perubahan")
        send_telegram("🔗 *Internal Linker:* Semua artikel sudah ter-link ✅")
        return
    
    # Simpan perubahan ke file JSON
    for art in all_articles:
        filepath = art.get("_file", "")
        if filepath:
            # Remove internal keys before saving
            save_data = {k: v for k, v in art.items() if not k.startswith("_")}
            with open(filepath, "w") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
    
    # Generate site
    log(f"📤 Publishing {articles_updated} artikel dengan internal links...")
    r1 = subprocess.run(["python3", os.path.join(BASE_DIR, "generate-site.py")],
                       capture_output=True, timeout=60, cwd=BASE_DIR)
    if r1.returncode != 0:
        log(f"❌ Generate error")
        send_telegram("⚠️ *Internal Linker:* Gagal generate site")
        return
    
    # Commit & push
    r3 = subprocess.run(["git", "commit", "-m", f"seo: internal linking {articles_updated} articles"],
                       capture_output=True, timeout=10, cwd=BASE_DIR)
    if r3.returncode == 0:
        subprocess.run(["git", "push", "origin", "main"], capture_output=True, timeout=30, cwd=BASE_DIR)
    
    msg = f"🔗 *Internal Linker:* {articles_updated} artikel + {total_links} internal link baru!\n📈 Semua artikel sekarang saling terhubung"
    send_telegram(msg)
    log(f"✅ Done — {articles_updated} artikel updated dengan {total_links} internal links!")

if __name__ == "__main__":
    run()

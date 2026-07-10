#!/usr/bin/env python3
"""DailyMoney — Master Writer Agent v2
Mengatur produksi konten: market update, edukasi, analisis, dan evergreen.
Menulis artikel berkualitas tinggi berdasarkan data pasar real-time."""
import json, os, subprocess, sys, re, random
from datetime import datetime, timedelta, date

PROJECT = "/root/workspace/dailymoney-site"
ID_DIR = os.path.join(PROJECT, "_articles")
EN_DIR = os.path.join(PROJECT, "_articles", "en")
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(EN_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
    with open(os.path.join(LOG_DIR, "master-writer.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15)
    except:
        pass

def save_article(article, directory, lang="id"):
    """Save article JSON file."""
    title = article["judul"]
    slug = re.sub(r'[^a-z0-9]+', '-', title.lower().strip())[:50].strip('-')
    if not slug:
        slug = f"artikel-{datetime.now().strftime('%d%m%Y')}"
    date_prefix = datetime.now().strftime('%Y-%m-%d')
    today_str = date.today().strftime('%Y-%m-%d')
    if date_prefix > today_str:
        date_prefix = today_str
    filename = f"{date_prefix}-{slug}.json"
    filepath = os.path.join(directory, filename)
    if os.path.exists(filepath):
        return None
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(article, f, ensure_ascii=False, indent=2)
    log(f"✅ Saved {'ID' if lang=='id' else 'EN'}: {filename}")
    return filepath

def trigger_generate_and_push(commit_msg=None):
    """Jalankan generate-site.py dan push ke GitHub."""
    log("🏗️ Running generate-site.py...")
    r = subprocess.run(["python3", "generate-site.py"], capture_output=True, text=True, timeout=60, cwd=PROJECT)
    if r.returncode != 0:
        log(f"❌ Generate failed: {r.stderr[:200]}")
        return False
    log("📤 Pushing to GitHub...")
    subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10, cwd=PROJECT)
    r2 = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True, timeout=10, cwd=PROJECT)
    if r2.returncode == 0:
        log("No changes")
        return True
    msg = commit_msg or f"feat: master writer {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    subprocess.run(["git", "commit", "-m", msg], capture_output=True, timeout=10, cwd=PROJECT)
    r3 = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True, timeout=30, cwd=PROJECT)
    if r3.returncode == 0:
        log("✅ Pushed")
        return True
    log(f"❌ Push failed: {r3.stderr[:200]}")
    return False

# =========================================================
# 1. MARKET UPDATE — Daily market commentary from live data
# =========================================================

def get_price_data():
    """Baca data harga terkini."""
    path = os.path.join(PROJECT, "_price_data.json")
    try:
        with open(path) as f:
            return json.load(f)
    except:
        return {}

def generate_market_update():
    """Hasilkan artikel market update berdasarkan data harga real-time."""
    prices = get_price_data()
    if not prices:
        log("❌ No price data available")
        return [], []
    
    doc = datetime.now()
    day = doc.strftime('%A')
    date_str = doc.strftime('%d/%m/%Y')
    
    id_articles = []
    en_articles = []
    
    symbols = {
        "BTC": ("Bitcoin", "₿", "crypto"),
        "ETH": ("Ethereum", "⟠", "crypto"),
        "IHSG": ("IHSG", "🇮🇩", "saham"),
        "XAU": ("Emas", "🥇", "emas"),
        "USDIDR": ("USD/IDR", "💵", "rupiah"),
        "SPX": ("S&P 500", "🇺🇸", "saham"),
    }
    
    # Check if already posted today
    today_prefix = doc.strftime('%Y-%m-%d')
    existing_market = [f for f in os.listdir(ID_DIR) if f.startswith(today_prefix) and "market-update" in f.lower()]
    if existing_market:
        log(f"⏭️ Market update today already exists: {existing_market[0]}")
        return [], []
    
    # Build top movers
    movers = []
    for key, (name, icon, cat) in symbols.items():
        if key in prices:
            p = prices[key]
            price = p.get("price", p.get("harga", "?"))
            change = p.get("change", p.get("perubahan", p.get("change_pct", "0")))
            try:
                change_f = float(str(change).replace('%', '').replace(',', ''))
            except:
                change_f = 0
            movers.append({"key": key, "name": name, "icon": icon, "price": price, "change": change_f, "cat": cat})
    
    if not movers:
        return [], []
    
    movers.sort(key=lambda x: abs(x["change"]), reverse=True)
    top_gainer = next((m for m in movers if m["change"] > 0), None)
    top_loser = next((m for m in movers if m["change"] < 0), None)
    
    # === ID VERSION ===
    gainers_line = ""
    losers_line = ""
    for m in movers[:5]:
        arrow = "📈" if m["change"] >= 0 else "📉"
        sign = "+" if m["change"] >= 0 else ""
        gainers_line += f"- {m['icon']} {m['name']}: {m['price']} ({arrow} {sign}{m['change']}%)\n"
    
    change_desc = "beragam"
    if top_gainer and top_loser:
        change_desc = f"{top_gainer['name']} naik {top_gainer['change']}% sementara {top_loser['name']} turun {abs(top_loser['change'])}%"
    elif top_gainer:
        change_desc = f"mayoritas menguat dipimpin {top_gainer['name']} +{top_gainer['change']}%"
    elif top_loser:
        change_desc = f"mayoritas melemah dengan {top_loser['name']} -{abs(top_loser['change'])}%"
    
    id_title = f"Update Pasar {day}: {change_desc}"
    if len(id_title) > 65:
        id_title = id_title[:62].rsplit(' ', 1)[0] + "..."
    
    id_meta = f"Ringkasan pergerakan pasar hari ini — {date_str}. Bitcoin, IHSG, Emas, Rupiah, dan indeks saham utama Indonesia dan global."
    
    id_content = f"""JAKARTA — Pasar keuangan Indonesia dan global mencatat pergerakan {change_desc} pada perdagangan hari ini, {date_str}.

Berikut adalah ringkasan pergerakan harga aset-aset utama:

{gainers_line}
## ANALISIS PASAR HARI INI

Pergerakan pasar hari ini mencerminkan sentimen investor yang terus berkembang terhadap prospek ekonomi global dan domestik. Beberapa faktor yang mempengaruhi pergerakan pasar antara lain:

**Faktor Eksternal:**
- Pergerakan indeks Wall Street dan kebijakan moneter The Fed
- Harga komoditas global termasuk minyak dan emas
- Ketegangan geopolitik yang mempengaruhi aliran modal

**Faktor Domestik:**
- Data ekonomi Indonesia yang dirilis hari ini
- Pergeratan nilai tukar rupiah terhadap dolar AS
- Sentimen investor asing terhadap pasar modal Indonesia

## STRATEGI INVESTASI

Melihat dinamika pasar saat ini, perencana keuangan menyarankan:

1. **Tetap tenang dan disiplin** — Fluktuasi pasar harian adalah hal normal. Jangan membuat keputusan impulsif.
2. **Dollar-cost averaging** — Investasi berkala membantu meratakan harga beli.
3. **Re-balance portofolio** — Sesuaikan alokasi aset jika ada perubahan signifikan.

*DailyMoney akan terus memantau pergerakan pasar dan menyajikan update terkini. Dapatkan informasi pasar real-time di dailymoney.my.id.*"""

    # Use image pool for unique images
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
        from dailymoney_image_pool import get_unique_image
        id_img_url, id_img_cap = get_unique_image(id_title)
    except Exception:
        id_img_url = "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80"
        id_img_cap = f"Pergerakan pasar keuangan — {date_str}. Sumber: dokumentasi DailyMoney."

    id_article = {
        "judul": id_title.strip(),
        "meta_desc": id_meta.strip(),
        "date": date_str,
        "tags": "IHSG, Pasar Saham, Investasi, Reksadana, Ekonomi, Pasar Keuangan",
        "image_url": id_img_url,
        "image_caption": id_img_cap,
        "content_markdown": id_content.strip(),
        "pair_id": int(doc.timestamp()) % 1000
    }
    saved_id = save_article(id_article, ID_DIR, "id")
    if saved_id:
        id_articles.append(saved_id)
    
    # === EN VERSION ===
    en_title = f"Market Update {day}: {change_desc}"
    if len(en_title) > 65:
        en_title = en_title[:62].rsplit(' ', 1)[0] + "..."
    
    en_meta = f"Daily market summary — {date_str}. Bitcoin, IHSG (IDX), Gold, Rupiah, and major Indonesia stock indices."
    
    en_gainers = ""
    for m in movers[:5]:
        arrow = "📈" if m["change"] >= 0 else "📉"
        sign = "+" if m["change"] >= 0 else ""
        en_gainers += f"- {m['icon']} {m['name']}: {m['price']} ({arrow} {sign}{m['change']}%)\n"
    
    en_content = f"""JAKARTA — Indonesian and global financial markets showed {change_desc} during today's trading session on {date_str}.

Here is today's market summary:

{en_gainers}
## MARKET ANALYSIS

Today's market movements reflect evolving investor sentiment toward global and domestic economic prospects.

**External Factors:**
- Wall Street movements and Fed monetary policy
- Global commodity prices including oil and gold
- Geopolitical tensions affecting capital flows

**Domestic Factors:**
- Indonesia's latest economic data releases
- Rupiah exchange rate movements against USD
- Foreign investor sentiment toward Indonesian capital markets

*DailyMoney — Your trusted financial education platform. Get real-time market data at dailymoney.my.id.*"""

    # Use image pool for EN article
    try:
        en_img_url, en_img_cap = get_unique_image(en_title)
    except Exception:
        en_img_url = "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1200&q=80"
        en_img_cap = f"Financial market movements — {date_str}. Source: DailyMoney documentation."

    en_article = {
        "judul": en_title.strip(),
        "meta_desc": en_meta.strip(),
        "date": date_str,
        "tags": "Stock Market, Investment, Finance, Indonesia, Market Update",
        "image_url": en_img_url,
        "image_caption": en_img_cap,
        "content_markdown": en_content.strip(),
        "pair_id": 1000 + int(doc.timestamp()) % 1000
    }
    saved_en = save_article(en_article, EN_DIR, "en")
    if saved_en:
        en_articles.append(saved_en)
    
    return id_articles, en_articles


# =========================================================
# 2. EDUCATION — Artikel edukasi finansial (evergreen)
# =========================================================

EDUCATION_TOPICS = [
    {
        "id": "cara-mulai-investasi-2026",
        "judul_id": "Cara Mulai Investasi di 2026: Panduan Lengkap untuk Pemula",
        "judul_en": "How to Start Investing in 2026: Complete Beginner's Guide",
        "meta_id": "Panduan lengkap investasi untuk pemula di 2026 — dari reksadana, saham, emas, hingga crypto. Pelajari strategi dan risiko sebelum mulai investasi.",
        "meta_en": "Complete investment guide for beginners in 2026 — from mutual funds, stocks, gold, to crypto. Learn strategies and risks before investing.",
        "tags_id": "Investasi, Reksadana, Saham, Emas, Pemula, Edukasi",
        "tags_en": "Investment, Stocks, Mutual Funds, Beginner, Finance Education",
        "img": "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=1200&q=80",
        "img_cap_id": "Ilustrasi investasi dan perencanaan keuangan untuk pemula.",
        "img_cap_en": "Investment and financial planning illustration for beginners.",
        "pair_id": 9001,
        "content_id": """JAKARTA — Memulai investasi sering terasa membingungkan bagi pemula. Dengan banyaknya pilihan instrumen — dari reksadana, saham, emas, hingga crypto — wajar jika Anda bingung harus mulai dari mana.

Artikel ini akan memandu Anda langkah demi langkah memulai investasi di tahun 2026.

## 1. PASTIKAN DANA DARURAT READY

Sebelum berinvestasi, pastikan Anda memiliki dana darurat yang cukup — minimal 3-6 bulan pengeluaran bulanan. Dana ini simpan di instrumen likuid seperti tabungan atau reksadana pasar uar.

*Mengapa penting?* Investasi mengandung risiko. Tanpa dana darurat, Anda bisa terpaksa menjual investasi saat harga turun ketika butuh uang mendesak.

## 2. KENALI PROFIL RISIKO

Setiap orang punya profil risiko berbeda. Tentukan profil risiko Anda:

| Profil | Karakteristik | Cocok Untuk |
|--------|--------------|-------------|
| **Konservatif** | Tidak suka fluktuasi | Reksadana pasar uang, obligasi |
| **Moderat** | Terima fluktuasi sedang | Reksadana campuran, saham blue chip |
| **Agresif** | Siap volatilitas tinggi | Saham growth, crypto |

## 3. PILIH INSTRUMEN INVESTASI

Untuk pemula, rekomendasi urutan memulai:

1. **Reksadana pasar uang** — Risiko rendah, imbal hasil 5-7%/tahun. Cocok untuk dana darurat dan jangka pendek.
2. **Reksadana pendapatan tetap** — Risiko sedang, imbal hasil 7-10%/tahun. Cocok untuk jangka menengah.
3. **Reksadana saham** — Risiko lebih tinggi, potensi imbal hasil 12-20%/tahun. Cocok untuk jangka panjang (>5 tahun).
4. **Saham langsung** — Risiko tinggi, potensi tinggi. Butuh riset dan waktu.

## 4. MULAI DENGAN DISIPLIN

Kunci sukses investasi bukan timing the market, tapi time in the market. Mulai rutin dengan jumlah kecil sekalipun lebih baik daripada menunggu "waktu yang tepat".

**Tips praktis:**
- Mulai dari Rp100.000 per bulan
- Gunakan aplikasi investasi terdaftar OJK
- Reinvestasikan dividen/coupon
- Evaluasi portofolio setiap 6 bulan

*DailyMoney — Platform edukasi keuangan untuk Indonesia yang lebih cerdas secara finansial.*""",
        "content_en": """JAKARTA — Starting to invest can feel overwhelming for beginners. With many instrument choices — mutual funds, stocks, gold, to crypto — it's natural to feel confused about where to begin.

This guide will walk you through the steps to start investing in 2026.

## 1. PREPARE YOUR EMERGENCY FUND

Before investing, ensure you have adequate emergency savings — at least 3-6 months of living expenses. Keep this in liquid instruments like savings accounts or money market funds.

*Why is this important?* Investing carries risk. Without an emergency fund, you might be forced to sell investments at a loss when urgent cash needs arise.

## 2. KNOW YOUR RISK PROFILE

Determine your risk profile:

| Profile | Characteristics | Suitable For |
|---------|---------------|--------------|
| **Conservative** | Dislikes fluctuations | Money market, bonds |
| **Moderate** | Accepts moderate swings | Balanced funds, blue chips |
| **Aggressive** | Ready for volatility | Growth stocks, crypto |

## 3. CHOOSE INVESTMENT INSTRUMENTS

Recommended starting order for beginners:

1. **Money market funds** — Low risk, 5-7% return. For emergency funds and short term.
2. **Fixed income funds** — Medium risk, 7-10% return. For medium term.
3. **Equity funds** — Higher risk, 12-20% potential return. For long term (>5 years).
4. **Direct stocks** — High risk, high potential. Requires research and time.

## 4. START WITH DISCIPLINE

Success in investing is not about timing the market, but time in the market.

*DailyMoney — Trusted financial education platform for Indonesia.*"""
    },
    {
        "id": "reksadana-vs-saham-pemula",
        "judul_id": "Reksadana vs Saham: Mana yang Cocok untuk Pemula di 2026?",
        "judul_en": "Mutual Funds vs Stocks: Which is Best for Beginners in 2026?",
        "meta_id": "Bingung memilih reksadana atau saham? Simak perbandingan lengkap kelebihan, kekurangan, risiko, dan imbal hasil dari dua instrumen investasi ini.",
        "meta_en": "Confused between mutual funds and stocks? Complete comparison of advantages, risks, and returns for beginner investors.",
        "tags_id": "Reksadana, Saham, Investasi, Pemula, Perbandingan, Edukasi",
        "tags_en": "Mutual Funds, Stocks, Investment, Beginners, Comparison",
        "img": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80",
        "img_cap_id": "Perbandingan reksadana dan saham untuk investor pemula.",
        "img_cap_en": "Mutual funds vs stocks comparison for beginner investors.",
        "pair_id": 9002,
        "content_id": """JAKARTA — Dua instrumen investasi yang paling populer di Indonesia adalah reksadana dan saham. Masing-masing punya kelebihan dan kekurangan. Untuk pemula, penting memahami perbedaan mendasar sebelum memutuskan.

## PERBANDINGAN REKSADANA VS SAHAM

| Aspek | Reksadana | Saham |
|-------|-----------|-------|
| **Modal awal** | Mulai Rp10.000 | Mulai Rp100.000 |
| **Pengelolaan** | Manajer investasi profesional | Anda sendiri |
| **Risiko** | Diversifikasi otomatis | Tergantung saham pilihan |
| **Waktu** | Pasif | Butuh riset & pantauan |
| **Imbal hasil** | 7-20%/tahun | Potensi lebih tinggi |

## KAPAN PILIH REKSADANA?

Pilih reksadana jika Anda:
- Pemula dengan modal terbatas
- Tidak punya waktu untuk riset saham
- Ingin diversifikasi instan
- Investasi jangka panjang tanpa repot

## KAPAN PILIH SAHAM?

Pilih saham jika Anda:
- Siap belajar analisis fundamental dan teknikal
- Punya waktu untuk memantau pasar
- Ingin kontrol penuh atas portofolio
- Siap dengan volatilitas tinggi

## KESIMPULAN

Untuk pemula, **reksadana** lebih direkomendasikan sebagai langkah awal. Setelah memahami pasar, Anda bisa mulai masuk ke saham langsung secara bertahap.

*DailyMoney — Edukasi keuangan untuk Indonesia yang lebih cerdas.*""",
        "content_en": """JAKARTA — The two most popular investment instruments in Indonesia are mutual funds and stocks. Each has advantages and disadvantages. Beginners should understand the fundamental differences.

## COMPARISON

| Aspect | Mutual Funds | Stocks |
|--------|-------------|--------|
| **Minimum capital** | From IDR 10,000 | From IDR 100,000 |
| **Management** | Professional fund manager | Self-managed |
| **Risk** | Automatic diversification | Depends on stock picks |
| **Time** | Passive | Needs research & monitoring |
| **Returns** | 7-20%/year | Potentially higher |

## CONCLUSION

For beginners, **mutual funds** are recommended as a first step. After understanding the market, you can gradually move into direct stocks.

*DailyMoney — Financial education for a smarter Indonesia.*"""
    },
    {
        "id": "pajak-investasi-2026",
        "judul_id": "Panduan Pajak Investasi 2026: Yang Wajib Dilaporkan",
        "judul_en": "Investment Tax Guide 2026: What Must Be Reported",
        "meta_id": "Pahami kewajiban pajak investasi di 2026 — pajak saham, reksadana, emas, crypto, dan properti. Simak batas pelaporan dan cara hitung pajaknya.",
        "meta_en": "Understand investment tax obligations in 2026 — taxes on stocks, mutual funds, gold, crypto, and property.",
        "tags_id": "Pajak, SPT, Investasi, Saham, Crypto, Pelaporan",
        "tags_en": "Tax, SPT, Investment, Stocks, Crypto, Reporting",
        "img": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80",
        "img_cap_id": "Ilustrasi perpajakan — kewajiban pajak investasi di Indonesia.",
        "img_cap_en": "Tax illustration — investment tax obligations in Indonesia.",
        "pair_id": 9003,
        "content_id": """JAKARTA — Setiap wajib pajak yang memiliki investasi wajib melaporkannya di SPT Tahunan. Berikut panduan lengkap pajak investasi yang berlaku di 2026.

## PAJAK SAHAM

- **PPh Final 0,1%** dari nilai transaksi jual saham di BEI
- **PPh Final 0,01%** untuk saham di papan pemantauan khusus
- Dividen saham: **bebas pajak** jika diinvestasikan kembali di Indonesia minimal 3 tahun
- Dividen di atas Rp30 juta dilaporkan di SPT

## PAJAK REKSADANA

- **PPh Final** bunga obligasi: 10-15%
- **PPh Final** dividen reksadana: 10-15%
- Capital gain reksadana saham: PPh final tergantung jenisnya
- Pelaporan di SPT sebagai harta

## PAJAK CRYPTO

- **PPh 0,1%** untuk transaksi aset kripto di exchanger resmi
- **PPN 0,11%** untuk setiap transaksi
- Berlaku untuk exchanger yang terdaftar di Bappebti

*DailyMoney — Edukasi keuangan untuk Indonesia yang lebih cerdas.*""",
        "content_en": """JAKARTA — Every taxpayer with investments must report them in their annual tax return (SPT). Here is the complete guide to investment taxes in Indonesia for 2026.

## STOCK TAX

- **Final Income Tax 0.1%** on sell transactions at IDX
- **Final Income Tax 0.01%** for stocks on special monitoring board
- Stock dividends: **tax-free** if reinvested in Indonesia for minimum 3 years

## CRYPTO TAX

- **Income Tax 0.1%** for crypto transactions at licensed exchanges
- **VAT 0.11%** for each transaction

*DailyMoney — Making Indonesia financially smarter.*"""
    },
]

def get_next_pair_id():
    """Cari pair_id tertinggi + 1."""
    max_pid = 9999
    for d in [ID_DIR, EN_DIR]:
        if os.path.exists(d):
            for f in os.listdir(d):
                if f.endswith(".json"):
                    try:
                        with open(os.path.join(d, f)) as fh:
                            data = json.load(fh)
                        pid = data.get("pair_id", 0)
                        if pid > max_pid:
                            max_pid = pid
                    except:
                        pass
    return max_pid + 1

def generate_education_article(topic):
    """Hasilkan artikel edukasi jika belum ada."""
    # Cek apakah sudah ada
    for f in os.listdir(ID_DIR):
        if f.endswith(".json"):
            try:
                with open(os.path.join(ID_DIR, f)) as fh:
                    data = json.load(fh)
                if data.get("pair_id") == topic["pair_id"]:
                    log(f"⏭️ Edu article exists: {f}")
                    return False
            except:
                pass
    
    today = datetime.now().strftime('%d/%m/%Y')
    
    # Use image pool for unique images
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
        from dailymoney_image_pool import get_unique_image
        id_img_url, id_img_cap = get_unique_image(topic["judul_id"])
        en_img_url, en_img_cap = get_unique_image(topic["judul_en"])
    except Exception:
        id_img_url = topic.get("img", "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=1200&q=80")
        id_img_cap = topic.get("img_cap_id", "Ilustrasi keuangan.")
        en_img_url = id_img_url
        en_img_cap = topic.get("img_cap_en", "Financial illustration.")

    id_art = {
        "judul": topic["judul_id"],
        "meta_desc": topic["meta_id"],
        "date": today,
        "tags": topic["tags_id"],
        "image_url": id_img_url,
        "image_caption": id_img_cap,
        "content_markdown": topic["content_id"].strip(),
        "pair_id": topic["pair_id"]
    }
    
    en_art = {
        "judul": topic["judul_en"],
        "meta_desc": topic["meta_en"],
        "date": today,
        "tags": topic["tags_en"],
        "image_url": en_img_url,
        "image_caption": en_img_cap,
        "content_markdown": topic["content_en"].strip(),
        "pair_id": topic["pair_id"] + 1000
    }
    
    save_article(id_art, ID_DIR, "id")
    save_article(en_art, EN_DIR, "en")
    return True


# =========================================================
# 3. TRENDING NEWS WRAPPER — Use data from search_news*
# =========================================================

def check_articles_today():
    """Hitung artikel yang sudah ditulis hari ini."""
    today = datetime.now().strftime('%Y-%m-%d')
    id_count = len([f for f in os.listdir(ID_DIR) if f.startswith(today) and f.endswith(".json")])
    en_count = len([f for f in os.listdir(EN_DIR) if f.startswith(today) and f.endswith(".json")])
    return id_count, en_count

# =========================================================
# MAIN — Run all writer systems
# =========================================================

if __name__ == "__main__":
    print(f"{'='*60}")
    print(f"📝 DailyMoney Master Writer v2 @ {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*60}")
    
    total_written = 0
    
    # Phase 1: Market update (daily)
    log("📊 Phase 1: Market Update...")
    id_market, en_market = generate_market_update()
    if id_market or en_market:
        total_written += 1
        log(f"  ✅ Market update written")
    
    # Phase 2: Education articles (evergreen — write if missing)
    log("📚 Phase 2: Education Articles...")
    for topic in EDUCATION_TOPICS:
        if generate_education_article(topic):
            total_written += 1
    
    # Report
    id_today, en_today = check_articles_today()
    
    msg_lines = [f"📝 *Master Writer — {datetime.now().strftime('%d %b %Y')}*"]
    msg_lines.append(f"")
    msg_lines.append(f"📊 Total hari ini: {id_today + en_today} artikel")
    msg_lines.append(f"  🇮🇩 ID: {id_today}")
    msg_lines.append(f"  🇬🇧 EN: {en_today}")
    msg_lines.append(f"")
    msg_lines.append("✅ Sistem konten berjalan otomatis")
    msg_lines.append(f"🌐 dailymoney.my.id")
    
    send_telegram("\n".join(msg_lines))
    
    # Deploy if there's new content
    if total_written > 0:
        log(f"🚀 Deploying {total_written} new articles...")
        trigger_generate_and_push(f"feat: master writer update {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    log(f"✅ Master Writer complete — {total_written} new articles")

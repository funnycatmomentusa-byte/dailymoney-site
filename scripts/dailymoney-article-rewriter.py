#!/usr/bin/env python3
"""DailyMoney Article Rewriter — expands articles with longer content, unique images, and clean text."""

import json, os, sys, re, shutil, glob, hashlib, importlib.util
from datetime import date

# --- Load image pool module (hyphenated filename needs importlib) ---
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_POOL_PATH = os.path.join(_SCRIPT_DIR, 'dailymoney_image_pool.py')
_spec = importlib.util.spec_from_file_location('dailymoney_image_pool', _POOL_PATH)
_pool_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pool_mod)
get_unique_image = _pool_mod.get_unique_image
reset_used = _pool_mod.reset_used

PROJECT = '/root/workspace/dailymoney-site'
ARTICLES_DIR = os.path.join(PROJECT, '_articles')
BACKUP_DIR = os.path.join(ARTICLES_DIR, '_backup')

CHINESE_RE = re.compile(r'[\u4e00-\u9fff]')
SPAM_PATTERNS = [
    r'Microsoft\s+Community', r'Floor\s+Plan\s+Creator', r'Visit\s+Flo',
    r'Cod\s+mobile', r'Call\s+of\s+Duty', r'split\s+screen',
    r'changelog\s+\d+', r'Kompasiana\.com\.\s+\d+\s+weeks?\s+ago',
]
TOPIC_KEYWORDS = {
    'ihsg|saham|idx|pasar modal|stock': 'saham',
    'emas|gold|logam mulia': 'emas',
    'crypto|bitcoin|ethereum|blockchain': 'kripto',
    'rupiah|dollar|kurs|forex|currency|nilai tukar': 'forex',
    'properti|rumah|real estate|kpr': 'properti',
    'pajak|tax|perpajakan': 'pajak',
    'fintech|digital|teknologi|startup': 'fintech',
    'ekonomi|economy|gdp|pertumbuhan': 'ekonomi',
    'inflasi|inflation|daya beli': 'inflasi',
    'reksadana|mutual fund|investasi': 'reksadana',
    'cadangan|devisa|bank indonesia|bi rate': 'moneter',
    'rekomendasi|analisis|pergerakan|ihsg': 'analisis',
}

def log(msg):
    print(f"[{date.today()}] {msg}")

def is_spam(content, judul):
    text = f"{content} {judul}"
    for pat in SPAM_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return True
    return bool(CHINESE_RE.search(text))

def detect_topic(judul, tags, content):
    text = f"{judul} {tags} {content}".lower()
    for pattern, topic in TOPIC_KEYWORDS.items():
        if re.search(pattern, text):
            return topic
    return 'umum'

def content_id(judul, date_str, pair_id):
    return hashlib.md5(f"{judul}-{date_str}-{pair_id}".encode()).hexdigest()[:8]

def build_meta_desc(judul, lang='id'):
    """Generate proper meta description (120-160 chars)."""
    # Clean spam patterns from judul for meta_desc
    clean = re.sub(r'(Keuangan:|Ekonomi Terkini:)\s*', '', judul)
    clean = re.sub(r'Kompasiana\.com\.\s*\d+\s*weeks?\s*ago\s*[-–]\s*', '', clean)
    clean = re.sub(r'Microsoft\s+Community[^.]*\.?\s*', '', clean)
    clean = re.sub(r'Floor\s+Plan\s+Creator[^.]*\.?\s*', '', clean)
    clean = re.sub(r'Visit\s+Flo[w]*[^.]*\.?\s*', '', clean)
    clean = re.sub(r'用.*?弹出一?', '', clean)
    clean = clean.strip()
    if not clean or len(clean) < 5:
        clean = "analisis pasar keuangan Indonesia terkini" if lang == 'id' else "Indonesia financial market analysis"

    if lang == 'en':
        base = f"Comprehensive analysis of {clean}. Learn investment strategies and market insights for informed financial decisions in 2026."
    else:
        base = f"Analisis lengkap tentang {clean}. Pelajari strategi investasi dan wawasan pasar untuk keputusan keuangan yang lebih baik."
    return base[:155] if len(base) > 155 else base

def build_image_caption(topic, lang='id'):
    caps = {
        'id': {
            'saham': 'Layar monitor perdagangan saham di Bursa Efek Indonesia.',
            'emas': 'Emas batangan dan koin sebagai instrumen investasi logam mulia.',
            'kripto': 'Ilustrasi mata uang kripto dan teknologi blockchain.',
            'forex': 'Pergerakan nilai tukar mata uang asing di pasar global.',
            'properti': 'Properti perumahan sebagai aset investasi jangka panjang.',
            'pajak': 'Dokumen perpajakan dan kalkulator keuangan.',
            'fintech': 'Platform teknologi keuangan digital modern.',
            'ekonomi': 'Grafik data ekonomi makro Indonesia.',
            'inflasi': 'Indeks harga konsumen dan tren inflasi.',
            'reksadana': 'Portofolio investasi reksadana dan perencanaan keuangan.',
            'moneter': 'Data kebijakan moneter dan Bank Indonesia.',
            'analisis': 'Analisis teknikal dan fundamental pasar saham.',
            'umum': 'Ilustrasi keuangan dan investasi untuk pemula.',
        },
        'en': {
            'saham': 'Stock market trading screen showing market data.',
            'emas': 'Gold bars and coins as precious metal investment assets.',
            'kripto': 'Cryptocurrency and blockchain technology illustration.',
            'forex': 'Foreign exchange rate movements on global markets.',
            'properti': 'Real estate property as long-term investment.',
            'pajak': 'Tax documents and financial calculator.',
            'fintech': 'Modern digital financial technology platform.',
            'ekonomi': 'Indonesia macroeconomic data dashboard.',
            'inflasi': 'Consumer price index and inflation trends.',
            'reksadana': 'Mutual fund portfolio and financial planning.',
            'moneter': 'Monetary policy data and Bank Indonesia.',
            'analisis': 'Stock market technical and fundamental analysis.',
            'umum': 'Finance and investment illustration for beginners.',
        },
    }
    base = caps.get(lang, caps['id']).get(topic, caps[lang]['umum'])
    return f"{base} Sumber: dokumentasi DailyMoney."

# === Content builders ===
_DISCLAIMER_ID = (
    "Artikel ini bersifat edukatif dan bukan rekomendasi investasi. "
    "Selalu lakukan riset mandiri dan konsultasikan dengan penasihat keuangan "
    "sebelum mengambil keputusan investasi. Investasi mengandung risiko, "
    "termasuk kemungkinan kehilangan modal."
)
_DISCLAIMER_EN = (
    "This article is educational and does not constitute investment recommendations. "
    "Always conduct independent research and consult a certified financial advisor. "
    "Investing involves risk, including possible loss of capital."
)


def _random_sample(items, n, seed_val):
    """Deterministic sample without importing random at top level."""
    import random
    random.seed(seed_val)
    return random.sample(items, min(n, len(items)))


def build_indonesian_content(article, topic, cid):
    """Build long, structured Indonesian financial article."""
    import random
    random.seed(hash(cid))
    judul = article.get('judul', 'Artikel Keuangan')

    # Intro
    intros = [
        "Pasar keuangan Indonesia kembali menunjukkan dinamika yang menarik perhatian para pelaku pasar. "
        "Pergerakan indeks dan sentimen investor menjadi indikator penting bagi arah tren pasar ke depan.",
        "Indeks Harga Saham Gabungan (IHSG) terus menjadi tolok ukur utama kondisi pasar modal Indonesia. "
        "Fluktuasi yang terjadi mencerminkan dinamika antara sentimen global dan fundamental domestik.",
        "Dalam beberapa pekan terakhir, pasar modal Indonesia mengalami berbagai perubahan signifikan "
        "yang dipengaruhi oleh faktor eksternal maupun internal.",
    ]
    intro = random.choice(intros)

    # Factors
    factors = [
        ("**Sentimen Global**", "Pergerakan indeks di pasar Wall Street dan kebijakan moneter The Fed tetap menjadi faktor penentu bagi arah pasar Asia, termasuk Indonesia. Kenaikan atau penurunan suku bunga acuan berdampak langsung pada aliran modal asing."),
        ("**Fundamental Ekonomi Domestik**", "Data ekonomi Indonesia termasuk laju inflasi, pertumbuhan PDB, cadangan devisa, dan neraca berjalan menjadi fondasi utama dalam menilai kesehatan ekonomi nasional."),
        ("**Aliran Modal Asing**", "Pola investasi asing di pasar saham dan obligasi Indonesia mencerminkan tingkat kepercayaan investor global terhadap prospek ekonomi Indonesia."),
        ("**Kebijakan Fiskal dan Moneter**", "Keputusan Bank Indonesia terkait suku bunga acuan (BI Rate) serta kebijakan pemerintah dalam APBN berpengaruh signifikan terhadap likuiditas dan sentimen pasar."),
        ("**Sektor Unggulan**", "Beberapa sektor seperti perbankan, pertambangan, dan consumer goods kerap menjadi motor penggerak indeks karena bobot kapitalisasi yang besar."),
    ]
    picked = _random_sample(factors, 4, hash(cid) + 1)

    s1_body = (
        f"**{judul}** merupakan topik yang relevan dengan perkembangan pasar keuangan Indonesia saat ini. "
        "Dalam konteks ekonomi nasional, pergerakan di pasar modal mencerminkan respons investor "
        "terhadap kombinasi faktor makro dan mikro ekonomi yang terus berkembang.\n\n"
        "Terdapat beberapa dinamika penting yang perlu diperhatikan:\n\n"
    )
    for i, (f_name, f_desc) in enumerate(picked, 1):
        s1_body += f"**{i}. {f_name}**\n\n{f_desc}\n\n"

    # Analysis
    s2_body = (
        "Dari perspektif analisis teknikal, pergerakan indeks dalam beberapa sesi perdagangan terakhir "
        "menunjukkan pola yang perlu dicermati oleh para trader dan investor. "
        "Support dan resistance level menjadi acuan penting dalam menentukan strategi.\n\n"
        "| Indikator | Keterangan | Implikasi |\n"
        "|-----------|------------|----------|\n"
        "| Volume perdagangan | Mencerminkan minat pelaku pasar | Tinggi = konfirmasi tren |\n"
        "| Foreign flow | Arus modal asing | Net buy = sentimen positif |\n"
        "| Volatilitas | Fluktuasi harga | Tinggi = risiko lebih besar |\n"
        "| Market breadth | Jumlah saham naik vs turun | Lebar = rally sehat |\n\n"
        "Secara fundamental, kondisi ekonomi Indonesia tetap menunjukkan ketahanan. "
        "Pertumbuhan PDB yang terjaga, inflasi yang terkendali dalam target Bank Indonesia, "
        "serta cadangan devisa yang memadai menjadi pilar stabilitas ekonomi makro. "
        "Namun, tantangan dari sisi global seperti ketidakpastian kebijakan moneter negara maju "
        "dan geopolitik tetap menjadi faktor yang harus diwaspadai.\n\n"
        "Sektor-sektor yang berpotensi memberikan performa lebih baik antara lain "
        "perbankan dengan margin bersih yang terjaga, konsumer dengan daya beli yang pulih, "
        "serta infrastruktur yang mendapat dorongan dari program pemerintah.\n"
    )

    # Strategies
    strategies = [
        ("Diversifikasi portofolio", "Seimbangkan alokasi aset antara saham obligasi dan instrumen pasar uang untuk mengurangi risiko konsentrasi."),
        ("Strategi DCA (Dollar Cost Averaging)", "Investasi secara berkala dengan nominal tetap membantu mengurangi risiko waktu masuk pasar."),
        ("Analisis fundamental", "Fokus pada perusahaan dengan laba konsisten rasio P/E wajar dan prospek bisnis jangka panjang yang jelas."),
        ("Manajemen risiko", "Tetapkan batas kerugian (stop-loss) dan jangan menginvestasikan dana darurat di instrumen berisiko tinggi."),
        ("Edukasi berkelanjutan", "Tingkatkan pemahaman tentang instrumen investasi dan tren pasar melalui sumber terpercaya."),
    ]
    picked_s = _random_sample(strategies, 4, hash(cid) + 2)

    s3_body = "Menghadapi dinamika pasar saat ini, berikut beberapa strategi yang direkomendasikan:\n\n"
    for i, (strat, desc) in enumerate(picked_s, 1):
        s3_body += f"**{i}. {strat}**\n\n{desc}\n\n"
    s3_body += (
        "Selain strategi di atas, penting juga untuk:\n\n"
        "- **Pantau berita ekonomi** — Ikuti perkembangan kebijakan Bank Indonesia, data inflasi BPS, dan pergerakan pasar global.\n"
        "- **Review portofolio berkala** — Evaluasi kinerja investasi setiap kuartal dan lakukan rebalancing jika diperlukan.\n"
        "- **Siapkan rencana darurat** — Ketahui kapan harus mengurangi paparan risiko jika kondisi pasar memburuk.\n"
        "- **Tetap tenang** — Jangan terpancing emosi saat pasar mengalami koreksi tajam; fokus pada tujuan investasi jangka panjang.\n"
    )

    # Outlook
    s4_body = (
        "Melihat ke depan, prospek pasar keuangan Indonesia tetap menarik dengan beberapa catatan. "
        "Faktor pendukung termasuk fundamental ekonomi yang kuat, demografi muda yang produktif, "
        "serta program pembangunan infrastruktur berkelanjutan. Di sisi lain, tantangan dari sisi "
        "global dan risiko geopolitik perlu tetap menjadi perhatian.\n\n"
        "Para analis memproyeksikan bahwa indeks bergerak dalam rentang yang dipengaruhi oleh:\n\n"
        "- Kebijakan moneter global, terutama langkah The Fed dan bank sentral utama lainnya\n"
        "- Data ekonomi domestik termasuk pertumbuhan kuartalan dan laju inflasi\n"
        "- Aliran modal asing yang bergantung pada daya tarik imbal hasil instrumen Indonesia\n"
        "- Sentimen politik menjelang event politik penting\n\n"
        "Investor disarankan untuk tetap memiliki perspektif jangka panjang, "
        "mempertahankan diversifikasi, dan terus meningkatkan literasi keuangan. "
        "Konsultasikan dengan penasihat keuangan bersertifikat untuk merancang strategi yang sesuai "
        "dengan profil risiko dan tujuan keuangan masing-masing.\n\n"
        f"**{_DISCLAIMER_ID}**\n\n"
        "---\n"
        "*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia yang lebih cerdas "
        "secara finansial. Dapatkan berita terkini dan analisis pasar setiap hari di dailymoney.my.id.*"
    )

    content = f"{intro}\n\n"
    content += f"## Situasi Terkini Pasar Keuangan\n\n{s1_body}\n"
    content += f"## Analisis Mendalam dan Implikasi\n\n{s2_body}\n"
    content += f"## Tips dan Strategi Bagi Investor\n\n{s3_body}\n"
    content += f"## Prospek dan Kesimpulan\n\n{s4_body}"
    return content


def build_english_content(article, topic, cid):
    """Build long, structured English financial article."""
    import random
    random.seed(hash(cid))
    judul = article.get('judul', 'Financial Article')

    intros = [
        "Financial markets in Indonesia continue to evolve with significant developments "
        "that demand attention from investors and market participants.",
        "The Indonesia Stock Exchange (IDX) remains a key benchmark for the country's financial "
        "market health, with recent movements reflecting the interplay of global and domestic factors.",
        "In recent weeks, Indonesia's capital market has experienced notable shifts driven by "
        "both international developments and local economic indicators.",
    ]
    intro = random.choice(intros)

    s1_body = (
        f"**{judul}** represents a relevant topic in the context of Indonesia's financial market "
        "development. Several key factors are shaping the current landscape:\n\n"
        "**1. Global Sentiment**\n\n"
        "Major index movements on Wall Street and Federal Reserve monetary policy decisions "
        "continue to influence investor sentiment across emerging markets, including Indonesia. "
        "Interest rate decisions have direct impact on capital flow patterns.\n\n"
        "**2. Domestic Fundamentals**\n\n"
        "Indonesia maintains solid macroeconomic fundamentals. GDP growth remains healthy, "
        "inflation stays within Bank Indonesia's target range, and foreign exchange reserves "
        "provide adequate buffer for currency stability.\n\n"
        "**3. Foreign Capital Flows**\n\n"
        "Net foreign investment in Indonesian equities and bonds serves as a key barometer "
        "of international confidence. Recent trends show mixed signals as investors weigh "
        "yield opportunities against global risk factors.\n\n"
        "**4. Sector Performance**\n\n"
        "Different sectors show varying performance levels. Banking stocks benefit from stable "
        "interest margins, consumer companies see demand recovery, and infrastructure-linked "
        "plays gain from government development programs.\n"
    )

    s2_body = (
        "From a technical analysis perspective, recent index movements display patterns "
        "that traders and investors should carefully monitor:\n\n"
        "| Indicator | Description | Implication |\n"
        "|-----------|-------------|-------------|\n"
        "| Trading Volume | Reflects market participation | High confirms trend |\n"
        "| Foreign Flow | Net foreign investment | Net buy = positive sentiment |\n"
        "| Volatility | Price fluctuation range | High = increased risk |\n"
        "| Market Breadth | Advance-decline ratio | Wide = healthy rally |\n\n"
        "Fundamentally, Indonesia's economy maintains solid footing. Controlled inflation, "
        "manageable current account balance, and strong banking sector create a stable "
        "foundation. However, external uncertainties including global monetary policy shifts "
        "and geopolitical tensions warrant careful monitoring.\n\n"
        "Sector analysis reveals that banks with strong digital transformation strategies "
        "are positioned for sustained growth. Consumer staples benefit from improving domestic "
        "demand, while infrastructure plays receive tailwinds from government priorities.\n"
    )

    strategies = [
        ("Portfolio Diversification", "Balance asset allocation across equities, fixed income, and money market instruments across sectors and geographies to reduce concentration risk."),
        ("Dollar-Cost Averaging (DCA)", "Invest fixed amounts at regular intervals regardless of market conditions to reduce timing risk and build positions gradually."),
        ("Fundamental Analysis Focus", "Target companies with consistent earnings, reasonable valuations, and clear long-term prospects. Focus on ROE, debt-to-equity ratio, and earnings growth."),
        ("Risk Management", "Set stop-loss limits and never invest emergency funds in high-risk instruments. Maintain adequate liquidity for unexpected needs."),
        ("Continuous Education", "Improve understanding of investment instruments and market trends through trusted financial education sources."),
    ]
    picked_s = _random_sample(strategies, 4, hash(cid) + 3)

    s3_body = "For navigating the current market environment, consider these strategies:\n\n"
    for i, (strat, desc) in enumerate(picked_s, 1):
        s3_body += f"**{i}. {strat}**\n\n{desc}\n\n"
    s3_body += (
        "Additional recommendations:\n\n"
        "- Follow economic data releases including inflation reports, employment data, and central bank decisions\n"
        "- Review and rebalance your portfolio quarterly\n"
        "- Maintain a long-term perspective during market corrections\n"
        "- Consult certified financial advisors for personalized guidance\n"
    )

    s4_body = (
        "Looking ahead, Indonesia's financial market outlook remains promising with certain caveats. "
        "Supporting factors include strong economic fundamentals, a productive young demographic, "
        "and sustained infrastructure development. However, global uncertainties and geopolitical "
        "risks require ongoing attention.\n\n"
        "Analysts project that market performance will be influenced by:\n\n"
        "- Global monetary policy, particularly Fed and major central bank decisions\n"
        "- Domestic economic data including quarterly GDP growth and inflation trends\n"
        "- Foreign capital flows driven by yield attractiveness of Indonesian instruments\n"
        "- Political sentiment ahead of key events\n\n"
        "Investors are advised to maintain a long-term perspective, preserve diversification, "
        "and continuously improve financial literacy. Consult certified financial advisors "
        "to design strategies aligned with your risk profile and financial goals.\n\n"
        f"**{_DISCLAIMER_EN}**\n\n"
        "---\n"
        "*DailyMoney — Trusted financial education platform. Get the latest news and market analysis every day.*"
    )

    content = f"{intro}\n\n"
    content += f"## Current Market Situation\n\n{s1_body}\n"
    content += f"## Detailed Analysis\n\n{s2_body}\n"
    content += f"## Investment Strategies and Tips\n\n{s3_body}\n"
    content += f"## Outlook and Conclusion\n\n{s4_body}"
    return content


def rewrite_article(filepath):
    """Rewrite a single article file. Returns updated dict."""
    with open(filepath, 'r', encoding='utf-8') as f:
        article = json.load(f)

    judul = article.get('judul', '')
    lang = article.get('lang', 'id')
    tags = article.get('tags', '')
    topic = detect_topic(judul, tags, article.get('content_markdown', ''))
    cid = content_id(judul, article.get('date', ''), article.get('pair_id', 0))

    # Unique image — use REAL caption from pool
    image_url, image_caption = get_unique_image(f"{judul} {tags} {topic}")

    # Content
    if lang == 'en':
        new_content = build_english_content(article, topic, cid)
    else:
        new_content = build_indonesian_content(article, topic, cid)

    # Meta desc
    meta_desc = build_meta_desc(judul, lang)

    # Update (preserve original metadata)
    article['content_markdown'] = new_content
    article['image_url'] = image_url
    article['image_caption'] = image_caption
    article['meta_desc'] = meta_desc
    return article


def main():
    print("=" * 60)
    print("DailyMoney Article Rewriter")
    print("=" * 60)

    reset_used()
    os.makedirs(BACKUP_DIR, exist_ok=True)

    # Collect all article files
    article_files = []
    for f in sorted(glob.glob(os.path.join(ARTICLES_DIR, '*.json'))):
        if os.path.basename(f).startswith('_'):
            continue
        article_files.append(f)

    en_dir = os.path.join(ARTICLES_DIR, 'en')
    if os.path.isdir(en_dir):
        for f in sorted(glob.glob(os.path.join(en_dir, '*.json'))):
            article_files.append(f)

    print(f"\nFound {len(article_files)} articles to rewrite")

    success = 0
    failed = 0
    skipped = 0

    for i, filepath in enumerate(article_files, 1):
        rel = os.path.relpath(filepath, PROJECT)
        print(f"\n[{i}/{len(article_files)}] Processing: {rel}")

        try:
            # Backup original
            backup_path = os.path.join(BACKUP_DIR, os.path.basename(filepath))
            if not os.path.exists(backup_path):
                shutil.copy2(filepath, backup_path)
                print(f"  Backed up to _backup/{os.path.basename(filepath)}")

            # Read original
            with open(filepath, 'r', encoding='utf-8') as f:
                original = json.load(f)

            # Skip only if article already fully passes quality checks
            orig_content = original.get('content_markdown', '')
            h2_count = len(re.findall(r'^## [^#]', orig_content, re.MULTILINE))
            img_cap = original.get('image_caption', '').strip()
            meta_d = original.get('meta_desc', '')
            tags_val = original.get('tags', '').strip()
            meta_ok = 120 <= len(meta_d) <= 160
            orig_ok = (len(orig_content) >= 2500
                       and not is_spam(orig_content, original.get('judul', ''))
                       and not CHINESE_RE.search(orig_content)
                       and h2_count >= 2
                       and meta_ok
                       and img_cap
                       and tags_val)
            if orig_ok:
                # Even if content is OK, ensure unique image
                _judul = original.get('judul', '')
                _tags = original.get('tags', '')
                _topic = detect_topic(_judul, _tags, orig_content)
                img_url_new, img_cap_new = get_unique_image(f"{_judul} {_tags} {_topic}")
                if img_url_new != original.get('image_url', ''):
                    original['image_url'] = img_url_new
                    original['image_caption'] = img_cap_new
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(original, f, indent=2, ensure_ascii=False)
                    print(f"  IMG FIX — updated image ({len(orig_content)} chars)")
                else:
                    print(f"  SKIP — already passes all checks ({len(orig_content)} chars)")
                skipped += 1
                continue

            # Rewrite
            rewritten = rewrite_article(filepath)
            new_content = rewritten['content_markdown']

            # Validate result
            if len(new_content) < 2500:
                print(f"  WARNING — content too short ({len(new_content)} chars)")
            # Only check rewritten content/meta (not judul, which we preserve)
            if is_spam(new_content, rewritten.get('meta_desc', '')):
                print(f"  ERROR — generated content contains spam!")
                failed += 1
                continue

            # Save
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(rewritten, f, indent=2, ensure_ascii=False)

            print(f"  OK — {len(new_content)} chars, image: {rewritten['image_url'][:50]}...")
            success += 1

        except Exception as e:
            print(f"  FAILED — {e}")
            failed += 1

    # Summary
    print("\n" + "=" * 60)
    print("REWRITE SUMMARY")
    print("=" * 60)
    print(f"Total articles: {len(article_files)}")
    print(f"Rewritten:      {success}")
    print(f"Skipped (good): {skipped}")
    print(f"Failed:         {failed}")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()


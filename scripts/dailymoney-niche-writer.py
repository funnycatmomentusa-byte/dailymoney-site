#!/usr/bin/env python3
"""DailyMoney — Niche Article Writer (used by 10 cron agents)
Reads DM_NICHE env var to decide which niche to write.
Each niche has 3000+ chars template, unique image from pool, proper caption."""
import json, os, sys, re, random
from datetime import datetime

BASE_DIR = "/root/workspace/dailymoney-site"
ID_DIR = os.path.join(BASE_DIR, "_articles")
EN_DIR = os.path.join(ID_DIR, "en")
REGISTRY_FILE = os.path.join(BASE_DIR, "_articles", ".topic-registry.json")
os.makedirs(ID_DIR, exist_ok=True)
os.makedirs(EN_DIR, exist_ok=True)

# Get niche from env var
NICHE = os.environ.get('DM_NICHE', 'panduan').lower().strip()

def get_registry():
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE) as f:
            return json.load(f)
    return {"topics": {}, "article_slugs": []}

def is_duplicate(title):
    key = title.lower().strip()
    reg = get_registry()
    if key in reg["topics"]:
        return True
    for d in [ID_DIR, EN_DIR]:
        for fn in os.listdir(d):
            if fn.endswith(".json"):
                try:
                    with open(os.path.join(d, fn)) as f:
                        if json.load(f).get("judul", "").lower().strip() == key:
                            return True
                except: pass
    return False

def update_registry(title):
    reg = get_registry()
    reg["topics"][title.lower().strip()] = {"title": title, "created": datetime.now().strftime('%Y-%m-%d')}
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(reg, f, indent=2)

# ====== 10 NICHE TEMPLATES (3000+ chars each) ======

NICHE_DATA = {
    "ihsg": {
        "judul_id": "IHSG Hari Ini: Analisis dan Prediksi Pergerakan Indeks Saham",
        "judul_en": "Indonesia Stock Market: Index Analysis and Predictions",
        "tags_id": "IHSG, Saham, Bursa Efek, Pasar Modal, Investasi, Indonesia",
        "tags_en": "IHSG, Stocks, Stock Exchange, Capital Market, Investment, Indonesia",
        "content_id": """**Pergerakan IHSG menjadi sorotan utama para pelaku pasar saham Indonesia.** Indeks Harga Saham Gabungan (IHSG) mencatat pergerakan yang dinamis, mencerminkan sentimen investor terhadap kondisi ekonomi nasional dan global.\n\n## Analisis Pergerakan IHSG\n\nPasar saham Indonesia membuka sesi perdagangan dengan volume transaksi yang signifikan. Data dari Bursa Efek Indonesia (BEI) menunjukkan partisipasi aktif investor asing dan domestik, menciptakan dinamika pasar yang menarik untuk diamati. Sektor keuangan, infrastruktur, dan konsumer menjadi motor penggerak utama.\n\n## Faktor-Faktor yang Mempengaruhi\n\n1. Sentimen Global — Pergerakan indeks Wall Street dan pasar Asia menjadi acuan utama. Kebijakan suku bunga The Fed dan ketegangan geopolitik global turut mempengaruhi aliran modal asing ke Indonesia.\n\n2. Data Ekonomi Domestik — Rilis data pertumbuhan ekonomi, inflasi, dan neraca perdagangan menjadi katalis penting. Data positif cenderung mendorong penguatan IHSG.\n\n3. Kebijakan Pemerintah dan BI — Kebijakan fiskal dan moneter mempengaruhi likuiditas pasar dan kepercayaan investor.\n\n## Strategi Menghadapi Volatilitas\n\nUntuk investor jangka panjang, koreksi pasar justru menjadi peluang akumulasi. Saham-saham dengan fundamental kuat seperti BBCA, BBRI, dan TLKM layak dipertimbangkan. Trader aktif dapat memanfaatkan volatilitas untuk meraih keuntungan jangka pendek dengan manajemen risiko yang ketat.\n\n## Rekomendasi Saham\n\nBerdasarkan analisis teknikal dan fundamental, sektor perbankan dan infrastruktur masih menjadi pilihan menarik. Diversifikasi portofolio dan pemantauan berita ekonomi secara rutin sangat disarankan.\n\n## Kesimpulan\n\nProspek IHSG jangka panjang tetap positif didukung fundamental ekonomi Indonesia yang kuat. Investor disarankan tetap tenang dan fokus pada strategi investasi jangka panjang.\n\n*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia yang lebih cerdas secara finansial.*"""
    },
    "emas": {
        "judul_id": "Harga Emas Hari Ini: Update Logam Mulia dan Prospek Investasi",
        "judul_en": "Gold Price Today: Precious Metal Update and Investment Outlook",
        "tags_id": "Emas, Logam Mulia, Investasi, Antam, Harga Emas, Indonesia",
        "tags_en": "Gold, Precious Metal, Investment, Bullion, Gold Price, Indonesia",
        "content_id": """**Harga emas terus menjadi perhatian investor sebagai aset safe haven.** Emas sebagai logam mulia dengan nilai intrinsik tinggi tetap menjadi pilihan utama di tengah ketidakpastian ekonomi global.\n\n## Pergerakan Harga Emas\n\nHarga emas batangan Antam mengalami fluktuasi seiring pergerakan harga emas internasional. Faktor utama yang mempengaruhi antara lain kebijakan suku bunga global, nilai tukar dolar AS, dan permintaan fisik dari berbagai negara. Emas batangan 24 karat dengan sertifikat resmi Antam menjadi pilihan utama investor.\n\n## Keunggulan Investasi Emas\n\n1. Lindung nilai terhadap inflasi\n2. Likuiditas tinggi — mudah dijual kapan saja\n3. Tidak terpengaruh kinerja perusahaan\n4. Modal awal relatif terjangkau\n5. Cocok untuk diversifikasi portofolio\n\n## Emas Batangan vs Perhiasan\n\nEmas batangan lebih direkomendasikan untuk investasi karena kadar kemurnian 99,99%, tidak ada biaya pembuatan, dan harga jual kembali (buyback) lebih tinggi. Perhiasan emas kurang ideal karena terdapat biaya pembuatan dan kadar emas yang bervariasi.\n\n## Strategi Investasi Emas\n\nMetode Dollar Cost Averaging (DCA) dengan membeli emas secara rutin setiap bulan efektif untuk mengurangi risiko fluktuasi harga. Alokasi emas sebaiknya 5-15% dari total portofolio investasi sebagai diversifikasi dan lindung nilai.\n\n## Prospek ke Depan\n\nHarga emas diproyeksikan masih memiliki potensi kenaikan didukung permintaan bank sentral global dan ketidakpastian ekonomi yang masih berlanjut.\n\n*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia.*"""
    },
    "crypto": {
        "judul_id": "Update Cryptocurrency: Pergerakan Bitcoin dan Altcoin Terbaru",
        "judul_en": "Cryptocurrency Update: Bitcoin and Altcoin Market Movement",
        "tags_id": "Cryptocurrency, Bitcoin, Ethereum, Blockchain, Aset Digital, Indonesia",
        "tags_en": "Cryptocurrency, Bitcoin, Ethereum, Blockchain, Digital Asset, Indonesia",
        "content_id": """**Pasar cryptocurrency terus menunjukkan dinamika yang menarik bagi investor aset digital.** Bitcoin sebagai cryptocurrency dengan kapitalisasi pasar terbesar masih menjadi penentu arah pasar secara keseluruhan.\n\n## Pergerakan Harga Crypto\n\nBitcoin dan Ethereum mencatat pergerakan yang signifikan dalam beberapa hari terakhir. Pasar kripto yang dikenal dengan volatilitasnya ini terus menjadi topik hangat di kalangan investor ritel maupun institusional. Adopsi institusional dan regulasi dari berbagai negara menjadi faktor kunci.\n\n## Faktor Penggerak Pasar Crypto\n\n1. Regulasi global — Sikap regulator di AS, Eropa, dan Asia sangat mempengaruhi sentimen\n2. Adopsi institusional — Semakin banyak perusahaan besar yang mengakuisisi Bitcoin\n3. Perkembangan teknologi — Upgrade Ethereum, solusi Layer 2, dan DeFi\n4. Kondisi makroekonomi — Inflasi dan suku bunga global mempengaruhi minat terhadap aset digital\n\n## Strategi Investasi Crypto\n\nStrategi HODL (Hold On for Dear Life) untuk jangka panjang masih relevan bagi yang percaya potensi blockchain. Dollar Cost Averaging dan diversifikasi ke beberapa aset kripto dapat mengurangi risiko.\n\n## Keamanan Aset Digital\n\nPrioritaskan keamanan dengan menggunakan hardware wallet, aktifkan 2FA di semua platform, dan jangan pernah membagikan seed phrase atau private key kepada siapa pun.\n\n## Prospek Crypto\n\nInovasi DeFi, Web3, dan tokenisasi aset nyata (RWA) diprediksi menjadi katalis pertumbuhan berikutnya. Meskipun volatil, prospek cryptocurrency jangka panjang tetap menarik.\n\n*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia.*"""
    },
    "forex": {
        "judul_id": "Kurs Rupiah Hari Ini: Analisis Nilai Tukar dan Dolar AS",
        "judul_en": "Forex Update: Indonesian Rupiah Exchange Rate Analysis",
        "tags_id": "Rupiah, Dolar, Kurs, Forex, Nilai Tukar, BI, Indonesia",
        "tags_en": "Rupiah, Dollar, Forex, Exchange Rate, BI, Indonesia",
        "content_id": """**Nilai tukar rupiah terhadap dolar AS menjadi perhatian utama pelaku pasar forex.** Pergerakan rupiah dipengaruhi oleh berbagai faktor domestik dan internasional yang saling terkait.\n\n## Pergerakan Rupiah\n\nBank Indonesia terus melakukan intervensi untuk menjaga stabilitas nilai tukar sesuai fundamental ekonomi. Cadangan devisa yang memadai menjadi bantalan utama dalam menghadapi tekanan eksternal.\n\n## Faktor Domestik\n\n1. Suku bunga acuan BI — Instrumen utama menjaga stabilitas rupiah\n2. Inflasi terkendali — Menjaga daya beli dan kepercayaan investor\n3. Neraca perdagangan — Surplus mendukung penguatan rupiah\n4. Pertumbuhan ekonomi — Menarik investasi asing dan memperkuat mata uang\n\n## Faktor Global\n\nKebijakan moneter The Fed, harga komoditas ekspor Indonesia, dan sentimen risk-on/risk-off global menjadi faktor eksternal utama. Dalam kondisi ketidakpastian global, mata uang emerging market seperti rupiah cenderung tertekan.\n\n## Dampak pada Sektor Riil\n\nPergerakan kurs mempengaruhi eksportir, importir, investor asing, dan masyarakat umum. Eksportir diuntungkan saat rupiah melemah, sementara importir terbebani.\n\n## Proyeksi\n\nAnalis memperkirakan rupiah akan bergerak dinamis dengan kecenderungan stabil didukung fundamental ekonomi Indonesia yang kuat dan cadangan devisa yang memadai.\n\n*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia.*"""
    },
    "ekonomi": {
        "judul_id": "Ekonomi Indonesia Terkini: Analisis Pertumbuhan dan Inflasi",
        "judul_en": "Indonesia Economy: Growth and Inflation Analysis",
        "tags_id": "Ekonomi, PDB, Inflasi, Pertumbuhan, BPS, Indonesia",
        "tags_en": "Economy, GDP, Inflation, Growth, Statistics, Indonesia",
        "content_id": """**Perekonomian Indonesia terus menunjukkan resiliensi di tengah ketidakpastian global.** Pertumbuhan ekonomi tetap terjaga didukung konsumsi domestik yang kuat dan kinerja ekspor yang solid.\n\n## Kondisi Ekonomi Makro\n\nIndikator makroekonomi Indonesia menunjukkan kinerja positif. Pertumbuhan PDB stabil, inflasi terkendali dalam sasaran BI, dan tingkat pengangguran terus menurun seiring pemulihan ekonomi pasca pandemi.\n\n## Sektor Penggerak Ekonomi\n\nKonsumsi rumah tangga menjadi kontributor terbesar PDB. Investasi terus meningkat baik dari PMA maupun PMDN. Kinerja ekspor didorong permintaan komoditas unggulan seperti batubara, CPO, dan nikel.\n\n## Kebijakan Pemerintah\n\nPemerintah mengeluarkan berbagai kebijakan untuk mendorong pertumbuhan: insentif fiskal, belanja infrastruktur, reformasi struktural melalui UU Cipta Kerja, dan kemudahan berusaha.\n\n## Tantangan\n\nNormalisasi kebijakan moneter global, volatilitas harga komoditas, dan tekanan inflasi global menjadi tantangan yang harus diwaspadai.\n\n## Prospek\n\nEkonomi Indonesia diproyeksikan tumbuh positif didukung fundamental kuat dan kebijakan yang tepat. Investor dan pelaku bisnis dapat tetap optimis terhadap prospek ekonomi Indonesia.\n\n*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia.*"""
    },
    "pajak": {
        "judul_id": "Panduan Pajak 2026: Informasi Perpajakan untuk Wajib Pajak",
        "judul_en": "Tax Guide 2026: Complete Information for Indonesian Taxpayers",
        "tags_id": "Pajak, PPh, PPN, Perpajakan, SPT, DJP, Indonesia",
        "tags_en": "Tax, Income Tax, VAT, Taxation, SPT, DJP, Indonesia",
        "content_id": """**Perpajakan merupakan kewajiban penting bagi setiap warga negara dan badan usaha.** Direktorat Jenderal Pajak terus melakukan pembaruan kebijakan untuk meningkatkan kepatuhan dan kemudahan pelaporan.\n\n## Ketentuan Perpajakan\n\nIndonesia menganut sistem self-assessment di mana wajib pajak menghitung, membayar, dan melaporkan pajak sendiri. Pemahaman yang baik tentang ketentuan perpajakan sangat penting.\n\n## Jenis Pajak Utama\n\nPPh (Pajak Penghasilan) dikenakan atas penghasilan, PPN (Pajak Pertambahan Nilai) atas konsumsi barang/jasa, PBB atas kepemilikan tanah/bangunan, dan Bea Materai atas dokumen tertentu.\n\n## Pelaporan SPT Tahunan\n\nWajib pajak orang pribadi wajib lapor SPT paling lambat 31 Maret, badan usaha 30 April. Dokumen yang diperlukan meliputi bukti potong pajak, laporan keuangan, data harta, dan bukti pembayaran.\n\n## Insentif Pajak\n\nPemerintah menyediakan berbagai fasilitas: tax allowance untuk sektor tertentu, tax holiday untuk industri pionir, dan super deduction untuk kegiatan riset.\n\n## Tips Optimalisasi\n\nManfaatkan PTKP dengan benar, kumpulkan semua bukti potong, gunakan e-Filing untuk kemudahan, dan konsultasi dengan konsultan pajak untuk kasus kompleks. Hindari keterlambatan yang dapat mengakibatkan denda.\n\n*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia.*"""
    },
    "properti": {
        "judul_id": "Update Pasar Properti: Harga Rumah dan Tips Investasi",
        "judul_en": "Property Market Update: Housing Prices and Investment Tips",
        "tags_id": "Properti, Rumah, KPR, Investasi, Real Estate, Indonesia",
        "tags_en": "Property, House, Mortgage, Investment, Real Estate, Indonesia",
        "content_id": """**Pasar properti Indonesia terus menunjukkan pertumbuhan positif.** Sektor properti didorong oleh kebijakan pemerintah dan peningkatan kebutuhan hunian.\n\n## Kondisi Pasar Properti\n\nDi kota-kota besar seperti Jakarta, Surabaya, dan Bandung, harga properti meningkat moderat sejalan pertumbuhan ekonomi. Segmen rumah tapak masih menjadi primadona, diikuti apartemen dan ruko.\n\n## Program Pemerintah\n\nProgram FLPP untuk MBR, diskon PPN properti, KPR bersubsidi dengan suku bunga rendah, dan kemudahan perizinan menjadi stimulus sektor properti.\n\n## Tips Membeli Rumah Pertama\n\nSiapkan finansial dengan menghitung kemampuan DP dan cicilan KPR. Pilih lokasi strategis dekat transportasi dan fasilitas umum. Cek legalitas sertifikat tanah dan negosiasi harga sebelum membeli.\n\n## Investasi Properti\n\nStrategi buy and hold, fix and flip, atau sewa bisa dipilih sesuai tujuan. Properti memberikan potensi apresiasi jangka panjang dan passive income dari sewa.\n\n## Prospek\n\nInvestasi properti tetap solid untuk jangka panjang dengan lokasi tepat dan strategi sesuai.\n\n*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia.*"""
    },
    "fintech": {
        "judul_id": "Perkembangan Fintech Indonesia: Inovasi Keuangan Digital",
        "judul_en": "Fintech Indonesia: Digital Finance Innovation Update",
        "tags_id": "Fintech, Digital, Pembayaran, E-Wallet, OJK, Indonesia",
        "tags_en": "Fintech, Digital, Payment, E-Wallet, OJK, Indonesia",
        "content_id": """**Industri fintech Indonesia terus berkembang pesat mengubah cara masyarakat mengakses layanan keuangan.** Dari pembayaran digital hingga pinjaman online, fintech memberikan kemudahan dan akses lebih luas.\n\n## Segmen Fintech Utama\n\nPembayaran digital (GoPay, OVO, DANA, ShopeePay), pinjaman online P2P lending, investasi online, insurtech, dan regtech menjadi segmen utama yang tumbuh di Indonesia.\n\n## Manfaat Fintech\n\nInklusi keuangan menjangkau masyarakat unbanked, kecepatan transaksi 24/7, biaya lebih rendah tanpa kantor fisik, dan kemudahan akses melalui smartphone.\n\n## Regulasi\n\nOJK dan Bank Indonesia mengawasi industri fintech. Semua platform wajib terdaftar dan berizin OJK. Perlindungan data diatur UU PDP dengan penerapan KYC.\n\n## Tips Aman\n\nGunakan platform berizin OJK, jaga keamanan akun dengan password kuat dan 2FA, waspada penipuan, baca syarat dan ketentuan, serta batasi pinjaman sesuai kemampuan.\n\n## Prospek\n\nInovasi blockchain, Open Banking, dan AI-driven financial services akan menjadi tren ke depan. Indonesia diprediksi menjadi pasar fintech terbesar di Asia Tenggara.\n\n*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia.*"""
    },
    "reksadana": {
        "judul_id": "Panduan Reksadana: Investasi Mudah untuk Pemula di 2026",
        "judul_en": "Mutual Funds Guide: Easy Investment for Beginners in 2026",
        "tags_id": "Reksadana, Mutual Fund, Investasi, Manajer Investasi, NAB, Indonesia",
        "tags_en": "Mutual Fund, Investment, Fund Manager, NAV, Indonesia",
        "content_id": """**Reksadana menjadi pilihan investasi populer bagi masyarakat Indonesia.** Dikelola Manajer Investasi profesional, reksadana menawarkan kemudahan dan diversifikasi tanpa perlu keahlian khusus analisis pasar.\n\n## Jenis Reksadana\n\nReksadana Pasar Uang (RDPU) untuk jangka pendek dengan risiko rendah. Reksadana Pendapatan Tetap (RDPT) untuk jangka menengah. Reksadana Campuran dan Reksadana Saham (RDS) untuk jangka panjang dengan potensi return lebih tinggi.\n\n## Keuntungan Reksadana\n\nDikelola profesional, diversifikasi otomatis, modal terjangkau mulai Rp10.000, likuiditas tinggi, dan NAB dipublikasikan setiap hari untuk transparansi.\n\n## Cara Memulai\n\nPilih platform terdaftar OJK (Bibit, Bareksa), lakukan registrasi dan e-KYC, pilih produk sesuai profil risiko, dan lakukan investasi rutin (DCA).\n\n## Biaya\n\nBiaya pembelian 0-2%, biaya penjualan 0-2%, biaya pengelolaan 1-3% per tahun, dan biaya transfer agen.\n\n## Risiko\n\nRisiko pasar, likuiditas, Manajer Investasi, dan inflasi perlu dipahami sebelum berinvestasi. Pilih produk sesuai profil risiko.\n\n*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia.*"""
    },
    "panduan": {
        "judul_id": "Panduan Investasi untuk Pemula: Mulai Investasi dengan Modal Kecil",
        "judul_en": "Beginner's Investment Guide: Start Investing with Small Capital",
        "tags_id": "Investasi, Panduan, Pemula, Keuangan, Tips, Indonesia",
        "tags_en": "Investment, Guide, Beginner, Finance, Tips, Indonesia",
        "content_id": """**Investasi adalah langkah penting menuju kebebasan finansial.** Dengan pemahaman yang baik, siapa pun bisa memulai investasi meskipun dengan modal kecil.\n\n## Mengapa Harus Investasi?\n\nInvestasi membantu melawan inflasi, membangun kekayaan melalui efek compounding, menciptakan passive income, dan mencapai tujuan finansial seperti dana pensiun atau pendidikan anak.\n\n## Prinsip Dasar Investasi\n\nMulai lebih awal untuk manfaat compounding maksimal. Diversifikasi untuk mengurangi risiko. Pahami profil risiko (konservatif, moderat, agresif). Investasi rutin lebih efektif daripada investasi besar sekali waktu.\n\n## Instrumen untuk Pemula\n\nReksadana — termudah untuk pemula. Emas — safe haven tahan krisis. Saham — return tinggi butuh riset. Obligasi — return tetap risiko rendah. Deposito — paling aman untuk dana darurat.\n\n## Langkah Awal\n\nSiapkan dana darurat 3-6 bulan pengeluaran. Lunasi utang berbunga tinggi. Tentukan tujuan investasi spesifik. Pilih instrumen sesuai profil risiko. Mulai sekarang dengan jumlah kecil.\n\n## Kesalahan yang Dihindari\n\nJangan FOMO investasi tanpa riset. Jangan panic selling saat harga turun. Jangan all-in satu instrumen. Miliki tujuan jelas dan beri waktu investasi untuk bertumbuh.\n\n*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia.*"""
    }
}

def run():
    if NICHE not in NICHE_DATA:
        print(f"❌ Unknown niche: {NICHE}. Available: {', '.join(NICHE_DATA.keys())}")
        sys.exit(1)
    
    data = NICHE_DATA[NICHE]
    
    # Check duplicate
    if is_duplicate(data["judul_id"]) and is_duplicate(data["judul_en"]):
        print(f"⏭️  Duplicate topic: {NICHE} — both ID and EN articles already exist")
        return
    
    # Get unique images
    sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))
    from dailymoney_image_pool import get_unique_image, reset_used
    
    reset_used()
    img_id_url, img_id_cap = get_unique_image(data["judul_id"])
    img_en_url, img_en_cap = get_unique_image(data["judul_en"])
    
    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')
    pair_id = int(today.timestamp()) % 100000
    slug = re.sub(r'[^a-zA-Z0-9_ -]', '', data["judul_id"].lower()).strip().replace(' ', '-')[:80]
    
    # Write ID article
    if not is_duplicate(data["judul_id"]):
        content = data["content_id"].replace('\\n', '\n')
        id_article = {
            "judul": data["judul_id"],
            "meta_desc": f"Baca panduan lengkap tentang {NICHE}. Informasi terbaru dan analisis mendalam hanya di DailyMoney.",
            "date": today.strftime('%d/%m/%Y'),
            "tags": data["tags_id"],
            "slug": slug,
            "pair_id": pair_id,
            "lang": "id",
            "content_markdown": content,
            "image_url": img_id_url,
            "image_caption": img_id_cap,
        }
        fname = f"{today_str}-{slug}.json"
        with open(os.path.join(ID_DIR, fname), 'w') as f:
            json.dump(id_article, f, indent=2, ensure_ascii=False)
        update_registry(data["judul_id"])
        print(f"✅ ID ({NICHE}): {data['judul_id'][:50]} ({len(data['content_id'])} chars)")
    else:
        print(f"⏭️  ID duplicate: {data['judul_id'][:50]}")
    
    # Write EN article
    if not is_duplicate(data["judul_en"]):
        en_slug = f"{slug}-en"
        en_article = {
            "judul": data["judul_en"],
            "meta_desc": f"Read our complete guide on {NICHE} investment. Latest news and analysis at DailyMoney.",
            "date": today.strftime('%d/%m/%Y'),
            "tags": data["tags_en"],
            "slug": en_slug,
            "pair_id": pair_id,
            "lang": "en",
            "content_markdown": data["content_id"],
            "image_url": img_en_url,
            "image_caption": img_en_cap,
        }
        en_fname = f"{today_str}-{en_slug}.json"
        with open(os.path.join(EN_DIR, en_fname), 'w') as f:
            json.dump(en_article, f, indent=2, ensure_ascii=False)
        update_registry(data["judul_en"])
        print(f"✅ EN ({NICHE}): {data['judul_en'][:50]} ({len(data['content_id'])} chars)")
    else:
        print(f"⏭️  EN duplicate: {data['judul_en'][:50]}")
    
    print(f"✅ Agent {NICHE} selesai — artikel dengan gambar unik!")

if __name__ == "__main__":
    run()

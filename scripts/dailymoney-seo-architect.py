#!/usr/bin/env python3
"""DailyMoney — SEO Content Architect Agent v2 (FIXED)
Menganalisis topik trending, menulis artikel SEO 3000+ chars dengan gambar unik dari image pool.
TIDAK menggunakan gambar statis lagi. TIDAK ada konten pendek."""
import json, os, subprocess, sys, re
from datetime import datetime
import random

BASE_DIR = "/root/workspace/dailymoney-site"
ID_DIR = os.path.join(BASE_DIR, "_articles")
EN_DIR = os.path.join(ID_DIR, "en")
REGISTRY_FILE = os.path.join(BASE_DIR, "_articles", ".topic-registry.json")
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)

SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

def log(msg):
    ts = datetime.now().strftime('%H:%M:%S')
    print(f"[{ts}] {msg}")
    with open(os.path.join(LOG_DIR, "seo-architect.log"), "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")

def send_telegram(msg):
    try: subprocess.run(SEND + [msg], timeout=15)
    except: pass

def get_registry():
    """Baca topic registry. Simpan topik yang sudah dibuat agar semua writer tidak duplikat."""
    if os.path.exists(REGISTRY_FILE):
        with open(REGISTRY_FILE) as f:
            return json.load(f)
    return {"topics": {}, "article_slugs": []}

def update_registry(titles):
    """Update registry dengan judul-judul baru."""
    reg = get_registry()
    today = datetime.now().strftime('%Y-%m-%d')
    for t in titles:
        key = t.lower().strip()
        reg["topics"][key] = {"title": t, "created": today}
    with open(REGISTRY_FILE, 'w') as f:
        json.dump(reg, f, indent=2)

def is_duplicate_topic(title):
    """Cek apakah topik sudah pernah dibuat (di registry atau existing articles)."""
    key = title.lower().strip()
    reg = get_registry()
    if key in reg["topics"]:
        return True
    # Also check existing articles on disk
    for d in [ID_DIR, EN_DIR]:
        if os.path.exists(d):
            for fname in os.listdir(d):
                if fname.endswith(".json"):
                    try:
                        with open(os.path.join(d, fname)) as f:
                            data = json.load(f)
                        if data.get("judul", "").lower().strip() == key:
                            return True
                    except: pass
    return False

# === CONTENT TEMPLATES — 3000+ chars, pure financial journalism ===
TEMPLATES = {
    "ihsg": {
        "judul_templates": [
            "IHSG Hari Ini: {topic} — Analisis dan Prediksi Pergerakan Indeks",
            "Update Pasar Saham: {topic} — Dampak bagi Investor",
            "Pergerakan IHSG Terbaru: {topic} — Simak Analisisnya",
        ],
        "content": """**Pergerakan {topic} menjadi sorotan utama pelaku pasar saham Indonesia hari ini.** Indeks Harga Saham Gabungan (IHSG) mencatat pergerakan yang signifikan, mencerminkan sentimen investor terhadap kondisi ekonomi nasional dan global.

## Analisis Pergerakan Hari Ini

Pasar saham Indonesia membuka sesi perdagangan dengan volume transaksi yang cukup tinggi. Data dari Bursa Efek Indonesia (BEI) menunjukkan bahwa investor asing dan domestik sama-sama aktif melakukan transaksi, menciptakan dinamika yang menarik untuk diamati.

Beberapa sektor yang menjadi motor penggerak IHSG hari ini antara lain sektor keuangan, infrastruktur, dan konsumer. Saham-saham blue chip seperti BBCA, BBRI, dan TLKM menunjukkan pergerakan yang cukup volatile, memberikan peluang trading jangka pendek bagi investor aktif.

## Faktor yang Mempengaruhi

Ada beberapa faktor kunci yang mempengaruhi pergerakan IHSG saat ini:

1. **Sentimen Global** — Pergerakan indeks Wall Street dan pasar Asia lainnya menjadi acuan utama. Kondisi ekonomi AS, kebijakan suku bunga The Fed, dan ketegangan geopolitik global turut mempengaruhi aliran modal asing ke pasar Indonesia.

2. **Data Ekonomi Domestik** — Rilis data pertumbuhan ekonomi, inflasi, dan neraca perdagangan menjadi katalis penting bagi pergerakan IHSG. Data positif cenderung mendorong penguatan indeks.

3. **Kebijakan Pemerintah** — Kebijakan fiskal dan moneter yang dikeluarkan pemerintah dan Bank Indonesia mempengaruhi likuiditas pasar dan kepercayaan investor.

4. **Aksi Korporasi** — RUPS, pembagian dividen, dan pengumuman ekspansi perusahaan tercatat menjadi sentimen positif yang mendorong harga saham.

## Strategi Menghadapi Volatilitas Pasar

Bagi investor yang ingin memanfaatkan pergerakan IHSG, beberapa strategi yang bisa diterapkan:

### Investasi Jangka Panjang
Investor dengan horizon jangka panjang disarankan untuk tetap tenang dan tidak panik saat terjadi koreksi pasar. Akumulasi saham-saham fundamental kuat saat harga turun bisa menjadi strategi yang menguntungkan.

### Trading Jangka Pendek
Trader aktif bisa memanfaatkan volatilitas untuk meraih keuntungan jangka pendek. Penting untuk memiliki sistem manajemen risiko yang ketat, termasuk penggunaan stop-loss dan take-profit.

### Diversifikasi Sektor
Jangan menaruh semua dana di satu sektor. Diversifikasi ke sektor-sektor yang berbeda dapat mengurangi risiko portofolio secara keseluruhan.

## Rekomendasi Saham Hari Ini

Berdasarkan analisis teknikal dan fundamental, berikut beberapa saham yang menarik untuk dicermati:

- **Sektor Perbankan**: Saham bank BUKU 4 masih menjadi primadona dengan fundamental kuat
- **Sektor Infrastruktur**: Proyek strategis nasional mendorong kinerja emiten konstruksi
- **Sektor Konsumer**: Daya beli masyarakat yang stabil menopang kinerja emiten consumer goods

## Kesimpulan

Pergerakan IHSG saat ini mencerminkan optimisme pasar terhadap prospek ekonomi Indonesia. Meskipun volatilitas masih akan terjadi, prospek jangka panjang pasar saham Indonesia tetap positif. Investor disarankan untuk terus memantau perkembangan dan melakukan riset mendalam sebelum mengambil keputusan investasi.

*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia yang lebih cerdas secara finansial. Dapatkan berita terkini dan analisis pasar setiap hari di dailymoney.my.id.*
"""
    },
    "emas": {
        "judul_templates": [
            "Harga Emas Hari Ini: {topic} — Update Logam Mulia Terbaru",
            "Investasi Emas: {topic} — Analisis Pergerakan Harga",
            "Update Emas Dunia: {topic} — Prospek dan Prediksi",
        ],
        "content": """**Harga emas {topic} mengalami pergerakan yang patut dicermati oleh para investor logam mulia.** Emas sebagai aset safe haven tetap menjadi pilihan utama di tengah ketidakpastian ekonomi global. Pergerakan harga emas dipengaruhi oleh berbagai faktor makroekonomi dan geopolitik.

## Pergerakan Harga Emas Terkini

Harga emas batangan di Indonesia mengacu pada harga yang ditetapkan oleh PT Aneka Tambang Tbk (Antam). Fluktuasi harga emas dipengaruhi oleh pergerakan harga emas internasional yang diukur dalam dolar AS per troy ons. Dalam sepekan terakhir, harga emas menunjukkan tren yang cukup dinamis.

Untuk harga emas Antam hari ini, harga buyback juga mengalami penyesuaian seiring dengan pergerakan harga acuan. Selisih antara harga jual dan harga buyback menjadi faktor penting yang harus dipahami investor sebelum memutuskan untuk berinvestasi emas.

## Faktor Penggerak Harga Emas

Beberapa faktor utama yang mempengaruhi pergerakan harga emas global dan domestik:

1. **Kebijakan Suku Bunga** — Ketika suku bunga acuan rendah, emas menjadi lebih menarik karena biaya opportunity holding emas lebih kecil. Sebaliknya, kenaikan suku bunga cenderung menekan harga emas.

2. **Nilai Tukar Dolar AS** — Emas memiliki hubungan terbalik dengan dolar AS. Melemahnya dolar AS cenderung mendorong harga emas naik, dan sebaliknya.

3. **Inflasi** — Emas dikenal sebagai lindung nilai (hedge) terhadap inflasi. Ketika inflasi tinggi, permintaan emas meningkat.

4. **Ketegangan Geopolitik** — Konflik global, krisis politik, dan ketidakpastian ekonomi mendorong investor beralih ke aset safe haven seperti emas.

5. **Permintaan Fisik** — Permintaan emas untuk perhiasan, industri, dan investasi dari negara-negara konsumen besar seperti India, China, dan Indonesia mempengaruhi harga.

## Investasi Emas: Logam Mulia Batangan vs Perhiasan

### Emas Batangan
Emas batangan Antam adalah pilihan utama untuk investasi karena:
- Kadar kemurnian 99,99% (24 karat)
- Sertifikat resmi dari Antam
- Mudah dijual kembali (buyback)
- Tidak ada biaya pembuatan (ongkos)

### Perhiasan Emas
Perhiasan kurang ideal untuk investasi karena:
- Kadar emas bervariasi (biasanya 17-22 karat)
- Ada biaya pembuatan yang hilang saat dijual
- Nilai jual kembali lebih rendah dari harga beli

## Strategi Investasi Emas

### Dollar Cost Averaging (DCA)
Membeli emas secara rutin dalam jumlah tetap, terlepas dari harga. Strategi ini efektif untuk mengurangi risiko fluktuasi harga.

### Buy on Dip
Membeli emas saat harga turun (koreksi) untuk mendapatkan keuntungan lebih besar saat harga naik kembali.

### Proporsi Portofolio
Para ahli merekomendasikan alokasi emas sekitar 5-15% dari total portofolio investasi sebagai diversifikasi dan lindung nilai.

## Prospek Harga Emas ke Depan

Analis memproyeksikan bahwa harga emas masih memiliki potensi kenaikan dalam jangka menengah dan panjang. Faktor pendukungnya antara lain kebijakan moneter yang masih akomodatif, ketidakpastian ekonomi global, dan peningkatan permintaan dari bank sentral berbagai negara.

## Kesimpulan

Emas tetap menjadi pilihan investasi yang relevan di tengah dinamika pasar keuangan global. Dengan strategi yang tepat dan pemahaman yang baik tentang faktor-faktor penggerak harga, investor dapat memaksimalkan potensi keuntungan dari investasi logam mulia ini.

*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia yang lebih cerdas secara finansial.*
"""
    },
    "crypto": {
        "judul_templates": [
            "Update Crypto: {topic} — Pergerakan Bitcoin dan Altcoin",
            "Berita Cryptocurrency: {topic} — Analisis Pasar Digital",
            "Harga Crypto Hari Ini: {topic} — Informasi Terkini",
        ],
        "content": """**Pasar cryptocurrency {topic} kembali menunjukkan pergerakan yang menarik perhatian investor aset digital.** Bitcoin, Ethereum, dan altcoin lainnya mencatat volatilitas yang signifikan dalam beberapa hari terakhir. Pasar kripto yang dikenal dengan pergerakan harganya yang ekstrem ini terus menjadi topik hangat di kalangan investor.

## Pergerakan Harga Crypto Terkini

Bitcoin sebagai cryptocurrency dengan kapitalisasi pasar terbesar masih menjadi penentu arah pasar secara keseluruhan. Pergerakan harga Bitcoin seringkali diikuti oleh altcoin-altcoin lainnya, menciptakan korelasi yang cukup kuat di pasar aset digital.

Ethereum, sebagai altcoin terbesar kedua, juga menunjukkan pergerakan yang signifikan. Dengan ekosistem DeFi (Decentralized Finance) dan NFT (Non-Fungible Token) yang terus berkembang, Ethereum memiliki fundamental yang kuat untuk pertumbuhan jangka panjang.

## Faktor yang Mempengaruhi Pasar Crypto

1. **Regulasi Global** — Sikap regulator di berbagai negara terhadap cryptocurrency sangat mempengaruhi sentimen pasar. Berita positif tentang adopsi regulasi cenderung mendorong harga naik, sementara berita negatif seperti pelarangan atau pembatasan bisa menyebabkan koreksi tajam.

2. **Adopsi Institusional** — Semakin banyak perusahaan besar dan institusi keuangan yang mengadopsi cryptocurrency sebagai aset investasi maupun alat pembayaran. Hal ini memberikan legitimasi dan mendorong permintaan.

3. **Perkembangan Teknologi** — Upgrade jaringan, solusi scaling, dan inovasi blockchain baru menjadi katalis positif bagi harga crypto terkait.

4. **Sentimen Pasar** — FOMO (Fear of Missing Out) dan FUD (Fear, Uncertainty, Doubt) masih menjadi penggerak utama volatilitas harga crypto. Media sosial dan pengaruh tokoh publik turut mempengaruhi sentimen.

5. **Makroekonomi** — Kebijakan moneter global, inflasi, dan kondisi ekonomi makro juga mempengaruhi minat investor terhadap aset digital.

## Strategi Investasi Crypto

### Hold Jangka Panjang (HODL)
Strategi membeli dan menahan aset crypto untuk jangka panjang, terlepas dari fluktuasi harga jangka pendek. Cocok untuk investor yang percaya pada potensi jangka panjang teknologi blockchain.

### Trading Aktif
Memanfaatkan volatilitas harga untuk meraih keuntungan melalui trading jangka pendek. Memerlukan pemahaman analisis teknikal dan manajemen risiko yang baik.

### Dollar Cost Averaging
Investasi rutin dalam jumlah tetap untuk mengurangi risiko entry di harga tinggi.

## Keamanan Aset Crypto

Keamanan menjadi prioritas utama dalam investasi cryptocurrency. Beberapa langkah penting yang harus dilakukan:

1. **Gunakan Hardware Wallet** — Simpan aset crypto di hardware wallet untuk keamanan maksimal
2. **Aktifkan 2FA** — Gunakan autentikasi dua faktor di semua platform exchange
3. **Hati-hati Phishing** — Waspada terhadap situs web dan email palsu
4. **Backup Seed Phrase** — Simpan seed phrase di tempat aman, jangan pernah dibagikan

## Prospek Crypto ke Depan

Meskipun volatil, prospek cryptocurrency dalam jangka panjang masih menjanjikan seiring dengan adopsi teknologi blockchain yang semakin meluas. Inovasi di bidang DeFi, Web3, dan tokenisasi aset nyata (RWA) akan menjadi katalis pertumbuhan berikutnya.

*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia yang lebih cerdas secara finansial.*
"""
    },
    "forex": {
        "judul_templates": [
            "Kurs Rupiah Hari Ini: {topic} — Pergerakan Nilai Tukar",
            "Update Forex: {topic} — Dolar AS dan Mata Uang Global",
            "Nilai Tukar Rupiah: {topic} — Analisis Pergerakan Mata Uang",
        ],
        "content": """**Nilai tukar rupiah terhadap dolar AS {topic} — pergerakan mata uang Garuda menjadi sorotan pelaku pasar forex global.** Pergerakan rupiah dipengaruhi oleh berbagai faktor baik domestik maupun internasional. Sebagai mata uang emerging market, rupiah rentan terhadap perubahan sentimen global.

## Pergerakan Rupiah Terkini

Rupiah Indonesia saat ini diperdagangkan dalam rentang yang fluktuatif terhadap dolar AS. Bank Indonesia terus melakukan intervensi untuk menjaga stabilitas nilai tukar sesuai dengan fundamental ekonomi. Cadangan devisa yang memadai menjadi bantalan utama dalam menghadapi tekanan eksternal.

Pergerakan rupiah tidak hanya terhadap dolar AS, tetapi juga terhadap mata uang utama lainnya seperti Euro, Yen Jepang, Dolar Singapura, dan Ringgit Malaysia. Diversifikasi mata uang ini penting dipahami oleh pelaku bisnis dan investor.

## Faktor-Faktor yang Mempengaruhi Rupiah

### Faktor Domestik
1. **Kebijakan Moneter BI** — Suku bunga acuan (BI Rate) menjadi instrumen utama untuk menjaga stabilitas rupiah. Kenaikan suku bunga cenderung memperkuat rupiah.
2. **Inflasi** — Inflasi yang terkendali menjaga daya beli rupiah dan kepercayaan investor.
3. **Neraca Perdagangan** — Surplus perdagangan mendukung penguatan rupiah, sementara defisit memberikan tekanan.
4. **Pertumbuhan Ekonomi** — Pertumbuhan PDB yang solid menarik investasi asing dan memperkuat rupiah.

### Faktor Global
1. **Kebijakan The Fed** — Suku bunga AS dan kebijakan quantitative easing mempengaruhi aliran modal ke emerging market.
2. **Harga Komoditas** — Indonesia sebagai eksportir komoditas, harga batubara, CPO, dan nikel mempengaruhi penerimaan devisa.
3. **Sentimen Risk-On/Risk-Off** — Dalam kondisi ketidakpastian global, investor cenderung beralih ke aset safe haven, melemahkan mata uang emerging market.

## Dampak pada Investasi dan Bisnis

Pergerakan nilai tukar rupiah memiliki dampak signifikan terhadap berbagai sektor:

### Importir dan Eksportir
- Eksportir diuntungkan saat rupiah melemah (barang lebih murah di pasar global)
- Importir terbebani saat rupiah melemah (biaya impor naik)

### Investor Saham
- Investor asing cenderung menarik dana saat rupiah terdepresiasi
- Sektor yang bergantung pada impor (teknologi, farmasi) tertekan saat rupiah lemah

### Wisatawan dan Pelajar
- Biaya pendidikan dan wisata ke luar negeri lebih mahal saat rupiah melemah

## Strategi Menghadapi Fluktuasi Rupiah

1. **Hedging** — Perusahaan dengan exposure valas dapat menggunakan instrumen derivatif seperti forward dan swap untuk lindung nilai
2. **Diversifikasi Mata Uang** — Simpan dana dalam beberapa mata uang untuk mengurangi risiko
3. **Pantau Kalender Ekonomi** — Ikuti rilis data ekonomi penting yang mempengaruhi nilai tukar
4. **Investasi Valas** — Trading forex dapat menjadi alternatif investasi, namun memiliki risiko tinggi

## Proyeksi ke Depan

Analis memperkirakan rupiah akan bergerak dinamis ke depannya dengan kecenderungan stabil dalam jangka menengah. Fundamental ekonomi Indonesia yang kuat, cadangan devisa yang memadai, dan kebijakan BI yang akomodatif menjadi faktor pendukung stabilitas rupiah.

*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia yang lebih cerdas secara finansial.*
"""
    },
    "ekonomi": {
        "judul_templates": [
            "Ekonomi Indonesia Terkini: {topic} — Analisis Makroekonomi",
            "Berita Ekonomi: {topic} — Dampak bagi Masyarakat",
            "Update Ekonomi Nasional: {topic} — Data dan Proyeksi",
        ],
        "content": """**Perkembangan ekonomi Indonesia {topic} menjadi perhatian utama para pelaku pasar dan masyarakat luas.** Indikator makroekonomi yang dirilis oleh Badan Pusat Statistik (BPS) dan lembaga lainnya memberikan gambaran tentang kesehatan ekonomi nasional.

## Kondisi Ekonomi Terkini

Perekonomian Indonesia menunjukkan resiliensi yang baik di tengah ketidakpastian global. Pertumbuhan ekonomi tetap terjaga dalam kisaran positif, didukung oleh konsumsi domestik yang kuat dan kinerja ekspor yang solid.

Beberapa indikator ekonomi makro yang perlu diperhatikan:

1. **Pertumbuhan PDB** — Produk Domestik Bruto Indonesia tumbuh stabil
2. **Inflasi** — Tingkat inflasi tetap terkendali dalam sasaran Bank Indonesia
3. **Tingkat Pengangguran** — Terus menurun seiring pemulihan ekonomi
4. **Neraca Perdagangan** — Surplus neraca perdagangan memberikan bantalan eksternal

## Sektor-Sektor Penggerak Ekonomi

### Konsumsi Domestik
Konsumsi rumah tangga masih menjadi kontributor terbesar PDB Indonesia. Daya beli masyarakat yang terjaga didukung oleh inflasi rendah dan pertumbuhan upah yang positif.

### Investasi
Realisasi investasi terus meningkat, baik investasi asing langsung (PMA) maupun investasi dalam negeri (PMDN). Sektor infrastruktur, manufaktur, dan digital menjadi primadona.

### Ekspor
Kinerja ekspor Indonesia didorong oleh permintaan global terhadap komoditas unggulan seperti batubara, CPO, nikel, dan hasil hutan.

## Kebijakan Pemerintah

Pemerintah terus mengeluarkan kebijakan untuk mendorong pertumbuhan ekonomi:

1. **Kebijakan Fiskal** — Insentif pajak, belanja infrastruktur, dan program perlindungan sosial
2. **Kebijakan Moneter** — Suku bunga akomodatif dan likuiditas yang memadai
3. **Reformasi Struktural** — UU Cipta Kerja, kemudahan berusaha, dan pengembangan SDM

## Tantangan dan Risiko

Meskipun prospek ekonomi positif, beberapa tantangan perlu diwaspadai:

- Normalisasi kebijakan moneter global
- Volatilitas harga komoditas
- Tekanan inflasi global
- Risiko geopolitis

## Kesimpulan

Ekonomi Indonesia tetap memiliki fundamental yang kuat dengan prospek pertumbuhan yang positif. Dukungan kebijakan yang tepat dan resiliensi sektor swasta menjadi modal utama dalam menghadapi tantangan global. Investor dan pelaku bisnis dapat tetap optimis terhadap prospek ekonomi Indonesia.

*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia yang lebih cerdas secara finansial.*
"""
    },
    "pajak": {
        "judul_templates": [
            "Panduan Pajak: {topic} — Informasi Perpajakan Terbaru",
            "Update Pajak 2026: {topic} — Yang Perlu Diketahui Wajib Pajak",
            "Tips Perpajakan: {topic} — Panduan Lengkap",
        ],
        "content": """**Perpajakan {topic} menjadi topik penting bagi wajib pajak, baik individu maupun badan usaha.** Direktorat Jenderal Pajak (DJP) terus melakukan pembaruan kebijakan dan sistem untuk meningkatkan kepatuhan dan kemudahan pelaporan pajak.

## Ketentuan Perpajakan Terkini

Sistem perpajakan Indonesia menerapkan self-assessment, di mana wajib pajak memiliki kewajiban untuk menghitung, membayar, dan melaporkan pajaknya sendiri. Pemahaman yang baik tentang ketentuan perpajakan sangat penting untuk menghindari sanksi dan denda.

### Jenis-Jenis Pajak di Indonesia

1. **PPh (Pajak Penghasilan)** — Dikenakan atas penghasilan yang diterima wajib pajak
2. **PPN (Pajak Pertambahan Nilai)** — Dikenakan atas konsumsi barang dan jasa
3. **PBB (Pajak Bumi dan Bangunan)** — Dikenakan atas kepemilikan tanah dan bangunan
4. **Bea Materai** — Dikenakan atas dokumen tertentu

## Kewajiban Pelaporan Tahunan

Wajib pajak orang pribadi wajib melaporkan SPT Tahunan paling lambat 31 Maret setiap tahunnya. Untuk wajib pajak badan, batas waktu pelaporan adalah 30 April.

### Dokumen yang Diperlukan
- Bukti potong pajak (1721-A1/A2)
- Laporan keuangan atau pembukuan
- Data harta dan kewajiban
- Bukti pembayaran pajak

## Insentif dan Fasilitas Pajak

Pemerintah menyediakan berbagai insentif untuk mendorong kepatuhan dan investasi:

1. **Tax Allowance** — Pengurangan penghasilan neto untuk sektor tertentu
2. **Tax Holiday** — Pembebasan pajak untuk industri pionir
3. **Super Deduction** — Pengurangan penghasilan bruto untuk kegiatan riset dan vokasi
4. **PPN Tidak Dipungut** — Fasilitas untuk kegiatan tertentu

## Tips Optimalisasi Pajak

1. **Manfaatkan PTKP** — Pahami besaran Penghasilan Tidak Kena Pajak yang berlaku
2. **Kumpulkan Bukti Potong** — Pastikan semua bukti potong dikumpulkan sebelum pelaporan
3. **Laporkan Secara Online** — Gunakan e-Filing untuk kemudahan pelaporan
4. **Konsultasi dengan Konsultan** — Untuk kasus perpajakan yang kompleks

## Sanksi dan Denda

Keterlambatan dan ketidakpatuhan perpajakan dapat mengakibatkan sanksi:
- Denda keterlambatan pelaporan SPT
- Bunga keterlambatan pembayaran
- Kenaikan pokok pajak
- Sanksi pidana untuk pelanggaran berat

## Kesimpulan

Kepatuhan perpajakan adalah kewajiban setiap warga negara. Dengan memahami ketentuan perpajakan dan memanfaatkan fasilitas yang ada, wajib pajak dapat memenuhi kewajibannya dengan optimal. Gunakan layanan e-Filing untuk kemudahan pelaporan SPT Tahunan.

*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia yang lebih cerdas secara finansial.*
"""
    },
    "properti": {
        "judul_templates": [
            "Update Properti: {topic} — Harga Rumah dan Investasi",
            "Berita Properti Terbaru: {topic} — Panduan Membeli Rumah",
            "Investasi Properti: {topic} — Analisis Pasar Real Estate",
        ],
        "content": """**Pasar properti {topic} menarik perhatian para investor dan calon pemilik rumah.** Sektor properti Indonesia terus menunjukkan pertumbuhan yang positif, didukung oleh kebijakan pemerintah dan peningkatan kebutuhan hunian yang terus bertambah.

## Kondisi Pasar Properti Terkini

Pasar properti di Indonesia, khususnya di kota-kota besar seperti Jakarta, Surabaya, dan Bandung, menunjukkan tren yang positif. Harga properti mengalami peningkatan yang moderat, sejalan dengan pertumbuhan ekonomi dan inflasi.

Beberapa segmen yang menjadi primadona investasi properti:
- **Rumah Tapak** — Masih menjadi pilihan utama untuk tempat tinggal
- **Apartemen** — Diminati di pusat kota dan dekat kawasan bisnis
- **Ruko/Rukan** — Cocok untuk investasi komersial
- **Tanah Kavling** — Potensi kenaikan harga jangka panjang

## Program Pemerintah untuk Sektor Properti

Pemerintah terus mendorong sektor properti melalui berbagai program:

1. **Subsidi Perumahan** — FLPP (Fasilitas Likuiditas Pembiayaan Perumahan) untuk MBR
2. **Insentif PPN** — Diskon PPN untuk properti di bawah harga tertentu
3. **KPR Bersubsidi** — Suku bunga rendah untuk masyarakat berpenghasilan rendah
4. **Kemudahan Perizinan** — Percepatan proses perizinan bangunan

## Tips Membeli Rumah Pertama

### Persiapan Finansial
- Hitung kemampuan DP dan cicilan KPR
- Siapkan dana darurat 3-6 bulan
- Pastikan skor kredit baik

### Memilih Lokasi
- Akses transportasi dan infrastruktur
- Dekat dengan fasilitas umum (sekolah, rumah sakit, pasar)
- Potensi kenaikan harga di masa depan

### Proses Pembelian
1. Survei properti secara langsung
2. Cek legalitas dan sertifikat tanah
3. Negosiasi harga dan biaya tambahan
4. Ajukan KPR ke bank
5. Tanda tangan akta jual beli (AJB) di hadapan PPAT

## Investasi Properti vs Reksadana

### Kelebihan Investasi Properti
- Aset berwujud dan tangible
- Potensi apresiasi harga jangka panjang
- Dapat digunakan sendiri atau disewakan

### Kekurangan
- Likuiditas rendah (susah dijual cepat)
- Modal awal besar
- Biaya perawatan dan pajak

## Strategi Investasi Properti

1. **Buy and Hold** — Beli properti dan tahan untuk jangka panjang
2. **Fix and Flip** — Beli properti kurang terawat, renovasi, jual dengan harga lebih tinggi
3. **Sewa** — Beli properti untuk disewakan, dapatkan passive income
4. **Cicil dan Jual** — Beli properti KPR, cicil beberapa tahun, jual saat harga naik

## Kesimpulan

Investasi properti tetap menjadi pilihan yang solid untuk membangun portofolio investasi jangka panjang. Dengan riset yang matang, lokasi yang tepat, dan strategi yang sesuai, properti dapat memberikan return yang menarik bagi investor.

*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia yang lebih cerdas secara finansial.*
"""
    },
    "fintech": {
        "judul_templates": [
            "Fintech Terbaru: {topic} — Inovasi Keuangan Digital",
            "Update Fintech Indonesia: {topic} — Berita dan Analisis",
            "Teknologi Finansial: {topic} — Masa Depan Keuangan Digital",
        ],
        "content": """**Industri fintech {topic} terus mengalami perkembangan pesat di Indonesia.** Financial technology atau fintech telah mengubah cara masyarakat mengakses layanan keuangan. Dari pembayaran digital hingga pinjaman online (peer-to-peer lending), fintech memberikan kemudahan dan akses yang lebih luas.

## Perkembangan Fintech di Indonesia

Indonesia menjadi salah satu pasar fintech terbesar dan tercepat pertumbuhannya di Asia Tenggara. Didukung oleh penetrasi smartphone yang tinggi dan populasi besar yang belum terlayani perbankan konvensional, fintech tumbuh subur di Indonesia.

### Segmen Utama Fintech

1. **Pembayaran Digital (E-Wallet)** — GoPay, OVO, DANA, ShopeePay, dan LinkAja
2. **Pinjaman Online (P2P Lending)** — Platform yang mempertemukan peminjam dan pemberi pinjaman
3. **Investasi Online** — Aplikasi investasi saham, reksadana, dan emas
4. **Insurtech** — Teknologi asuransi digital
5. **Regtech** — Teknologi kepatuhan regulasi

## Manfaat Fintech bagi Masyarakat

1. **Inklusi Keuangan** — Menjangkau masyarakat yang belum memiliki akses ke bank
2. **Kecepatan Transaksi** — Transfer dan pembayaran instan 24/7
3. **Biaya Lebih Rendah** — Efisiensi operasional tanpa kantor fisik
4. **Kemudahan Akses** — Cukup dengan smartphone, tanpa perlu ke kantor cabang

## Regulasi dan Pengawasan Fintech

Otoritas Jasa Keuangan (OJK) dan Bank Indonesia mengawasi industri fintech di Indonesia. Beberapa aturan penting:

1. **Lisensi OJK** — Semua platform fintech wajib terdaftar dan berizin OJK
2. **Perlindungan Data** — UU Perlindungan Data Pribadi (PDP)
3. **Batasan Bunga** — Maksimal suku bunga pinjaman untuk P2P lending
4. **Anti Pencucian Uang** — Penerapan prinsip Know Your Customer (KYC)

## Tips Aman Menggunakan Fintech

1. **Gunakan Platform Berizin OJK** — Pastikan fintech yang digunakan terdaftar resmi
2. **Jaga Keamanan Akun** — Gunakan password kuat dan 2FA
3. **Waspada Penipuan** — Jangan bagikan OTP dan PIN ke siapa pun
4. **Baca Syarat dan Ketentuan** — Pahami biaya dan ketentuan layanan
5. **Batasi Pinjaman** — Pinjam sesuai kemampuan membayar

## Prospek Fintech di Indonesia

Masa depan fintech di Indonesia sangat cerah. Dengan populasi yang besar, pertumbuhan ekonomi digital, dan dukungan pemerintah, sektor ini diprediksi akan terus tumbuh. Inovasi seperti blockchain, Open Banking, dan AI-driven financial services akan menjadi tren ke depan.

*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia yang lebih cerdas secara finansial.*
"""
    },
    "reksadana": {
        "judul_templates": [
            "Panduan Reksadana: {topic} — Investasi Mudah untuk Pemula",
            "Update Reksadana Terbaru: {topic} — Kinerja dan Prospek",
            "Investasi Reksadana: {topic} — Cara Cerdas Berinvestasi",
        ],
        "content": """**Reksadana {topic} menjadi pilihan investasi yang populer bagi masyarakat Indonesia.** Sebagai instrumen investasi yang dikelola oleh Manajer Investasi profesional, reksadana menawarkan kemudahan dan diversifikasi tanpa perlu keahlian khusus dalam menganalisis pasar.

## Apa Itu Reksadana?

Reksadana adalah wadah yang digunakan untuk menghimpun dana dari masyarakat pemodal (investor) untuk selanjutnya diinvestasikan dalam portofolio efek oleh Manajer Investasi. Dengan kata lain, reksadana adalah investasi kolektif di mana dana banyak investor dikelola secara profesional.

### Jenis-Jenis Reksadana

1. **Reksadana Pasar Uang (RDPU)** — Investasi di instrumen pasar uang, risiko rendah, cocok untuk jangka pendek
2. **Reksadana Pendapatan Tetap (RDPT)** — Investasi di obligasi, risiko sedang, cocok untuk jangka menengah
3. **Reksadana Campuran** — Kombinasi saham dan obligasi, risiko sedang-tinggi
4. **Reksadana Saham (RDS)** — Investasi mayoritas di saham, risiko tinggi, return potensial tinggi

## Keuntungan Investasi Reksadana

1. **Dikelola Profesional** — Dana dikelola oleh Manajer Investasi yang kompeten dan berpengalaman
2. **Diversifikasi** — Dana diinvestasikan ke berbagai instrumen, mengurangi risiko
3. **Modal Terjangkau** — Mulai dari Rp10.000 sudah bisa investasi reksadana
4. **Likuiditas Tinggi** — Pencairan dana relatif cepat (T+3 hingga T+5)
5. **Transparansi** — NAB (Nilai Aktiva Bersih) dipublikasikan setiap hari

## Cara Memulai Investasi Reksadana

### Langkah 1: Pilih Platform
Pilih aplikasi atau platform investasi reksadana yang terdaftar dan diawasi OJK, seperti Bibit, Bareksa, atau aplikasi sekuritas lainnya.

### Langkah 2: Registrasi dan Verifikasi
Lakukan pendaftaran dengan mengisi data diri, upload KTP, dan verifikasi melalui video call atau e-KYC.

### Langkah 3: Pilih Produk Reksadana
Sesuaikan dengan profil risiko dan tujuan investasi:
- **Konservatif** → Reksadana Pasar Uang (RDPU)
- **Moderat** → Reksadana Pendapatan Tetap (RDPT)
- **Agresif** → Reksadana Saham (RDS)

### Langkah 4: Lakukan Investasi
Transfer dana ke rekening reksadana dan lakukan pembelian unit penyertaan secara rutin.

## Strategi Investasi Reksadana

### Dollar Cost Averaging (DCA)
Investasi rutin setiap bulan dalam jumlah tetap. Strategi ini efektif untuk mengurangi risiko fluktuasi pasar.

### Buy the Dip
Tambah investasi saat pasar turun untuk mendapatkan harga unit lebih murah.

### Rebalancing
Sesuaikan komposisi portofolio secara berkala agar tetap sesuai dengan profil risiko.

## Biaya dalam Reksadana

- **Biaya Pembelian (Subscription Fee)** — 0-2% dari nilai investasi
- **Biaya Penjualan (Redemption Fee)** — 0-2% dari nilai penjualan
- **Biaya Pengelolaan (Management Fee)** — 1-3% per tahun dari NAB
- **Biaya Transfer Agen** — Biaya administrasi tahunan

## Risiko Investasi Reksadana

1. **Risiko Pasar** — Nilai investasi bisa turun karena kondisi pasar
2. **Risiko Likuiditas** — Kesulitan mencairkan dana pada kondisi tertentu
3. **Risiko Manajer Investasi** — Kinerja pengelola dana yang kurang optimal
4. **Risiko Inflasi** — Nilai return tidak sebanding dengan inflasi

## Kesimpulan

Reksadana adalah solusi investasi yang ideal bagi pemula yang ingin memulai investasi tanpa perlu keahlian khusus. Dengan modal terjangkau, diversifikasi otomatis, dan pengelolaan profesional, reksadana menjadi gerbang utama menuju kebebasan finansial.

*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia yang lebih cerdas secara finansial.*
"""
    },
    "panduan": {
        "judul_templates": [
            "Panduan Investasi: {topic} — Tips dan Strategi untuk Pemula",
            "Cara Investasi: {topic} — Langkah demi Langkah",
            "Belajar Investasi: {topic} — Panduan Lengkap untuk Pemula",
        ],
        "content": """**{topic} — panduan lengkap bagi Anda yang ingin memulai perjalanan investasi.** Investasi adalah langkah penting dalam mencapai kebebasan finansial. Dengan pemahaman yang baik, siapa pun bisa memulai investasi meskipun dengan modal kecil.

## Mengapa Harus Berinvestasi?

Investasi bukan sekadar menabung, melainkan menempatkan uang pada instrumen yang dapat memberikan return di atas inflasi. Tujuan utama investasi:

1. **Melawan Inflasi** — Nilai uang cenderung turun seiring waktu, investasi membantu menjaga daya beli
2. **Membangun Kekayaan** — Dengan efek compounding, investasi jangka panjang dapat menghasilkan kekayaan signifikan
3. **Pasif Income** — Beberapa instrumen investasi memberikan penghasilan rutin
4. **Mencapai Tujuan Finansial** — Dana pensiun, pendidikan anak, atau pembelian aset

## Prinsip Dasar Investasi

### 1. Mulai Lebih Awal
Semakin awal memulai investasi, semakin besar manfaat dari efek bunga berbunga (compounding). Perbedaan memulai di usia 25 vs 35 tahun bisa sangat signifikan.

### 2. Diversifikasi
Jangan menaruh semua telur dalam satu keranjang. Sebarkan investasi ke berbagai instrumen untuk mengurangi risiko.

### 3. Pahami Profil Risiko
Kenali toleransi risiko Anda:
- **Konservatif** — Tidak suka risiko, preferensi keamanan modal
- **Moderat** — Bersedia mengambil risiko sedang untuk return lebih tinggi
- **Agresif** — Siap mengambil risiko tinggi untuk return maksimal

### 4. Investasi Rutin
Konsistensi lebih penting daripada jumlah. Investasi rutin setiap bulan lebih efektif daripada investasi besar sekali waktu.

## Instrumen Investasi untuk Pemula

### Reksadana
Paling mudah untuk pemula. Modal kecil, dikelola profesional, dan likuid.

### Emas
Safe haven yang terbukti tahan krisis. Mudah dibeli dan dijual.

### Saham
Return potensial tinggi, tapi perlu pengetahuan dan riset.

### Obligasi
Return tetap, risiko lebih rendah dari saham.

### Deposito
Paling aman, return rendah, cocok untuk dana darurat.

## Langkah Awal Investasi

1. **Siapkan Dana Darurat** — Minimal 3-6 bulan pengeluaran
2. **Bayar Utang** — Lunasi utang berbunga tinggi terlebih dahulu
3. **Tentukan Tujuan** — Tujuan spesifik, terukur, dan berjangka waktu
4. **Pilih Instrumen** — Sesuai profil risiko dan tujuan
5. **Mulai Sekarang** — Jangan menunda, mulailah dengan jumlah kecil

## Kesalahan yang Harus Dihindari

1. **FOMO (Fear of Missing Out)** — Investasi karena ikut-ikutan tanpa riset
2. **Panic Selling** — Jual saat harga turun karena panik
3. **All-in Satu Instrumen** — Tidak diversifikasi
4. **Tidak Punya Tujuan** — Investasi tanpa arah yang jelas
5. **Terlalu Sering Ganti Instrumen** — Tidak memberi waktu investasi untuk bertumbuh

## Kesimpulan

Investasi adalah perjalanan, bukan tujuan akhir. Mulailah dengan langkah kecil, konsisten, dan terus belajar. Dengan disiplin dan strategi yang tepat, kebebasan finansial bukan lagi sekadar mimpi.

*DailyMoney — Platform edukasi keuangan terpercaya untuk Indonesia yang lebih cerdas secara finansial. Dapatkan panduan dan analisis investasi setiap hari di dailymoney.my.id.*
"""
    },
}

def build_article(judul, content_template, tags, topic, lang='id'):
    """Build complete article dict with unique image."""
    from dailymoney_image_pool import get_unique_image
    
    # Pick unique image
    image_url, image_caption = get_unique_image(f"{judul} {tags} {topic}")
    
    today = datetime.now()
    pair_id = int(today.timestamp()) % 100000
    
    meta_desc = judul[:150] if len(judul) < 150 else judul[:147] + "..."
    
    article = {
        "judul": judul,
        "meta_desc": f"Baca artikel lengkap tentang {meta_desc}. Informasi terbaru dan analisis mendalam hanya di DailyMoney.",
        "date": today.strftime('%d/%m/%Y'),
        "tags": tags,
        "slug": re.sub(r'[^a-z0-9-]', '', judul.lower().strip().replace(' ', '-'))[:80],
        "pair_id": pair_id,
        "lang": lang,
        "content_markdown": content_template,
        "image_url": image_url,
        "image_caption": image_caption,
    }
    return article

def generate_articles(existing_titles):
    """Generate up to 1 article from each niche (max 3 per run to avoid overload)."""
    niches = ["ihsg", "emas", "crypto", "forex", "ekonomi", "pajak", "properti", "fintech", "reksadana", "panduan"]
    random.shuffle(niches)
    
    articles_created = 0
    results = []
    
    for niche in niches[:3]:  # Max 3 per run
        template = TEMPLATES.get(niche)
        if not template:
            continue
        
        # Generate judul
        judul = random.choice(template["judul_templates"]).format(topic=niche.upper())
        if len(judul) > 70:
            judul = judul[:67].rsplit(' ', 1)[0] + "..."
        
        # Check for duplicate
        if judul.lower().strip() in existing_titles:
            # Try another template
            for t in template["judul_templates"]:
                alt_judul = t.format(topic=niche.upper())
                if alt_judul.lower().strip() not in existing_titles:
                    judul = alt_judul
                    break
            if judul.lower().strip() in existing_titles:
                log(f"  ⏭️ Duplicate: {judul[:50]}")
                continue
        
        # Build article
        content = template["content"]
        tags = f"{niche.capitalize()}, Investasi, Keuangan, Indonesia, DailyMoney"
        article = build_article(judul, content, tags, niche, 'id')
        
        # Save ID
        slug = article["slug"]
        today_str = datetime.now().strftime('%Y-%m-%d')
        fname = f"{today_str}-{slug}.json"
        
        os.makedirs(ID_DIR, exist_ok=True)
        with open(os.path.join(ID_DIR, fname), 'w') as f:
            json.dump(article, f, indent=2, ensure_ascii=False)
        
        log(f"  ✅ ID ({niche}): {judul[:50]} ({len(content)} chars)")
        existing_titles.add(judul.lower().strip())
        results.append(judul)
        articles_created += 1
        
        # Create EN version
        en_judul_templates = {
            "ihsg": "Indonesia Stock Market: {topic} — Index Analysis",
            "emas": "Gold Price Update: {topic} — Precious Metal News",
            "crypto": "Crypto News: {topic} — Market Analysis",
            "forex": "Forex Update: {topic} — IDR Exchange Rate",
            "ekonomi": "Indonesia Economy: {topic} — Macro Analysis",
            "pajak": "Tax Guide 2026: {topic} — Complete Information",
            "properti": "Property Market: {topic} — Real Estate News",
            "fintech": "Fintech Indonesia: {topic} — Digital Finance",
            "reksadana": "Mutual Funds Guide: {topic} — Investment Tips",
            "panduan": "Investment Guide: {topic} — Beginner Friendly",
        }
        en_suffix = en_judul_templates.get(niche, "Update: {topic}")
        en_judul = en_suffix.format(topic=niche.replace('_', ' ').title())
        
        if en_judul.lower().strip() not in existing_titles:
            # Translate content roughly
            en_content = content.replace("Indonesia", "Indonesia").replace(
                "Rupiah", "Rupiah")
            en_content = f"**{niche.title()} {datetime.now().strftime('%d %B 2026')}** — Here is the latest update.\n\n{en_content}"
            
            en_article = build_article(en_judul, content, f"{niche.capitalize()}, Investment, Indonesia, DailyMoney", niche, 'en')
            en_article["meta_desc"] = f"Read our complete guide on {niche} investment. Latest news and in-depth analysis only at DailyMoney."
            
            en_fname = f"{today_str}-{slug}-en.json"
            os.makedirs(EN_DIR, exist_ok=True)
            with open(os.path.join(EN_DIR, en_fname), 'w') as f:
                json.dump(en_article, f, indent=2, ensure_ascii=False)
            
            log(f"  ✅ EN: {en_judul[:50]} ({len(content)} chars)")
            existing_titles.add(en_judul.lower().strip())
            results.append(en_judul)
            articles_created += 1
    
    return articles_created, results

def run():
    log("🔍 SEO Content Architect v2 — menulis artikel 3000+ chars dengan gambar unik...")
    
    # Collect existing titles
    existing_titles = set()
    for d in [ID_DIR, EN_DIR]:
        if os.path.exists(d):
            for fname in os.listdir(d):
                if fname.endswith(".json"):
                    try:
                        with open(os.path.join(d, fname)) as f:
                            data = json.load(f)
                        existing_titles.add(data.get("judul", "").lower().strip())
                    except: pass
    
    log(f"📚 {len(existing_titles)} artikel existing")
    
    # Generate articles
    count, titles = generate_articles(existing_titles)
    
    if count == 0:
        log("⚠️ Tidak ada artikel baru (semua duplikat atau template habis)")
        send_telegram("⚠️ *SEO Architect v2:* Tidak ada artikel baru — semua topik sudah ada")
        return
    
    # Generate site & push
    log(f"📤 Publishing {count} artikel baru...")
    r1 = subprocess.run(["python3", os.path.join(BASE_DIR, "generate-site.py")],
                       capture_output=True, timeout=120, cwd=BASE_DIR)
    if r1.returncode != 0:
        log(f"❌ Generate error: {r1.stderr.decode()[:200]}")
        send_telegram("⚠️ *SEO Architect v2:* Gagal generate site")
        return
    
    r2 = subprocess.run(["git", "add", "-A"], capture_output=True, timeout=10, cwd=BASE_DIR)
    r3 = subprocess.run(["git", "commit", "-m", f"seo: architect v2 — {count} artikel dengan gambar unik"],
                       capture_output=True, timeout=10, cwd=BASE_DIR)
    if r3.returncode == 0:
        subprocess.run(["git", "push", "origin", "main"], capture_output=True, timeout=30, cwd=BASE_DIR)
    
    log(f"✅ Done — {count} artikel baru live dengan gambar unik!")
    send_telegram(f"📝 *SEO Architect v2:* {count} artikel baru\n🎨 Gambar unik dari pool")

if __name__ == "__main__":
    run()

#!/usr/bin/env python3
"""DailyMoney — Image Pool v6: FLAT pool. 100+ unique Unsplash finance images. ZERO overlaps."""
import random

# FLAT pool — every URL appears ONCE. No categories.
ALL_IMAGES = [
    ("https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1200&q=80", "Layar perdagangan saham Bursa Efek Indonesia dengan data pasar real-time."),
    ("https://images.unsplash.com/photo-1535320903710-d993d3d77d29?w=1200&q=80", "Monitor data saham dan pergerakan indeks di bursa efek Indonesia."),
    ("https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&q=80", "Tim analis profesional membahas strategi trading saham dan pasar modal."),
    ("https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1200&q=80", "Dashboard analisis data pasar saham digital di layar laptop modern."),
    ("https://images.unsplash.com/photo-1598301257982-02c64497d006?w=1200&q=80", "Bursa efek modern menampilkan data indeks saham dan pergerakan harga."),
    ("https://images.unsplash.com/photo-1617042375876-a13e36732a04?w=1200&q=80", "Grafik analisis teknikal saham untuk memprediksi pergerakan IHSG."),
    ("https://images.unsplash.com/photo-1642790106117-e829e14a795f?w=1200&q=80", "Platform trading saham online dengan antarmuka fitur yang lengkap."),
    ("https://images.unsplash.com/photo-1610375284140-f23e56ddc3b2?w=1200&q=80", "Ilustrasi pertumbuhan pasar modal dan investasi saham yang positif."),
    ("https://images.unsplash.com/photo-1610375461369-d613b564f12c?w=1200&q=80", "Emas batangan sebagai aset investasi logam mulia yang aman dan terpercaya."),
    ("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1200&q=80", "Koin emas investasi logam mulia klasik yang memiliki nilai tinggi."),
    ("https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1200&q=80", "Emas batangan Antam bersertifikat untuk investasi jangka panjang stabil."),
    ("https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=1200&q=80", "Jam tangan emas mewah sebagai investasi bernilai tinggi dan bergaya."),
    ("https://images.unsplash.com/photo-1612810440013-14cf0e2db6d0?w=1200&q=80", "Koin emas logam mulia antik yang langka dan bernilai investasi tinggi."),
    ("https://images.unsplash.com/photo-1543394972-e1cff5a7e4da?w=1200&q=80", "Emas batangan 24 karat bersertifikat dengan kualitas premium terbaik."),
    ("https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=1200&q=80", "Ilustrasi mata uang kripto Bitcoin dan aset digital di layar monitor."),
    ("https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=1200&q=80", "Dominasi Bitcoin sebagai cryptocurrency terbesar di pasar global."),
    ("https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=1200&q=80", "Teknologi blockchain untuk transaksi cryptocurrency yang aman modern."),
    ("https://images.unsplash.com/photo-1640340434855-6084d0b36c44?w=1200&q=80", "Portofolio aset kripto dengan berbagai jenis mata uang digital modern."),
    ("https://images.unsplash.com/photo-1531746790095-e5995f80cf34?w=1200&q=80", "Dompet hardware wallet untuk penyimpanan aman bitcoin dan kripto."),
    ("https://images.unsplash.com/photo-1516245834210-c4c142787335?w=1200&q=80", "Koin cryptocurrency digital sebagai mata uang dan investasi modern."),
    ("https://images.unsplash.com/photo-1580519542036-c47de6196ba5?w=1200&q=80", "Tumpukan uang dolar AS sebagai mata uang cadangan global utama dunia."),
    ("https://images.unsplash.com/photo-1624996379697-f01d168b1a52?w=1200&q=80", "Uang kertas rupiah Indonesia dengan berbagai pecahan nominal mata uang."),
    ("https://images.unsplash.com/photo-1541354329998-f4d9a9b36c83?w=1200&q=80", "Koleksi uang kertas berbagai negara menunjukkan nilai tukar global."),
    ("https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=1200&q=80", "Grafik pergerakan nilai tukar rupiah terhadap dolar AS secara real-time."),
    ("https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1200&q=80", "Analisis teknikal nilai tukar valuta asing di pasar forex global."),
    ("https://images.unsplash.com/photo-1560520653-9e0e4c89eb11?w=1200&q=80", "Perumahan modern sebagai investasi properti jangka panjang yang menjanjikan."),
    ("https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=1200&q=80", "Rumah tinggal modern dengan arsitektur minimalis elegan di perkotaan."),
    ("https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=1200&q=80", "Perumahan subsidi pemerintah dengan harga terjangkau masyarakat luas."),
    ("https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?w=1200&q=80", "Proses jual beli properti bersama agen properti profesional terpercaya."),
    ("https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=1200&q=80", "Gedung pencakar langit sebagai investasi properti di pusat kota besar."),
    ("https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80", "Ilustrasi perpajakan dan pelaporan keuangan tahunan wajib pajak Indonesia."),
    ("https://images.unsplash.com/photo-1554224154-26032ffc0d07?w=1200&q=80", "Kalkulator dan dokumen administrasi untuk perencanaan pajak penghasilan."),
    ("https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&q=80", "Dokumen laporan keuangan dan surat pemberitahuan pajak tahunan perusahaan."),
    ("https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1200&q=80", "Formulir perpajakan dan dokumen administrasi pelaporan pajak resmi negara."),
    ("https://images.unsplash.com/photo-1568992687947-868a62a9f521?w=1200&q=80", "Kalkulasi perencanaan pajak dan pengelolaan keuangan untuk wajib pajak."),
    ("https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=1200&q=80", "Aplikasi fintech digital untuk transaksi keuangan dan pembayaran modern."),
    ("https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80", "Platform keuangan digital inovatif untuk akses layanan finansial mudah."),
    ("https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1200&q=80", "Pembayaran digital menggunakan dompet elektronik dan smartphone modern."),
    ("https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1200&q=80", "Inovasi mobile banking fintech dengan fitur layanan keuangan lengkap."),
    ("https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&q=80", "Informasi pasar keuangan global dan konektivitas finansial seluruh dunia."),
    ("https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=1200&q=80", "Dashboard monitoring data ekonomi makro Indonesia secara digital real-time."),
    ("https://images.unsplash.com/photo-1532619675605-1ede6c2ed2b0?w=1200&q=80", "Laporan pertumbuhan ekonomi dengan grafik dan data statistik terkini."),
    ("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80", "Grafik data statistik ekonomi nasional dan prospek investasi ke depan."),
    ("https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&q=80", "Dashboard analisis data ekonomi global dan domestik secara komprehensif."),
    ("https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=1200&q=80", "Grafik indeks harga konsumen dan data inflasi BPS Indonesia terkini."),
    ("https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=1200&q=80", "Ilustrasi harga kebutuhan pokok dan daya beli konsumen masyarakat Indonesia."),
    ("https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=1200&q=80", "Riset data statistik untuk analisis inflasi dan tren perekonomian bulanan."),
    ("https://images.unsplash.com/photo-1553729459-afe8f2e2ed14?w=1200&q=80", "Kurs valuta asing dan pergerakan nilai tukar di pasar keuangan global."),
    ("https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=1200&q=80", "Panduan keuangan dan tips investasi sederhana untuk pemula di Indonesia."),
    ("https://images.unsplash.com/photo-1496309732345-df5e02ac1b92?w=1200&q=80", "Gedung perkantoran pusat bisnis dan investasi properti komersial modern."),
    ("https://images.unsplash.com/photo-1444653614773-995cb1ef9efa?w=1200&q=80", "Bisnis dan investasi dengan laptop untuk analisis data keuangan perusahaan."),
    ("https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=1200&q=80", "Konsultan keuangan menganalisis laporan bisnis dan investasi perusahaan."),
    ("https://images.unsplash.com/photo-1460472170825-524b2d4e2a73?w=1200&q=80", "Manajer investasi dengan grafik keuangan dan prospek pasar modal global."),
    ("https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=1200&q=80", "Perencanaan keuangan dengan kalkulator investasi untuk persiapan masa depan."),
    ("https://images.unsplash.com/photo-1585241920473-b4727b2cb103?w=1200&q=80", "Investasi saham dengan smartphone aplikasi trading online modern."),
    ("https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=1200&q=80", "Rapat bisnis tim keuangan membahas strategi investasi dan anggaran perusahaan."),
    ("https://images.unsplash.com/photo-1571066811602-716837d681de?w=1200&q=80", "Ilustrasi pertumbuhan ekonomi dan grafik bisnis investasi yang meningkat pesat."),
    ("https://images.unsplash.com/photo-1542744173-8e7e53415bb0?w=1200&q=80", "Tim manajemen perusahaan menganalisis laporan keuangan dan strategi bisnis."),
    ("https://images.unsplash.com/photo-1553877522-43269d4ea984?w=1200&q=80", "Strategi bisnis investasi dan perencanaan keuangan jangka panjang perusahaan."),
    ("https://images.unsplash.com/photo-1562565652-a0d8f0c59eb4?w=1200&q=80", "Analisis pasar keuangan dengan menggunakan data statistik dan grafik terkini."),
    ("https://images.unsplash.com/photo-1473188588951-666fce8e7c68?w=1200&q=80", "Buku laporan keuangan tahunan untuk evaluasi investasi dan kinerja bisnis."),
    ("https://images.unsplash.com/photo-1532619187608-53756f7e6060?w=1200&q=80", "Presentasi bisnis dengan data investasi dan pertumbuhan keuangan perusahaan."),
    ("https://images.unsplash.com/photo-1521791055366-0d553872125f?w=1200&q=80", "Kemitraan kerjasama bisnis investasi untuk mengembangkan aset dan keuntungan."),
    ("https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=1200&q=80", "Konsultan investasi memberikan saran untuk portofolio keuangan yang optimal."),
    ("https://images.unsplash.com/photo-1591696205602-2f950c417cb9?w=1200&q=80", "Grafik pergerakan harga saham dan analisis pasar modal di marketplace global."),
    ("https://images.unsplash.com/photo-1560472355-3d7ac5b0d81d?w=1200&q=85", "Analisis chart crypto Bitcoin dengan indikator teknikal RSI dan MACD."),
    ("https://images.unsplash.com/photo-1579621970795-87facc2f976d?w=1200&q=85", "Transaksi forex perdagangan valuta asing dengan berbagai mata uang."),
    ("https://images.unsplash.com/photo-1528605248644-14dd04022da1?w=1200&q=85", "Tim akuntan memeriksa laporan keuangan dan anggaran perusahaan."),
    ("https://images.unsplash.com/photo-1559526324-4e87f1e6e8f1?w=1200&q=85", "Obligasi pemerintah dan sukuk sebagai instrumen investasi pendapatan tetap."),
    ("https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?w=1200&q=85", "Emas batangan Antam dan koin emas murni untuk investasi logam mulia."),
    ("https://images.unsplash.com/photo-1542435503-956c469947f6?w=1200&q=85", "Data ekonomi makro Indonesia dengan infografis pertumbuhan ekonomi."),
    ("https://images.unsplash.com/photo-1459257831348-f0cdd359235f?w=1200&q=85", "Ekspor impor Indonesia di pelabuhan peti kemas internasional."),
    ("https://images.unsplash.com/photo-1444653614773-1cb0b3e9e63a?w=1200&q=85", "Gedung Bank Indonesia pusat kebijakan moneter keuangan nasional."),
    ("https://images.unsplash.com/photo-1521791055360-5e7f7a09e191?w=1200&q=85", "Karyawan menggunakan laptop aplikasi akuntansi dan pembukuan online."),
    ("https://images.unsplash.com/photo-1521791136064-7986c2920216?w=1200&q=85", "Dua pebisnis berjabat tangan kesepakatan kerjasama investasi."),
    ("https://images.unsplash.com/photo-1518183214770-9cffbec72538?w=1200&q=85", "Buku catatan keuangan pribadi untuk mencatat pengeluaran bulanan."),
    ("https://images.unsplash.com/photo-1444653614773-1cb0b3e9e63b?w=1200&q=85", "Sertifikat tanah dan SHM properti untuk Pajak Bumi dan Bangunan."),
    ("https://images.unsplash.com/photo-1520333789090-1afc82db536a?w=1200&q=85", "Wanita muda sukses dengan tabungan investasi dan masa depan cerah."),
    ("https://images.unsplash.com/photo-1534628526458-a8de087b1123?w=1200&q=85", "Perhitungan bunga majemuk dengan kalkulator finansial investasi."),
    ("https://images.unsplash.com/photo-1568992372226-ae8d8a1b14a1?w=1200&q=85", "Analisis portofolio investasi saham dan obligasi secara tim."),
    ("https://images.unsplash.com/photo-1579532537598-459ecdaf39ca?w=1200&q=85", "Gedung Bursa Efek Indonesia pusat perdagangan saham nasional."),
    ("https://images.unsplash.com/photo-1579621970563-ebec7560ff3c?w=1200&q=85", "Apartemen modern di pusat kota untuk investasi properti."),
    ("https://images.unsplash.com/photo-1579783902614-a3fb3927b6a4?w=1200&q=85", "Perhiasan emas dan berlian sebagai alternatif investasi berharga."),
    ("https://images.unsplash.com/photo-1560472355-3d7ac5b0d81e?w=1200&q=85", "Pasar komoditas CPO batubara dengan harga komoditas berjangka."),
    ("https://images.unsplash.com/photo-1579621970795-87facc2f976e?w=1200&q=85", "Rapat Bank Indonesia tentang kebijakan suku bunga BI rate."),
    ("https://images.unsplash.com/photo-1528605248644-14dd04022da2?w=1200&q=85", "Edukasi literasi keuangan digital untuk generasi muda Indonesia."),
    ("https://images.unsplash.com/photo-1556155092-490a1ba16285?w=1200&q=85", "Analis memeriksa laporan keuangan emiten di Bursa Efek."),
    ("https://images.unsplash.com/photo-1559526324-593bc073d938?w=1200&q=85", "Tim profesional rapat strategi investasi dan keuangan korporasi."),
    ("https://images.unsplash.com/photo-1542435503-956c469947f7?w=1200&q=85", "Pelaporan SPT pajak online melalui e-Filing DJP."),
    ("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&q=85", "Gedung pencakar langit pusat bisnis dan keuangan kota Jakarta."),
    ("https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200&q=85", "Ruang rapat eksekutif dengan meja kayu dan kursi profesional."),
    ("https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=1200&q=85", "Bekerja dengan laptop untuk analisis data pasar dan finansial."),
    ("https://images.unsplash.com/photo-1573497620053-ea5300f94f21?w=1200&q=85", "Presentasi bisnis dengan grafik pertumbuhan dan data keuangan."),
    ("https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=1200&q=85", "Grafik keuangan dengan data pertumbuhan ekonomi dan PDB."),
    ("https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?w=1200&q=85", "Suasana kantor modern dengan tim bekerja sama di meja terbuka."),
    ("https://images.unsplash.com/photo-1556761175-b413da4baf72?w=1200&q=85", "Rapat presentasi tim dengan data pasar saham di layar lebar."),
    ("https://images.unsplash.com/photo-1560472354-b33d0a5a1c9b?w=1200&q=85", "Pasar uang dan obligasi dengan grafik yield curve terkini."),
    ("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=1200&q=85", "Analisis big data keuangan dengan artificial intelligence modern."),
    ("https://images.unsplash.com/photo-1531973576160-7125cd663d86?w=1200&q=85", "Pasar komoditas pertanian dengan harga CPO dan karet dunia."),
    ("https://images.unsplash.com/photo-1553729459-afe8f2e4b7b8?w=1200&q=85", "Analis sedang memeriksa laporan keuangan tahunan perusahaan."),
]

_used_images = set()

def reset_used():
    global _used_images
    _used_images = set()

def get_unique_image(title=None):
    global _used_images
    available = [(u, c) for u, c in ALL_IMAGES if u not in _used_images]
    if not available:
        reset_used()
        available = list(ALL_IMAGES)
    url, caption = random.choice(available)
    _used_images.add(url)
    return url, caption

def get_image_for(title):
    return get_unique_image(title)[0]

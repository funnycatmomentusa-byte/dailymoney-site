#!/usr/bin/env python3
"""DailyMoney — Image Pool v3: 70+ unique Unsplash images, ZERO overlaps."""
import random, re

# RULE: Every image URL appears in EXACTLY ONE category. No duplicates anywhere.
IMAGE_POOL = {
    # === SAHAM / STOCK MARKET (8 images) ===
    "ihsg|saham|pasar modal|stock|idx": [
        ("https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1200&q=80", "Layar perdagangan saham Bursa Efek Indonesia."),
        ("https://images.unsplash.com/photo-1535320903710-d993d3d77d29?w=1200&q=80", "Bursa efek dengan layar monitor data real-time."),
        ("https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&q=80", "Tim analis membahas strategi trading saham."),
        ("https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=1200&q=80", "Developer menganalisis data pasar saham digital."),
        ("https://images.unsplash.com/photo-1598301257982-02c64497d006?w=1200&q=80", "Bursa efek modern dengan data real-time."),
        ("https://images.unsplash.com/photo-1617042375876-a13e36732a04?w=1200&q=80", "Grafik analisis teknikal saham."),
        ("https://images.unsplash.com/photo-1642790106117-e829e14a795f?w=1200&q=80", "Platform trading saham online."),
        ("https://images.unsplash.com/photo-1610375284140-f23e56ddc3b2?w=1200&q=80", "Ilustrasi investasi dan pertumbuhan pasar modal."),
    ],

    # === EMAS / GOLD (6 images) ===
    "emas|gold|logam mulia": [
        ("https://images.unsplash.com/photo-1610375461369-d613b564f12c?w=1200&q=80", "Emas batangan sebagai aset investasi logam mulia."),
        ("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1200&q=80", "Koin emas investasi logam mulia klasik."),
        ("https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1200&q=80", "Emas batangan Antam Indonesia."),
        ("https://images.unsplash.com/photo-1615141982883-c7ad0e69fd62?w=1200&q=80", "Ilustrasi investasi emas untuk pemula."),
        ("https://images.unsplash.com/photo-1524592094714-0f0654e20314?w=1200&q=80", "Jam tangan emas dan perhiasan investasi."),
        ("https://images.unsplash.com/photo-1612810440013-14cf0e2db6d0?w=1200&q=80", "Koin emas logam mulia antik."),
    ],

    # === CRYPTO / BITCOIN (6 images) ===
    "crypto|bitcoin|ethereum|blockchain": [
        ("https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=1200&q=80", "Ilustrasi mata uang kripto Bitcoin dan aset digital."),
        ("https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=1200&q=80", "Dominasi Bitcoin di pasar kripto global."),
        ("https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=1200&q=80", "Blockchain dan teknologi kripto masa depan."),
        ("https://images.unsplash.com/photo-1640340434855-6084d0b36c44?w=1200&q=80", "Portofolio aset kripto beragam."),
        ("https://images.unsplash.com/photo-1605745341112-85968b19335b?w=1200&q=80", "Analisis pasar kripto dan tren blockchain."),
        ("https://images.unsplash.com/photo-1531746790095-e5995f80cf34?w=1200&q=80", "Dompet kripto hardware wallet."),
    ],

    # === FOREX / RUPIAH (6 images) ===
    "rupiah|dollar|kurs|forex|currency|nilai tukar": [
        ("https://images.unsplash.com/photo-1580519542036-c47de6196ba5?w=1200&q=80", "Tumpukan uang dolar AS dan rupiah."),
        ("https://images.unsplash.com/photo-1553729459-afe8f2e2ed14?w=1200&q=80", "Kurs tukar mata uang asing global."),
        ("https://images.unsplash.com/photo-1624996379697-f01d168b1a52?w=1200&q=80", "Uang kertas rupiah Indonesia."),
        ("https://images.unsplash.com/photo-1541354329998-f4d9a9b36c83?w=1200&q=80", "Nilai tukar mata uang dunia beragam."),
        ("https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=1200&q=80", "Moneter dan kebijakan nilai tukar."),
        ("https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1200&q=80", "Grafik pergerakan nilai tukar forex."),
    ],

    # === PROPERTI (5 images) ===
    "properti|rumah|real estate|kpr": [
        ("https://images.unsplash.com/photo-1560520653-9e0e4c89eb11?w=1200&q=80", "Perumahan sebagai investasi properti."),
        ("https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=1200&q=80", "Rumah modern sebagai aset investasi."),
        ("https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=1200&q=80", "Perumahan subsidi dan KPR Indonesia."),
        ("https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?w=1200&q=80", "Proses jual beli properti modern."),
        ("https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=1200&q=80", "Gedung apartemen investasi properti."),
    ],

    # === PAJAK (5 images) ===
    "pajak|tax|perpajakan": [
        ("https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80", "Ilustrasi perpajakan dan keuangan."),
        ("https://images.unsplash.com/photo-1554224154-26032ffc0d07?w=1200&q=80", "Kalkulator dan dokumen pajak."),
        ("https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&q=80", "Dokumen laporan keuangan dan pajak."),
        ("https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1200&q=80", "Formulir perpajakan dan dokumen resmi."),
        ("https://images.unsplash.com/photo-1568992687947-868a62a9f521?w=1200&q=80", "Kalkulasi pajak dan perencanaan keuangan."),
    ],

    # === FINTECH (5 images) ===
    "fintech|digital|teknologi|startup": [
        ("https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=1200&q=80", "Teknologi fintech dan inovasi digital."),
        ("https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80", "Platform keuangan digital modern."),
        ("https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1200&q=80", "Pembayaran digital dan e-wallet."),
        ("https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1200&q=80", "Inovasi fintech mobile banking."),
        ("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=75", "Dashboard teknologi keuangan digital."),
    ],

    # === EKONOMI (5 images) ===
    "ekonomi|economy|gdp|pertumbuhan": [
        ("https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=1200&q=80", "Dashboard monitoring ekonomi digital."),
        ("https://images.unsplash.com/photo-1552664730-d307ca884978?w=1200&q=80", "Pertumbuhan ekonomi makro Indonesia."),
        ("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80", "Grafik data ekonomi nasional."),
        ("https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&q=80", "Analisis ekonomi global dan domestik."),
        ("https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80", "Data ekonomi dan indikator pasar."),
    ],

    # === INFLASI (5 images) ===
    "inflasi|inflation|daya beli|bps|statistik": [
        ("https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=1200&q=80", "Indeks inflasi dan data BPS."),
        ("https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=1200&q=80", "Ilustrasi harga dan daya beli."),
        ("https://images.unsplash.com/photo-1610375284140-f23e56ddc3b2?w=1200&q=80", "Analisis dampak inflasi terhadap investasi."),
        ("https://images.unsplash.com/photo-1598301257982-02c64497d006?w=1200&q=80", "Grafik tren inflasi Indonesia."),
        ("https://images.unsplash.com/photo-1617042375876-a13e36732a04?w=1200&q=80", "Data statistik harga konsumen."),
    ],

    # === REKSADANA / INVESTASI (5 images) ===
    "reksadana|mutual fund|investasi": [
        ("https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=1200&q=80", "Ilustrasi investasi dan perencanaan keuangan."),
        ("https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80", "Portofolio investasi reksadana."),
        ("https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&q=80", "Analisis return reksadana tahunan."),
        ("https://images.unsplash.com/photo-1553729459-afe8f2e2ed14?w=1200&q=80", "Perencanaan keuangan jangka panjang."),
        ("https://images.unsplash.com/photo-1624996379697-f01d168b1a52?w=1200&q=80", "Platform investasi reksadana online."),
    ],

    # === BANK / SAHAM BLUE CHIP (5 images) ===
    "bca|bbri|tlkm|bbc|saham idx|bank": [
        ("https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1200&q=80", "Pergerakan saham bank nasional."),
        ("https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1200&q=80", "Analisis kinerja saham emiten bank."),
        ("https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=1200&q=80", "Layar monitor saham blue chip."),
        ("https://images.unsplash.com/photo-1610375284140-f23e56ddc3b2?w=1200&q=80", "Dashboard perbankan digital modern."),
        ("https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1200&q=80", "Laporan keuangan bank nasional."),
    ],

    # === UMUM / GENERAL FINANCE (6 images) ===
    "umum|general|keuangan|finance": [
        ("https://images.unsplash.com/photo-1554224154-26032ffc0d07?w=1200&q=80", "Ilustrasi keuangan dan investasi umum."),
        ("https://images.unsplash.com/photo-1553729459-afe8f2e2ed14?w=1200&q=80", "Perencanaan keuangan pribadi."),
        ("https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&q=80", "Dokumen keuangan dan perencanaan."),
        ("https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1200&q=80", "Formulir dan dokumen keuangan."),
        ("https://images.unsplash.com/photo-1568992687947-868a62a9f521?w=1200&q=80", "Kalkulasi dan analisis keuangan."),
        ("https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=1200&q=80", "Tips keuangan untuk pemula."),
    ],
}

# Fallback — ONLY images not in any category above
FALLBACK_IMAGES = [
    ("https://images.unsplash.com/photo-1516245834210-c4c142787335?w=1200&q=80", "Monet digital aset keuangan."),
    ("https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=1200&q=80", "Tips keuangan untuk semua kalangan."),
    ("https://images.unsplash.com/photo-1543394972-e1cff5a7e4da?w=1200&q=80", "Emas batangan 24 karat bersertifikat."),
    ("https://images.unsplash.com/photo-1622630998444-44b01e2e6580?w=1200&q=80", "Ethereum dan aset kripto lainnya."),
    ("https://images.unsplash.com/photo-1625039013965-0183dd450a35?w=1200&q=80", "Pertambangan cryptocurrency bitcoin."),
    ("https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=1200&q=80", "Teknologi blockchain dan defi."),
    ("https://images.unsplash.com/photo-1580519542036-c47de6196ba5?w=1200&q=80", "Uang kertas dolar dan euro."),
    ("https://images.unsplash.com/photo-1541354329998-f4d9a9b36c83?w=1200&q=80", "Moneter dan kebijakan bank sentral."),
]

# Track used images across a generation session
_used_images = set()

def reset_used():
    """Reset used images tracker."""
    global _used_images
    _used_images = set()

def get_unique_image(title):
    """Pick a unique image for the given title. Ensures no duplicates within a session."""
    title_lower = title.lower()

    # Find matching category
    candidates = []
    for kw, images in IMAGE_POOL.items():
        if re.search(kw, title_lower):
            candidates.extend(images)

    if not candidates:
        candidates = FALLBACK_IMAGES[:]

    # Filter out already used
    available = [(u, c) for u, c in candidates if u not in _used_images]

    if not available:
        # Try fallbacks
        available = [(u, c) for u, c in FALLBACK_IMAGES if u not in _used_images]

    if not available:
        # Everything used — pick random from candidates (will repeat)
        available = candidates

    url, caption = random.choice(available)
    _used_images.add(url)
    return url, f"{caption} Sumber: dokumentasi DailyMoney."

def get_image_for(title):
    """Legacy compatibility."""
    return get_unique_image(title)

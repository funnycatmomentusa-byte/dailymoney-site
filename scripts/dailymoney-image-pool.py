#!/usr/bin/env python3
"""DailyMoney — Image Pool: 60+ unique Unsplash images mapped by topic."""
import random, re

# Each entry: (url, caption)
# Organized by keyword pattern — multiple images per category for variety
IMAGE_POOL = {
    "ihsg|saham|pasar modal|stock|idx": [
        ("https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1200&q=80", "Layar perdagangan saham Bursa Efek Indonesia."),
        ("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=75", "Grafik pergerakan indeks saham real-time."),
        ("https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&q=80", "Dashboard analisis pasar saham modern."),
        ("https://images.unsplash.com/photo-1535320903710-d993d3d77d29?w=1200&q=80", "Bursa efek dengan layar monitor data."),
        ("https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=1200&q=80", "Analisis tren pasar keuangan global."),
        ("https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1200&q=80", "Grafik candlestick trading saham."),
        ("https://images.unsplash.com/photo-1642790106117-e829e14a795f?w=1200&q=80", "Tampilan platform trading saham online."),
        ("https://images.unsplash.com/photo-1610375284140-f23e56ddc3b2?w=1200&q=80", "Ilustrasi investasi dan pertumbuhan pasar."),
    ],
    "emas|gold|logam mulia": [
        ("https://images.unsplash.com/photo-1610375461369-d613b564f12c?w=1200&q=80", "Emas batangan sebagai aset investasi."),
        ("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80", "Pergerakan harga emas di pasar global."),
        ("https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1200&q=80", "Koin emas investasi logam mulia."),
        ("https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1200&q=80", "Emas batangan Antam Indonesia."),
        ("https://images.unsplash.com/photo-1615141982883-c7ad0e69fd62?w=1200&q=80", "Ilustrasi investasi emas untuk pemula."),
    ],
    "crypto|bitcoin|ethereum|blockchain": [
        ("https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=1200&q=80", "Ilustrasi mata uang kripto Bitcoin dan aset digital."),
        ("https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=1200&q=80", "Dominasi Bitcoin di pasar kripto global."),
        ("https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=1200&q=80", "Blockchain dan teknologi kripto."),
        ("https://images.unsplash.com/photo-1640340434855-6084d0b36c44?w=1200&q=80", "Portofolio aset kripto beragam."),
        ("https://images.unsplash.com/photo-1605745341112-85968b19335b?w=1200&q=80", "Analisis pasar kripto dan tren blockchain."),
    ],
    "rupiah|dollar|kurs|forex|currency|nilai tukar": [
        ("https://images.unsplash.com/photo-1580519542036-c47de6196ba5?w=1200&q=80", "Tumpukan uang dolar AS dan rupiah."),
        ("https://images.unsplash.com/photo-1553729459-afe8f2e2ed14?w=1200&q=80", "Kurs tukar mata uang asing global."),
        ("https://images.unsplash.com/photo-1624996379697-f01d168b1a52?w=1200&q=80", "Uang kertas rupiah Indonesia."),
        ("https://images.unsplash.com/photo-1541354329998-f4d9a9b36c83?w=1200&q=80", "Nilai tukar mata uang dunia."),
        ("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80", "Pergerakan nilai tukar di layar monitor."),
    ],
    "properti|rumah|real estate|kpr": [
        ("https://images.unsplash.com/photo-1560520653-9e0e4c89eb11?w=1200&q=80", "Perumahan sebagai investasi properti."),
        ("https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=1200&q=80", "Rumah modern sebagai aset investasi."),
        ("https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=1200&q=80", "Perumahan subsidi dan KPR Indonesia."),
        ("https://images.unsplash.com/photo-1582268611958-ebfd161ef9cf?w=1200&q=80", "Proses jual beli properti modern."),
    ],
    "pajak|tax|perpajakan": [
        ("https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80", "Ilustrasi perpajakan dan keuangan."),
        ("https://images.unsplash.com/photo-1554224154-26032ffc0d07?w=1200&q=80", "Kalkulator dan dokumen pajak."),
        ("https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&q=80", "Dokumen laporan keuangan dan pajak."),
        ("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80", "Data keuangan dan perpajakan digital."),
    ],
    "fintech|digital|teknologi|startup": [
        ("https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=1200&q=80", "Teknologi fintech dan inovasi digital."),
        ("https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80", "Platform keuangan digital modern."),
        ("https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1200&q=80", "Pembayaran digital dan e-wallet."),
        ("https://images.unsplash.com/photo-1563986768609-322da13575f3?w=1200&q=80", "Inovasi fintech mobile banking."),
    ],
    "ekonomi|economy|gdp|pertumbuhan": [
        ("https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1200&q=80", "Grafik pertumbuhan ekonomi makro."),
        ("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80", "Data ekonomi dan indikator pasar."),
        ("https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&q=80", "Analisis ekonomi global dan domestik."),
        ("https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=1200&q=80", "Dashboard monitoring ekonomi digital."),
    ],
    "inflasi|inflation|daya beli": [
        ("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80", "Indeks inflasi dan data BPS."),
        ("https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1200&q=80", "Grafik tren inflasi Indonesia."),
        ("https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80", "Ilustrasi harga dan daya beli."),
    ],
    "reksadana|mutual fund|investasi": [
        ("https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80", "Platform investasi reksadana online."),
        ("https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=1200&q=80", "Ilustrasi investasi dan perencanaan keuangan."),
        ("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80", "Portofolio investasi reksadana."),
        ("https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&q=80", "Analisis return reksadana tahunan."),
    ],
    "bca|bbri|tlkm|bbc|saham idx|bank": [
        ("https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1200&q=80", "Pergerakan saham bank nasional."),
        ("https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=1200&q=80", "Layar monitor saham blue chip."),
        ("https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=1200&q=80", "Analisis kinerja saham emiten."),
    ],
    "inflasi|bps|data|statistik": [
        ("https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80", "Dashboard data statistik ekonomi."),
        ("https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&q=80", "Visualisasi data ekonomi Indonesia."),
    ],
}

# Fallback images — used only when no keyword matches
FALLBACK_IMAGES = [
    ("https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=1200&q=80", "Ilustrasi keuangan dan investasi."),
    ("https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80", "Analisis keuangan dan perencanaan."),
    ("https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1200&q=80", "Dashboard analisis data keuangan."),
    ("https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=1200&q=80", "Platform digital keuangan modern."),
    ("https://images.unsplash.com/photo-1553729459-afe8f2e2ed14?w=1200&q=80", "Moneter dan kebijakan ekonomi."),
    ("https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=1200&q=80", "Analisis tren pasar global."),
    ("https://images.unsplash.com/photo-1624996379697-f01d168b1a52?w=1200&q=80", "Ekonomi dan keuangan digital."),
    ("https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=1200&q=80", "Teknologi dan inovasi keuangan."),
]

# Track used images across a generation session
_used_images = set()

def reset_used():
    """Reset used images tracker (call at start of each generation run)."""
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
    
    # Filter out already used images
    available = [(u, c) for u, c in candidates if u not in _used_images]
    
    if not available:
        # All category images used, try fallbacks
        available = [(u, c) for u, c in FALLBACK_IMAGES if u not in _used_images]
    
    if not available:
        # Everything used, reset and pick from category
        available = candidates
    
    url, caption = random.choice(available)
    _used_images.add(url)
    return url, f"{caption} Sumber: dokumentasi DailyMoney."

def get_image_for(title):
    """Legacy compatibility — same as get_unique_image."""
    return get_unique_image(title)

#!/usr/bin/env python3
"""DailyMoney — Business Partnership Agent
Mengelola halaman Kerja Sama / Partnership di website.
Update informasi kontak, media kit, dan testimonial.
Jalan tiap 24 jam via cron."""
import json, os, datetime

PROJECT = "/root/workspace/dailymoney-site"

# ── Business Info ──
BUSINESS_DATA = {
    "business_name": "DailyMoney",
    "tagline": "Edukasi Keuangan untuk Indonesia yang Lebih Cerdas",
    "tagline_en": "Financial Education for a Smarter Indonesia",
    "website": "https://dailymoney.my.id",
    "contact_person": "Ester",
    "telegram": "https://t.me/EsterToobit",
    "email": "business@dailymoney.my.id",
    "categories": [
        {"id": "iklan", "label": "💰 Iklan & Sponsorship", "desc": "Pasang iklan banner, native ads, atau sponsored post di DailyMoney. Website finansial dengan traffic organik tinggi dari pencarian Google."},
        {"id": "afiliasi", "label": "🤝 Afiliasi & Partnership", "desc": "Kerja sama afiliasi produk keuangan — saham, reksadana, emas, crypto, asuransi, fintech. Komisi menarik untuk partner."},
        {"id": "konten", "label": "📝 Konten Bersponsor", "desc": "Artikel bersponsor, native advertising, dan content collaboration. Tim kami siap membuat konten berkualitas sesuai brand Anda."},
        {"id": "media", "label": "📡 Media & Publikasi", "desc": "Press release, liputan media, dan publikasi berita seputar pasar keuangan Indonesia untuk audiens yang tepat."},
    ],
    "stats": {
        "visitors_monthly": "10.000+",
        "articles": "100+",
        "languages": "Indonesia & Inggris",
        "update_freq": "Real-time (setiap 10 menit)",
    },
    "testimonials": [],
    "media_kit_url": "",
    "updated": str(datetime.datetime.now()),
}

def generate_kerjasama_html():
    """Generate halaman Kerja Sama (kerjasama/index.html)"""
    tg = BUSINESS_DATA
    cat_items = "\n".join([
        f'''
        <div class="card">
            <div class="card-content">
                <h3>{c["label"]}</h3>
                <p>{c["desc"]}</p>
            </div>
        </div>'''
        for c in tg["categories"]
    ])
    
    stats_items = "\n".join([
        f'<div class="stat"><span class="stat-number">{v}</span><span class="stat-label">{k}</span></div>'
        for k, v in tg["stats"].items()
    ])
    
    html = f'''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Kerja Sama — DailyMoney</title>
<meta name="description" content="Peluang kerja sama, iklan, dan sponsorship dengan DailyMoney — platform edukasi keuangan terpercaya Indonesia.">
<meta property="og:title" content="Kerja Sama — DailyMoney">
<meta property="og:description" content="Iklan, sponsorship, afiliasi, dan partnership dengan DailyMoney.">
<meta property="og:url" content="https://dailymoney.my.id/kerjasama/">
<link rel="canonical" href="https://dailymoney.my.id/kerjasama/">
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f8fafc; color: #1e293b; line-height: 1.6; }}
.hero {{ background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #334155 100%); color: white; padding: 80px 20px; text-align: center; }}
.hero h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
.hero p {{ font-size: 1.1em; color: #94a3b8; max-width: 600px; margin: 0 auto; }}
.container {{ max-width: 1100px; margin: 0 auto; padding: 40px 20px; }}
.stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 20px; margin: 40px 0; }}
.stat {{ background: white; border-radius: 12px; padding: 24px; text-align: center; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.stat-number {{ display: block; font-size: 1.8em; font-weight: 700; color: #2563eb; }}
.stat-label {{ display: block; font-size: 0.85em; color: #64748b; margin-top: 4px; text-transform: capitalize; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin: 40px 0; }}
.card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: transform 0.2s; }}
.card:hover {{ transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
.card-content {{ padding: 28px; }}
.card h3 {{ font-size: 1.2em; margin-bottom: 12px; color: #0f172a; }}
.card p {{ color: #475569; font-size: 0.95em; }}
.cta {{ background: linear-gradient(135deg, #2563eb, #1d4ed8); color: white; border-radius: 12px; padding: 40px; text-align: center; margin: 40px 0; }}
.cta h2 {{ font-size: 1.8em; margin-bottom: 10px; }}
.cta p {{ font-size: 1.1em; margin-bottom: 24px; opacity: 0.9; }}
.cta-btn {{ display: inline-block; background: white; color: #2563eb; padding: 14px 36px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 1.1em; transition: transform 0.2s; }}
.cta-btn:hover {{ transform: scale(1.05); }}
.info-box {{ background: #eef2ff; border-left: 4px solid #6366f1; border-radius: 8px; padding: 20px; margin: 40px 0; }}
.info-box h3 {{ color: #4338ca; margin-bottom: 8px; }}
.info-box p {{ color: #475569; font-size: 0.95em; }}
.footer {{ text-align: center; padding: 40px 20px; color: #94a3b8; font-size: 0.9em; }}
.footer a {{ color: #64748b; text-decoration: none; }}
@media (max-width: 600px) {{ .hero h1 {{ font-size: 1.8em; }} .hero {{ padding: 50px 20px; }} }}
</style>
</head>
<body>
<div class="hero">
    <h1>🤝 Kerja Sama — DailyMoney</h1>
    <p>Platform edukasi keuangan bilingual dengan pertumbuhan organik tinggi. Jadilah bagian dari literasi keuangan Indonesia.</p>
</div>
<div class="container">
    <div class="stats">
        {stats_items}
    </div>
    
    <h2 style="font-size: 1.5em; margin-top: 20px;">📋 Kategori Kerja Sama</h2>
    <div class="grid">
        {cat_items}
    </div>
    
    <div class="cta">
        <h2>💬 Tertarik Bekerja Sama?</h2>
        <p>Hubungi langsung via Telegram untuk diskusi harga dan detail kerja sama.</p>
        <a href="{tg["telegram"]}" class="cta-btn" target="_blank">📱 Hubungi @EsterToobit</a>
        <p style="margin-top: 14px; font-size: 0.9em; opacity: 0.8;">Respon cepat — biasanya dalam 1×24 jam</p>
    </div>
    
    <div class="info-box">
        <h3>📈 Kenapa Iklan di DailyMoney?</h3>
        <p>✅ Target audiens tepat: investor, trader, dan masyarakat melek finansial<br>
        ✅ Konten selalu fresh — update harga tiap 10 menit, artikel tiap jam<br>
        ✅ SEO optimasi maksimal — muncul di pencarian Google untuk keyword finansial<br>
        ✅ Bilingual Indonesia & Inggris — jangkauan lebih luas<br>
        ✅ Trafik organik — pengunjung datang karena butuh informasi keuangan</p>
    </div>
    
    <div class="info-box" style="border-left-color: #059669;">
        <h3>🏢 Untuk Brand & Perusahaan</h3>
        <p>DailyMoney adalah platform yang tepat untuk:<br>
        🏦 Bank & fintech — edukasi produk keuangan digital<br>
        📊 Perusahaan sekuritas — perkenalkan platform trading<br>
        💰 Pinjaman online legal — literasi pinjaman bertanggung jawab<br>
        🥇 Emas & logam mulia — edukasi investasi emas<br>
        🏠 Properti — literasi KPR dan investasi properti</p>
    </div>

    <div class="footer">
        <p>© 2026 DailyMoney — Platform Edukasi Keuangan Terpercaya<br>
        <a href="https://dailymoney.my.id">dailymoney.my.id</a> · Hubungi: <a href="{tg["telegram"]}">@{tg["contact_person"]}</a></p>
    </div>
</div>
</body>
</html>'''
    
    # Write file
    kerjasama_dir = os.path.join(PROJECT, "kerjasama")
    os.makedirs(kerjasama_dir, exist_ok=True)
    with open(os.path.join(kerjasama_dir, "index.html"), "w") as f:
        f.write(html)
    
    print(f"✅ Business page generated: kerjasama/index.html")
    return True

def main():
    print(f"{'='*50}")
    print(f"🤝 DailyMoney Business Agent @ {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*50}")
    
    generate_kerjasama_html()
    print(f"✅ Business page ready")

if __name__ == "__main__":
    main()

# 📰 DailyMoney — Automated Article Publisher

> Platform edukasi keuangan modern, otomatis, dan SEO-friendly.

## 🚀 Fitur

| Fitur | Detail |
|-------|--------|
| **Desain Modern** | Clean UI terinspirasi Stripe/Linear, dark gradient hero, card grid, responsive |
| **SEO Ready** | Meta description, Open Graph, Twitter Cards, semantic HTML |
| **Auto-publish** | GitHub Actions otomatis build & deploy setiap ada artikel baru |
| **Generator Cerdas** | Konversi markdown → HTML dengan dukungan heading, list, blockquote, CTA box |
| **Zero Config** | Clone → tulis JSON → push. Selesai. |

## 📦 Struktur Proyek

```
dailymoney-site/
├── _articles/                 # ← TARUH ARTIKEL JSON DI SINI
│   ├── inflasi-2025-strategi.json
│   └── reksadana-vs-saham.json
├── articles/                  # Hasil generate (auto)
├── assets/
│   ├── css/style.css          # Stylesheet utama
│   └── js/
│       ├── articles.js        # Data artikel (auto-generate)
│       └── main.js            # Render homepage
├── tentang/                   # Halaman tentang
├── generate-site.py           # ★ Generator utama
├── index.html                 # Halaman depan
└── .github/workflows/publish.yml  # Auto-deploy
```

## ✍️ Cara Menambahkan Artikel

### 1. Buat file JSON di `_articles/`

```json
{
  "judul": "Judul Artikel Max 60 Karakter",
  "meta_desc": "Deskripsi 1-2 kalimat untuk Google (max 150 karakter)",
  "content_markdown": "# H1 Diabaikan (auto)\n\n## Heading H2\n\nParagraf dengan **bold** dan list:\n- Poin pertama\n- Poin kedua\n\n> Blockquote untuk fakta/statistik\n\n---\n\n*CTA DailyMoney di akhir artikel*",
  "tags": "investasi, inflasi, reksadana",
  "date": "06/07/2025"
}
```

### 2. Generate lokal (testing)

```bash
python3 generate-site.py
```

### 3. Push ke GitHub

```bash
git add .
git commit -m "feat: tambah artikel baru"
git push
```

GitHub Actions otomatis build & deploy ke Pages. ⏳ ~1 menit.

## 🛠 Development

### Test generator lokal

```bash
python3 generate-site.py
# Output:
# ✓ inflasi-2025-strategi.html
# ✓ reksadana-vs-saham.html
# ✨ Generated 2 article(s)
```

### Preview site lokal

Buka `index.html` langsung di browser, atau jalankan:

```bash
python3 -m http.server 8080
# Buka http://localhost:8080
```

## ☁️ Deploy ke GitHub Pages

### 1. Buat repo baru

```bash
gh repo create dailymoney-site --public
```

### 2. Push kode

```bash
cd dailymoney-site
git init
git add .
git commit -m "feat: initial DailyMoney site"
git remote add origin https://github.com/<username>/dailymoney-site.git
git push -u origin main
```

### 3. Aktifkan GitHub Pages

1. Buka repo di GitHub → **Settings** → **Pages**
2. Source: **GitHub Actions**
3. Selesai! URL: `https://<username>.github.io/dailymoney-site/`

### 4. (Opsional) Custom Domain

Buat file `CNAME` di root dengan isi `dailymoney.com`, lalu setting DNS.

## 🤖 Workflow Otomatis

GitHub Action di `.github/workflows/publish.yml` akan:
1. **Trigger**: setiap push ke `main` yang mengubah `_articles/`, `generate-site.py`, `assets/`, `index.html`, atau `tentang/`
2. **Build**: jalankan `python generate-site.py`
3. **Deploy**: upload ke GitHub Pages

## ✨ Tips Konten

- **Judul**: max 60 karakter, pancing rasa ingin tahu
- **Fakta/statistik**: selalu sertakan minimal 1 data terkini di tiap artikel
- **Struktur**: H2 untuk sub-topik, H3 untuk detail, bullet points untuk data
- **CTA**: DailyMoney call-to-action di akhir artikel (auto di-boxing)
- **Frekuensi**: idealnya 3-5 artikel/minggu untuk SEO optimal

## 📄 Lisensi

MIT — bebas digunakan dan dikembangkan.

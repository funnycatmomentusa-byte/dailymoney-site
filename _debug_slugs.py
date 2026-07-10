import json, re, os

# Slug function as in internal-linker.py (line 41-44)
def make_slug(judul):
    s = judul.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s

# Slug function as in generate-site.py (line 176-179)
def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

# Check all EN article titles and what slugs they produce
en_dir = '_articles/en'
for fname in sorted(os.listdir(en_dir)):
    if not fname.endswith('.json'):
        continue
    with open(os.path.join(en_dir, fname)) as f:
        data = json.load(f)
    judul = data.get('judul', '')
    slug_linker = make_slug(judul)
    slug_gen = slugify(judul)
    if slug_linker != slug_gen:
        print(f'DIFF: {judul}')
        print(f'  linker: {slug_linker}')
        print(f'  gen:    {slug_gen}')
    # Check if the slug produces a file that exists
    html_file = f'en/articles/{slug_gen}.html'
    exists = 'EXISTS' if os.path.exists(html_file) else 'MISSING'
    if exists == 'MISSING':
        print(f'MISS: {html_file} (from slugify)')
        print(f'  title: {judul}')

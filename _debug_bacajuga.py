import json, os, re

ID_DIR = '_articles'
EN_DIR = '_articles/en'

def make_slug(judul):
    s = judul.lower().strip()
    s = re.sub(r'[^a-z0-9\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s).strip('-')
    return s

# Load all articles as internal linker does
articles = []
for d, lang in [(ID_DIR, "id"), (EN_DIR, "en")]:
    if os.path.exists(d):
        for fname in os.listdir(d):
            if fname.endswith(".json"):
                try:
                    with open(os.path.join(d, fname)) as f:
                        data = json.load(f)
                    data["_file"] = os.path.join(d, fname)
                    data["_lang"] = lang
                    slug = make_slug(data.get("judul", ""))
                    data["_slug"] = slug
                    articles.append(data)
                except Exception as e:
                    print(f"Error loading {fname}: {e}")

# For the ID article "Cara Mulai Investasi..."
target = None
for a in articles:
    if "Cara Mulai Investasi" in a.get("judul", ""):
        target = a
        break

if target:
    print(f"=== TARGET ARTICLE (ID) ===")
    print(f"Title: {target['judul']}")
    print(f"Lang: {target['_lang']}")
    print(f"Slug: {target['_slug']}")
    print(f"pair_id: {target.get('pair_id')}")
    
    # Now find what the linker would find as related
    print(f"\n=== RELATED ARTICLES FOUND BY LINKER ===")
    # Check for pair_id matching
    pair_id = target.get('pair_id')
    if pair_id:
        for a in articles:
            if a.get("pair_id") == pair_id and a["_slug"] != target["_slug"]:
                print(f"  PAIR_MATCH: {a['judul'][:60]}... lang={a['_lang']} slug={a['_slug']}")
    
    # Check for content of the Baca Juga section
    cm = target.get("content_markdown", "")
    if "Baca Juga" in cm:
        idx = cm.find("Baca Juga")
        print(f"\n=== ACTUAL BACA JUGA LINKS IN JSON ===")
        print(cm[idx:idx+500])
else:
    print("Target article not found!")

# Also find articles referenced by the Baca Juga links
print("\n=== SEARCHING FOR ARTICLES THAT WOULD CREATE EN LINKS ===")
for a in articles:
    slug = a["_slug"]
    if "reksadana-vs-saham" in slug:
        print(f"FOUND: {a['judul'][:70]} lang={a['_lang']} slug={slug}")
    if "investasi-09-jul" in slug:
        print(f"FOUND: {a['judul'][:70]} lang={a['_lang']} slug={slug}")
    if "idx-menyediakan-data-pasar-investasi" in slug:
        print(f"FOUND: {a['judul'][:70]} lang={a['_lang']} slug={slug}")

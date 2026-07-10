#!/usr/bin/env python3
"""Full article audit: title sync, markdown, weird content, duplicates."""
import json, os, re

articles_dir = '/root/workspace/dailymoney-site/_articles'
issues = []

for d in [articles_dir, f'{articles_dir}/en']:
    lang = 'EN' if '/en/' in d else 'ID'
    for f in sorted(os.listdir(d)):
        if not f.endswith('.json') or f.startswith('.'):
            continue
        fp = os.path.join(d, f)
        with open(fp) as fh:
            a = json.load(fh)

        slug = a.get('slug', '')
        judul = a.get('judul', '')
        c = a.get('content_markdown', '')
        meta = a.get('meta_desc', '')
        img = a.get('image_url', '')
        caption = a.get('image_caption', '')

        # 1. Title-content mismatch
        title_words = set(re.findall(r'\b\w{4,}\b', judul.lower()))
        content_lower = c.lower()
        missing = [w for w in title_words if w not in content_lower]
        if title_words and len(missing) > len(title_words) * 0.5:
            issues.append(f"TITLE_MISMATCH [{lang}] {slug[:35]}: missing {missing[:3]}")

        # 2. Markdown artifacts
        if '**' in c:
            issues.append(f"MARKDOWN_BOLD [{lang}] {slug[:35]}")
        if re.search(r'(?<!\*)\*([^*\n]{2,})\*(?!\*)', c):
            issues.append(f"MARKDOWN_ITALIC [{lang}] {slug[:35]}")
        if re.search(r'`[^`]+`', c):
            issues.append(f"MARKDOWN_CODE [{lang}] {slug[:35]}")
        if re.search(r'!\[', c):
            issues.append(f"MARKDOWN_IMG [{lang}] {slug[:35]}")

        # 3. Weird content
        if 'undefined' in c.lower() or 'null' in c.lower():
            issues.append(f"PLACEHOLDER [{lang}] {slug[:35]}")
        if '\\n' in c and '\\n' not in repr(c):
            issues.append(f"LITERAL_BACKSLASH_N [{lang}] {slug[:35]}")

        # 4. Title overlap
        content_words = set(re.findall(r'\b\w{4,}\b', content_lower))
        if title_words:
            overlap = len(title_words & content_words) / len(title_words)
            if overlap < 0.3:
                issues.append(f"LOW_OVERLAP [{lang}] {slug[:35]}: {overlap:.0%}")

        # 5. Image
        if not img:
            issues.append(f"NO_IMAGE [{lang}] {slug[:35]}")
        elif '//' in img.replace('https://', ''):
            issues.append(f"DOUBLE_SLASH [{lang}] {slug[:35]}")

        # 6. Caption
        if caption and 'sumber: dokumentasi' not in caption.lower():
            issues.append(f"BAD_CAPTION [{lang}] {slug[:35]}: {caption[:50]}")

        # 7. Length
        if len(c) < 2500:
            issues.append(f"SHORT [{lang}] {slug[:35]}: {len(c)} chars")

        # 8. Meta desc
        if len(meta) > 160:
            issues.append(f"LONG_META [{lang}] {slug[:35]}: {len(meta)} chars")
        if len(meta) < 120:
            issues.append(f"SHORT_META [{lang}] {slug[:35]}: {len(meta)} chars")

# Duplicate intros
seen = {}
dups = 0
total = 0
for d in [articles_dir, f'{articles_dir}/en']:
    for f in sorted(os.listdir(d)):
        if not f.endswith('.json') or f.startswith('.'):
            continue
        total += 1
        with open(os.path.join(d, f)) as fh:
            a = json.load(fh)
        c = a.get('content_markdown', '')
        intro = c.strip()[:80].lower()
        if intro in seen:
            dups += 1
            issues.append(f"DUP_INTRO [{a.get('slug','')[:35]}] same as {seen[intro]}")
        else:
            seen[intro] = a.get('slug', '')[:35]

print("=" * 60)
print("ARTICLE DEEP AUDIT RESULTS")
print("=" * 60)
for i in sorted(issues):
    print(f"  {i}")
print(f"\nTotal articles: {total}")
print(f"Total issues: {len(issues)}")
if not issues:
    print("ALL ARTICLES CLEAN")

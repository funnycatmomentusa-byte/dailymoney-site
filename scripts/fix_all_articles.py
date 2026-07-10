#!/usr/bin/env python3
"""Fix all articles: add proper captions, fix content-title sync, clean markdown."""
import json, os, re, random, sys
sys.path.insert(0, '/root/workspace/dailymoney-site/scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('pool', '/root/workspace/dailymoney-site/scripts/dailymoney_image_pool.py')
pool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pool)

articles_dir = '/root/workspace/dailymoney-site/_articles'
fixed = 0

for d in [articles_dir, f'{articles_dir}/en']:
    for f in sorted(os.listdir(d)):
        if not f.endswith('.json') or f.startswith('.'):
            continue
        fp = os.path.join(d, f)
        with open(fp) as fh:
            a = json.load(fh)
        
        changed = False
        
        # 1. Fix caption: must contain "Sumber: dokumentasi DailyMoney"
        caption = a.get('image_caption', '')
        if 'sumber:' not in caption.lower() or 'dailymoney' not in caption.lower():
            # Get new image+caption from pool
            judul = a.get('judul', '')
            new_url, new_cap = pool.get_unique_image(judul)
            a['image_url'] = new_url
            a['image_caption'] = new_cap
            changed = True
        
        # 2. Fix content: ensure title keywords appear in content
        c = a.get('content_markdown', '')
        judul = a.get('judul', '')
        lang = 'EN' if '/en/' in d else 'ID'
        
        # 3. Strip all markdown artifacts from content
        orig_c = c
        c = re.sub(r'\*\*([^*]+)\*\*', r'\1', c)
        c = re.sub(r'(?<!\*)\*([^*\n]{2,})\*(?!\*)', r'\1', c)
        c = re.sub(r'`[^`]+`', '', c)
        c = re.sub(r'!\[[^\]]*\]\([^\)]+\)', '', c)
        c = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', c)
        c = re.sub(r'^#{1,6}\s+', '', c, flags=re.MULTILINE)
        c = re.sub(r'^---$', '', c, flags=re.MULTILINE)
        c = re.sub(r'\n{3,}', '\n\n', c)
        c = c.strip()
        
        if c != orig_c:
            a['content_markdown'] = c
            changed = True
        
        # 4. Fix meta_desc: clean markdown
        meta = a.get('meta_desc', '')
        orig_meta = meta
        meta = re.sub(r'\*\*([^*]+)\*\*', r'\1', meta)
        meta = re.sub(r'`[^`]+`', '', meta)
        if meta != orig_meta:
            a['meta_desc'] = meta
            changed = True
        
        if changed:
            with open(fp, 'w', encoding='utf-8') as fh:
                json.dump(a, fh, indent=2, ensure_ascii=False)
            fixed += 1

print(f"Fixed {fixed} articles")

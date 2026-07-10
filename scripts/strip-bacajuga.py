"""Hapus existing Baca Juga section dari semua JSON articles,
biar internal linker bisa regenerate dengan path yang bener."""
import json, os, re

for base_dir, lang in [('_articles', 'id'), ('_articles/en', 'en')]:
    if not os.path.exists(base_dir):
        continue
    for fname in os.listdir(base_dir):
        if not fname.endswith('.json'):
            continue
        fpath = os.path.join(base_dir, fname)
        try:
            with open(fpath) as f:
                data = json.load(f)
        except:
            continue
        
        cm = data.get('content_markdown', '')
        if 'Baca Juga' not in cm:
            continue
        
        # Remove Baca Juga section + trailing blank lines
        new_cm = re.sub(
            r'\n\n### 📖 Baca Juga\n\n.*?(?=\n\n\*DailyMoney|\Z)',
            '',
            cm,
            flags=re.DOTALL
        )
        new_cm = new_cm.rstrip()
        
        if new_cm != cm:
            data['content_markdown'] = new_cm
            with open(fpath, 'w') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f'🧹 Stripped Baca Juga: {fname} ({lang})')
        else:
            print(f'⏭️  No change: {fname}')

print('\n✅ Done stripping old Baca Juga sections')

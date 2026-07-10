#!/usr/bin/env python3
"""DailyMoney Article Validator — checks article quality, uniqueness, and structure."""

import json, os, sys, re, glob
from datetime import date

PROJECT = '/root/workspace/dailymoney-site'
ARTICLES_DIR = os.path.join(PROJECT, '_articles')

CHINESE_RE = re.compile(r'[\u4e00-\u9fff]')
SPAM_PATTERNS = [
    r'Microsoft\s+Community', r'Floor\s+Plan\s+Creator', r'Visit\s+Flo',
    r'Cod\s+mobile', r'Call\s+of\s+Duty', r'split\s+screen',
    r'changelog\s+\d+', r'Kompasiana\.com\.\s+\d+\s+weeks?\s+ago',
    r'wondering\s+is\s+there\s+any\s+way',
]


def check_article(filepath):
    """Validate a single article. Returns (pass_bool, list_of_reasons)."""
    reasons = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        return False, [f"JSON parse error: {e}"]
    except Exception as e:
        return False, [f"File read error: {e}"]

    content = data.get('content_markdown', '')
    image_url = data.get('image_url', '')
    image_caption = data.get('image_caption', '')
    meta_desc = data.get('meta_desc', '')
    tags = data.get('tags', '')
    judul = data.get('judul', '')

    # 1. Content length >= 2500
    if len(content) < 2500:
        reasons.append(f"content_markdown too short: {len(content)} chars (min 2500)")

    # 2. No Chinese characters
    if CHINESE_RE.search(content):
        chinese_matches = CHINESE_RE.findall(content)
        reasons.append(f"Contains Chinese characters: {''.join(chinese_matches[:5])}")

    # 3. No spam patterns
    check_text = f"{content} {judul} {meta_desc}"
    for pat in SPAM_PATTERNS:
        if re.search(pat, check_text, re.IGNORECASE):
            reasons.append(f"Spam pattern detected: {pat}")

    # 4. Valid markdown — at least 2 H2 headers
    h2_count = len(re.findall(r'^## [^#]', content, re.MULTILINE))
    if h2_count < 2:
        reasons.append(f"Insufficient H2 headers: {h2_count} (min 2)")

    # 5. meta_desc length 120-160
    if len(meta_desc) < 120:
        reasons.append(f"meta_desc too short: {len(meta_desc)} chars (min 120)")
    elif len(meta_desc) > 160:
        reasons.append(f"meta_desc too long: {len(meta_desc)} chars (max 160)")

    # 6. image_caption not empty
    if not image_caption or not image_caption.strip():
        reasons.append("image_caption is empty")

    # 7. tags not empty
    if not tags or not tags.strip():
        reasons.append("tags is empty")

    return len(reasons) == 0, reasons


def run_validation():
    """Run full validation across all articles. Returns exit code."""
    print("=" * 70)
    print("DailyMoney Article Validator Report")
    print(f"Generated: {date.today().isoformat()}")
    print("=" * 70)

    # Collect articles
    article_files = []
    article_langs = {}

    for f in sorted(glob.glob(os.path.join(ARTICLES_DIR, '*.json'))):
        if os.path.basename(f).startswith('_'):
            continue
        article_files.append(f)
        article_langs[f] = 'id'

    en_dir = os.path.join(ARTICLES_DIR, 'en')
    if os.path.isdir(en_dir):
        for f in sorted(glob.glob(os.path.join(en_dir, '*.json'))):
            article_files.append(f)
            article_langs[f] = 'en'

    print(f"\nTotal articles found: {len(article_files)}")
    print(f"  Indonesian: {sum(1 for v in article_langs.values() if v == 'id')}")
    print(f"  English:    {sum(1 for v in article_langs.values() if v == 'en')}")

    # Validate each
    pass_list = []
    fail_list = []
    image_urls = []
    content_lengths = []

    for filepath in article_files:
        rel = os.path.relpath(filepath, PROJECT)
        passed, reasons = check_article(filepath)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            content_lengths.append(len(data.get('content_markdown', '')))
            image_urls.append((data.get('image_url', ''), rel))
        except Exception:
            pass

        status = "PASS" if passed else "FAIL"
        print(f"\n  [{status}] {rel}")
        if not passed:
            fail_list.append((rel, reasons))
            for r in reasons:
                print(f"         - {r}")
        else:
            pass_list.append(rel)

    # Image duplication report
    print("\n" + "=" * 70)
    print("IMAGE DUPLICATION REPORT")
    print("=" * 70)

    url_map = {}
    for url, rel in image_urls:
        url_map.setdefault(url, []).append(rel)

    duplicates = {u: files for u, files in url_map.items() if len(files) > 1}
    unique_count = len(url_map)

    if duplicates:
        print(f"\n  UNIQUE IMAGES: {unique_count}")
        print(f"  DUPLICATE GROUPS: {len(duplicates)}")
        for url, files in duplicates.items():
            print(f"\n  Used {len(files)} times:")
            print(f"    URL: {url[:70]}...")
            for f in files:
                print(f"    - {f}")
    else:
        print(f"\n  All {unique_count} images are unique — no duplicates found!")

    # Content length distribution
    print("\n" + "=" * 70)
    print("CONTENT LENGTH DISTRIBUTION")
    print("=" * 70)

    avg_len = sum(content_lengths) / len(content_lengths) if content_lengths else 0
    if content_lengths:
        min_len = min(content_lengths)
        max_len = max(content_lengths)
        under_2500 = sum(1 for l in content_lengths if l < 2500)
        print(f"\n  Min:    {min_len} chars")
        print(f"  Max:    {max_len} chars")
        print(f"  Avg:    {avg_len:.0f} chars")
        print(f"  Under 2500: {under_2500} articles")

    # Final summary
    total = len(article_files)
    passed_count = len(pass_list)
    failed_count = len(fail_list)

    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"  Total articles:  {total}")
    print(f"  PASS:            {passed_count}")
    print(f"  FAIL:            {failed_count}")
    print(f"  Unique images:   {unique_count}")
    print(f"  Duplicate groups: {len(duplicates)}")
    if content_lengths:
        print(f"  Content avg:     {avg_len:.0f} chars")
    print("=" * 70)

    if failed_count > 0:
        print(f"\nRESULT: {failed_count} article(s) FAILED validation.")
        return 1
    else:
        print(f"\nRESULT: All {total} articles PASSED validation.")
        return 0


if __name__ == '__main__':
    sys.exit(run_validation())

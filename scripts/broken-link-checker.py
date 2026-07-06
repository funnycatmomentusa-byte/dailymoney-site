#!/usr/bin/env python3
"""DailyMoney — Auto Broken Link Checker Agent
Scans all pages for broken links and reports them."""
import urllib.request, ssl, re, json, os, sys
from urllib.parse import urljoin

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASE = "https://dailymoney.my.id"
LOG = os.path.expanduser("~/.hermes/logs/broken-links.log")
os.makedirs(os.path.dirname(LOG), exist_ok=True)

def get(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DailyMoneyBot/1.0"})
        resp = urllib.request.urlopen(req, context=ctx, timeout=10)
        return resp.read().decode(), resp.status
    except Exception as e:
        return None, str(e)

# Get sitemap
content, status = get(f"{BASE}/sitemap.xml")
if not content:
    print(f"❌ Cannot fetch sitemap: {status}")
    sys.exit(1)

urls = re.findall(r'<loc>(.*?)</loc>', content)
broken = []

for url in urls:
    _, status = get(url)
    if isinstance(status, int) and status == 200:
        pass
    elif isinstance(status, str):
        broken.append((url, status))
    else:
        broken.append((url, f"HTTP {status}"))

with open(LOG, 'a') as f:
    f.write(f"\n{'='*60}\n")
    f.write(f"[{__import__('datetime').datetime.now().isoformat()}]\n")
    if broken:
        f.write(f"❌ {len(broken)} broken links found:\n")
        for url, err in broken:
            f.write(f"  - {url}: {err}\n")
        print(f"❌ {len(broken)} broken links found")
    else:
        f.write("✅ No broken links!\n")
        print(f"✅ No broken links! ({len(urls)} URLs checked)")

print(f"📄 Log written to {LOG}")

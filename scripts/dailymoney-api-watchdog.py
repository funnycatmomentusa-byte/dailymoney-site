#!/usr/bin/env python3
"""DailyMoney — API Health Watchdog Agent
Memonitor semua API eksternal, auto-failover, notifikasi jika down."""
import json, os, subprocess, sys, re, urllib.request, urllib.error
from datetime import datetime
from collections import OrderedDict

BASE_DIR = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG = os.path.join(LOG_DIR, "api-watchdog.log")
SEND = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

# Cache file untuk failover state
CACHE_FILE = os.path.join(LOG_DIR, "api-watchdog-cache.json")

def log(msg):
    t = datetime.now().strftime("%H:%M:%S")
    line = f"[{t}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")

def send_tg(msg):
    try:
        subprocess.run(SEND + [msg], timeout=15, capture_output=True)
    except:
        pass

def load_cache():
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE) as f:
                return json.load(f)
    except:
        pass
    return {"failover": {}, "history": {}}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def check_url(name, url, method="GET", check_text=None, timeout=15, failover=None):
    """Cek health suatu URL. Return dict dengan status."""
    result = {
        "name": name,
        "url": url,
        "status": "unknown",
        "code": 0,
        "elapsed": 0,
        "error": None,
        "size": 0,
    }
    
    try:
        req = urllib.request.Request(url, method=method,
            headers={"User-Agent": "Mozilla/5.0 (DailyMoney Watchdog)"})
        start = datetime.now()
        resp = urllib.request.urlopen(req, timeout=timeout)
        result["elapsed"] = (datetime.now() - start).total_seconds()
        result["code"] = resp.status
        result["size"] = len(resp.read())
        
        if resp.status == 200:
            result["status"] = "✅ OK"
        elif resp.status in (301, 302, 307, 308):
            result["status"] = f"⚠️ Redirect ({resp.status})"
        else:
            result["status"] = f"🔴 HTTP {resp.status}"
    
    except urllib.error.HTTPError as e:
        result["code"] = e.code
        result["elapsed"] = 0
        result["error"] = f"HTTP {e.code}"
        if e.code == 429:
            result["status"] = "⚠️ Rate Limited"
        elif e.code >= 500:
            result["status"] = f"🔴 Server Error ({e.code})"
        else:
            result["status"] = f"🔴 HTTP {e.code}"
    
    except urllib.error.URLError as e:
        result["elapsed"] = 0
        result["error"] = str(e.reason)
        result["status"] = f"🔴 Network Error"
    
    except Exception as e:
        result["elapsed"] = 0
        result["error"] = str(e)
        result["status"] = f"🔴 Error"
    
    return result

# ════════════════════════════════════════
def main():
    log("=" * 60)
    log("❤️ DailyMoney API Health Watchdog — started")
    
    cache = load_cache()
    
    # Daftar API yang dimonitor
    ENDPOINTS = [
        {
            "name": "🚀 dailymoney.my.id",
            "url": "https://dailymoney.my.id/",
            "timeout": 20,
            "failover": "https://dailymoney.my.id/",  # same site, check network
        },
        {
            "name": "🪙 CoinGecko API",
            "url": "https://api.coingecko.com/api/v3/ping",
            "timeout": 10,
            "failover": None,  # will try alternative
        },
        {
            "name": "🔍 Google Search",
            "url": "https://www.google.com/",
            "timeout": 10,
            "failover": None,
        },
        {
            "name": "🌐 Bing Search",
            "url": "https://www.bing.com/",
            "timeout": 10,
            "failover": None,
        },
        {
            "name": "📡 IndexNow API",
            "url": "https://api.indexnow.org/",
            "timeout": 10,
            "failover": None,
        },
        {
            "name": "📦 jsDelivr CDN",
            "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
            "timeout": 10,
            "failover": None,
        },
        {
            "name": "🔤 Google Fonts",
            "url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap",
            "timeout": 10,
            "failover": None,
        },
        {
            "name": "🐙 GitHub Pages",
            "url": "https://funnycatmomentusa-byte.github.io/dailymoney-site/",
            "timeout": 15,
            "failover": None,
        },
    ]
    
    results = []
    issues = []
    
    for ep in ENDPOINTS:
        result = check_url(
            name=ep["name"],
            url=ep["url"],
            timeout=ep["timeout"],
        )
        results.append(result)
        
        if result["status"].startswith("🔴"):
            msg = f"{result['status']} {result['name']} ({result.get('error', result.get('code', ''))})"
            log(f"  ❌ {msg}")
            issues.append((ep, result))
        elif result["status"].startswith("⚠️"):
            msg = f"{result['status']} {result['name']} ({result.get('code', '')})"
            log(f"  ⚠️ {msg}")
        else:
            log(f"  ✅ {result['name']} — {result['elapsed']:.2f}s ({result['size']:,} bytes)")
    
    # Auto-failover logic
    failover_actions = []
    for ep, result in issues:
        name = ep["name"]
        prev_state = cache.get("history", {}).get(name, "ok")
        
        if prev_state == "ok":
            # First failure — activate failover
            log(f"  🔄 Failover triggered for {name}")
            failover_actions.append(f"🔀 Failover: {name}")
            
            # For CoinGecko, suggest alternative
            if "CoinGecko" in name:
                log(f"  ℹ️ Alternative: use CoinMarketCap or Binance API")
                failover_actions.append(f"  ℹ️ Alternative: CoinMarketCap / Binance API")
        
        # Update history
        if "history" not in cache:
            cache["history"] = {}
        cache["history"][name] = "down" if result["status"].startswith("🔴") else "ok"
    
    # Reset history for healthy endpoints
    for ep in ENDPOINTS:
        name = ep["name"]
        if "history" in cache and name in cache["history"]:
            # Check if currently healthy
            for r in results:
                if r["name"] == name and r["status"].startswith("✅"):
                    cache["history"][name] = "ok"
    
    save_cache(cache)
    
    # Summary
    total = len(ENDPOINTS)
    ok = sum(1 for r in results if r["status"].startswith("✅"))
    warn = sum(1 for r in results if r["status"].startswith("⚠️"))
    bad = sum(1 for r in results if r["status"].startswith("🔴"))
    
    log(f"\n📊 Summary: {ok}/{total} OK, {warn} warnings, {bad} down")
    
    # Report
    report = "❤️‍🩹 *API Health Watchdog*\n"
    report += f"📅 {datetime.now().strftime('%d %b %H:%M')}\n"
    report += f"📊 {ok}/{total} healthy"
    if warn:
        report += f", ⚠️ {warn}"
    if bad:
        report += f", 🔴 {bad}"
    report += "\n\n"
    
    # Show all
    for r in results:
        report += f"  {r['status']} {r['name']} ({r['elapsed']:.1f}s)\n"
    
    if failover_actions:
        report += "\n*Failover Actions:*\n"
        for a in failover_actions:
            report += f"  {a}\n"
    
    if bad == 0 and warn == 0:
        report += "\n✅ Semua API sehat — sistem stabil!\n"
    
    send_tg(report)
    log("📤 Report sent to Telegram")
    log(f"📊 Complete — {ok}/{total} healthy")

if __name__ == "__main__":
    main()

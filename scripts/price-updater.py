#!/usr/bin/env python3
"""DailyMoney — Market Price Updater
Updates _price_data.json independently from site generation.
Runs every 10 minutes via cronjob.
"""
import json, os, urllib.request, sys
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def fetch_yahoo_finance(ticker):
    """Fetch current price from Yahoo Finance (same as generate-site.py)."""
    import ssl
    ctx = ssl._create_unverified_context()
    
    urls = [
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=1d&interval=1m",
        f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}?range=1d&interval=1m",
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    
    for url in urls:
        try:
            req = urllib.request.Request(url, headers=headers)
            resp = urllib.request.urlopen(req, context=ctx, timeout=10)
            data = json.loads(resp.read().decode())
            meta = data.get('chart', {}).get('result', [{}])[0].get('meta', {})
            quote = data.get('chart', {}).get('result', [{}])[0].get('indicators', {}).get('quote', [{}])[0]
            close = quote.get('close', [])
            prev_close = meta.get('chartPreviousClose')
            current = None
            
            for c in reversed(close):
                if c is not None:
                    current = c
                    break
            
            if current and prev_close:
                change = ((current - prev_close) / prev_close) * 100
                return {'price': round(current, 2), 'change': round(change, 2)}
        except:
            continue
    return None


def fetch_all_prices():
    """Fetch all market prices and save to _price_data.json."""
    symbols = {
        'BTC': 'BTC-USD',
        'ETH': 'ETH-USD',
        'IHSG': '^JKSE',
        'XAU': 'GC=F',
        'USDIDR': 'USDIDR=X',
        'TLKM': 'TLKM.JK',
        'BBRI': 'BBRI.JK',
        'BBCA': 'BBCA.JK',
        'ASII': 'ASII.JK',
        'UNVR': 'UNVR.JK',
        'BMRI': 'BMRI.JK',
        'SPX': '^GSPC',
    }
    
    prices = {}
    fetched_count = 0
    
    # Load existing prices for fallback
    try:
        with open(os.path.join(BASE_DIR, '_price_data.json')) as f:
            existing = json.load(f).get('data', {})
    except:
        existing = {}
    
    for sym, ticker in symbols.items():
        print(f"  Fetching {sym}...", end=' ')
        data = fetch_yahoo_finance(urllib.parse.quote(ticker, safe='') if sym == 'IHSG' else ticker)
        if data:
            prices[sym] = data
            fetched_count += 1
            print(f"✅ {data['price']} ({data['change']:+.2f}%)")
        elif sym in existing and existing[sym].get('price') is not None:
            # Keep old value if fetch fails
            prices[sym] = existing[sym]
            print(f"⚠ using cached ({existing[sym]['price']})")
        else:
            print(f"❌ failed")
    
    # Save _price_data.json
    output = {'data': prices, 'updated': datetime.now().isoformat()}
    price_path = os.path.join(BASE_DIR, '_price_data.json')
    with open(price_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    # Also save IHSG separately
    if 'IHSG' in prices:
        ihsg_path = os.path.join(BASE_DIR, 'assets', 'data', 'ihsg.json')
        with open(ihsg_path, 'w') as f:
            json.dump(prices['IHSG'], f)
    
    print(f"\n📊 Updated {fetched_count}/{len(symbols)} prices → _price_data.json")
    return fetched_count


if __name__ == '__main__':
    import urllib.parse
    print(f"📈 DailyMoney Price Updater @ {datetime.now().strftime('%H:%M:%S')}")
    fetch_all_prices()

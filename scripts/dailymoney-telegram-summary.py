#!/usr/bin/env python3
"""DailyMoney — Send market summary to Telegram every 30 min."""
import json, os, sys
from datetime import datetime

# Paths
PRICE_FILE = "/root/workspace/dailymoney-site/_price_data.json"
SEND_SCRIPT = "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py"

# Read price data
if not os.path.exists(PRICE_FILE):
    msg = "⚠️ Data harga belum tersedia"
    os.system(f'python3 {SEND_SCRIPT} --message "{msg}"')
    sys.exit(1)

with open(PRICE_FILE) as f:
    data = json.load(f)

prices = data.get("prices", data) if isinstance(data, dict) else {}

# Build message
lines = ["📊 *DailyMoney — Update Pasar*", f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}", ""]

symbols = {
    "BTC": "₿ Bitcoin",
    "ETH": "⟠ Ethereum",
    "IHSG": "🇮🇩 IHSG",
    "XAU": "🥇 Emas",
    "USDIDR": "💵 USD/IDR",
    "TLKM": "📡 TLKM",
    "BBRI": "🏦 BBRI",
    "BBCA": "🏦 BBCA",
    "ASII": "🚗 ASII",
    "UNVR": "🧴 UNVR",
    "BMRI": "🏦 BMRI",
    "SPX": "🇺🇸 S&P 500",
}

for key, label in symbols.items():
    if key in prices:
        p = prices[key]
        price = p.get("price", p.get("harga", "?"))
        change = p.get("change", p.get("perubahan", p.get("change_pct", "")))
        if change:
            sign = "📈" if float(change) >= 0 else "📉"
            lines.append(f"{label}: *{price}* {sign} {change}%")
        else:
            lines.append(f"{label}: *{price}*")

# Site URL
lines.append("")
lines.append("🌐 dailymoney.my.id")

msg = "\n".join(lines)

# Escape for shell
msg_escaped = msg.replace("'", "'\\''")
os.system(f'python3 {SEND_SCRIPT} --message \'{msg_escaped}\'')

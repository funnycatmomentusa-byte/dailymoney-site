#!/usr/bin/env python3
"""DailyMoney — Notification Relay System
Semua agent pakai utility ini untuk kirim notifikasi ke Telegram.
Output: stdout (untuk cron log) + Telegram (jika ada pesan penting)."""
import os, sys, subprocess, json
from datetime import datetime

# ── Config ──
SEND_SCRIPT = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]
CHAT_ID = "746951685"

def send_telegram(message, silent=False):
    """Kirim pesan ke Telegram @dailymoneyfnd_bot"""
    try:
        full_msg = f"{message}"
        subprocess.run(SEND_SCRIPT + [full_msg], timeout=15, capture_output=True)
        return True
    except Exception as e:
        print(f"  ⚠️  Telegram send failed: {e}")
        return False

def notify(agent_name, status, details=""):
    """Format notifikasi standar untuk semua agent"""
    icons = {"ok": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    icon = icons.get(status, "🤖")
    msg = f"{icon} *{agent_name}*"
    if details:
        msg += f"\n{details}"
    msg += f"\n📅 {datetime.now().strftime('%d %b %H:%M')}"
    return msg

def report(agent_name, items, send_tg=True):
    """Buat laporan lengkap + kirim ke Telegram"""
    now = datetime.now().strftime('%d %b %H:%M')
    lines = [f"🤖 *{agent_name}*", f"📅 {now}", ""]
    
    ok_items = [x for x in items if x.get("status") == "ok"]
    warn_items = [x for x in items if x.get("status") == "warning"]
    err_items = [x for x in items if x.get("status") == "error"]
    
    if err_items:
        lines.append(f"❌ *{len(err_items)} masalah:*")
        for item in err_items:
            lines.append(f"  ❌ {item.get('msg', '')}")
        lines.append("")
    
    if warn_items:
        for item in warn_items:
            lines.append(f"  ⚠️  {item.get('msg', '')}")
        lines.append("")
    
    if ok_items:
        lines.append(f"✅ *{len(ok_items)} berhasil:*")
        for item in ok_items:
            lines.append(f"  ✅ {item.get('msg', '')}")
    
    report_text = "\n".join(lines)
    print(report_text)
    
    if send_tg and (err_items or warn_items):
        tg_msg = f"{'❌' if err_items else '⚠️'} *{agent_name}*\n"
        for item in (err_items + warn_items):
            tg_msg += f"{item.get('msg', '')}\n"
        tg_msg += f"\n📅 {now}"
        send_telegram(tg_msg)
    
    return report_text

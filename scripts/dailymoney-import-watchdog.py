#!/usr/bin/env python3
"""DailyMoney — Import Watchdog Agent
Menjaga semua dependency Python tetap sehat.
Jalan tiap 1 jam, lewat cron.
Hanya kirim pesan kalau ada masalah."""
import os, sys, subprocess, json
from datetime import datetime

PROJECT = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG = os.path.join(LOG_DIR, "import-watchdog.log")

SEND_SCRIPT = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

# ── Critical imports yang WAJIB bisa di-resolve ──
CRITICAL_IMPORTS = {
    "ddgs": ["DDGS"],
    "duckduckgo_search": ["DDGS"],
    "requests": None,
    "urllib": None,  # stdlib, always fine
}

# ── Mapping modul yang sudah ganti nama ──
RENAME_MAP = {
    "ddgs": "duckduckgo_search",
}

# ── Files yang perlu dicek ──
CRITICAL_FILES = [
    "search_news.py", "search_news2.py", "search_news3.py",
    "search_news4.py", "search_news5.py", "search_news6.py",
    "get_forex_data.py", "get_forex_data2.py", "get_forex_data3.py",
    "generate-site.py",
]


def log(msg):
    t = datetime.now().strftime("%H:%M:%S")
    line = f"[{t}] {msg}"
    print(line)
    with open(LOG, "a") as f:
        f.write(line + "\n")


def send_alert(msg):
    try:
        subprocess.run(SEND_SCRIPT + [msg], timeout=15)
    except Exception:
        pass


def check_import_subprocess(module_name):
    """Cek import via subprocess — isolated, akurat, zero false positive."""
    try:
        r = subprocess.run(
            [sys.executable, "-c", f"import {module_name}"],
            capture_output=True, text=True, timeout=10
        )
        return r.returncode == 0
    except Exception:
        return False


def fix_and_install(missing_module):
    """Coba install modul yang hilang + rewrite import statement kalau perlu."""
    # Cek rename map dulu
    if missing_module in RENAME_MAP:
        target = RENAME_MAP[missing_module]
        if check_import_subprocess(target):
            log(f"  ✅ {missing_module} → {target} sudah terinstall, fix import statement...")
            return "rename", target
        # Coba install target
        log(f"  🔧 Installing {target}...")
        r = subprocess.run(
            ["pip3", "install", "--break-system-packages", target],
            capture_output=True, text=True, timeout=30
        )
        if r.returncode == 0 and check_import_subprocess(target):
            log(f"  ✅ {target} installed")
            return "rename", target
        return None

    # Install langsung
    log(f"  🔧 Installing {missing_module}...")
    r = subprocess.run(
        ["pip3", "install", "--break-system-packages", missing_module],
        capture_output=True, text=True, timeout=30
    )
    if r.returncode == 0 and check_import_subprocess(missing_module):
        log(f"  ✅ {missing_module} installed & verified")
        return "ok", missing_module
    return None


def rewrite_imports(filepath, old_mod, new_mod):
    """Rewrite semua import dari old_mod ke new_mod di file."""
    try:
        with open(filepath) as f:
            content = f.read()
        changes = 0
        for pattern in [f"from {old_mod} import", f"import {old_mod}"]:
            if pattern in content:
                content = content.replace(pattern, pattern.replace(old_mod, new_mod))
                changes += 1
        if changes > 0:
            with open(filepath, 'w') as f:
                f.write(content)
            log(f"  ✅ Rewrote {changes} import(s) in {os.path.basename(filepath)}: {old_mod} → {new_mod}")
            return True
    except Exception as e:
        log(f"  ❌ Failed to rewrite {filepath}: {e}")
    return False


def main():
    print(f"{'='*50}")
    print(f"👁️  Import Watchdog @ {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"{'='*50}")

    issues = []
    fixes = []

    # ── 1. Check all critical imports ──
    for mod in CRITICAL_IMPORTS:
        if not check_import_subprocess(mod):
            log(f"❌ Critical import fails: {mod}")
            result = fix_and_install(mod)
            if result:
                action, target = result
                if action == "rename":
                    # Rewrite imports in all critical files
                    for fname in CRITICAL_FILES:
                        fpath = os.path.join(PROJECT, fname)
                        if os.path.exists(fpath):
                            if rewrite_imports(fpath, mod, target):
                                fixes.append(f"{fname}: {mod}→{target}")
                fixes.append(f"installed {mod}")
            else:
                issues.append(f"❌ Cannot fix: {mod}")

    # ── 2. Check project files have correct imports ──
    for fname in CRITICAL_FILES:
        fpath = os.path.join(PROJECT, fname)
        if not os.path.exists(fpath):
            continue
        try:
            with open(fpath) as f:
                content = f.read()
            # Check for known bad patterns
            for old_mod, new_mod in RENAME_MAP.items():
                if f"from {old_mod} import" in content:
                    # Only flag if new_mod is importable
                    if check_import_subprocess(new_mod):
                        log(f"⚠️  {fname} still uses {old_mod}, should be {new_mod}")
                        if rewrite_imports(fpath, old_mod, new_mod):
                            fixes.append(f"{fname}: {old_mod}→{new_mod}")
        except Exception as e:
            issues.append(f"❌ Error reading {fname}: {e}")

    # ── 3. Check duckduckgo_search version ──
    try:
        r = subprocess.run(
            [sys.executable, "-c", "import duckduckgo_search; print(getattr(duckduckgo_search, '__version__', '?'))"],
            capture_output=True, text=True, timeout=5
        )
        dg_version = r.stdout.strip()
        log(f"ℹ️  duckduckgo_search version: {dg_version}")
    except Exception:
        pass

    # ── Report ──
    status_lines = ["👁️ *Import Watchdog Report*", f"📅 {datetime.now().strftime('%d %b %H:%M')}", ""]

    if not issues:
        status_lines.append("✅ *Semua import sehat*")
    else:
        status_lines.append(f"❌ *{len(issues)} masalah:*")
        for i in issues:
            status_lines.append(i)

    if fixes:
        status_lines.append("")
        status_lines.append(f"🔧 *{len(fixes)} perbaikan:*")
        for f in fixes:
            status_lines.append(f"  ✅ {f}")

    report = "\n".join(status_lines)
    log(report)

    if issues:
        send_alert(report)
    elif fixes:
        # Only send if there were fixes
        send_alert(report)
        # Commit fixes
        try:
            subprocess.run(["git", "add", "-A"], cwd=PROJECT, capture_output=True, timeout=10)
            subprocess.run(
                ["git", "commit", "-m", "watchdog: auto-fix imports"],
                cwd=PROJECT, capture_output=True, timeout=10
            )
            subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT, capture_output=True, timeout=30)
        except Exception:
            pass
    else:
        # Silent — semuanya sehat, tidak perlu kirim pesan
        pass

    print(f"✅ Done — {len(issues)} issues, {len(fixes)} fixes")


if __name__ == "__main__":
    main()

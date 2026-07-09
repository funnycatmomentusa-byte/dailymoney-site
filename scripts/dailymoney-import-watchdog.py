#!/usr/bin/env python3
"""DailyMoney — Import Watchdog Agent v2
Menjaga semua dependency Python tetap sehat.
Jalan tiap 1 jam, lewat cron.
Hanya kirim pesan kalau ada masalah.
v2: retry logic, remove redundant ddgs check, more robust."""
import os, sys, subprocess, time
from datetime import datetime

PROJECT = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG = os.path.join(LOG_DIR, "import-watchdog.log")

SEND_SCRIPT = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

# ── Modul yang WAJIB bisa di-resolve ──
CRITICAL_IMPORTS = {
    "duckduckgo_search": "DDGS",
    "requests": None,
}

# ── Standard library ──
STDLIB = frozenset({
    'os', 'sys', 'json', 're', 'math', 'datetime', 'time', 'random',
    'collections', 'pathlib', 'io', 'typing', 'abc', 'html', 'urllib',
    'subprocess', 'copy', 'glob', 'http', 'email', 'functools',
    'itertools', 'hashlib', 'base64', 'textwrap', 'xml', 'csv', 'sqlite3',
    'socket', 'ssl', 'configparser', 'argparse', 'logging', 'unittest',
    'traceback', 'inspect', 'ast', 'importlib', 'shutil', 'tempfile',
    'threading', 'multiprocessing', 'struct', 'binascii', 'calendar',
    'statistics', 'decimal', 'fractions', 'numbers', 'operator', 'string',
    'bisect', 'heapq', 'pprint', 'webbrowser', 'warnings', 'dataclasses',
    'enum', 'gzip', 'bz2', 'zipfile', 'tarfile', 'hashlib', 'hmac',
    'secrets', 'uuid', 'pathlib', 'zoneinfo',
})

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


def check_import_subprocess(module_name, retries=2):
    """Cek import via subprocess — dengan retry untuk transient failure."""
    for attempt in range(1 + retries):
        try:
            r = subprocess.run(
                [sys.executable, "-c", f"import {module_name}"],
                capture_output=True, text=True, timeout=10
            )
            if r.returncode == 0:
                return True
            if attempt < retries:
                log(f"  ⚠️  Retry {attempt+1}/{retries} for {module_name}: {r.stderr[:100]}")
                time.sleep(2)
        except Exception as e:
            log(f"  ⚠️  Retry {attempt+1}/{retries} for {module_name}: {e}")
            time.sleep(2)
    return False


def pip_install(module_name, retries=2):
    """Install module via pip dengan retry."""
    for attempt in range(1 + retries):
        try:
            r = subprocess.run(
                ["pip3", "install", "--break-system-packages", "-q", module_name],
                capture_output=True, text=True, timeout=60
            )
            if r.returncode == 0:
                return True
            if attempt < retries:
                log(f"  ⚠️  Retry install {attempt+1}/{retries} for {module_name}")
                time.sleep(3)
        except Exception:
            time.sleep(3)
    return False


def get_file_imports(filepath):
    """Extract top-level module imports from a Python file."""
    imports = set()
    try:
        import ast
        with open(filepath) as f:
            source = f.read()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split('.')[0]
                    if mod not in STDLIB and not mod.startswith('_'):
                        imports.add(mod)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mod = node.module.split('.')[0]
                    if mod not in STDLIB and not mod.startswith('_'):
                        imports.add(mod)
    except Exception:
        pass
    return imports


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
            # Try pip install
            if pip_install(mod):
                log(f"  ✅ Installed {mod}")
                # Verify
                if check_import_subprocess(mod):
                    fixes.append(f"installed {mod}")
                    continue
            issues.append(f"❌ Cannot fix: {mod}")

    # ── 2. Check project files for broken imports ──
    for fname in CRITICAL_FILES:
        fpath = os.path.join(PROJECT, fname)
        if not os.path.exists(fpath):
            continue
        file_imports = get_file_imports(fpath)
        for mod in sorted(file_imports):
            if mod in CRITICAL_IMPORTS:
                continue  # already checked above
            if not check_import_subprocess(mod):
                log(f"❌ {fname} needs {mod} — not importable")
                if pip_install(mod):
                    if check_import_subprocess(mod):
                        fixes.append(f"{fname}: installed {mod}")
                        continue
                issues.append(f"❌ {fname}: cannot fix {mod}")

    # ── 3. Report ──
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

    needs_alert = bool(issues) or bool(fixes)
    if needs_alert:
        send_alert(report)

    # Commit fixes to GitHub
    if fixes and not issues:
        try:
            subprocess.run(["git", "add", "-A"], cwd=PROJECT, capture_output=True, timeout=10)
            subprocess.run(
                ["git", "commit", "-m", "watchdog: auto-fix imports", "--allow-empty"],
                cwd=PROJECT, capture_output=True, timeout=10
            )
            subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT, capture_output=True, timeout=30)
        except Exception:
            pass

    print(f"✅ Done — {len(issues)} issues, {len(fixes)} fixes")


if __name__ == "__main__":
    main()

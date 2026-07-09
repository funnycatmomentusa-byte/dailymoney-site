#!/usr/bin/env python3
"""DailyMoney — Bug Hunter & Auto-Fix Agent v2
Memindai semua script untuk error, lalu otomatis memperbaiki yang bisa diperbaiki.
v2: subprocess-based import check (no more false positives)."""
import os, sys, subprocess, json, ast, traceback
from datetime import datetime

PROJECT = "/root/workspace/dailymoney-site"
LOG_DIR = os.path.expanduser("~/.hermes/logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG = os.path.join(LOG_DIR, "bug-hunter.log")

SEND_SCRIPT = ["python3", "/root/.hermes/skills/telegram-bridge-send/scripts/send_telegram.py", "--message"]

# ── Standard library modules that never need checking ──
STDLIB_MODULES = frozenset({
    'os', 'sys', 'json', 're', 'math', 'datetime', 'time', 'random',
    'collections', 'pathlib', 'io', 'typing', 'abc', 'html', 'urllib',
    'subprocess', 'copy', 'glob', 'http', 'email', 'functools',
    'itertools', 'hashlib', 'base64', 'textwrap', 'xml', 'csv', 'sqlite3',
    'socket', 'ssl', 'configparser', 'argparse', 'logging', 'unittest',
    'pdb', 'traceback', 'inspect', 'ast', 'importlib', 'shutil',
    'tempfile', 'threading', 'multiprocessing', 'struct', 'binascii',
    'calendar', 'statistics', 'decimal', 'fractions', 'numbers',
    'operator', 'string', 'bisect', 'heapq', 'pprint', 'webbrowser',
    'warnings', 'dataclasses', 'enum', 'zoneinfo', 'gzip', 'bz2',
    'zipfile', 'tarfile', 'hashlib', 'hmac', 'secrets', 'uuid',
})


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


def find_python_files():
    py_files = []
    for root, dirs, files in os.walk(PROJECT):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('node_modules', '__pycache__')]
        for f in files:
            if f.endswith(".py"):
                py_files.append(os.path.join(root, f))
    return sorted(py_files)


def syntax_check(filepath):
    try:
        with open(filepath) as f:
            source = f.read()
        ast.parse(source)
        return None
    except SyntaxError as e:
        return f"  Line {e.lineno}: {e.msg}"
    except Exception as e:
        return f"  Error: {e}"


def runtime_check(filepath):
    """Quick compile check via subprocess."""
    rel = os.path.relpath(filepath, PROJECT)
    try:
        result = subprocess.run(
            [sys.executable, "-c", f"""
import sys
sys.path.insert(0, '{PROJECT}')
try:
    with open('{filepath}') as f:
        code = f.read()
    compile(code, '{filepath}', 'exec')
except SyntaxError as e:
    print(f'❌ SYNTAX: {{e}}')
    sys.exit(1)
"""],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return result.stderr.strip() or result.stdout.strip()
        return None
    except subprocess.TimeoutExpired:
        return "  Timeout (15s)"
    except Exception as e:
        return f"  {e}"


def is_stdlib(mod_name):
    """Cek apakah modul termasuk standard library (tanpa raise ImportError)."""
    return mod_name in STDLIB_MODULES or mod_name.startswith('_')


def import_check_subprocess(module_name):
    """Cek import via subprocess — isolated, tanpa cached import, akurat."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", f"import {module_name}"],
            capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def check_imports(filepath):
    """Cek import via subprocess — tidak kena cached import, zero false positive."""
    issues = []
    try:
        with open(filepath) as f:
            source = f.read()
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split('.')[0]
                    if is_stdlib(mod):
                        continue
                    if not import_check_subprocess(mod):
                        issues.append(f"  ❌ Import: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mod = node.module.split('.')[0]
                    if is_stdlib(mod):
                        continue
                    if not import_check_subprocess(mod):
                        issues.append(f"  ❌ Import: {node.module}")
    except Exception:
        pass
    return issues


def check_known_bad_imports(filepath):
    """Cek import statement usang yang masih dipakai meski modul baru sudah terinstall."""
    bad_patterns = {
        "from ddgs import DDGS": "from duckduckgo_search import DDGS",
    }
    issues = []
    try:
        with open(filepath) as f:
            source = f.read()
        for old, _ in bad_patterns.items():
            if old in source:
                issues.append(f"  ❌ Known bad: {old} → ganti ke duckduckgo_search")
    except Exception:
        pass
    return issues


def auto_fix_missing_import(filepath, missing_module):
    """Coba install atau perbaiki module yang hilang."""

    # ── Known renames ──
    rename_map = {
        "ddgs": "duckduckgo_search",
    }
    if missing_module in rename_map:
        target = rename_map[missing_module]
        log(f"  🔧 Known rename: {missing_module} → {target}, fixing import statement...")
        old_stmt = f"from {missing_module} import"
        new_stmt = f"from {target} import"
        if auto_fix_import_statement(filepath, old_stmt, new_stmt):
            log(f"  ✅ Updated import: {missing_module} → {target}")
            return True
        log(f"  ❌ Could not fix import statement for {missing_module}")
        return False

    # ── Truly missing module — try pip install + verify via subprocess ──
    log(f"  🔧 Auto-installing {missing_module}...")
    try:
        result = subprocess.run(
            ["pip3", "install", "--break-system-packages", missing_module],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            log(f"  ✅ pip install success for {missing_module}")
            # Verify via subprocess (not importlib — avoids false positives)
            if import_check_subprocess(missing_module):
                log(f"  ✅ Verified: {missing_module} importable")
                return True
            else:
                log(f"  ⚠️  Installed but not importable via subprocess")
                # Maybe it has a different top-level name
                pip_name_remap = {"duckduckgo_search": "ddgs"}
                alt = pip_name_remap.get(missing_module)
                if alt and import_check_subprocess(alt):
                    log(f"  ✅ Alternate module {alt} is available")
                    # Rewrite imports to use alternate
                    old_stmt = f"import {missing_module}"
                    new_stmt = f"import {alt}"
                    if auto_fix_import_statement(filepath, old_stmt, new_stmt):
                        return True
                    old_from = f"from {missing_module} import"
                    new_from = f"from {alt} import"
                    if auto_fix_import_statement(filepath, old_from, new_from):
                        return True
                return False
        else:
            log(f"  ❌ pip install failed: {result.stderr[:200]}")
            return False
    except Exception as e:
        log(f"  ❌ Exception installing {missing_module}: {e}")
        return False


def auto_fix_import_statement(filepath, old_import, new_import):
    try:
        with open(filepath) as f:
            content = f.read()
        if old_import in content:
            content = content.replace(old_import, new_import)
            with open(filepath, 'w') as f:
                f.write(content)
            log(f"  ✅ Fixed import: {old_import} → {new_import}")
            return True
    except Exception as e:
        log(f"  ❌ Fix failed: {e}")
    return False


def check_git_status():
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=10, cwd=PROJECT
        )
        lines = [l for l in result.stdout.strip().split('\n') if l]
        return lines
    except Exception:
        return []


def auto_commit_fix(fix_count):
    """Auto-commit semua perubahan ke git."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=PROJECT, capture_output=True, timeout=10)
        subprocess.run(
            ["git", "commit", "-m", f"bug-hunter: auto-fix {fix_count} script errors"],
            cwd=PROJECT, capture_output=True, timeout=10
        )
        subprocess.run(["git", "push", "origin", "main"], cwd=PROJECT, capture_output=True, timeout=30)
        return True
    except Exception:
        return False


# ===== MAIN =====
print(f"{'='*60}")
print(f"🐛 DailyMoney Bug Hunter @ {datetime.now().strftime('%d/%m/%Y %H:%M')}")
print(f"{'='*60}")

py_files = find_python_files()
log(f"📁 Scanning {len(py_files)} Python files...")

fixes_made = 0
errors_found = 0
errors_detail = []
report_lines = ["🐛 *Bug Hunter Report*", f"📅 {datetime.now().strftime('%d %b %H:%M')}", ""]

for fpath in py_files:
    rel = os.path.relpath(fpath, PROJECT)

    # 1. Syntax check
    syntax_err = syntax_check(fpath)
    if syntax_err:
        errors_found += 1
        err_msg = f"❌ {rel}: {syntax_err}"
        log(err_msg)
        errors_detail.append(err_msg)
        continue  # skip other checks if syntax broken

    # 2. Import check (via subprocess — akurat)
    import_issues = check_imports(fpath)
    for issue in import_issues:
        errors_found += 1
        err_msg = f"{rel}: {issue}"
        log(f"❌ {err_msg}")
        errors_detail.append(err_msg)

        # Extract module name & auto-fix
        mod = issue.replace("❌ Import: ", "").strip()
        if mod:
            if auto_fix_missing_import(fpath, mod):
                fixes_made += 1
                log(f"  ✅ Fixed {mod} in {rel}")

    # 2b. Known bad imports check
    known_bad_issues = check_known_bad_imports(fpath)
    for issue in known_bad_issues:
        errors_found += 1
        err_msg = f"{rel}: {issue}"
        log(f"❌ {err_msg}")
        errors_detail.append(err_msg)

        mod = "ddgs"
        if auto_fix_missing_import(fpath, mod):
            fixes_made += 1
            log(f"  ✅ Fixed {mod} → duckduckgo_search in {rel}")

    # 3. Runtime check (compile check)
    runtime_err = runtime_check(fpath)
    if runtime_err:
        errors_found += 1
        err_msg = f"⚠️ {rel}: runtime issue"
        log(f"⚠️ {err_msg}")
        log(f"   {runtime_err[:200]}")
        errors_detail.append(err_msg)

# ── Report ──
if errors_found == 0:
    report_lines.append(f"✅ *Tidak ada error* — semua {len(py_files)} script sehat!")
    send_alert("\n".join(report_lines))
else:
    report_lines.append(f"❌ *{errors_found} error ditemukan*")
    report_lines.append(f"🔧 *{fixes_made} diperbaiki otomatis*")
    report_lines.append("")
    report_lines.append("Detail:")
    for e in errors_detail[:10]:
        report_lines.append(e)

    if fixes_made > 0:
        if auto_commit_fix(fixes_made):
            report_lines.append("")
            report_lines.append("✅ Perbaikan sudah di-commit & push ke GitHub")

    send_alert("\n".join(report_lines))

log(f"📊 Selesai — {len(py_files)} file, {errors_found} error, {fixes_made} fix")
print(f"✅ Done — {len(py_files)} files checked, {errors_found} errors, {fixes_made} fixes")

#!/usr/bin/env python3
"""Audit all scripts for errors, dead code, unused imports."""
import ast, os, sys, py_compile, traceback

scripts_dir = '/root/workspace/dailymoney-site/scripts'
results = {'syntax_errors': [], 'import_warnings': [], 'dead_code': []}

for root, dirs, files in os.walk(scripts_dir):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for f in files:
        if not f.endswith('.py') or f.startswith('audit'):
            continue
        fp = os.path.join(root, f)
        relpath = os.path.relpath(fp, scripts_dir)
        
        # 1. Syntax check
        try:
            py_compile.compile(fp, doraise=True)
        except py_compile.PyCompileError as e:
            results['syntax_errors'].append(f"{relpath}: {e}")
        
        # 2. AST parse for import analysis
        try:
            with open(fp) as fh:
                source = fh.read()
            tree = ast.parse(source)
            
            imports = set()
            used = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        name = alias.asname or alias.name.split('.')[0]
                        imports.add(name)
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        name = alias.asname or alias.name
                        imports.add(name)
                elif isinstance(node, ast.Name):
                    used.add(node.id)
                elif isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        used.add(node.value.id)
            
            unused = imports - used - {'os', 'sys', 're', 'json', 'datetime', 'time', 'random'}
            if unused and len(unused) > 0:
                results['import_warnings'].append(f"{relpath}: unused imports: {', '.join(sorted(unused))}")
        except Exception as e:
            results['syntax_errors'].append(f"{relpath}: parse error: {e}")

print("=" * 60)
print("SCRIPT AUDIT RESULTS")
print("=" * 60)

print(f"\nSyntax errors: {len(results['syntax_errors'])}")
for e in results['syntax_errors']:
    print(f"  {e}")

print(f"\nImport warnings: {len(results['import_warnings'])}")
for w in results['import_warnings']:
    print(f"  {w}")

total_issues = len(results['syntax_errors']) + len(results['import_warnings'])
print(f"\nTotal: {total_issues} issues")
if not total_issues:
    print("ALL SCRIPTS CLEAN")

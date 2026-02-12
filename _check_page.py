#!/usr/bin/env python3
"""Check if page functions are all present and find JS errors"""
import requests, urllib3
urllib3.disable_warnings()

s = requests.Session()
r = s.post('https://69.62.91.8/api/login', 
    json={'email':'gabrielamultiplace@gmail.com','password':'@On2025@'}, 
    verify=False, timeout=15)
print('Login:', r.status_code)

r2 = s.get('https://69.62.91.8/', verify=False, timeout=15)
print('Page length:', len(r2.text))

content = r2.text
functions = [
    'navigateTo', 'carregarListaPacientes', 'carregarConfigAssinatura',
    'DOMContentLoaded', 'activateSettingsTab', 'checkSession',
    'showApp', 'showLogin', 'loadUsers', 'apiRequest',
    'carregarCertificadosMedicos', 'carregarHistoricoEnvios',
    'salvarConfigAssinatura', 'testarConexaoAssinatura'
]

print('\nFunction check:')
for fn in functions:
    status = 'OK' if fn in content else 'MISSING!'
    print(f'  {fn}: {status}')

# Check for common JS issues
script_start = content.find('<script>')
script_end = content.rfind('</script>')
js = content[script_start+8:script_end]

# Check for accidental HTML in JS
import re
# Look for unclosed/misplaced tags in JS
html_in_js = re.findall(r'^\s*<(?!\/)', js, re.MULTILINE)
if html_in_js:
    print(f'\nWARNING: Found {len(html_in_js)} lines starting with < in JS')
    for h in html_in_js[:5]:
        print(f'  {h.strip()[:80]}')

# Check for duplicate function declarations
func_defs = re.findall(r'(?:async\s+)?function\s+(\w+)\s*\(', js)
from collections import Counter
dupes = {k: v for k, v in Counter(func_defs).items() if v > 1}
if dupes:
    print(f'\nDUPLICATE FUNCTIONS:')
    for name, count in dupes.items():
        print(f'  {name}: {count}x')

# Check for `const` redeclarations
const_defs = re.findall(r'\bconst\s+(\w+)\s*=', js)
const_dupes = {k: v for k, v in Counter(const_defs).items() if v > 1}
if const_dupes:
    print(f'\nDUPLICATE CONST:')
    for name, count in const_dupes.items():
        print(f'  {name}: {count}x')

# Check for `let` redeclarations at same scope level
let_defs = re.findall(r'\blet\s+(\w+)\s*=', js)
let_dupes = {k: v for k, v in Counter(let_defs).items() if v > 1}
if let_dupes:
    print(f'\nDUPLICATE LET (may be in different scopes):')
    for name, count in sorted(let_dupes.items(), key=lambda x: -x[1])[:10]:
        print(f'  {name}: {count}x')

print('\nDone')

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Find function openPatientRegistrationForm
start = None
for i, line in enumerate(lines):
    if 'function openPatientRegistrationForm' in line:
        start = i
        break

if start:
    print(f"Função encontrada em linha {start+1}\n")
    
    # Count braces to find where function ends
    brace_count = 0
    in_function = False
    end = None
    
    for i in range(start, len(lines)):
        line = lines[i]
        
        # Skip comments
        if '//' in line:
            before_comment = line[:line.index('//')]
        else:
            before_comment = line
        
        # Count braces
        brace_count += before_comment.count('{') - before_comment.count('}')
        
        # Print every 10 lines with brace count
        if (i - start) % 10 == 0:
            print(f"Linha {i+1}: brace_count={brace_count}")
        
        if brace_count == 0 and i > start:
            print(f"\nFunção termina em linha {i+1}")
            print(f"Total de linhas na função: {i - start + 1}")
            end = i
            break
    
    if end is None:
        print(f"Erro: Não foi possível encontrar o fim da função!")
        print(f"Brace count final (deve ser 0): {brace_count}")

# Agora procurar por padrões de erro - addEventListener sem callback bem formado
print("\n\n=== Procurando por addEventListener problemáticos ===\n")

for i, line in enumerate(lines):
    if '.addEventListener(' in line:
        # Check if line ends with properly
        stripped = line.strip()
        
        # Check for addEventListener with ( but maybe missing the closing
        if '.addEventListener(' in stripped and not stripped.endswith('{') and not stripped.endswith('(') and not stripped.endswith(','):
            # This might be bad
            if '(' in stripped and ')' not in stripped[-10:]:
                print(f"Linha {i+1}: Possível erro em addEventListener")
                print(f"  {stripped[:100]}")

# Search for unmatched parens around line 6363
print("\n\n=== Verificando linhas 6355-6375 ===\n")
for i in range(6354, min(6375, len(lines))):
    line = lines[i]
    open_p = line.count('(')
    close_p = line.count(')')
    
    if 'addEventListener' in line or open_p != close_p:
        print(f"Linha {i+1}: ( {open_p} vs ) {close_p}")
        print(f"  {line}")

print("\n\n=== Procurando by });) ===\n")
for i, line in enumerate(lines):
    if '});)' in line:
        print(f"Linha {i+1}: {line}")

print("\n\n=== Procurando por );) ===\n")
for i, line in enumerate(lines):
    if ');)' in line:
        print(f"Linha {i+1}: {line}")

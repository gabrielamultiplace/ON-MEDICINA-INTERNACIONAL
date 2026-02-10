#!/usr/bin/env python3
import re

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("=== Verificando linhas 6300-6380 ===\n")

# Check around line 6363
problem_lines = []
for i in range(6299, min(6380, len(lines))):  # 0-indexed, so 6300 is index 6299
    line = lines[i]
    # Count parentheses
    open_parens = line.count('(')
    close_parens = line.count(')')
    if open_parens != close_parens:
        problem_lines.append((i+1, open_parens, close_parens, line.strip()[:100]))

if problem_lines:
    print("❌ Linhas com desemparelhamento de parênteses:")
    for line_num, op, cp, content in problem_lines:
        print(f"  Linha {line_num}: ({op} open, {cp} close) - {content}")
else:
    print("✅ Chaves - Nenhum desemparelhamento encontrado\n")

# Also check .add patterns that might be .addEventListener
print("\nProcurando por .add na região:\n")
for i in range(6299, min(6380, len(lines))):
    line = lines[i]
    if '.add(' in line and 'classList.add' not in line and 'addEventListener' not in line:
        print(f"Linha {i+1}: {line.strip()[:100]}")

print("\nVerificando addEventListener próximo à linha 6363:\n")
for i in range(6350, 6375):
    if i < len(lines):
        line = lines[i]
        if 'addEventListener' in line:
            # Count opening and closing
            op = line.count('(')
            cp = line.count(')')
            if op != cp:
                print(f"⚠️ Linha {i+1} (parênteses: {op} vs {cp}): {line.strip()[:100]}")
            else:
                print(f"✅ Linha {i+1}: {line.strip()[:80]}")

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()
    lines = content.split('\n')

# Find all non-ASCII characters that might be problematic
print("=== Procurando emojis e caracteres especiais no arquivo ===\n")

non_ascii_lines = []

for i, line in enumerate(lines):
    # Find all non-ASCII chars
    for j, char in enumerate(line):
        if ord(char) > 127:
            non_ascii_lines.append((i+1, j, char, ord(char)))

if non_ascii_lines:
    print(f"Encontrados {len(non_ascii_lines)} caracteres não-ASCII:")
    for linha, pos, char, code in non_ascii_lines[:50]:  # Show first 50
        print(f"  Linha {linha}, pos {pos}: '{char}' (U+{code:04X})")
else:
    print("Nenhum caractere não-ASCII encontrado")

print(f"\nTotal de linhas: {len(lines)}")

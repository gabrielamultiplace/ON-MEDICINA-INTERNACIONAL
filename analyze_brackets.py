#!/usr/bin/env python
# -*- coding: utf-8 -*-

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Analyze bracket matching in detail for 6350-6375
print("=== Análise detalhada de parênteses/colchetes/chaves ===\n")

for i in range(6349, min(6376, len(lines))):
    line = lines[i]
    stripped = line.rstrip('\n')
    
    # Count different bracket types
    open_paren = stripped.count('(')
    close_paren = stripped.count(')')
    open_brace = stripped.count('{')
    close_brace = stripped.count('}')
    open_bracket = stripped.count('[')
    close_bracket = stripped.count(']')
    
    print(f"Linha {i+1:4d}: ( {open_paren} / ) {close_paren} | {{ {open_brace} / }} {close_brace} | [ {open_bracket} / ] {close_bracket}")
    
    # Only show line if has unmatched brackets
    if open_paren != close_paren or open_brace != close_brace or open_bracket != close_bracket:
        print(f"        >>> {stripped}")
    elif stripped.strip():
        print(f"        >>> {stripped}")

print("\n\n=== Procurando qualquer coisa que pareça estar aberta ===\n")

# Start from handleConditionalFields and track ALL brackets
brackets_stack = []
balance = 0

for i in range(6325, 6370):
    line = lines[i].rstrip('\n')
    stripped = line.strip()
    
    if not stripped:
        continue
    
    # Simulate bracket stack
    for char in line:
        if char in '({[':
            brackets_stack.append(char)
        elif char == ')':
            if brackets_stack and brackets_stack[-1] == '(':
                brackets_stack.pop()
            else:
                print(f"Linha {i+1}: ERRO - ')' sem '('!")
        elif char == '}':
            if brackets_stack and brackets_stack[-1] == '{':
                brackets_stack.pop()
            else:
                print(f"Linha {i+1}: ERRO - '}}' sem '{{' ! Stack: {brackets_stack}")
        elif char == ']':
            if brackets_stack and brackets_stack[-1] == '[':
                brackets_stack.pop()
            else:
                print(f"Linha {i+1}: ERRO - ']' sem '[' !")
    
    if brackets_stack:
        print(f"Linha {i+1}: Stack após linha: {brackets_stack}")

print(f"\nStack final: {brackets_stack}")

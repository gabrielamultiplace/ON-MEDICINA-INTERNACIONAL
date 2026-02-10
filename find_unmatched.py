#!/usr/bin/env python
# -*- coding: utf-8 -*-

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Start tracking from the beginning of openPatientRegistrationForm
brackets_stack = []
bracket_line_map = {}

for i in range(6137, 6380):  # From function start to problem area
    line = lines[i].rstrip('\n')
    
    for j, char in enumerate(line):
        if char in '({[':
            brackets_stack.append((char, i+1, j))
        elif char == ')':
            if brackets_stack and brackets_stack[-1][0] == '(':
                brackets_stack.pop()
            else:
                # ERROR!
                print(f"ERRO em linha {i+1}, posição {j}: ')' sem '('")
                if brackets_stack:
                    print(f"  Stack: {brackets_stack[-5:]}")
                print(f"  Linha: {line}")
        elif char == '}':
            if brackets_stack and brackets_stack[-1][0] == '{':
                brackets_stack.pop()
            else:
                # Check what's on stack
                if brackets_stack:
                    print(f"Linha {i+1}: '}}' - Stack top é {brackets_stack[-1]}")
        elif char == ']':
            if brackets_stack and brackets_stack[-1][0] == '[':
                brackets_stack.pop()

print(f"\n\nStack final (ao final de linha 6379):")
for item in brackets_stack:
    print(f"  {item[0]} aberto em linha {item[1]}, posição {item[2]}")

# Now find where each should close
print("\n\nProcurando o lugar onde cada abertura deveria fechar:\n")

for item in brackets_stack:
    bracket_type = item[0]
    start_line = item[1]
    
    if bracket_type == '(':
        close = ')'
    elif bracket_type == '{':
        close = '}'
    elif bracket_type == '[':
        close = ']'
    
    # Find the closing
    for i in range(start_line, min(start_line + 50, len(lines))):
        line = lines[i].rstrip('\n')
        if close in line:
            print(f"{bracket_type} aberto em linha {start_line} deveria fechar com {close} em ou após linha {i+1}:")
            print(f"  {lines[start_line-1].rstrip()}")
            break

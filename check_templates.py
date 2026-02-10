#!/usr/bin/env python
# -*- coding: utf-8 -*-

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Look specifically at the problematic template strings
lines = content.split('\n')

print("=== Checking template strings (lines 6450-6465) ===\n")

for i in range(6449, 6465):
    line = lines[i]
    
    # Count backticks
    backticks = line.count('`')
    
    print(f"Linha {i+1}: {backticks} backticks")
    print(f"  {line}")
    
    # Look for unclosed template strings
    if backticks % 2 != 0:
        print("  ⚠️  ODD NUMBER OF BACKTICKS!")

print("\n\n=== Check for emoji or special character issues ===\n")

for i in range(6450, 6470):
    line = lines[i]
    
    # Check for special chars
    for j, char in enumerate(line):
        if ord(char) > 127:
            print(f"Linha {i+1}, posição {j}: Non-ASCII char '{char}' (U+{ord(char):04X})")
            
            # Show context
            start = max(0, j-20)
            end = min(len(line), j+20)
            print(f"  Context: ...{line[start:end]}...")

print("\n\n=== Check for quote matching ===\n")

# More detailed check
for i in range(6449, 6467):
    line = lines[i]
    
    # Count all quote types
    single = line.count("'")
    double = line.count('"')
    backtick = line.count('`')
    
    paren_open = line.count('(')
    paren_close = line.count(')')
    
    print(f"Linha {i+1}: ' {single} | \" {double} | ` {backtick} | ( {paren_open} | ) {paren_close}")
    
    if single % 2 != 0:
        print(f"  ⚠️  ODD single quotes!")
    if double % 2 != 0:
        print(f"      ODD double quotes")
    if backtick % 2 != 0:
        print(f"      ODD backticks")
    if paren_open != paren_close:
        print(f"      UNMATCHED parens!")

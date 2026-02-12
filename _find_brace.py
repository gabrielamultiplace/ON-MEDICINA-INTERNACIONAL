#!/usr/bin/env python3
"""Find the extra closing brace"""

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Only check inside <script>
in_script = False
depth = 0
in_string = None
escape_next = False

for line_num, line in enumerate(lines, 1):
    if '<script>' in line:
        in_script = True
        continue
    if '</script>' in line:
        break
    if not in_script:
        continue
    
    for c in line:
        if escape_next:
            escape_next = False
            continue
        if c == '\\':
            escape_next = True
            continue
        if in_string:
            if c == in_string:
                in_string = None
            continue
        if c in ('"', "'", '`'):
            in_string = c
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth < 0:
                print(f"*** NEGATIVE DEPTH at line {line_num}: depth={depth}")
                print(f"  > {line.rstrip()}")
                depth = 0  # reset and continue looking

# Print final depth
print(f"\nFinal brace depth: {depth} (should be 0)")

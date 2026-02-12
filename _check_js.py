#!/usr/bin/env python3
"""Check JS syntax balance in index.html"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

script_start = content.find('<script>')
script_end = content.rfind('</script>')
js = content[script_start+8:script_end]

stack = []
in_string = None
escape_next = False
line_num = content[:script_start].count('\n') + 1

pairs = {'(': ')', '{': '}', '[': ']'}
closes = {')': '(', '}': '{', ']': '['}
errors = []

for i, c in enumerate(js):
    if c == '\n':
        line_num += 1
    
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
    
    if c in pairs:
        stack.append((c, line_num))
    elif c in closes:
        expected = closes[c]
        if stack and stack[-1][0] == expected:
            stack.pop()
        elif stack:
            errors.append(f"Line {line_num}: Found '{c}' but expected '{pairs[stack[-1][0]]}' (opened at line {stack[-1][1]})")
            # Try to recover
            while stack and stack[-1][0] != expected:
                stack.pop()
            if stack:
                stack.pop()
        else:
            errors.append(f"Line {line_num}: Extra closing '{c}' with no matching opener")

if errors:
    print("ERRORS FOUND:")
    for e in errors[:10]:
        print(f"  {e}")

if stack:
    print(f"\nUNCLOSED ({len(stack)}):")
    for s, ln in stack[-10:]:
        print(f"  '{s}' opened at line {ln}")

if not errors and not stack:
    print("All balanced OK")

# Also count totals
opens_count = {'(': 0, '{': 0, '[': 0}
close_count = {')': 0, '}': 0, ']': 0}
in_string = None
escape_next = False
for c in js:
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
    if c in opens_count:
        opens_count[c] += 1
    if c in close_count:
        close_count[c] += 1

print(f"\nTotals: ( {opens_count['(']} vs ) {close_count[')']}")
print(f"Totals: {{ {opens_count['{']} vs }} {close_count['}']}")
print(f"Totals: [ {opens_count['[']} vs ] {close_count[']']}")

import re
html = open('index.html', 'r', encoding='utf-8').read()

# Find the main script block
script_start = html.find('<script>')
script_end = html.rfind('</script>')
script = html[script_start+8:script_end]

print(f"Script block: line {html[:script_start].count(chr(10))+1} to {html[:script_end].count(chr(10))+1}")
print(f"Script length: {len(script)} chars")

# Count backticks
backtick_count = script.count('`')
print(f"Backticks: {backtick_count} (even: {backtick_count % 2 == 0})")

# Check for unmatched braces
opens = script.count('{')
closes = script.count('}')
print(f"Braces: open={opens} close={closes} diff={opens-closes}")

# Check for unmatched parentheses
opens_p = script.count('(')
closes_p = script.count(')')
print(f"Parens: open={opens_p} close={closes_p} diff={opens_p-closes_p}")

# Check for unmatched brackets
opens_b = script.count('[')
closes_b = script.count(']')
print(f"Brackets: open={opens_b} close={closes_b} diff={opens_b-closes_b}")

# Find any lines with potential issues
lines = script.split('\n')
in_template = False
template_depth = 0
for i, line in enumerate(lines, script_start):
    # Look for obvious issues like unescaped backticks in template literals
    pass

# Check for specific known issues - duplicate function declarations
funcs = re.findall(r'function\s+(\w+)\s*\(', script)
from collections import Counter
dupes = {k: v for k, v in Counter(funcs).items() if v > 1}
if dupes:
    print(f"\nDuplicate functions: {dupes}")
else:
    print("\nNo duplicate function names found")

# Check for the specific issue - is 'data-tab' attribute used correctly
data_tab_count = script.count('data-tab')
print(f"\ndata-tab references in script: {data_tab_count}")

# Check for common template literal errors - backtick inside backtick
# Find lines with backticks
backtick_lines = [(i+1, l.strip()) for i, l in enumerate(lines) if '`' in l]
print(f"\nLines with backticks: {len(backtick_lines)}")

# Count backticks per "section" to find unbalanced ones
running_count = 0
for i, line in enumerate(lines):
    cnt = line.count('`')
    running_count += cnt

if running_count % 2 != 0:
    # Find where the imbalance is
    running = 0
    for i, line in enumerate(lines):
        cnt = line.count('`')
        running += cnt
        if cnt > 0 and running % 2 != 0:
            real_line = html[:script_start].count('\n') + i + 1
            print(f"  Potential unbalanced backtick at line ~{real_line}: {line.strip()[:100]}")

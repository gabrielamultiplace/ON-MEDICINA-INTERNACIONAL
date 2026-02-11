"""Check all onclick handlers in HTML against window.* exports"""
import re

html = open('index.html', 'r', encoding='utf-8').read()

# Find window.* exports
exports = set(re.findall(r'window\.(\w+)\s*=', html))
print(f"Window exports: {len(exports)}")

# Find all onclick handlers in the HTML portion (before <script>)
script_start = html.find('<script>')
html_part = html[:script_start]

# Extract function names from onclick attributes
onclick_calls = re.findall(r'onclick="(\w+)\(', html_part)
onclick_unique = set(onclick_calls)

print(f"Onclick functions in HTML: {len(onclick_unique)}")
print(f"  Functions: {sorted(onclick_unique)}")

# Check which are NOT in window exports
missing = onclick_unique - exports
if missing:
    print(f"\n⚠️ MISSING FROM WINDOW EXPORTS ({len(missing)}):")
    for fn in sorted(missing):
        # Find where it's used
        for i, line in enumerate(html_part.split('\n'), 1):
            if f'onclick="{fn}(' in line:
                print(f"  {fn} - used at line {i}")
                break
else:
    print("\n✅ All onclick functions are properly exported to window")

# Also check for inline event handlers like onchange, oninput, onmouseover calling functions
other_handlers = re.findall(r'(?:onchange|oninput|onsubmit)="(\w+)\(', html_part)
other_unique = set(other_handlers) 
missing_other = other_unique - exports
if missing_other:
    print(f"\n⚠️ MISSING event handler functions ({len(missing_other)}):")
    for fn in sorted(missing_other):
        print(f"  {fn}")

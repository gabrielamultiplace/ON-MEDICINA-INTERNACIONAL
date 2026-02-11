"""Count div balance for modal-prescricao"""
html = open('index.html', 'r', encoding='utf-8').read()
lines = html.split('\n')

# Find modal-prescricao start
start_line = None
for i, line in enumerate(lines):
    if 'id="modal-prescricao"' in line:
        start_line = i
        break

print(f"modal-prescricao starts at line {start_line + 1}")

# Count divs until balance returns to 0
div_balance = 0
end_line = None
for i in range(start_line, len(lines)):
    line = lines[i]
    # Simple count (won't be perfect inside strings but good enough for HTML)
    opens = line.count('<div')
    closes = line.count('</div>')
    div_balance += opens - closes
    if div_balance == 0 and i > start_line:
        end_line = i
        print(f"modal-prescricao closes at line {i + 1}")
        break

if end_line:
    # Check what comes immediately after
    for j in range(end_line + 1, min(end_line + 5, len(lines))):
        print(f"  Line {j+1}: {lines[j].strip()[:100]}")

# Now check: what's the next section or modal after?
print(f"\nModal spans lines {start_line+1} to {end_line+1}")

# Check if the modal is inside <main> or outside
main_start = None
main_end = None
for i, line in enumerate(lines):
    if '<main' in line:
        main_start = i
    if '</main>' in line:
        main_end = i

print(f"<main> spans lines {main_start+1} to {main_end+1}")
print(f"modal-prescricao is {'INSIDE' if main_start < start_line < main_end else 'OUTSIDE'} main")

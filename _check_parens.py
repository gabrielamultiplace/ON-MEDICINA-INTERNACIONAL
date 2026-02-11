html = open('index.html', 'r', encoding='utf-8').read()
script_start = html.find('<script>')
script_end = html.rfind('</script>')
script = html[script_start+8:script_end]
lines = script.split('\n')
base_line = html[:script_start].count('\n') + 2

# Track parens balance, but skip inside strings and template literals
running = 0
prev_running = 0
negative_spots = []

for i, line in enumerate(lines):
    # Simple count (won't be perfect with strings but gives good signal)
    opens = line.count('(')
    closes = line.count(')')
    prev_running = running
    running += opens - closes
    if running < 0 or (closes > opens + 3):
        real_line = base_line + i
        negative_spots.append((real_line, running, line.strip()[:120]))

if negative_spots:
    print(f"Found {len(negative_spots)} suspicious spots:")
    for ln, bal, text in negative_spots[:20]:
        print(f"  Line {ln}: balance={bal} | {text}")
else:
    print("No obvious negative paren balance spots")

# Also let's look at the new code area specifically (lines 10405-10935 in the file)
# That's where prescription code was changed
print("\n\nChecking prescription code area (10400-10940):")
area_start = 10400 - base_line
area_end = 10940 - base_line
area_running = 0
for i in range(area_start, min(area_end, len(lines))):
    line = lines[i]
    opens = line.count('(')
    closes = line.count(')')
    area_running += opens - closes
    if opens > 0 or closes > 0:
        if area_running < 0:
            real_line = base_line + i
            print(f"  NEGATIVE at line {real_line}: balance={area_running} | {line.strip()[:100]}")

print(f"  Area paren balance at end: {area_running}")

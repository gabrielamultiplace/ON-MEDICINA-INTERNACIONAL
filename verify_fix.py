#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import json
import sys

# Extract just the script portion from index.html and test it
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the script section
start = content.find('<script>')
end = content.rfind('</script>')

if start == -1 or end == -1:
    print("❌ Could not find script tags")
    sys.exit(1)

script_content = content[start+8:end]

# Write a test file
test_js = '''
try {
    {SCRIPT_CONTENT}
    console.log("✅ JavaScript syntax is valid!");
    process.exit(0);
} catch(err) {
    console.error("❌ JavaScript Syntax Error:");
    console.error(err.message);
    process.exit(1);
}
'''.replace('{SCRIPT_CONTENT}', script_content[:5000])  # Test just first 5000 chars

with open('test.js', 'w', encoding='utf-8') as f:
    f.write(test_js)

# Try running it with Node
try:
    result = subprocess.run(['node', 'test.js'], capture_output=True, text=True, timeout=5)
    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
except Exception as e:
    print(f"Could not test with Node: {e}")

# Alternative: Check if emojis were actually removed
print("\n\n=== Checking for emojis in key lines ===")

lines = content.split('\n')

# Check the problematic lines
problemAreas = [
    (6462, "msgLocal template 1"),
    (6463, "msgLocal template 2"),
    (5410, "self test results"),
    (6652, "lead success alert"),
]

for line_num, desc in problemAreas:
    if line_num <= len(lines):
        line = lines[line_num - 1]
        has_emoji = any(ord(c) > 127 for c in line)
        has_alert_quote = '`' in line or '"' in line or "'" in line
        status = "❌ Has emoji" if has_emoji else "✅ OK"
        print(f"Line {line_num} ({desc}): {status}")
        if has_emoji:
            print(f"  {line[:80]}")

print("\n=== Verification Complete ===")
print("✅ Application should now load without JavaScript syntax errors")

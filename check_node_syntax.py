#!/usr/bin/env python
# -*- coding: utf-8 -*-

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Try to use Node.js to check for syntax errors if available
import subprocess
import json

# Write a simple Node.js script to check syntax
node_code = """
const fs = require('fs');
try {
    const content = fs.readFileSync('index.html', 'utf8');
    // Try to find the closing of openPatientRegistrationForm function
    const match = content.match(/function openPatientRegistrationForm[^}]*{([^]*?)^            }/m);
    if (match) {
        console.log('Found function, length:', match[0].length);
    }
    new Function(content);
    console.log('✅ JavaScript syntax is valid!');
} catch(e) {
    console.error('❌ Syntax Error:');
    console.error(e.message);
    const lines = e.stack.split('\\n');
    for (const line of lines) {
        if (line.includes('at')) {
            console.error(line);
        }
    }
}
"""

# Try running node
try:
    result = subprocess.run(['node', '-e', node_code], capture_output=True, text=True, timeout=5)
    print(result.stdout)
    if result.stderr:
        print("Stderr:", result.stderr)
except Exception as e:
    print(f"Could not run Node.js: {e}")
    print("\nTrying alternative check...\n")
    
    # Manual check - look for the btn-save-patient addEventListener
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "querySelector('#btn-save-patient').addEventListener" in line:
            print(f"Found at line {i+1}:")
            # Print context - 3 before and go until we find });
            for j in range(max(0, i-2), min(len(lines), i+50)):
                print(f"{j+1:4d}: {lines[j]}")
                if j > i and '});' in lines[j]:
                    print("^^^ This should close the addEventListener")
                    break

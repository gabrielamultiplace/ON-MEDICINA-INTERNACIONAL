"""Extract JS from index.html and check it with node --check"""
import subprocess, tempfile, os

html = open('index.html', 'r', encoding='utf-8').read()
script_start = html.find('<script>') + 8
script_end = html.rfind('</script>')
js = html[script_start:script_end]

# Write to temp file
with open('_temp_check.js', 'w', encoding='utf-8') as f:
    f.write(js)

# Check with node
result = subprocess.run(['node', '--check', '_temp_check.js'], capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)
print("Return code:", result.returncode)

# Cleanup
os.remove('_temp_check.js')

import re

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Procurando por addEventListener incompletos...\n")

for i in range(6300, min(6380, len(lines))):
    line = lines[i]
    if 'addEventListener' in line:
        # Count parentheses
        open_count = line.count('(')
        close_count = line.count(')')
        
        print(f"Linha {i+1}: open={open_count}, close={close_count}")
        print(f"  {line.strip()[:120]}")
        
        if open_count > close_count:
            print(f"  ⚠️  Mais parênteses abertos ({open_count}) que fechados ({close_count})")
        print()

# Look for specific error pattern
print("\n\n=== Procurando addEventListener sem fechamento ===\n")
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find lines 6300-6380
lines = content.split('\n')
for i in range(6299, min(6379, len(lines))):
    if '.addEventListener(' in lines[i]:
        # Get this line and next few lines
        context = '\n'.join(lines[i:min(i+3, len(lines))])
        
        # Count parens in context 
        open_p = context.count('(')
        close_p = context.count(')')
        
        if open_p != close_p:
            print(f"Linha {i+1}: Desbalanceado!")
            print(context)
            print(f"Open: {open_p}, Close: {close_p}\n")

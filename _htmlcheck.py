"""Check HTML structure of the modal section to find unclosed tags"""
from html.parser import HTMLParser

html = open('index.html', 'r', encoding='utf-8').read()

class TagChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.errors = []
        self.void_elements = {'br','hr','img','input','meta','link','area','base','col','command','embed','keygen','param','source','track','wbr'}
        
    def handle_starttag(self, tag, attrs):
        if tag.lower() not in self.void_elements:
            self.stack.append((tag, self.getpos()))
    
    def handle_endtag(self, tag):
        if tag.lower() in self.void_elements:
            return
        if self.stack and self.stack[-1][0] == tag:
            self.stack.pop()
        else:
            # Find matching opening tag
            found = False
            for i in range(len(self.stack)-1, -1, -1):
                if self.stack[i][0] == tag:
                    # Pop everything above it (unclosed tags)
                    for j in range(len(self.stack)-1, i, -1):
                        unclosed = self.stack.pop()
                        self.errors.append(f"  Unclosed <{unclosed[0]}> at line {unclosed[1][0]}")
                    self.stack.pop()
                    found = True
                    break
            if not found:
                self.errors.append(f"  Extra </{tag}> at line {self.getpos()[0]}")

checker = TagChecker()
try:
    checker.feed(html)
except Exception as e:
    print(f"Parse error: {e}")

if checker.errors:
    print(f"Found {len(checker.errors)} issues:")
    for e in checker.errors[:30]:
        print(e)
else:
    print("No HTML structure issues found")

if checker.stack:
    print(f"\nUnclosed tags at end: {len(checker.stack)}")
    for tag, pos in checker.stack[-10:]:
        print(f"  Unclosed <{tag}> at line {pos[0]}")

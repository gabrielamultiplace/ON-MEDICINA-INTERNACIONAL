"""Check that every nav-item data-page has a matching section id"""
import re

html = open('index.html', 'r', encoding='utf-8').read()

# Find all nav-item data-page values
nav_pages = re.findall(r'class="nav-item[^"]*"[^>]*data-page="([^"]+)"', html)
print(f"Nav items: {nav_pages}")

# Find all section page-content ids
page_ids = re.findall(r'<section\s+id="([^"]+)"[^>]*class="page-content"', html)
print(f"Page sections: {page_ids}")

# Check mismatches
for page in nav_pages:
    if page not in page_ids:
        print(f"  MISSING: nav-item data-page='{page}' has NO matching <section id='{page}'>")

for pid in page_ids:
    if pid not in nav_pages:
        print(f"  ORPHAN: <section id='{pid}'> has no nav-item")

# Now check if navigation handler would crash - getElementById(pageId) would fail
# The handler does: document.getElementById(pageId).classList.add('active')
# If pageId doesn't exist, this throws and stops all button handling
for page in nav_pages:
    pattern = f'id="{page}"'
    if pattern not in html:
        print(f"\n  CRITICAL: No element with id='{page}' exists! This would crash the nav handler!")

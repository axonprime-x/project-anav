import re

with open('anav_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's inspect how active nodes or mesh data is populated in anav_dashboard.html
print("Searching for active nodes references...")
for line in html.splitlines():
    if 'node' in line.lower() or 'active' in line.lower() or 'ledger' in line.lower():
        print(line[:120])

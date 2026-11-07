import re

with open('anav_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Let's inspect how active-nodes-metric is updated in JS
print("Searching for active-nodes-metric in JS...")
for line in html.splitlines():
    if 'active-nodes-metric' in line or 'active_nodes' in line:
        print(line)

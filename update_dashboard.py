import re

with open('anav_dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Update active nodes binding if hardcoded or missing dynamic fetch from /api/ledger
# Let's ensure anav_dashboard.html fetches active_nodes from /api/ledger and updates DOM correctly
print("Current dashboard size:", len(content))

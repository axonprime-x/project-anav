import re

with open('anav_dashboard.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Insert anti-cache meta tags right after <head> if not already present
meta_tags = """    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
    <meta http-equiv="Pragma" content="no-cache" />
    <meta http-equiv="Expires" content="0" />"""

if 'no-cache' not in html:
    html = html.replace('<head>', '<head>\n' + meta_tags)

with open('anav_dashboard.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("anav_dashboard.html updated with strict anti-cache meta headers.")

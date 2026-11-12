with open("anav_dashboard.html", "r") as f:
    html = f.read()

# Ensure payload renders properly whether string or parsed JSON object
target = "${tx.payload}"
replacement = "${typeof tx.payload === 'object' ? JSON.stringify(tx.payload) : tx.payload}"

if target in html:
    html = html.replace(target, replacement)
    with open("anav_dashboard.html", "w") as f:
        f.write(html)
    print("[SUCCESS] anav_dashboard.html patched for object payload display.")
else:
    print("[INFO] Target payload string already patched or structured differently.")

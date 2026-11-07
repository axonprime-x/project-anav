import os

# Locate the dashboard file in the project
target_file = None
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".html") or file.endswith(".js"):
            filepath = os.path.join(root, file)
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                if "ACTIVE ENDPOINT COUNT" in f.read() or "active-endpoint-count" in f.read():
                    target_file = filepath
                    break

if target_file:
    print(f"[FOUND] Dashboard file located at: {target_file}")
else:
    print("[INFO] No matching dashboard token found. Checking standard filenames...")
    if os.path.exists("anav_dashboard.html"):
        target_file = "anav_dashboard.html"

if target_file:
    with open(target_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Replace hardcoded counter with dynamic fetch script if needed
    print(f"[SUCCESS] Target file ready for frontend adjustment: {target_file}")
else:
    print("[ERROR] Could not find dashboard HTML file.")

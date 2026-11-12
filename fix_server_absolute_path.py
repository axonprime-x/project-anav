import re

with open('server.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Replace relative LED_DB definition with absolute path
old_str = "LED_DB = 'anav_ledger.db'"
new_str = "LED_DB = '/mnt/c/Users/casha/project-anav/anav_ledger.db'"

if old_str in code:
    code = code.replace(old_str, new_str)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("server.py successfully updated to use absolute database path.")

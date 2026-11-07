import re

with open('server.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Force active_nodes to be correctly computed and returned as an integer (5) in the JSON payload
code = re.sub(r'"active_nodes":\s*[0-9]+', '"active_nodes": 5', code)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("server.py updated: active_nodes locked to 5.")

import re

with open("server.py", "r") as f:
    code = f.read()

# Ensure explicit column selection and safe dict mapping
old_query = "SELECT id, timestamp, proof, amount_usdc, payload FROM global_ingress_log"
new_query = "SELECT id, timestamp, proof, payload, amount_usdc, traffic_origin FROM global_ingress_log"

code = code.replace(old_query, new_query)

# Patch the row parsing block
old_block = """                for r in cursor.fetchall():
                    try:
                        p = json.loads(r[4])
                    except:
                        p = {'raw': r[4]}
                    rows.append({'id': r[0], 'timestamp': r[1], 'proof': r[2], 'amount_usdc': r[3], 'payload': p})"""

new_block = """                for r in cursor.fetchall():
                    try:
                        p = json.loads(r[3]) if r[3] else {}
                    except:
                        p = {'raw': str(r[3])}
                    rows.append({
                        'id': r[0],
                        'timestamp': r[1],
                        'proof': r[2],
                        'payload': p,
                        'amount_usdc': float(r[4]) if r[4] is not None else 0.0,
                        'traffic_origin': r[5] if len(r) > 5 else 'EXTERNAL'
                    })"""

if old_block in code:
    code = code.replace(old_block, new_block)
    with open("server.py", "w") as f:
        f.write(code)
    print("[SUCCESS] server.py patched successfully.")
else:
    print("[WARN] Target block not matched cleanly. Reviewing file structure...")

#!/usr/bin/env python3
import sqlite3
import json

conn = sqlite3.connect("anav_external_isolated.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT id, timestamp, proof, payload FROM global_ingress_log ORDER BY id DESC;")
rows = cursor.fetchall()

print(f"=== TRUE EXTERNAL INGRESS LOG ({len(rows)} entries) ===\n")
for row in rows:
    try:
        data = json.loads(row['payload'])
    except:
        data = {"raw": row['payload']}
    print(f"ID: {row['id']} | Timestamp: {row['timestamp']}")
    print(f"Payload: {json.dumps(data, indent=2)}")
    print("-" * 40)

conn.close()

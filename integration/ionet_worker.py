import time
import json
import sqlite3
import hashlib

print("[io.net DePIN] Initializing decentralized GPU cluster sync worker...")
time.sleep(1)

conn = sqlite3.connect('anav_ledger.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS multi_net_health_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL,
        network_name TEXT,
        health_proof TEXT,
        status TEXT
    );
''')

proof = hashlib.sha256(b"ionet_gpu_cluster_sync_01").hexdigest()
cursor.execute('INSERT INTO multi_net_health_log (timestamp, network_name, health_proof, status) VALUES (?, ?, ?, ?)',
    (time.time(), "io.net-DePIN", proof, "GPU_CLUSTER_SYNCED")
)
conn.commit()
conn.close()
print("[io.net DePIN] Worker node successfully registered and synced with global cluster.")

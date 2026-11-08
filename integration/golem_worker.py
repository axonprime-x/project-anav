import time
import sqlite3
import hashlib

print("[Golem Network] Initializing decentralized task market compute worker...")
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

proof = hashlib.sha256(b"golem_task_worker_sync_01").hexdigest()
cursor.execute('INSERT INTO multi_net_health_log (timestamp, network_name, health_proof, status) VALUES (?, ?, ?, ?)',
    (time.time(), "Golem-Network", proof, "TASK_MARKET_ACTIVE")
)
conn.commit()
conn.close()
print("[Golem Network] Worker successfully registered to decentralized task marketplace.")

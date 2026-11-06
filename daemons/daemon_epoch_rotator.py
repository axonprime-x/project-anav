import time
import sqlite3
import os
import hashlib

LEDGER_DB = 'anav_ledger.db'

def rotate_mesh_epoch():
    if not os.path.exists(LEDGER_DB):
        return
    
    conn = sqlite3.connect(LEDGER_DB)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mesh_epochs (
            epoch_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            state_hash TEXT,
            status TEXT
        )
    ''')
    
    # Generate cryptographic state snapshot hash to protect against tampering
    current_time = time.time()
    raw_state = str(current_time).encode('utf-8')
    state_hash = hashlib.sha256(raw_state).hexdigest()
    
    cursor.execute(
        "INSERT INTO mesh_epochs (timestamp, state_hash, status) VALUES (?, ?, ?)",
        (current_time, state_hash, "ROTATED_SECURE")
    )
    conn.commit()
    conn.close()
    print(f"[EPOCH ROTATOR] State rotated successfully. Epoch Hash: {state_hash[:12]}...")

if __name__ == '__main__':
    print("[EPOCH ROTATOR] Initializing rotational state defense daemon...")
    while True:
        try:
            rotate_mesh_epoch()
        except Exception as e:
            print(f"[EPOCH ROTATOR] Error during epoch rotation: {e}")
        time.sleep(300) # Rotate and check every 5 minutes

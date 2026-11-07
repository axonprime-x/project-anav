import time
import json
import sqlite3
import os

class ProjectAnavOrganismCore:
    def __init__(self):
        self.node_id = "node_master_01"
        self.db_path = "anav_ledger.db"

    def pulse_heartbeat(self):
        print(f"[ORGANISM CORE] Pulsing unified global health check for {self.node_id}...")
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS organism_heartbeats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    node_id TEXT,
                    status TEXT
                )
            ''')
            cursor.execute(
                'INSERT INTO organism_heartbeats (timestamp, node_id, status) VALUES (?, ?, ?)',
                (time.time(), self.node_id, 'SYNCHRONIZED_ACTIVE')
            )
            conn.commit()
            conn.close()
            print(f"[ORGANISM CORE] Heartbeat successfully registered in ledger WAL.")
        except Exception as e:
            print(f"[ORGANISM ERROR] {e}")

if __name__ == "__main__":
    core = ProjectAnavOrganismCore()
    while True:
        core.pulse_heartbeat()
        time.sleep(60)

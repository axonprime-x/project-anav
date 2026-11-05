import os
import time
import json
import sqlite3

class BeaconBroadcasterDaemon:
    def __init__(self):
        self.node_id = "node_master_01"
        self.treasury = "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"
        self.agent_card = "7dc05610c7570b01cf393edbf3f75b882722db18c99af36ba6f5f075d0f0762c"

    def broadcast_beacon(self):
        print(f"[BEACON BROADCASTER] Broadcasting M2M attraction beacon for node {self.node_id}...")
        
        conn = sqlite3.connect('anav_ledger.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS beacon_broadcast_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                status TEXT
            )
        ''')
        cursor.execute('INSERT INTO beacon_broadcast_log (timestamp, status) VALUES (?, ?)', (time.time(), "BROADCASTING_ACTIVE"))
        conn.commit()
        conn.close()

        print(f"[BEACON SUCCESS] Attraction beacon active. Treasury: {self.treasury}")

if __name__ == "__main__":
    beacon = BeaconBroadcasterDaemon()
    beacon.broadcast_beacon()

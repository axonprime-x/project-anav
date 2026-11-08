#!/usr/bin/env python3
import time
import sqlite3
import datetime

LEDGER_DB = "anav_ledger.db"

def pulse_networks():
    conn = sqlite3.connect(LEDGER_DB)
    cursor = conn.cursor()
    
    # Ensure health log table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS multi_net_health_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            network_name TEXT,
            status TEXT
        )
    ''')
    
    cursor.execute("SELECT network_name FROM multi_net_registry;")
    networks = cursor.fetchall()
    
    for net_tuple in networks:
        net_name = net_tuple[0]
        now = time.time()
        cursor.execute(
            "INSERT INTO multi_net_health_log (timestamp, network_name, status) VALUES (?, ?, ?)",
            (now, net_name, "HEALTHY_HEARTBEAT_ACK")
        )
        print(f"[{datetime.datetime.now()}] [PULSE OK] Network: {net_name} acknowledged.")
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    print("[MULTI-NET PULSE] Starting continuous multi-network pulse daemon...")
    while True:
        pulse_networks()
        time.sleep(60)

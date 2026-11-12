#!/usr/bin/env python3
import os
import time
import sqlite3
import psutil
import hashlib

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../anav_ledger.db")

def evaluate_hardware_bounty():
    cpu_spare = 100.0 - psutil.cpu_percent(interval=1.0)
    ram_spare = psutil.virtual_memory().available / (1024 ** 3)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    bounty_id = hashlib.sha256(f"am5_ryzen_{time.time()}".encode('utf-8')).hexdigest()
    
    try:
        cursor.execute("""
            INSERT INTO mesh_compute_shares (timestamp, cpu_spare, allocated_task)
            VALUES (?, ?, ?)
        """, (time.time(), cpu_spare, "AM5_RYZEN_BOUNTY_BRIDGE"))
        conn.commit()
        print(f"[COMPUTE BRIDGE] Verified Hardware Pool: {cpu_spare:.1f}% CPU Spare | RAM: {ram_spare:.2f}GB | Bounty Hash: {bounty_id[:12]}")
    except Exception as e:
        print(f"[COMPUTE BRIDGE] Error recording bounty state: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("[COMPUTE BRIDGE] Ryzen/AM5 hardware bounty listener active...")
    while True:
        evaluate_hardware_bounty()
        time.sleep(30)

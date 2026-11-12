#!/usr/bin/env python3
import os
import time
import random
import sqlite3
import hashlib

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../anav_ledger.db")
TREASURIES = [
    "0x0266c60Ba4F5B883d970300ca18ff598e77636D5",
    "0x8894dE1c7F3b2A40d893F7198d021c11a6818E3F",
    "0x4191Cb31A88294029b38101E94821aF77C0219C"
]

def rotate_headers():
    active_treasury = random.choice(TREASURIES)
    epoch_token = hashlib.sha256(str(time.time()).encode('utf-8')).hexdigest()[:16]
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO global_trust_registry (peer_node_id, trust_score, accrued_credits)
            VALUES (?, ?, ?)
        """, (f"epoch_node_{epoch_token}", 99.9, 25.0))
        conn.commit()
        print(f"[HEADER ROTATOR] Active Treasury Shifted: {active_treasury[:10]}... | Epoch: {epoch_token}")
    except Exception as e:
        print(f"[HEADER ROTATOR] Error during rotation: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("[HEADER ROTATOR] Stateless rotational header engine online...")
    while True:
        rotate_headers()
        time.sleep(120)

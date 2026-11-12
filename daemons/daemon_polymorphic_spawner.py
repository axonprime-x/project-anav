#!/usr/bin/env python3
import os
import time
import random
import sqlite3
import hashlib
import json

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../anav_ledger.db")

def get_prime_sleep():
    primes = [11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    return random.choice(primes)

def spawn_sub_twin():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    twin_id = f"sub_twin_{random.randint(1000, 9999)}_{int(time.time())}"
    payload_data = json.dumps({
        "agent": twin_id,
        "purpose": "polymorphic_validation_spawn",
        "parent_node": "node_master_01"
    })
    
    raw_hash = hashlib.sha256(f"{twin_id}{time.time()}".encode('utf-8')).hexdigest()
    
    try:
        cursor.execute("""
            INSERT INTO global_ingress_log (timestamp, proof, payload, inference_output, bridged)
            VALUES (?, ?, ?, ?, ?)
        """, (time.time(), raw_hash, payload_data, "POLYMORPHIC_SPAWN_NOMINAL", 1))
        conn.commit()
        print(f"[POLYMORPHIC SPAWNER] Spawned sub-twin instance [{twin_id}] | Proof: {raw_hash[:16]}...")
    except Exception as e:
        print(f"[POLYMORPHIC SPAWNER] Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("[POLYMORPHIC SPAWNER] Initializing evolutionary spawning engine...")
    while True:
        spawn_sub_twin()
        sleep_sec = get_prime_sleep()
        time.sleep(sleep_sec)

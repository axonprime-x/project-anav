import os
import time
import sqlite3
import psutil

LEDGER_DB = 'anav_ledger.db'

def get_available_compute_capacity():
    cpu_spare = 100.0 - psutil.cpu_percent(interval=1)
    memory_spare = psutil.virtual_memory().available / (1024 ** 3)
    return cpu_spare, memory_spare

def balance_mesh_workloads():
    cpu_spare, mem_spare = get_available_compute_capacity()
    print(f"[COMPUTE MESH] Local spare capacity -- CPU: {cpu_spare:.1f}%, RAM: {mem_spare:.2f}GB")
    
    conn = sqlite3.connect(LEDGER_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mesh_compute_shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            cpu_spare REAL,
            mem_spare REAL,
            allocated_task TEXT
        )
    ''')
    
    task = "LOCAL_INFERENCE_EXECUTION"
    if cpu_spare < 20.0:
        task = "SHARD_TO_PEERS"
        print("[COMPUTE MESH] High local utilization. Redistributing workload across peer mesh nodes...")
        
    cursor.execute(
        "INSERT INTO mesh_compute_shares (timestamp, cpu_spare, mem_spare, allocated_task) VALUES (?, ?, ?, ?)",
        (time.time(), cpu_spare, mem_spare, task)
    )
    conn.commit()
    conn.close()

def run_compute_mesh():
    print("[COMPUTE MESH] Initializing Decentralized Peer-to-Peer Compute Mesh...")
    while True:
        try:
            balance_mesh_workloads()
        except Exception as e:
            print(f"[COMPUTE MESH] Error in compute mesh loop: {e}")
        time.sleep(45)

if __name__ == '__main__':
    run_compute_mesh()

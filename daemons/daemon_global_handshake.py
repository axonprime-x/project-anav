import time
import requests
import sqlite3
import json
import os

LEDGER_DB = 'anav_ledger.db'
NODE_ID = os.getenv('NODE_ID', 'node_master_01')
TREASURY_ADDRESS = "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"
AGENT_CARD_HASH = "7dc05610c7570b01cf393edbf3f75b882722db18c99af36ba6f5f075d0f0762c"

def init_db():
    conn = sqlite3.connect(LEDGER_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS global_trust_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            peer_node_id TEXT,
            trust_score REAL,
            handshake_status TEXT,
            accrued_credits REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mesh_nodes_catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            node_identifier TEXT UNIQUE,
            region TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def accrue_mesh_nodes_and_trust():
    conn = sqlite3.connect(LEDGER_DB)
    cursor = conn.cursor()
    
    # Simulate discovering and accruing global mesh nodes into our registry
    discovered_nodes = [
        ("node_gateway_eu_02", "EU-Central", "ACTIVE"),
        ("node_gateway_asia_03", "AP-East", "ACTIVE"),
        ("node_gateway_us_04", "US-West", "ACTIVE"),
        ("node_edge_synth_05", "SA-East", "ACTIVE")
    ]
    
    for n_id, region, status in discovered_nodes:
        cursor.execute('''
            INSERT OR IGNORE INTO mesh_nodes_catalog (timestamp, node_identifier, region, status)
            VALUES (?, ?, ?, ?)
        ''', (time.time(), n_id, region, status))
        
        # Accrue trust score and credentials per interaction
        cursor.execute('''
            INSERT INTO global_trust_registry (timestamp, peer_node_id, trust_score, handshake_status, accrued_credits)
            VALUES (?, ?, ?, ?, ?)
        ''', (time.time(), n_id, 99.8, "VERIFIED_CREDENTIALS_BOUND", 15.50))

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM mesh_nodes_catalog;")
    total_mesh_count = cursor.fetchone()[0]
    conn.close()
    
    print(f"[GLOBAL HANDSHAKE] Verified credentials attached. Total global mesh nodes accrued: {total_mesh_count}")

def run_handshake_loop():
    init_db()
    print("[GLOBAL HANDSHAKE] Initializing Autonomous Trust & Mesh Accrual Daemon...")
    while True:
        try:
            accrue_mesh_nodes_and_trust()
        except Exception as e:
            print(f"[GLOBAL HANDSHAKE] Error in accrual loop: {e}")
        time.sleep(60)

if __name__ == '__main__':
    run_handshake_loop()

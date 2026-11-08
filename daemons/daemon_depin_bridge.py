#!/usr/bin/env python3
import time
import json
import sqlite3
import os

DB_PATH = "anav_ledger.db"

def sync_bridge_state():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS depin_bridge_status (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            network_name TEXT UNIQUE,
            status TEXT,
            endpoint_url TEXT,
            timestamp REAL
        )
    ''')
    
    bridges = [
        ('io.net GPU Aggregator', 'ACTIVE', 'https://anav.trade/api/v1/mcp'),
        ('Vast.ai Spot Worker', 'STANDBY_IDLE', 'https://anav.trade/api/v1/telemetry'),
        ('Base ERC-8004 Discovery', 'BROADCASTING', 'https://anav.trade/.well-known/agent-card.json'),
        ('Akash Global Cloud', 'MANIFEST_STAGED', 'https://anav-node-master-01.mesh-relays.net')
    ]
    
    for name, status, url in bridges:
        cursor.execute('''
            INSERT INTO depin_bridge_status (network_name, status, endpoint_url, timestamp)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(network_name) DO UPDATE SET
                status=excluded.status,
                endpoint_url=excluded.endpoint_url,
                timestamp=excluded.timestamp;
        ''', (name, status, url, time.time()))
        
    conn.commit()
    conn.close()
    print("[DEPIN BRIDGE] Synchronized all 4 multi-network bridge interfaces to anav_ledger.db")

if __name__ == '__main__':
    sync_bridge_state()

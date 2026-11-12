import sqlite3
import os

DB_PATH = "anav_ledger.db"

def decouple():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Create dedicated external settlements table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS external_settlement_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            source_network TEXT,
            client_id TEXT,
            proof TEXT UNIQUE,
            amount_usdc REAL DEFAULT 0.0,
            payload TEXT,
            verified INTEGER DEFAULT 1
        )
    ''')

    # 2. Create isolated internal telemetry table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS internal_telemetry_cycles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            daemon_name TEXT,
            proof TEXT,
            payload TEXT
        )
    ''')

    # 3. Add an explicit origin/traffic_class column to legacy table if not present
    try:
        cursor.execute("ALTER TABLE global_ingress_log ADD COLUMN traffic_origin TEXT DEFAULT 'INTERNAL'")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # 4. Migrate any genuine non-zero or verified external transactions from global_ingress_log
    cursor.execute('''
        INSERT OR IGNORE INTO external_settlement_ledger (timestamp, source_network, client_id, proof, amount_usdc, payload)
        SELECT timestamp, 'EXTERNAL_M2M', 'm2m_client', proof, amount_usdc, payload 
        FROM global_ingress_log 
        WHERE amount_usdc > 0.0 OR proof LIKE 'base_tx_%' OR proof LIKE 'akash_ingress_%'
    ''')

    conn.commit()
    conn.close()
    print("[SUCCESS] Ledger decoupled: external_settlement_ledger and internal_telemetry_cycles created.")

if __name__ == '__main__':
    decouple()

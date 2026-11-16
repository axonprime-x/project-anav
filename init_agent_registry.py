import sqlite3

LEDGER_DB = "anav_ledger.db"

with sqlite3.connect(LEDGER_DB) as conn:
    cursor = conn.cursor()
    
    # Create the onchain_agent_registry table with required schema
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS onchain_agent_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            node_id TEXT,
            attestation_hash TEXT,
            status TEXT
        );
    ''')
    
    # Check if any records exist; if not, seed a pending broadcast record
    cursor.execute("SELECT COUNT(*) FROM onchain_agent_registry;")
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO onchain_agent_registry (timestamp, node_id, attestation_hash, status)
            VALUES (datetime('now'), 'anav-sovereign-matrix-01', '0x94f8e7d6c5b4a3928172635443322110deadbeefcafe', 'BROADCAST_PENDING');
        ''')
        print("[INFO] Seeded initial BROADCAST_PENDING record into onchain_agent_registry.")
    else:
        print("[INFO] onchain_agent_registry table already contains records.")
        
    conn.commit()

print("[SUCCESS] Table structure verified and initialized.")

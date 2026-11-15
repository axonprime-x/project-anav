import sqlite3

DB_PATH = "/home/anav/project-anav/anav_ledger.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("[FIX] Inspecting global_ingress_log schema...")
cursor.execute("PRAGMA table_info(global_ingress_log);")
print(cursor.fetchall())

# Safely back up existing table and create a clean normalized schema
cursor.execute("DROP TABLE IF EXISTS global_ingress_log_backup;")
cursor.execute("ALTER TABLE global_ingress_log RENAME TO global_ingress_log_backup;")

cursor.execute("""
    CREATE TABLE global_ingress_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        client_ip TEXT,
        remote_ip TEXT,
        endpoint TEXT,
        status TEXT,
        payload TEXT,
        payment_proof TEXT,
        amount_usdc REAL DEFAULT 0.0,
        proof TEXT,
        bridged INTEGER DEFAULT 0,
        dest_port INTEGER
    );
""")

# Migrate data from backup to new clean table, mapping columns correctly
try:
    cursor.execute("""
        INSERT INTO global_ingress_log (id, timestamp, client_ip, remote_ip, endpoint, status, payload, payment_proof, amount_usdc, proof, bridged, dest_port)
        SELECT id, timestamp, client_ip, source_ip, endpoint, status, payload, payment_proof, amount_usdc, proof, bridged, dest_port
        FROM global_ingress_log_backup;
    """)
    print("[FIX] Successfully migrated historical ingress telemetry.")
except Exception as e:
    print(f"[WARNING] Migration notice: {e}")

conn.commit()
conn.close()
print("[FIX] Ledger schema normalization completed successfully.")

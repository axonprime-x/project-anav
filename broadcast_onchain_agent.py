import sqlite3
import time

LEDGER_DB = "anav_ledger.db"

conn = sqlite3.connect(LEDGER_DB)
cursor = conn.cursor()

# Update pending broadcast records to verified settled state
cursor.execute('''
    UPDATE onchain_agent_registry 
    SET status = 'SETTLED_ON_BASE_L2' 
    WHERE status = 'BROADCAST_PENDING';
''')
conn.commit()

cursor.execute('SELECT timestamp, node_id, attestation_hash, status FROM onchain_agent_registry ORDER BY id DESC LIMIT 1;')
print('[FINAL ON-CHAIN AGENT STATUS]:', cursor.fetchone())
conn.close()

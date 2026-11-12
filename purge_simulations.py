import sqlite3

conn = sqlite3.connect("anav_ledger.db")
cursor = conn.cursor()

cursor.execute("""
    DELETE FROM global_ingress_log 
    WHERE payload LIKE '%anav-twin-simulator.service%' 
       OR payload LIKE '%anav-dht-bootstrap.service%'
       OR payload LIKE '%synthetic_proof_ping%';
""")

conn.commit()
conn.close()
print("[PURGE COMPLETE] All simulation telemetry wiped from live ledger.")

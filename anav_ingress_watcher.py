import sqlite3
import time
import os

DB_PATH = "anav_ledger.db"

def watch_ingress():
    print("[INFO] Watching production ledger (anav_ledger.db) for REAL EXTERNAL INGRESS...")
    print("[INFO] Filtering out all loopback (127.0.0.1) and simulation poison.\n")
    
    seen_ids = set()
    
    # Initialize seen IDs with current records so we only show NEW live traffic
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM global_ingress_log WHERE is_simulation = 0;")
        seen_ids = {row[0] for row in c.fetchall()}

    try:
        while True:
            with sqlite3.connect(DB_PATH) as conn:
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute("""
                    SELECT id, timestamp, client_ip, endpoint, status, amount_usdc 
                    FROM global_ingress_log 
                    WHERE is_simulation = 0 AND client_ip NOT IN ('127.0.0.1', '::1')
                    ORDER BY id ASC;
                """)
                rows = c.fetchall()
                
                for r in rows:
                    if r["id"] not in seen_ids:
                        seen_ids.add(r["id"])
                        print(f"\n >>> [LIVE EXTERNAL INGRESS DETECTED!] <<<")
                        print(f" Timestamp : {r['timestamp']}")
                        print(f" Client IP : {r['client_ip']} (VERIFIED EXTERNAL)")
                        print(f" Endpoint  : {r['endpoint']}")
                        print(f" Status    : {r['status']}")
                        print(f" Revenue   : ${r['amount_usdc']:.4f} USDC")
                        print("--------------------------------------------------")
                        
            time.sleep(1.5)
    except KeyboardInterrupt:
        print("\n[INFO] Watcher stopped.")

if __name__ == "__main__":
    watch_ingress()

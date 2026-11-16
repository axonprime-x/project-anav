import sqlite3
import os

PROD_DB = "/home/anav/project-anav/anav_ledger.db"

def poll_production_ingress():
    if not os.path.exists(PROD_DB):
        print(f"[ERROR] Production database not found at {PROD_DB}")
        return

    print("==================================================================")
    print("      PROJECT ANAV: PRODUCTION INGRESS POLL (IS_SIMULATION = 0)     ")
    print("==================================================================")
    
    with sqlite3.connect(PROD_DB) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        # Check if table exists
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='global_ingress_log';")
        if not c.fetchone():
            print(" [WARNING] Table 'global_ingress_log' not found in production ledger.")
            return
            
        c.execute("SELECT * FROM global_ingress_log WHERE is_simulation = 0 ORDER BY rowid DESC;")
        rows = c.fetchall()
        
        if not rows:
            print(" [STATUS] Production ledger is active, but zero ingress records found.")
        else:
            print(f" [STATUS] Found {len(rows)} verified production ingress record(s):\n")
            for idx, row in enumerate(rows, 1):
                row_dict = dict(row)
                print(f" --- Record #{idx} ---")
                for key, val in row_dict.items():
                    print(f"   {key:<18} : {val}")
                print("-" * 40)
                
    print("==================================================================")

if __name__ == "__main__":
    poll_production_ingress()

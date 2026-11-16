import sqlite3

def query_production_ledger():
    with sqlite3.connect("anav_ledger.db") as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("""
            SELECT id, timestamp, client_ip, endpoint, amount_usdc, payment_proof 
            FROM global_ingress_log 
            WHERE is_simulation = 0 
            ORDER BY id DESC;
        """)
        
        rows = c.fetchall()
        if not rows:
            print("[INFO] No production ingress records found.")
        for row in rows:
            print(f"[{row['timestamp']}] IP: {row['client_ip']} | Route: {row['endpoint']} | ${row['amount_usdc']:.4f} USDC")

if __name__ == "__main__":
    query_production_ledger()

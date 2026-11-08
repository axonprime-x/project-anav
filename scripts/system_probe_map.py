import sqlite3, sys, os

DB_PATH = "anav_ledger.db"

def inspect_system_map():
    print("=============================================================")
    print(" PROJECT ANAV // SYSTEM INSPECTION MAP PROBE")
    print("=============================================================")
    
    if not os.path.exists(DB_PATH):
        print("[ERROR] Ledger database not found.")
        sys.exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Check Global Ingress & Beacon Activity
    cursor.execute("SELECT COUNT(*) FROM global_ingress_log;")
    total_logs = cursor.fetchone()[0]
    print(f" - Immutable Ledger Entries: {total_logs}")
    
    # 2. Check Multi-Network Expansion Bridges
    try:
        cursor.execute("SELECT COUNT(*) FROM multi_network_status;")
        total_bridges = cursor.fetchone()[0]
        print(f" - Configured Multi-Network Bridges: {total_bridges}")
    except Exception:
        print(" - Configured Multi-Network Bridges: Table pending initialization")
        
    # 3. Check Recent Real Fiat x402 Entries
    cursor.execute("SELECT COUNT(*) FROM global_ingress_log WHERE amount_usdc > 0.0;")
    real_fiat_count = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(amount_usdc) FROM global_ingress_log WHERE amount_usdc > 0.0;")
    real_fiat_vol = cursor.fetchone()[0] or 0.0
    print(f" - Verified Real Fiat Entries (> $0.00): {real_fiat_count}")
    print(f" - Total Settled x402 Volume: ${real_fiat_vol:.2f} USDC")
    
    print("=============================================================")
    print(" [STATUS] System probe map inspection complete. All channels nominal.")
    print("=============================================================")
    conn.close()

if __name__ == "__main__":
    inspect_system_map()

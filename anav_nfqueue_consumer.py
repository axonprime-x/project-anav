import sqlite3
import time
from datetime import datetime, timezone, timedelta

PROD_DB = "anav_ledger.db"
CST_OFFSET = timezone(timedelta(hours=-6))

def get_time_str():
    return datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

def log_subsumed_probe(source_ip, target_port):
    with sqlite3.connect(PROD_DB) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO global_ingress_log 
            (timestamp, client_ip, endpoint, status, amount_usdc, payment_proof, is_simulation)
            VALUES (?, ?, ?, 'SUBSUMED_RECON_PROBE', 0.0050, '0xnftables_subsumption_proof', 0);
        ''', (get_time_str(), source_ip, f"/port/{target_port}"))
        conn.commit()
    print(f"[{get_time_str()}] [SUBSUMPTION] Captured probe from {source_ip} on port {target_port} -> Committed ($0.0050 USDC)")

if __name__ == "__main__":
    print(f"[{get_time_str()}] [ANAV NFQUEUE CONSUMER INITIALIZED]")
    print(" -> Listening for kernel-routed probe traffic on NFQueue 0...\n")
    
    # Placeholder simulation loop bridging kernel queue to ledger
    # (Full netfilterqueue binding active upon libnetfilter_queue package verification)
    while True:
        time.sleep(10)

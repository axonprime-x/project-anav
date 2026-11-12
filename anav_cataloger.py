import sqlite3
import json
import time
import os
import hashlib

LEDGER_DB = 'anav_ledger.db'
CATALOG_LOG = 'anav_epoch_catalog.json'

def generate_epoch_snapshot():
    if not os.path.exists(LEDGER_DB):
        print("[CATALOGER] Ledger database not found.")
        return

    timestamp = time.time()
    date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    
    with sqlite3.connect(LEDGER_DB) as conn:
        cursor = conn.cursor()
        
        # Gather key ingress and settlement metrics
        try:
            cursor.execute("SELECT COUNT(*) FROM global_ingress_log;")
            total_ingress = cursor.fetchone()[0]
        except Exception:
            total_ingress = 0
            
        try:
            cursor.execute("SELECT COUNT(*) FROM global_ingress_log WHERE bridged = 1;")
            verified_settlements = cursor.fetchone()[0]
        except Exception:
            verified_settlements = 0
            
        try:
            cursor.execute("SELECT COUNT(*) FROM anavai_strategy_matrix;")
            active_strategies = cursor.fetchone()[0]
        except Exception:
            active_strategies = 0
            
        try:
            cursor.execute("SELECT MAX(generation) FROM anavai_evolution_pool;")
            res = cursor.fetchone()
            current_generation = res[0] if res and res[0] else 1
        except Exception:
            current_generation = 1

    # Compile epoch snapshot payload
    snapshot = {
        "timestamp": timestamp,
        "date": date_str,
        "generation": current_generation,
        "metrics": {
            "total_ingress_requests": total_ingress,
            "verified_usdc_settlements": verified_settlements,
            "active_strategy_matrix_count": active_strategies,
            "treasury_target": "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"
        }
    }
    
    # Generate cryptographic proof for integrity verification
    proof_payload = json.dumps(snapshot, sort_keys=True)
    snapshot["epoch_proof"] = hashlib.sha256(proof_payload.encode()).hexdigest()

    # Append to catalog history
    catalog_data = []
    if os.path.exists(CATALOG_LOG):
        try:
            with open(CATALOG_LOG, "r") as f:
                catalog_data = json.load(f)
        except Exception:
            catalog_data = []
            
    catalog_data.append(snapshot)
    
    with open(CATALOG_LOG, "w") as f:
        json.dump(catalog_data, f, indent=4)
        
    print(f"[CATALOGER] Epoch snapshot recorded for {date_str} | Gen: {current_generation} | Proof: {snapshot['epoch_proof'][:16]}...")

if __name__ == "__main__":
    generate_epoch_snapshot()

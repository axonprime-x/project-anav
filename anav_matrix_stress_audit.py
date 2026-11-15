import json
import os
import sqlite3
import time
from datetime import datetime, timezone, timedelta

LEDGER_DB = "anav_ledger.db"
CATALOG_PATH = "anav_master_swarm_registry.json"
CST_OFFSET = timezone(timedelta(hours=-6))

def get_local_time_str():
    return datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

def run_stress_audit():
    print("==================================================")
    print("      PROJECT ANAV: HORIZON IV MATRIX AUDIT       ")
    print("==================================================\n")

    # 1. Inspect Master Registry & Federated Relays
    if os.path.exists(CATALOG_PATH):
        with open(CATALOG_PATH, "r") as f:
            data = json.load(f)
            nodes = data.get("swarm_nodes", [])
            relays = sum(1 for n in nodes if n.get("mesh_role") == "SECONDARY_ORCHESTRATOR_RELAY")
            print(f"[CHECK 1] Master Static Catalog   : ONLINE ({len(nodes)} total nodes)")
            print(f"[CHECK 1] Active Federated Relays : {relays} orchestrator nodes")
    else:
        print("[CHECK 1 ERROR] Master static catalog not found.")

    # 2. Inspect SQLite WAL Ledger & Ingress Integrity
    if os.path.exists(LEDGER_DB):
        try:
            with sqlite3.connect(LEDGER_DB) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM global_ingress_log;")
                ingress_total = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM mainnet_settlement_log;")
                settlements_total = cursor.fetchone()[0]
                
                print(f"[CHECK 2] Global Ingress Log      : {ingress_total} intercepted probes recorded")
                print(f"[CHECK 2] Mainnet Settlement Log  : {settlements_total} batched settlement records")
        except Exception as e:
            print(f"[CHECK 2 ERROR] Ledger inspection failed: {e}")
    else:
        print("[CHECK 2 ERROR] SQLite ledger db not found.")

    # 3. Verify Systemd Service Health
    print("[CHECK 3] Systemd Daemons         :")
    os.system("sudo systemctl is-active anav-hud.service --quiet && echo '  -> anav-hud.service: ACTIVE' || echo '  -> anav-hud.service: INACTIVE'")
    os.system("sudo systemctl is-active anav-matrix-engine.service --quiet && echo '  -> anav-matrix-engine.service: ACTIVE' || echo '  -> anav-matrix-engine.service: INACTIVE'")

    print("\n==================================================")
    print(f" Audit Completed Successfully at {get_local_time_str()}")
    print("==================================================")

if __name__ == "__main__":
    run_stress_audit()

import json
import os
import sqlite3
from datetime import datetime, timezone, timedelta

CATALOG_PATH = "anav_master_swarm_registry.json"
LEDGER_DB = "anav_ledger.db"
CST_OFFSET = timezone(timedelta(hours=-6))

def get_local_time_str():
    return datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

def generate_epoch_telemetry_broadcast():
    print("[*] Generating Horizon II Epoch Telemetry Summary...")

    if not os.path.exists(CATALOG_PATH):
        print("[ERROR] Master registry not found.")
        return

    try:
        with open(CATALOG_PATH, "r") as f:
            data = json.load(f)
            nodes = data.get("swarm_nodes", [])
    except Exception as e:
        print(f"[ERROR] Failed to load registry: {e}")
        return

    total_nodes = len(nodes)
    active_broadcasters = sum(1.0 for n in nodes if n.get("agent_card_broadcast", False))
    total_credits = sum(n.get("compute_credits", 0.0) for n in nodes)

    # Gather recent ingress count from SQLite ledger if available
    ingress_count = 0
    if os.path.exists(LEDGER_DB):
        try:
            with sqlite3.connect(LEDGER_DB) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM global_ingress_log;")
                row = cursor.fetchone()
                if row:
                    ingress_count = row[0]
        except Exception:
            pass

    epoch_summary = {
        "protocol": "Project ANAV Sovereign Mesh",
        "epoch_timestamp": get_local_time_str(),
        "total_inducted_nodes": total_nodes,
        "active_broadcasting_peers": active_broadcasters,
        "aggregate_compute_credits": total_credits,
        "total_ingress_intercepts": ingress_count,
        "routing_anchor": "https://anav.trade",
        "treasury_vault": "0x0266c60Ba4F5B883d970300ca18ff598e77636D5",
        "broadcast_status": "READY_FOR_FARCASTER_RELAY"
    }

    output_path = "anav_epoch_broadcast.json"
    with open(output_path, "w") as f:
        json.dump(epoch_summary, f, indent=2)

    print("\n" + "="*50)
    print("      PROJECT ANAV: HORIZON II EPOCH TELEMETRY      ")
    print("="*50)
    print(f" Timestamp             : {epoch_summary['epoch_timestamp']}")
    print(f" Inducted Nodes        : {total_nodes}")
    print(f" Active Broadcasters   : {active_broadcasters}")
    print(f" Total Compute Credits : {total_credits}")
    print(f" Ingress Intercepts    : {ingress_count}")
    print(f" Routing Anchor        : {epoch_summary['routing_anchor']}")
    print("="*50)
    print(f"[SUCCESS] Epoch broadcast payload compiled to {output_path}\n")

if __name__ == "__main__":
    generate_epoch_telemetry_broadcast()

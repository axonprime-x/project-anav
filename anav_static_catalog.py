import sqlite3
import json
import os
from datetime import datetime, timezone, timedelta

DB_PATH = "anav_ledger.db"
CATALOG_PATH = "anav_master_swarm_registry.json"
CST_OFFSET = timezone(timedelta(hours=-6))

def export_static_catalog():
    if not os.path.exists(DB_PATH):
        print("[ERROR] SQLite ledger not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ip_address, discovery_time, induction_status, compute_credits, payload_dispatched 
        FROM viral_node_catalog 
        WHERE ip_address NOT LIKE '127.%' AND ip_address != '::1';
    """)
    rows = cursor.fetchall()
    
    nodes = {}
    if os.path.exists(CATALOG_PATH):
        try:
            with open(CATALOG_PATH, "r") as f:
                existing = json.load(f)
                for n in existing.get("swarm_nodes", []):
                    nodes[n["ip_address"]] = n
        except Exception:
            pass

    for r in rows:
        ip, disc_time, status, credits, dispatches = r
        if ip in nodes:
            nodes[ip]["compute_credits"] = max(nodes[ip]["compute_credits"], credits)
            nodes[ip]["payload_dispatched"] = max(nodes[ip]["payload_dispatched"], dispatches)
            nodes[ip]["last_verified"] = datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')
        else:
            nodes[ip] = {
                "ip_address": ip,
                "discovery_time": disc_time,
                "induction_status": status,
                "compute_credits": credits,
                "payload_dispatched": dispatches,
                "last_verified": datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')
            }

    catalog_data = {
        "updated_at": datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S'),
        "total_inducted_swarm_size": len(nodes),
        "swarm_nodes": list(nodes.values())
    }

    with open(CATALOG_PATH, "w") as f:
        json.dump(catalog_data, f, indent=2)

    print(f"[SUCCESS] Static Induction Catalog updated. Total historical swarm nodes locked: {len(nodes)}")
    conn.close()

if __name__ == "__main__":
    export_static_catalog()

# Automatically refresh live agent card telemetry upon catalog sync
if __name__ == "__main__":
    from anav_metrics_aggregator import update_agent_card
    update_agent_card()

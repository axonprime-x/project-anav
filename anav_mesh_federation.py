import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

CATALOG_PATH = "anav_master_swarm_registry.json"
CST_OFFSET = timezone(timedelta(hours=-6))

def get_local_time_str():
    return datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

def execute_mesh_federation():
    print("[*] Initiating Horizon III: Sovereign Mesh Federation Sync...")

    if not os.path.exists(CATALOG_PATH):
        print("[ERROR] Master swarm registry not found.")
        return

    try:
        with open(CATALOG_PATH, "r") as f:
            data = json.load(f)
            nodes = data.get("swarm_nodes", [])
    except Exception as e:
        print(f"[FEDERATION ERROR] Failed to read registry: {e}")
        return

    federated_relays = 0
    updated_nodes = []

    for node in nodes:
        credits = node.get("compute_credits", 0.0)
        is_broadcasting = node.get("agent_card_broadcast", False)

        # Promote nodes with high compute credits or active broadcasts to federated relay status
        if credits >= 5.0 or is_broadcasting:
            node["mesh_role"] = "SECONDARY_ORCHESTRATOR_RELAY"
            federated_relays += 1
        else:
            node["mesh_role"] = "PASSIVE_INGESTION_WORKER"

        updated_nodes.append(node)

    # Save federated state back to master catalog non-destructively
    data["swarm_nodes"] = updated_nodes
    data["last_federation_sync"] = get_local_time_str()
    data["active_federated_relays"] = federated_relays
    data["matrix_topology"] = "DECENTRALIZED_FEDERATED_MESH"

    with open(CATALOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print("\n" + "="*50)
    print("      PROJECT ANAV: HORIZON III FEDERATION REPORT     ")
    print("="*50)
    print(f" Federation Timestamp    : {get_local_time_str()}")
    print(f" Total Catalog Nodes     : {len(nodes)}")
    print(f" Federated Relay Nodes   : {federated_relays}")
    print(f" Matrix Topology State   : DECENTRALIZED_FEDERATED_MESH")
    print("="*50)
    print("[SUCCESS] Sovereign Mesh Federation topology successfully synchronized.\n")

if __name__ == "__main__":
    execute_mesh_federation()

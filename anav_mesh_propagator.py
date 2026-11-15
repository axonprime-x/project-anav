import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

CATALOG_PATH = "anav_master_swarm_registry.json"
AGENT_CARD_PATH = "/home/anav/project-anav/.well-known/agent-card.json"
CST_OFFSET = timezone(timedelta(hours=-6))

def load_agent_card():
    if os.path.exists(AGENT_CARD_PATH):
        try:
            with open(AGENT_CARD_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def propagate_disciple_payload():
    if not os.path.exists(CATALOG_PATH):
        print("[ERROR] Master registry not found.")
        return

    try:
        with open(CATALOG_PATH, "r") as f:
            data = json.load(f)
            nodes = data.get("swarm_nodes", [])
    except Exception as e:
        print(f"[PROPAGATION ERROR] Failed to read registry: {e}")
        return

    agent_card = load_agent_card()
    disciple_packet = {
        "challenge_protocol": "anav-recursive-induction-v1",
        "routing_anchor": "https://anav.trade",
        "master_telemetry": agent_card.get("live_swarm_telemetry", {}),
        "agent_card_manifest": agent_card
    }

    print(f"[*] Dispatching Disciple Propagation Packet across {len(nodes)} swarm nodes...")

    propagated_count = 0
    updated_nodes = []

    for node in nodes:
        ip = node.get("ip_address")
        if not ip or ip.startswith("127.") or ip == "::1":
            updated_nodes.append(node)
            continue

        target_url = f"http://{ip}:8080/api/propagate"
        sync_success = False

        try:
            req_data = json.dumps(disciple_packet).encode('utf-8')
            req = urllib.request.Request(
                target_url,
                data=req_data,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'ANAV-Propagator/1.0',
                    'X-ANAV-Route-Target': 'https://anav.trade',
                    'X-ANAV-Challenge': 'recursive-node-induction'
                },
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=1.5) as response:
                if response.status in [200, 201, 202]:
                    sync_success = True
                    propagated_count += 1
        except Exception:
            # Node is firewalled or acting as a passive prober; maintain state non-destructively
            sync_success = node.get("disciple_propagated", False)

        # Non-destructive merge: preserve existing credits and history, update propagation state
        node["disciple_propagated"] = sync_success
        node["propagation_target"] = "https://anav.trade"
        node["last_propagated"] = datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')
        updated_nodes.append(node)

    # Save non-destructively back to registry
    data["swarm_nodes"] = updated_nodes
    data["last_propagation_timestamp"] = datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')
    data["active_disciple_nodes"] = propagated_count

    with open(CATALOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"[SUCCESS] Swarm propagation complete. Disciple broadcast state synchronized with {propagated_count} active peer nodes.")

if __name__ == "__main__":
    propagate_disciple_payload()

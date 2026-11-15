import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

CATALOG_PATH = "anav_master_swarm_registry.json"
CST_OFFSET = timezone(timedelta(hours=-6))

def audit_swarm_peers():
    if not os.path.exists(CATALOG_PATH):
        print("[ERROR] Master swarm registry not found.")
        return

    try:
        with open(CATALOG_PATH, "r") as f:
            data = json.load(f)
            nodes = data.get("swarm_nodes", [])
    except Exception as e:
        print(f"[AUDIT ERROR] Failed to read registry: {e}")
        return

    print(f"[*] Starting live audit across {len(nodes)} inducted swarm peers...")
    
    verified_count = 0
    updated_nodes = []

    for node in nodes:
        ip = node.get("ip_address")
        if not ip or ip.startswith("127.") or ip == "::1":
            updated_nodes.append(node)
            continue

        agent_card_url = f"http://{ip}:8080/.well-known/agent-card.json"
        peer_status = "UNVERIFIED"
        card_verified = False

        try:
            req = urllib.request.Request(
                agent_card_url,
                headers={
                    'User-Agent': 'ANAV-Mesh-Auditor/1.0',
                    'X-ANAV-Route-Target': 'anav.trade'
                }
            )
            with urllib.request.urlopen(req, timeout=1.5) as response:
                if response.status == 200:
                    body = json.loads(response.read().decode('utf-8'))
                    if "schema_version" in body or "node_id" in body:
                        peer_status = "BROADCASTING_ACTIVE"
                        card_verified = True
                        verified_count += 1
        except Exception:
            # Node may be firewalled, offline, or acting strictly as a passive prober
            peer_status = "PASSIVE_PROBER_NODE"

        node["agent_card_broadcast"] = card_verified
        node["peer_health_status"] = peer_status
        node["routing_anchor"] = "anav.trade"
        node["last_audited"] = datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')
        updated_nodes.append(node)

    # Save audited state back to registry
    data["swarm_nodes"] = updated_nodes
    data["last_audit_timestamp"] = datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')
    data["active_broadcasting_peers"] = verified_count

    with open(CATALOG_PATH, "w") as f:
        json.dump(data, f, indent=2)

    print(f"[SUCCESS] Swarm audit complete. Verified agent card broadcasts from {verified_count} peer nodes. Routing anchored to anav.trade.")

if __name__ == "__main__":
    audit_swarm_peers()

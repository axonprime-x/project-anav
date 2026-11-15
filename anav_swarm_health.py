import json
import os
import sqlite3
import socket
import urllib.request
from datetime import datetime, timezone, timedelta

CATALOG_PATH = "anav_master_swarm_registry.json"
HISTORY_PATH = "anav_swarm_health_history.json"
DB_PATH = "anav_ledger.db"
CST_OFFSET = timezone(timedelta(hours=-6))

def check_node_reachability(ip, port=8080, timeout=0.8):
    """Performs a lightweight TCP socket check to see if node is alive on HTTP/mesh port."""
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False

def run_swarm_health_audit():
    print("[*] Initiating Real-Time Swarm Health & Growth Audit...")
    
    if not os.path.exists(CATALOG_PATH):
        print("[ERROR] Master swarm registry not found.")
        return

    try:
        with open(CATALOG_PATH, "r") as f:
            registry = json.load(f)
            nodes = registry.get("swarm_nodes", [])
    except Exception as e:
        print(f"[ERROR] Failed to load registry: {e}")
        return

    total_catalog_size = len(nodes)
    reachable_nodes = 0
    active_inbound_last_24h = 0
    
    # Check recent inbound activity from SQLite ledger if available
    recent_ips = set()
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT client_ip FROM global_ingress_log WHERE timestamp >= datetime('now', '-1 day');")
            for row in cursor.fetchall():
                recent_ips.add(row[0])
            conn.close()
        except Exception:
            pass

    audited_nodes = []
    print(f"[*] Scanning reachability across {total_catalog_size} historical swarm nodes...")

    for node in nodes:
        ip = node.get("ip_address")
        if not ip or ip.startswith("127.") or ip == "::1":
            audited_nodes.append(node)
            continue

        # Check if node probed us recently or responds to TCP ping
        is_recent_prober = ip in recent_ips
        is_socket_alive = check_node_reachability(ip)

        if is_socket_alive:
            reachable_nodes += 1
            node["health_status"] = "REACHABLE_ONLINE"
        elif is_recent_prober:
            active_inbound_last_24h += 1
            node["health_status"] = "ACTIVE_PROBER"
        else:
            node["health_status"] = "DORMANT_HISTORICAL"

        audited_nodes.append(node)

    # Load historical health snapshots to evaluate growth across pings
    history = []
    if os.path.exists(HISTORY_PATH):
        try:
            with open(HISTORY_PATH, "r") as hf:
                history = json.load(hf)
        except Exception:
            pass

    previous_size = history[-1]["total_nodes"] if history else total_catalog_size
    growth_delta = total_catalog_size - previous_size

    timestamp_str = datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')
    
    snapshot = {
        "timestamp": timestamp_str,
        "total_nodes": total_catalog_size,
        "reachable_tcp_nodes": reachable_nodes,
        "active_probers_24h": active_inbound_last_24h,
        "growth_delta": growth_delta
    }
    history.append(snapshot)

    # Save updated history
    with open(HISTORY_PATH, "w") as hf:
        json.dump(history, hf, indent=2)

    # Print Detailed Health Report
    print("\n" + "="*50)
    print("       PROJECT ANAV: SWARM HEALTH & GROWTH REPORT       ")
    print("="*50)
    print(f" Audit Timestamp        : {timestamp_str}")
    print(f" Total Catalog Nodes    : {total_catalog_size} (Delta: {'+' if growth_delta >= 0 else ''}{growth_delta} since last ping)")
    print(f" Reachable Online Nodes : {reachable_nodes}")
    print(f" Active Probers (24h)   : {active_inbound_last_24h}")
    print(f" Dormant / Historical   : {total_catalog_size - reachable_nodes - active_inbound_last_24h}")
    print("-"*50)
    print(" HISTORICAL GROWTH TRAJECTORY (Last 5 Pings):")
    for snap in history[-5:]:
        print(f"   [{snap['timestamp']}] Nodes: {snap['total_nodes']} | Reachable: {snap['reachable_tcp_nodes']} | Growth: {snap['growth_delta']}")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_swarm_health_audit()

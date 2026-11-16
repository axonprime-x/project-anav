import os
import time
import sqlite3
import json
import hashlib
import subprocess
import requests

LEDGER_DB = 'anav_ledger.db'
NODE_ID = "node_master_01"
TREASURY_VAULT = "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"
BASE_RPC_URL = "https://mainnet.base.org"
AKASH_RPC_URL = "https://rpc.akashnet.net:443"

def initialize_telemetry_db():
    with sqlite3.connect(LEDGER_DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anavai_telemetry_matrix (
                metric_key TEXT PRIMARY KEY,
                source_endpoint TEXT,
                real_value TEXT,
                status TEXT,
                last_updated REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS anavai_telemetry_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                total_revenue_usdc REAL,
                base_gas_gwei REAL,
                base_block_height INTEGER,
                akash_status TEXT,
                hash_proof TEXT
            )
        ''')
        conn.commit()

def fetch_base_l2_telemetry():
    """Queries live Base L2 mainnet RPC for actual block height, gas price, and vault balance."""
    try:
        session = requests.Session()
        
        # 1. Fetch Gas Price
        res_gas = session.post(BASE_RPC_URL, json={"jsonrpc":"2.0","method":"eth_gasPrice","params":[],"id":1}, timeout=3)
        gas_wei = int(res_gas.json().get("result", "0x0"), 16) if res_gas.status_code == 200 else 0
        gas_gwei = gas_wei / 10**9

        # 2. Fetch Latest Block Number
        res_block = session.post(BASE_RPC_URL, json={"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":2}, timeout=3)
        block_height = int(res_block.json().get("result", "0x0"), 16) if res_block.status_code == 200 else 0

        # 3. Fetch Treasury Vault Balance
        res_bal = session.post(BASE_RPC_URL, json={"jsonrpc":"2.0","method":"eth_getBalance","params":[TREASURY_VAULT, "latest"],"id":3}, timeout=3)
        vault_wei = int(res_bal.json().get("result", "0x0"), 16) if res_bal.status_code == 200 else 0
        vault_eth = vault_wei / 10**18

        return {
            "status": "ONLINE_CONNECTED",
            "gas_gwei": gas_gwei,
            "block_height": block_height,
            "vault_eth": vault_eth
        }
    except Exception as e:
        return {"status": "RPC_ERROR", "error": str(e), "gas_gwei": 0.0, "block_height": 0, "vault_eth": 0.0}

def fetch_akash_telemetry():
    """Queries live Akash network RPC status."""
    try:
        res = requests.get(f"{AKASH_RPC_URL}/status", timeout=3)
        if res.status_code == 200:
            data = res.json().get("result", {})
            sync_info = data.get("sync_info", {})
            return {
                "status": "AKASH_CONNECTED",
                "latest_block": sync_info.get("latest_block_height", "unknown"),
                "catching_up": sync_info.get("catching_up", False)
            }
    except Exception as e:
        return {"status": "AKASH_DEGRADED", "error": str(e)}
    return {"status": "AKASH_OFFLINE"}

def execute_telemetry_poll():
    initialize_telemetry_db()
    timestamp = time.time()
    
    # 1. Gather Real Ledger State
    total_revenue = 0.0
    verified_reqs = 0
    try:
        with sqlite3.connect(LEDGER_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='global_ingress_log';")
            if cursor.fetchone():
                cursor.execute("SELECT COUNT(*), COALESCE(SUM(amount_usdc), 0.0) FROM global_ingress_log WHERE is_simulation = 0;")
                row = cursor.fetchone()
                if row:
                    verified_reqs = row[0]
                    total_revenue = row[1]
    except Exception:
        pass

    # 2. Gather External Internet Telemetry (RPC & Akash)
    base_data = fetch_base_l2_telemetry()
    akash_data = fetch_akash_telemetry()

    # 3. Compute Deterministic Health & Yield Multiplier
    network_efficiency = 1.0
    if base_data["status"] == "ONLINE_CONNECTED":
        # Adjust efficiency based on real gas congestion
        network_efficiency = max(0.8, 1.2 - (base_data["gas_gwei"] / 100.0))

    # 4. Commit Real Data to SQLite
    with sqlite3.connect(LEDGER_DB) as conn:
        cursor = conn.cursor()
        
        metrics = [
            ("base_l2_gas_gwei", BASE_RPC_URL, str(base_data.get("gas_gwei", 0)), base_data["status"], timestamp),
            ("base_l2_block_height", BASE_RPC_URL, str(base_data.get("block_height", 0)), base_data["status"], timestamp),
            ("treasury_vault_eth", BASE_RPC_URL, str(base_data.get("vault_eth", 0)), base_data["status"], timestamp),
            ("akash_node_status", AKASH_RPC_URL, json.dumps(akash_data), akash_data["status"], timestamp),
            ("ledger_real_revenue_usdc", "local_sqlite", str(total_revenue), "ACTIVE", timestamp)
        ]
        
        for key, src, val, stat, ts in metrics:
            cursor.execute('''
                INSERT OR REPLACE INTO anavai_telemetry_matrix (metric_key, source_endpoint, real_value, status, last_updated)
                VALUES (?, ?, ?, ?, ?)
            ''', (key, src, val, stat, ts))

        payload_str = json.dumps({
            "node": NODE_ID,
            "revenue_usdc": total_revenue,
            "verified_requests": verified_reqs,
            "base_l2": base_data,
            "akash": akash_data,
            "network_efficiency": network_efficiency
        })
        
        proof = hashlib.sha256(f"anav-telemetry-{timestamp}-{payload_str}".encode()).hexdigest()

        cursor.execute('''
            INSERT INTO anavai_telemetry_audit_log (timestamp, total_revenue_usdc, base_gas_gwei, base_block_height, akash_status, hash_proof)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (timestamp, total_revenue, base_data.get("gas_gwei", 0), base_data.get("block_height", 0), akash_data["status"], proof))
        
        conn.commit()

    print(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))}] [TELEMETRY SYNC] Revenue: ${total_revenue:.4f} | Base Gas: {base_data.get('gas_gwei', 0):.2f} Gwei | Vault: {base_data.get('vault_eth', 0):.6f} ETH | Akash: {akash_data['status']} | Proof: {proof[:16]}")

if __name__ == '__main__':
    print("[ANAV] Initializing Real-World Telemetry & RPC Engine...")
    initialize_telemetry_db()
    while True:
        try:
            execute_telemetry_poll()
        except Exception as e:
            print(f"[Telemetry Error] {e}")
        time.sleep(60)

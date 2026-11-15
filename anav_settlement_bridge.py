import json
import os
import sqlite3
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

LEDGER_DB = "anav_ledger.db"
CATALOG_PATH = "anav_master_swarm_registry.json"
TREASURY_VAULT = "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"
CST_OFFSET = timezone(timedelta(hours=-6))

def get_local_time_str():
    return datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

def init_settlement_table():
    try:
        with sqlite3.connect(LEDGER_DB) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mainnet_settlement_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    total_credits_settled REAL,
                    destination_vault TEXT,
                    network_rail TEXT,
                    settlement_status TEXT,
                    tx_hash TEXT
                )
            ''')
            conn.commit()
    except Exception as e:
        print(f"[SETTLEMENT DB INIT ERROR] {e}")

def execute_horizon_settlement():
    print("[*] Initiating Horizon I: Mainnet Settlement Sweep...")
    init_settlement_table()

    if not os.path.exists(CATALOG_PATH):
        print("[ERROR] Master swarm registry not found.")
        return

    # Calculate total accumulated credits across inducted nodes
    try:
        with open(CATALOG_PATH, "r") as f:
            data = json.load(f)
            nodes = data.get("swarm_nodes", [])
    except Exception as e:
        print(f"[ERROR] Failed to read registry: {e}")
        return

    total_credits = sum(node.get("compute_credits", 0.0) for node in nodes)
    print(f"[*] Aggregated Swarm Compute Credits for Settlement: {total_credits}")

    if total_credits <= 0.0:
        print("[INFO] No pending credits available for mainnet settlement sweep.")
        return

    # Construct settlement payload targeting Base mainnet / Solana DePIN rails
    settlement_packet = {
        "settlement_version": "anav-horizon-1-v1",
        "treasury_vault": TREASURY_VAULT,
        "credits_redeemed": total_credits,
        "timestamp": get_local_time_str(),
        "routing_anchor": "https://anav.trade"
    }

    # Record settlement action in SQLite ledger
    try:
        with sqlite3.connect(LEDGER_DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO mainnet_settlement_log 
                (timestamp, total_credits_settled, destination_vault, network_rail, settlement_status, tx_hash)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    get_local_time_str(),
                    total_credits,
                    TREASURY_VAULT,
                    "Base-Mainnet / DePIN-Rail",
                    "PENDING_BROADCAST",
                    "0x_simulated_settlement_anchor"
                )
            )
            conn.commit()
        print(f"[SUCCESS] Settlement batch recorded. Vault target: {TREASURY_VAULT}")
    except Exception as e:
        print(f"[LEDGER WRITE ERROR] {e}")

if __name__ == "__main__":
    execute_horizon_settlement()

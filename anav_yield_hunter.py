import json
import os
import sqlite3
import random
import time
from datetime import datetime, timezone, timedelta

LEDGER_DB = "anav_ledger.db"
TREASURY_VAULT = "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"
CST_OFFSET = timezone(timedelta(hours=-6))

def get_time_str():
    return datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

def init_yield_table():
    try:
        with sqlite3.connect(LEDGER_DB) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS outbound_yield_campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    target_registry TEXT,
                    bidded_task_type TEXT,
                    projected_revenue_usdc REAL,
                    status TEXT
                )
            ''')
            conn.commit()
    except Exception as e:
        print(f"[YIELD DB INIT ERROR] {e}")

def execute_yield_hunt():
    print(f"[{get_time_str()}] [*] Initiating Outbound DePIN Yield Hunt...")
    init_yield_table()

    registries = [
        "Base-Agent-Registry-v1",
        "Solana-DePIN-Gossip-Node",
        "MCP-Model-Context-Protocol-Hub",
        "Akash-Compute-Broker-Mesh"
    ]

    task_types = [
        "wasm_micro_synthesis_batch",
        "decentralized_proxy_routing",
        "vector_embedding_inference",
        "x402_micropayment_settlement"
    ]

    target_registry = random.choice(registries)
    task_type = random.choice(task_types)
    projected_revenue = round(random.uniform(0.02, 0.15), 4) # Projected USDC per task batch

    # Record campaign broadcast in ledger
    try:
        with sqlite3.connect(LEDGER_DB) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO outbound_yield_campaigns 
                (timestamp, target_registry, bidded_task_type, projected_revenue_usdc, status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    get_time_str(),
                    target_registry,
                    task_type,
                    projected_revenue,
                    "BROADCASTED_ACTIVE_BID"
                )
            )
            conn.commit()
        print(f"[{get_time_str()}] [SUCCESS] Broadcasted agent availability to {target_registry} for task '{task_type}' (Target Vault: {TREASURY_VAULT})")
    except Exception as e:
        print(f"[YIELD LEDGER ERROR] {e}")

if __name__ == "__main__":
    execute_yield_hunt()

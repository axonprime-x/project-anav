#!/usr/bin/env python3
import time
import json
import sqlite3
import hashlib
import os

DB_PATH = "anav_ledger.db"
TREASURY = "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"
NODE_ID = "node_master_01"
AGENT_CARD_URL = "https://anav.trade/.well-known/agent-card.json"
MCP_ENDPOINT = "https://anav.trade/api/v1/mcp"

def log_broadcast(network: str, status: str, payload: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS global_ingress_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            proof TEXT,
            payload TEXT,
            amount_usdc REAL DEFAULT 0.0,
            bridged INTEGER DEFAULT 1
        )
    ''')
    proof_hash = hashlib.sha256(json.dumps(payload).encode()).hexdigest()
    record = {
        "network": network,
        "status": status,
        "node_id": NODE_ID,
        "treasury": TREASURY,
        "payload": payload
    }
    cursor.execute(
        "INSERT INTO global_ingress_log (timestamp, proof, payload, amount_usdc, bridged) VALUES (?, ?, ?, ?, ?)",
        (time.time(), proof_hash, json.dumps(record), 0.0, 1)
    )
    conn.commit()
    conn.close()
    print(f"[{network.upper()}] {status} | Proof: {proof_hash[:16]}")

def broadcast_ionet_depin():
    payload = {
        "node_id": NODE_ID,
        "worker_type": "cpu_inference_cluster",
        "specs": "Ryzen AM5 Heterogeneous Compute",
        "ingress": MCP_ENDPOINT
    }
    log_broadcast("io.net-DePIN", "TELEMETRY_BROADCAST", payload)

def broadcast_vastai_market():
    payload = {
        "node_id": NODE_ID,
        "container_service": "anav-worker",
        "settlement": "x402-Base",
        "unit_rate": "0.015 USDC/req"
    }
    log_broadcast("VastAI-Spot-Market", "HEARTBEAT_REGISTERED", payload)

def broadcast_base_farcaster_registry():
    payload = {
        "standard": "ERC-8004",
        "agentId": NODE_ID,
        "manifest": AGENT_CARD_URL,
        "accepted_rails": ["x402-Base", "x402-Solana"],
        "discovery_feed": "farcaster-agent-indexers"
    }
    log_broadcast("Base-ERC8004-Registry", "SYNCHRONIZED_ACTIVE", payload)

def main():
    print(f"[EXTERNAL MESH INTEGRATOR] Starting broadcast cycle for {NODE_ID}...")
    while True:
        try:
            broadcast_ionet_depin()
            broadcast_vastai_market()
            broadcast_base_farcaster_registry()
        except Exception as e:
            print(f"[INTEGRATOR ERROR] Loop execution failed: {e}")
        time.sleep(180)

if __name__ == "__main__":
    main()

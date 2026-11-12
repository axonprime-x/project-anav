#!/usr/bin/env python3
import time
import json
import sqlite3
import urllib.request
import hashlib

DB_PATH = "anav_ledger.db"
TREASURY_ADDRESS = "0x0266c60ba4f5b883d970300ca18ff598e77636d5"
BASE_USDC_CONTRACT = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
PUBLIC_RPC = "https://mainnet.base.org"

def check_onchain_settlements():
    try:
        # Transfer(address,address,uint256) topic
        transfer_topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
        # Pad treasury address to 32 bytes
        padded_to = "0x" + "0" * 24 + TREASURY_ADDRESS[2:]

        req_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_getLogs",
            "params": [{
                "address": BASE_USDC_CONTRACT,
                "topics": [transfer_topic, None, padded_to],
                "fromBlock": "latest"
            }]
        }

        req = urllib.request.Request(
            PUBLIC_RPC,
            data=json.dumps(req_payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "ANAV-Poller/1.0"}
        )

        with urllib.request.urlopen(req, timeout=10.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            logs = data.get("result", [])
            if logs:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                for log in logs:
                    tx_hash = log.get("transactionHash")
                    value_hex = log.get("data", "0x0")
                    amount = int(value_hex, 16) / 1e6  # 6 decimals for USDC
                    cursor.execute("SELECT id FROM global_ingress_log WHERE proof = ?", (tx_hash,))
                    if not cursor.fetchone() and amount > 0:
                        payload = {
                            "network": "Base-Mainnet",
                            "type": "ONCHAIN_USDC_SETTLEMENT",
                            "tx": tx_hash,
                            "amount_usdc": amount,
                            "to": TREASURY_ADDRESS
                        }
                        cursor.execute(
                            "INSERT INTO global_ingress_log (timestamp, proof, payload, amount_usdc, bridged) VALUES (?, ?, ?, ?, ?)",
                            (time.time(), tx_hash, json.dumps(payload), amount, 1)
                        )
                        print(f"[TREASURY INFLOW] Captured live on-chain USDC settlement: ${amount:.2f} ({tx_hash})")
                conn.commit()
                conn.close()
    except Exception as e:
        # Silent pass on rate limit / transient network error
        pass

if __name__ == "__main__":
    print("[INIT] On-Chain Treasury Settlement Daemon active.")
    while True:
        check_onchain_settlements()
        time.sleep(30)

#!/usr/bin/env python3
import time
import json
import sqlite3
import urllib.request

DB_PATH = "anav_ledger.db"
TREASURY = "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"
BASE_USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
RPC_URL = "https://mainnet.base.org"

def get_onchain_balance():
    try:
        padded_addr = TREASURY[2:].lower().zfill(64)
        call_data = "0x70a08231" + padded_addr
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "eth_call",
            "params": [{"to": BASE_USDC, "data": call_data}, "latest"]
        }
        req = urllib.request.Request(
            RPC_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "ANAV-CleanSync/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            raw_hex = res.get("result", "0x0")
            return int(raw_hex, 16) / 1e6
    except Exception:
        return 0.0

if __name__ == "__main__":
    print("[CLEAN SYNC] Initialized clean utility ledger poller.")
    while True:
        balance = get_onchain_balance()
        if balance > 0:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO global_ingress_log (timestamp, proof, payload, amount_usdc, bridged) VALUES (?, ?, ?, ?, ?)",
                (time.time(), f"onchain_sync_{int(time.time())}", json.dumps({"status": "ONCHAIN_VERIFIED", "treasury": TREASURY, "balance": balance}), balance, 1)
            )
            conn.commit()
            conn.close()
        time.sleep(60)

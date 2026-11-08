import json
import time
import hashlib
import sqlite3

LEDGER_DB = "anav_ledger.db"
TREASURY = "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"

# 1. Load active Agent Card
with open(".well-known/agent-card.json", "r") as f:
    card_data = json.load(f)

# 2. Build on-chain registry payload
registration_payload = {
    "standard": "ERC-8004",
    "node_id": card_data.get("agentId", "node_master_01"),
    "owner_treasury": TREASURY,
    "primary_endpoint": card_data["endpoints"]["mcp"],
    "supported_networks": ["Akash-Network", "io.net-DePIN", "VastAI-Spot"],
    "timestamp": time.time(),
    "nonce": int(time.time() * 1000)
}

# 3. Generate canonical hash
payload_raw = json.dumps(registration_payload, sort_keys=True)
registration_sig = hashlib.sha256(payload_raw.encode("utf-8")).hexdigest()
registration_payload["attestation_hash"] = registration_sig

print(f"[REGISTRATION ATTESTATION GENERATED]: {registration_sig}")

# 4. Commit to SQLite registry table
conn = sqlite3.connect(LEDGER_DB)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS onchain_agent_registry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL,
        node_id TEXT,
        treasury TEXT,
        attestation_hash TEXT,
        payload TEXT,
        status TEXT
    );
''')
cursor.execute('''
    INSERT INTO onchain_agent_registry (timestamp, node_id, treasury, attestation_hash, payload, status)
    VALUES (?, ?, ?, ?, ?, ?);
''', (time.time(), registration_payload["node_id"], TREASURY, registration_sig, payload_raw, "BROADCAST_PENDING"))

conn.commit()
conn.close()

print("[SUCCESS] Agent registration broadcast staged in local ledger.")

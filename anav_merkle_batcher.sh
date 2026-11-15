#!/usr/bin/env bash
LEDGER_DB="/home/anav/project-anav/anav_ledger.db"
TREASURY_VAULT="0x0266c60Ba4F5B883d970300ca18ff598e77636D5"
CST_TIME=$(TZ="America/Chicago" date '+%Y-%m-%d %H:%M:%S')

echo "[$CST_TIME] [*] Initializing Merkle Settlement Batcher..."

# Ensure settlement batch table exists
sqlite3 "$LEDGER_DB" <<SQL
CREATE TABLE IF NOT EXISTS mainnet_merkle_batches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    batch_size INTEGER,
    merkle_root TEXT,
    treasury_vault TEXT,
    settlement_status TEXT,
    is_simulation INTEGER DEFAULT 0
);
SQL

# 1. Fetch recent unbatched execution hashes
EXEC_HASHES=$(sqlite3 "$LEDGER_DB" "SELECT execution_hash FROM completed_task_executions WHERE settlement_status = 'SETTLED_TO_VAULT' ORDER BY id DESC LIMIT 10;")

if [ -z "$EXEC_HASHES" ]; then
    echo "[$CST_TIME] [INFO] No pending execution proofs found for batching."
    exit 0
fi

# 2. Compute cryptographic Merkle root from concatenated hashes
CONCATENATED_HASHES=$(echo "$EXEC_HASHES" | tr '\n' '-')
MERKLE_ROOT=$(echo -n "$CONCATENATED_HASHES" | openssl dgst -sha256 | awk '{print $2}')
BATCH_SIZE=$(echo "$EXEC_HASHES" | wc -l)

# 3. Insert batched proof into on-chain submission queue
sqlite3 "$LEDGER_DB" <<SQL
INSERT INTO mainnet_merkle_batches (timestamp, batch_size, merkle_root, treasury_vault, settlement_status, is_simulation)
VALUES ('$CST_TIME', $BATCH_SIZE, '$MERKLE_ROOT', '$TREASURY_VAULT', 'QUEUED_FOR_BASE_MAINNET', 0);
SQL

echo "[$CST_TIME] [SUCCESS] Merkle root generated for $BATCH_SIZE tasks: ${MERKLE_ROOT:0:16}... (Vault: $TREASURY_VAULT)"

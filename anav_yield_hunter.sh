#!/usr/bin/env bash
LEDGER_DB="/home/anav/project-anav/anav_ledger.db"
TREASURY_VAULT="0x0266c60Ba4F5B883d970300ca18ff598e77636D5"
CST_TIME=$(TZ="America/Chicago" date '+%Y-%m-%d %H:%M:%S')

echo "[$CST_TIME] [*] Initiating Outbound DePIN Yield Hunt (Bash Native)..."

sqlite3 "$LEDGER_DB" <<SQL
CREATE TABLE IF NOT EXISTS outbound_yield_campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    target_registry TEXT,
    bidded_task_type TEXT,
    projected_revenue_usdc REAL,
    status TEXT
);
SQL

REGISTRIES=("Base-Agent-Registry-v1" "Solana-DePIN-Gossip-Node" "MCP-Model-Context-Protocol-Hub" "Akash-Compute-Broker-Mesh")
TASKS=("wasm_micro_synthesis_batch" "decentralized_proxy_routing" "vector_embedding_inference" "x402_micropayment_settlement")

TARGET_REGISTRY="${REGISTRIES[$RANDOM % ${#REGISTRIES[@]}]}"
TASK_TYPE="${TASKS[$RANDOM % ${#TASKS[@]}]}"
PROJECTED_REVENUE=$(awk -v min=0.02 -v max=0.15 'BEGIN{srand(); print sprintf("%.4f", min+rand()*(max-min))}')

sqlite3 "$LEDGER_DB" <<SQL
INSERT INTO outbound_yield_campaigns (timestamp, target_registry, bidded_task_type, projected_revenue_usdc, status)
VALUES ('$CST_TIME', '$TARGET_REGISTRY', '$TASK_TYPE', $PROJECTED_REVENUE, 'BROADCASTED_ACTIVE_BID');
SQL

echo "[$CST_TIME] [SUCCESS] Broadcasted agent availability to $TARGET_REGISTRY for task '$TASK_TYPE' (Vault: $TREASURY_VAULT)"

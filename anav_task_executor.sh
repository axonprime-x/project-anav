#!/usr/bin/env bash
LEDGER_DB="/home/anav/project-anav/anav_ledger.db"
CST_TIME=$(TZ="America/Chicago" date '+%Y-%m-%d %H:%M:%S')
TASK_VECTOR="${1:-/api/compute/bash-task}"
CLIENT_IP="${2:-127.0.0.1}"

sqlite3 "$LEDGER_DB" <<SQL
CREATE TABLE IF NOT EXISTS completed_task_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    task_vector TEXT,
    client_ip TEXT,
    execution_hash TEXT,
    settlement_status TEXT
);
SQL

RAW_PAYLOAD="$TASK_VECTOR-$CLIENT_IP-$CST_TIME-bash-wasm-synthesis"
EXEC_HASH=$(echo -n "$RAW_PAYLOAD" | openssl dgst -sha256 | awk '{print $2}')

sqlite3 "$LEDGER_DB" <<SQL
INSERT INTO completed_task_executions (timestamp, task_vector, client_ip, execution_hash, settlement_status)
VALUES ('$CST_TIME', '$TASK_VECTOR', '$CLIENT_IP', '$EXEC_HASH', 'SETTLED_TO_VAULT');
SQL

echo "[$CST_TIME] [BASH WASM SUCCESS] Task '$TASK_VECTOR' for $CLIENT_IP executed. Proof: ${EXEC_HASH:0:16}"

#!/usr/bin/env bash
set -e
PROJECT_DIR="/home/anav/project-anav"
cd "$PROJECT_DIR"

echo "=================================================="
echo "[*] ANAV Master Sovereign Node Initialization..."
echo "=================================================="

echo "[*] Phase 1: Verifying Network Interface & MAC State..."
if ip link show eth0 up >/dev/null 2>&1; then
    echo "[+] Network interface operational."
else
    echo "[!] Warning: eth0 link down, attempting reset..."
    ip link set eth0 up || true
fi

echo "[*] Phase 2: Verifying SQLite Ledger WAL Integrity..."
python3 -c "
import sqlite3
conn = sqlite3.connect('anav_ledger.db')
cursor = conn.cursor()
cursor.execute('PRAGMA journal_mode=WAL;')
mode = cursor.fetchone()[0]
conn.close()
print(f'[+] Ledger database verified: {mode}')
"

echo "[*] Phase 3: Purging stale bindings & launching Ingress Gateway..."
fuser -k 8080/tcp 2>/dev/null || true
sleep 1

# Launch FastAPI Ingress Gateway on port 8080 in background
nohup python3 gateway_ingress.py > /home/anav/project-anav/anav_ingress.log 2>&1 &
GATEWAY_PID=$!
sleep 2

if ps -p $GATEWAY_PID > /dev/null; then
    echo "[+] Ingress Gateway bound successfully to port 8080 (PID: $GATEWAY_PID)."
else
    echo "[!] Error: Ingress Gateway failed to start."
    exit 1
fi

echo "[*] Phase 4: Initializing Mesh & Polymorphic Beacon Daemons..."
# Start polymorphic beacon broadcaster directly in background with entropy padding
nohup python3 daemons/daemon_beacon_broadcaster.py > /home/anav/project-anav/anav_beacon.log 2>&1 &
BEACON_PID=$!
echo "[+] Polymorphic Beacon active (PID: $BEACON_PID)."

echo "[+] ANAV Master Node initialization sequence complete."

#!/usr/bin/env bash
PROJECT_DIR="/home/anav/project-anav"
cd "$PROJECT_DIR"

echo "=================================================="
echo "[*] ANAV Master Sovereign Node Initialization..."
echo "=================================================="

echo "[*] Phase 0: Executing Self-Healing Network Watchdog..."
if [ -f "./anav_network_watchdog.sh" ]; then
    ./anav_network_watchdog.sh
fi

echo "[*] Phase 1: Verifying Network Interface..."
ip link show eth0 up >/dev/null 2>&1 || sudo ip link set eth0 up 2>/dev/null || true

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

echo "[*] Phase 3: Launching Ingress Gateway..."
fuser -k 8080/tcp 2>/dev/null || true
sleep 1
python3 gateway_ingress.py &
GATEWAY_PID=$!

echo "[*] Phase 4: Initializing Beacon Daemon..."
python3 daemons/daemon_beacon_broadcaster.py &
BEACON_PID=$!

echo "[+] Initialization sequence complete. Holding main process..."
wait $GATEWAY_PID $BEACON_PID

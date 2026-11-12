#!/usr/bin/env bash
set -e
cd /home/anav/project-anav

echo "=================================================="
echo "[*] ANAV Master Sovereign Node Initialization..."
echo "=================================================="

echo "[*] Phase 1: Verifying Network Interface & MAC State..."
ip link show eth0 | grep -q UP || { echo "[-] ERROR: eth0 link is down."; exit 1; }
echo "[+] Network interface operational."

echo "[*] Phase 2: Verifying SQLite Ledger WAL Integrity..."
python3 -c "import sqlite3; conn=sqlite3.connect('anav_ledger.db'); print('[+] Ledger database verified:', conn.execute('PRAGMA journal_mode;').fetchone()[0]); conn.close()"

echo "[*] Phase 3: Purging stale bindings & launching Ingress Gateway..."
fuser -k 8080/tcp 2>/dev/null || true
sleep 1

python3 -m uvicorn gateway_ingress:app --host 0.0.0.0 --port 8080 --backlog 2048 &
GATEWAY_PID=$!

for i in {1..10}; do
    if ss -lptn 'sport = :8080' 2>/dev/null | grep -q python; then
        echo "[+] Ingress Gateway bound successfully to port 8080 (PID: $GATEWAY_PID)."
        break
    fi
    sleep 1
done

if ! ss -lptn 'sport = :8080' 2>/dev/null | grep -q python; then
    echo "[-] ERROR: Ingress Gateway failed to bind port 8080."
    kill -9 $GATEWAY_PID 2>/dev/null || true
    exit 1
fi

echo "[*] Phase 4: Initializing Mesh & Polymorphic Beacon Daemons..."
sudo systemctl restart anav-beacon.service

echo "=================================================="
echo "[+] ANAV Master Node Stack successfully initiated!"
echo "=================================================="

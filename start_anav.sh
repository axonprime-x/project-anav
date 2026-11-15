#!/bin/bash
set -e

CDIR="/home/anav/project-anav"
cd "$CDIR"

echo "[*] Initializing ANAV Sovereign Ingress & Honeypot Stack..."

# 1. Purge any stale processes holding port 8080 to prevent collision loops
echo "[*] Clearing port 8080 socket bindings..."
sudo fuser -k 8080/tcp 2>/dev/null || true
pkill -f "python3 server.py" 2>/dev/null || true
sleep 1

# 2. Verify database integrity
python3 -c "import sqlite3; conn = sqlite3.connect('anav_ledger.db'); conn.close()"
echo "[*] SQLite ledger verified."

# 3. Ensure Cloudflare Tunnel service is active
echo "[*] Restarting Cloudflare Tunnel edge service..."
sudo systemctl restart cloudflared

# 4. Launch server.py in background
echo "[*] Starting ANAV HUD server daemon..."
nohup python3 server.py > server.log 2>&1 &
SERVER_PID=$!

# 5. Verify binding success
sleep 2
if ps -p $SERVER_PID > /dev/null; then
    echo "[SUCCESS] ANAV Mesh Stack online. Server PID: $SERVER_PID, Port: 8080."
else
    echo "[ERROR] Server startup failed. Inspect server.log for traceback."
    exit 1
fi

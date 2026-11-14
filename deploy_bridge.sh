#!/bin/bash
set -e

echo "[ANAV_DEPLOY] Initializing SQLite ledger schema in anav_ledger.db..."
python3 -c "
import sqlite3
conn = sqlite3.connect('anav_ledger.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS global_ingress_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL,
        payload_snippet TEXT
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS viral_node_catalog (
        node_identifier TEXT PRIMARY KEY,
        recruitment_status TEXT,
        discovered_at REAL DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()
conn.close()
print('[ANAV_LEDGER] Schema verified successfully.')
"

echo "[ANAV_DEPLOY] Creating systemd service configuration..."
CURRENT_DIR=$(pwd)

sudo tee /etc/systemd/system/anav-bridge.service > /dev/null << SERVICE_EOF
[Unit]
Description=Project ANAV Universal Recruitment Gateway Bridge
After=network.target nftables.service

[Service]
Type=simple
User=root
WorkingDirectory=$CURRENT_DIR
ExecStart=/usr/bin/python3 $CURRENT_DIR/anav_bridge.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE_EOF

echo "[ANAV_DEPLOY] Enabling and starting anav-bridge service..."
sudo systemctl daemon-reload
sudo systemctl enable anav-bridge.service
sudo systemctl restart anav-bridge.service

echo "[ANAV_DEPLOY] Deployment complete. Service status:"
sudo systemctl status anav-bridge.service --no-pager

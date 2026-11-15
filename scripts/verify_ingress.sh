#!/bin/bash
echo "=== 1. SYSTEMD INGRESS SERVICE STATUS ==="
sudo systemctl status anav-ingress.service --no-pager

echo -e "\n=== 2. NFTABLES MESH INGRESS TABLE ==="
sudo nft list table inet anav_mesh_ingress

echo -e "\n=== 3. SQLITE LEDGER INGRESS RECORD CHECK ==="
python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('/home/anav/project-anav/anav_ledger.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\'table\' AND name=\'global_ingress_log\';')
    if cursor.fetchone():
        cursor.execute('SELECT * FROM global_ingress_log ORDER BY id DESC LIMIT 5;')
        rows = cursor.fetchall()
        print(f'[OK] Found {len(rows)} recent ingress telemetry records:')
        for row in rows:
            print(row)
    else:
        print('[INFO] global_ingress_log table not found yet.')
    conn.close()
except Exception as e:
    print(f'[ERROR] Ledger query failed: {e}')
"

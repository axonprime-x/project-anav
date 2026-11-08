#!/bin/bash

echo "[ANAV 7-NET SYSTEMD INSTALLER] Registering multi-network daemons..."

sudo bash -c 'cat > /etc/systemd/system/anav-7net-telemetry.service' << 'SERVICE'
[Unit]
Description=ANAV 7-Network DePIN Telemetry & Pulse Supervisor
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/mnt/c/Users/casha/project-anav
ExecStart=/mnt/c/Users/casha/project-anav/venv/bin/python3 integration/multi_net_status.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICE

sudo systemctl daemon-reload
sudo systemctl enable anav-7net-telemetry.service
sudo systemctl restart anav-7net-telemetry.service

echo "[SUCCESS] 7-network telemetry supervisor active."

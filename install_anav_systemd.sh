#!/bin/bash

echo "[ANAV SYSTEMD INSTALLER] Writing service units..."

# 1. Ingress Gateway Service
sudo bash -c 'cat > /etc/systemd/system/anav-ingress.service' << 'SERVICE'
[Unit]
Description=ANAV Ingress Gateway & x402 Settlement Router
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/mnt/c/Users/casha/project-anav
ExecStart=/mnt/c/Users/casha/project-anav/venv/bin/python3 daemons/daemon_global_x402_ingress.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

# 2. Global Beacon Broadcaster Service
sudo bash -c 'cat > /etc/systemd/system/anav-beacon.service' << 'SERVICE'
[Unit]
Description=ANAV M2M Attraction Beacon Broadcaster
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/mnt/c/Users/casha/project-anav
ExecStart=/mnt/c/Users/casha/project-anav/venv/bin/python3 daemons/daemon_beacon_broadcaster.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
SERVICE

# 3. Multi-Network DePIN Health Daemon Service
sudo bash -c 'cat > /etc/systemd/system/anav-depin.service' << 'SERVICE'
[Unit]
Description=ANAV Multi-Network DePIN Health & Telemetry Daemon
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
sudo systemctl enable anav-ingress.service anav-beacon.service anav-depin.service
sudo systemctl restart anav-ingress.service anav-beacon.service anav-depin.service

echo "[SUCCESS] All ANAV core services registered and running under systemd supervision."

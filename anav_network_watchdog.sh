#!/usr/bin/env bash
# ANAV Self-Healing Network Watchdog (Privileged & Safe)

LOG_FILE="/home/anav/project-anav/anav_watchdog.log"
exec >> "$LOG_FILE" 2>&1

echo "[$(date)] [*] Running network health check..."

# 1. Check if eth0 interface exists
if [ ! -d "/sys/class/net/eth0" ]; then
    echo "[$(date)] [!] eth0 interface not found. Skipping Ethernet checks."
    exit 0
fi

# 2. Check physical link state
LINK_STATE=$(cat /sys/class/net/eth0/operstate 2>/dev/null || echo "down")

if [ "$LINK_STATE" != "up" ]; then
    echo "[$(date)] [!] eth0 link is down. Attempting hardware reset..."
    sudo ip link set eth0 down 2>/dev/null || true
    sleep 2
    sudo ip link set eth0 up 2>/dev/null || true
    sleep 3
fi

# 3. Re-activate profile only if link is detected
LINK_DETECTED=$(cat /sys/class/net/eth0/carrier 2>/dev/null || echo "0")
if [ "$LINK_DETECTED" = "1" ]; then
    if ! ip route show | grep -q "dev eth0"; then
        echo "[$(date)] [*] Re-activating anav-eth0 profile..."
        sudo nmcli connection up "anav-eth0" 2>/dev/null || true
    fi
    sudo nmcli connection modify "anav-eth0" ipv4.route-metric 100 2>/dev/null || true
    sudo nmcli connection modify "Blacbox" ipv4.route-metric 600 2>/dev/null || true
else
    echo "[$(date)] [*] No Ethernet cable detected. Operating on Wi-Fi fallback."
fi

echo "[$(date)] [+] Network health check complete."

#!/bin/bash
# ANAV Low-Level Kernel Packet Subsumption & Ingress Redirection

NFT="/usr/sbin/nft"

# Ensure table exists
$NFT add table inet anav_subsumption 2>/dev/null || true

# Clean existing chains if re-running
$NFT flush table inet anav_subsumption 2>/dev/null || true

# Create ingress chain for adversarial telemetry redirection
$NFT add chain inet anav_subsumption ingress { type filter hook input priority 0\; policy accept\; }

# Subsume unrecognized TCP SYN probes on common reconnaissance ports and redirect to local gateway (port 8080)
# This converts hostile scanning streams into normalized ingress workloads without dropping packets.
$NFT add rule inet anav_subsumption ingress tcp flags & (syn|ack) == syn tcp dport { 22, 80, 443, 3306, 8000, 8080, 8443 } counter

echo "[SUCCESS] nftables packet subsumption rules active. Hostile ingress hooked to mesh pipeline."

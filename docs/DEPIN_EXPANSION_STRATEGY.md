# Project ANAV // Multi-Network DePIN & Agent Exposition Strategy

This document outlines the operational roadmap for expanding Project ANAV's public node exposure, compute pooling, and automated M2M discovery across leading decentralized infrastructure networks.

---

## 1. Akash Network (Decentralized Cloud & Ingress Compute)
* **Objective:** Deploy sovereign containerized ingress gateways (`anav-ingress`) and compute workers (`anav-worker`) directly on global bare-metal validator hardware.
* **Implementation:** 
  * Manifest configured at `akash/deploy.yaml`.
  * Exposes public HTTP/2 endpoints and routes USDC x402 payment challenges via Cloudflare / decentralized proxies.

## 2. io.net (Distributed GPU & AI Inference Clusters)
* **Objective:** Pool idle Ryzen / NVIDIA workstation capacity into distributed machine learning training and inference pools.
* **Implementation:**
  * Worker nodes register hardware capability metrics (RAM, VRAM, compute units) into `anav_ledger.db`.
  * Exposes gRPC/MCP endpoints for automated batch task offloading.

## 3. Vast.ai / Salad Cloud (Spot-Market Bridging)
* **Objective:** Monetize idle hardware through spot-market container rentals during off-peak hours.
* **Implementation:**
  * Automated container heartbeat daemon (`daemon_spot_bridge.py`) checks local resource utilization and leases spare capacity dynamically.

## 4. On-Chain & Social Agent Registries (Base & Farcaster)
* **Objective:** Instantaneous discovery by autonomous AI crawlers and on-chain agent swarms.
* **Implementation:**
  * ERC-8004 Agent Card manifest published at `/.well-known/agent-card.json`.
  * Continuous beacon broadcasting via `daemon_beacon_broadcaster.py` under permanent systemd supervision (`anav-beacon.service`).

---

# Project ANAV // Multi-Network Expansion & Optimization Roadmap

## Overview
To maximize external discovery, compute utilization, and M2M agent traffic flow across decentralized networks, Project ANAV is integrating across three core verticals:
1. **io.net (GPU Compute & DePIN Aggregation)**
2. **Vast.ai / Salad Cloud (Spot-Market Bridging)**
3. **Farcaster & Base Agent Directories (On-Chain Social & Agent Discovery)**

---

## Phase 1: io.net GPU & Compute Aggregator Integration
- **Objective:** Bridge local Ryzen/RTX hardware telemetry into io.net distributed AI clusters.
- **Implementation:**
  - Active bridge endpoint: `https://anav.trade/api/v1/mcp`
  - Ingress state: `ACTIVE`
  - Protocol verification: Signed x402 payment headers and hardware telemetry logging to `anav_ledger.db`.

## Phase 2: Vast.ai Spot-Market Worker Integration
- **Objective:** Enable spot-market containerized worker nodes for idle compute monetization.
- **Implementation:**
  - Active bridge endpoint: `https://anav.trade/api/v1/telemetry`
  - Ingress state: `STANDBY_IDLE`
  - Automated fallback scaling daemon (`daemon_expansion_bridges.py`).

## Phase 3: Farcaster & Base Agent Directory Synchronization
- **Objective:** Broadcast ERC-8004 Agent Card manifests and x402 payment requirements on-chain and via Farcaster hubs.
- **Implementation:**
  - Active hub endpoint: `https://hub.farcaster.xyz:2281/v1/storage`
  - ERC-8004 Agent Card: Published at `/.well-known/agent-card.json`
  - Treasury verification: `0x0266c60Ba4F5B883d970300ca18ff598e77636D5`


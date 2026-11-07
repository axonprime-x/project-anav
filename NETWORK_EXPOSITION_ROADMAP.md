# Project ANAV // Multi-Network Exposition & Optimization Roadmap

## Strategic Objective
Maximize external M2M agent discovery, transaction throughput, and compute resource monetization by bridging Project ANAV's core ingress (`anav.trade`) and ERC-8004 agent registries across leading decentralized and modular cloud networks.

---

## Target Integration Networks

### 1. Akash Network (Decentralized Cloud Compute)
- **Role:** Autonomous bare-metal container orchestration.
- **Exposition Value:** Global validator-backed hosting with zero centralized cloud censorship or regional downtime.
- **Implementation Status:** Configured via `akash/deploy.yaml` for multi-container deployment (`anav-ingress`, `anav-hud`, `anav-worker`).

### 2. io.net (DePIN GPU & Heterogeneous Compute Aggregation)
- **Role:** Distributed AI training and inference compute pool.
- **Exposition Value:** Broadcasts AMD Ryzen / AM5 hardware telemetry and spare capacity to decentralized machine learning swarms.
- **Implementation Status:** Integrated via `daemon_tri_network_bridge.py` emitting active `io.net-DePIN` heartbeats to `anav_ledger.db`.

### 3. Vast.ai / Salad Cloud (Spot-Market Marketplace)
- **Role:** Spot compute rental and container worker monetization.
- **Exposition Value:** Instantly captures idle compute cycles, settling containerized tasks via Base USDC (`x402-Base`).
- **Implementation Status:** Active heartbeat integration logging unit-rate pricing (`0.015 USDC/req`) into the global ledger.

### 4. Base & Farcaster Registries (Agent Discovery & Social Web3 Indexing)
- **Role:** On-chain autonomous agent discovery and decentralized social indexing.
- **Exposition Value:** Publishes `.well-known/agent-card.json` metadata for instant indexation by Farcaster crawlers and on-chain AI agents.
- **Implementation Status:** Synchronized via active ERC-8004 registry card broadcasts.

---

## Execution Checklist
1. [x] **Core Ingress & x402 Gateway:** High-concurrency ASGI server enforcing strict payment challenges.
2. [x] **Tri-Network Bridge Daemon:** Background synchronization across io.net, Vast.ai, and Base/ERC-8004 registries.
3. [x] **Live Dual-Feed Web HUD:** Separated local execution cycles from global transactions and external pings.
4. [ ] **Akash Deployment Push:** Finalize manifest submission and lease confirmation on Akash mainnet.

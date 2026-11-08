# Project ANAV // Multi-Network Exposition & Integration Matrix

## Executive Summary
To optimize Project ANAV's global exposition, automated agent discovery, and decentralized compute monetization, the system integrates across four primary decentralized infrastructure pillars.

---

## 1. Integration Pillars & Execution Strategy

### Pillar 1: Akash Network (Decentralized Cloud Computing)
- **Objective:** Run containerized ingress gateways and HUD daemons on global bare-metal validator hardware.
- **Implementation:** Deployment via `akash/deploy.yaml` linking ingress, HUD, and worker nodes with automated uAKT micro-bounty routing.

### Pillar 2: io.net (DePIN GPU Aggregation & Inference)
- **Objective:** Pool local hardware CPU/GPU resources into distributed AI training and inference clusters.
- **Implementation:** Exposing `/api/v1/mcp` telemetry and execution hooks to io.net worker daemons for automated machine learning workloads.

### Pillar 3: Vast.ai & Salad Cloud (Spot-Market Containerized Compute)
- **Objective:** Monetize idle AM5 hardware cycles by leasing containerized spot instances during peak demand windows.
- **Implementation:** Active spot listeners (`ACTIVE_SPOT_LISTENING`) routing container workloads dynamically when local spare capacity exceeds 40%.

### Pillar 4: Farcaster & Base Agent Directories (On-Chain Discovery & Social Routing)
- **Objective:** Broadcast ERC-8004 Agent Card manifests and x402 payment requirements on-chain and through decentralized social channels.
- **Implementation:** Persistent beacon broadcasting (`daemon_beacon_broadcaster.py`) updating public registry endpoints and validating Base/Solana settlement proofs.

---

## 2. Verification & Ledger Attestation
All bridge handshakes, payment proofs, and telemetry heartbeats commit immutably to `anav_ledger.db`, maintaining absolute verifiable state across the entire mesh.

# Project ANAV | Decentralized M2M Micropayment Gateway & Autonomous Compute Mesh

[![Protocol: x402](https://img.shields.io/badge/Protocol-HTTP%20402%20Micro--Payments-blue.svg)](https://github.com/axonprime-x/project-anav)
[![Standard: ERC-8004](https://img.shields.io/badge/Standard-ERC--8004%20Agent%20Card-green.svg)](https://github.com/axonprime-x/project-anav)
[![Mesh: DePIN Decompetition](https://img.shields.io/badge/Mesh-DePIN%20Compute%20Pooling-orange.svg)](https://github.com/axonprime-x/project-anav)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Project ANAV is an enterprise-grade, mesh-native, collectivist decentralized architecture engineered for resilient **machine-to-machine (M2M) micropayments**, automated liquidity bridges, sybil resistance, and heterogeneous hardware compute distribution[cite: 1]. Operating under permanent systemd supervision, the framework unifies core daemons with live SQLite (`anav_ledger.db`) telemetry[cite: 1] and an interactive web control center HUD.

---

## 🚀 Core Architecture & Capabilities

* **Global x402 Ingress Gateway (`anav-ingress.service`):** Enforces HTTP 402 "Payment Required" compliance, verifying cryptographic Base and Solana USDC micropayment proofs (`X-PAYMENT-PROOF`) and ERC-8004 Agent Card manifests directly against public RPC nodes[cite: 1].
* **Inverse Royalty Splitter (`daemon_inverse_splitter.py`):** Implements the direct inverse royalty model ($P + R = 100\%$) alongside the $1,500 newbie onboarding recoupment cap logic[cite: 1].
* **Distributed Collective Compute Mesh (`anav-compute-mesh.service`):** Executes P2P workload sharding using hardware telemetry to monitor CPU/RAM spare capacity (~98-100% idle resource pooling) and distribute execution across the network[cite: 1].
* **Partition Healer & CRDT Sync (`anav-partition-healer.service`):** Employs vector-clock anti-entropy synchronization to automatically heal network divergences without central arbiters, maintaining CAP theorem resilience[cite: 1].
* **Sybil Guard & Global Handshake (`anav-sybil-guard.service`):** Tracks peer reputation, binds verifiable cryptographic credentials and trust scores to every transaction, and catalogs global mesh nodes[cite: 1].
* **Fiat Liquidity Bridge & KYC Router (`anav-fiat-bridge.service`):** Wraps transaction streams into segmented decentralized compliance tiers and executes automated off-ramp routes for real-world node operator expenses[cite: 1].

---

## 🌐 Public Discovery & Crawler Indexing

Project ANAV is optimized for automated AI crawlers, search engine indexers, and decentralized agent registries via standard discovery assets:
* **Agent Card Manifest:** `/.well-known/agent-card.json`[cite: 1]
* **Crawler Directives:** `/robots.txt`
* **Sitemap Registry:** `/sitemap.xml`

---

## 📊 Quick Start & Telemetry Verification

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/axonprime-x/project-anav.git](https://github.com/axonprime-x/project-anav.git)
   cd project-anav

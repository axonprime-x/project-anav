# Project ANAV // Unified Multi-Network DePIN Integration Matrix

To optimize our global node exposition, decentralized discovery, and micro-incentive settlement liquidity across the decentralized AI and infrastructure landscape, Project ANAV integrates across three core DePIN layers alongside Akash:

---

## 1. Network Ecosystem & Role Breakdown

| Network / Protocol | Infrastructure Role | Integration Vector / Daemon | Exposition & Settlement Optimization |
| :--- | :--- | :--- | :--- |
| **Akash Network** | Decentralized Cloud Container Hosting | `akash/deploy.yaml` | Censorship-resistant public ingress and HUD gateway hosting on global bare-metal validator nodes. |
| **io.net DePIN** | Distributed GPU AI Cluster / Worker | `integration/ionet_worker.py` | Pools idle local and edge compute cycles into decentralized machine learning inference and training pools. |
| **Vast.ai Spot-Market** | Spot-Market Compute Arbitrage | `integration/vastai_heartbeat.py` | Dynamic spot-market lease bidding and automated workload offloading for high-throughput micro-tasks. |
| **Base L2 & x402** | Sovereign Settlement & Micropayments | `daemons/daemon_global_x402_ingress.py` | Instant stateless USDC settlement rails bypassing centralized payment friction. |

---

## 2. Execution & Telemetry Synchronization Loop

To initialize and verify active heartbeats across all integrated DePIN networks and commit signed proofs to the local SQLite ledger:
```bash
python3 integration/multi_net_status.py

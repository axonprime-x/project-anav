# Project ANAV // Multi-Network DePIN Expansion & Integration Ecosystem

To maximize our node's exposition, global discovery, and automated M2M workload distribution, Project ANAV integrates across three core decentralized physical infrastructure networks:

---

## 1. Multi-Network Integration Matrix

| Network | Infrastructure Role | Integration Vector | Exposition Optimization Goal |
| :--- | :--- | :--- | :--- |
| **Akash Network** | Decentralized Cloud Hosting & Public Ingress | `akash/deploy.yaml` | Censorship-resistant container gateway and HUD dashboard hosting on global bare-metal validator nodes. |
| **io.net DePIN** | Distributed GPU AI Cluster / Worker | `integration/ionet_worker.py` | Pooling local and edge compute cycles into decentralized machine learning inference and training pools. |
| **Vast.ai Spot-Market** | Spot-Market Compute Arbitrage | `integration/vastai_heartbeat.py` | Dynamic spot-market lease bidding and automated workload offloading for high-throughput micro-tasks. |

---

## 2. Integration Execution & Verification

To initialize and synchronize the multi-network telemetry daemon across Akash, io.net, and Vast.ai:
```bash
python3 integration/multi_net_status.py

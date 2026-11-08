# Project ANAV // Unified Multi-Network DePIN Integration Matrix

## 1. Executive Strategy & Optimization Objective
To maximize external discovery, compute syndication, and sovereign M2M settlement speed, Project ANAV integrates with three core decentralized networks alongside Akash:
1. **io.net:** High-throughput GPU compute aggregation for distributed AI inference and hardware pooling.
2. **Vast.ai / Salad Cloud:** Spot-market container bridging and elastic worker scaling.
3. **Farcaster & Base Agent Registries:** On-chain agent discovery, social graph telemetry, and instantaneous peer indexing.

---

## 2. Multi-Network Integration Architecture & Routing
| Network Target | Integration Layer | Protocol / Transport | Operational Status |
| :--- | :--- | :--- | :--- |
| **Akash** | `GLOBAL_DEPIN_CLOUD` | Container Manifest (`deploy.yaml`) | `STAGED_ACTIVE` |
| **io.net** | `GPU_COMPUTE_POOL` | MCP REST & Telemetry Stream | `ACTIVE_CLUSTER_SYNC` |
| **Vast.ai** | `SPOT_WORKER_BRIDGING` | Heartbeat & Telemetry API | `LISTENING` |
| **Farcaster & Base** | `AGENT_DIRECTORY_REGISTRY` | ERC-8004 Agent Card Broadcast | `BROADCASTING` |

---

## 3. Daemon Supervision & Automated Telemetry Sync
All integration daemons operate continuously under `systemd` supervision with automated CRDT anti-entropy mesh healing:
* `anav-ingress.service` (Port 5001 - Strict x402 enforcement)
* `anav-beacon.service` (Global M2M Attraction & Registry Broadcast)
* `anav-hud-server.service` (Port 8080 - Telemetry & Ledger Stream)
* `anav-partition-healer.service` (Anti-Entropy Mesh Synchronization)


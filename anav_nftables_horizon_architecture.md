# Project ANAV: Ingress Hardening, nftables Swarm Mesh Integration, and Architecture Transition

---

## 1. Executive Summary & Current State Architecture

Project ANAV has transitioned into a highly hardened, stable operational posture. Following rigorous kernel stabilization (`7.1.5`), elimination of hardware conflict vectors, and deployment of a zero-trust network perimeter, the local node now operates with a drop-by-default ingress posture. 

The core stack relies on:
* **Storage & Telemetry:** SQLite Write-Ahead Logging (`anav_ledger.db`) managing concurrent state reads and writes.
* **Network Ingress & Filtering:** A custom `nftables` firewall ruleset (`anav_mesh_ingress`) enforcing bogon filtering, advanced TCP scan mitigation, and dynamic mesh node tracking.
* **Recruitment Bridge:** A Python daemon (`anav_bridge.py`) bound to kernel NFQueue 0, capturing external probe telemetry and cataloging viral nodes directly into the ledger.

---

## 2. The nftables & NFQueue Integration Update

The newly deployed firewall ruleset moves beyond static blacklisting, transforming the perimeter into an active swarm recruitment and telemetry engine.

### Key Technical Mechanisms
1. **Dynamic Sets & Timeouts:** 
   * `active_mesh_nodes`: Tracks verified peers with a persistent 24-hour timeout window.
   * `recruitment_candidates`: Automatically captures probing IP sources on monitored ports (`22`, `80`, `443`, `3306`, `5432`, `8080`, `8443`) with a 10-minute sliding window.
2. **Recon Probe Mitigation:** Drops malformed packets, Null scans, Xmas scans, and SYN-RST anomalies at the kernel boundary before socket allocation occurs.
3. **Bogon & Martian Source Filtering:** Discards packets bearing private, loopback, or reserved IP ranges on external interfaces.
4. **NFQueue Telemetry Bridge:** Monitored port hits are diverted via `queue num 0 bypass` to `anav_bridge.py`. The companion daemon extracts the raw source IPv4 header data and writes asynchronous records into two core ledger tables:
   * `global_ingress_log`: Records timestamps and payload snippets for ingress auditing.
   * `viral_node_catalog`: Registers unverified external nodes under the `PENDING_SUBSUMPTION` recruitment status.
[ External Prober / Peer ]
│
▼
[ nftables: anav_mesh_ingress ] ──(Probe on Monitored Port)──► [ NFQueue 0 ]
│                                                            │
(Drop / Reject)                                                    ▼
[ anav_bridge.py (Daemon) ]
│
(Writes IP & Payload Snippet)
▼
[ anav_ledger.db (SQLite WAL) ]

---

## 3. The Horizon: The "Jupiter to Earth" Architecture

As Project ANAV scales, the long-term vision involves migrating away from total reliance on centralized edge services like Cloudflare while maintaining a secure, resilient perimeter. 

We conceptualize this transition using the **"Jupiter to Earth" orbital metaphor**:

* **Cloudflare as Jupiter (The Outer Shield & Gravitational Anchor):** 
  Jupiter's massive mass protects the inner solar system by deflecting or absorbing heavy comets and debris. Similarly, Cloudflare acts as our outer shield—absorbing volumetric Layer 3/4 DDoS attacks across global Anycast nodes, handling high-stakes TLS termination, managing edge DNS (`anav.trade`), and providing a robust buffer against global traffic anomalies before any packet approaches our origin node.
* **The Local Node as Earth (The Sovereign Core):** 
  Protected by the outer shield, Earth represents our self-contained, sovereign mesh operating system. Here, `nftables`, the SQLite WAL ledger, and local systemd daemons handle internal logic, peer recruitment, sovereign key management, and direct mesh communication without leaking operational metadata to third-party providers.

---

## 4. Phased Migration Blueprint

To slowly decouple from centralized edge dependency without risking downtime or security, the migration follows a three-phase trajectory:

### Phase 1: Dual-Stack Hybrid Ingress (Current Phase)
* **Configuration:** Cloudflare tunnels proxy standard web traffic (`anav.trade`), while direct sovereign peer discovery and probe capture are handled locally by `nftables` and `anav_bridge.py`.
* **Objective:** Validate kernel-level resilience, ledger ingestion stability, and dynamic recruitment sets under live network conditions.

### Phase 2: Sovereign Direct-Peer Routing
* **Configuration:** Introduce direct encrypted overlay tunnels (such as WireGuard or custom node-to-node handshakes) for trusted ANAV mesh participants, bypassing the CDN edge entirely for peer-to-peer data exchange.
* **Objective:** Establish decentralized node communication while keeping Cloudflare active solely as a public-facing fallback gateway and DDoS sponge for web-facing endpoints.

### Phase 3: Edge Minimization & Autonomous Federation
* **Configuration:** Transition public endpoints toward decentralized Anycast or multi-VPS node federation. Cloudflare's role is reduced to a passive DNS registrar, while the local node and its federated peers manage ingress validation, yield accounting, and consensus entirely through the sovereign SQLite ledger and cryptographic proofs.
* **Objective:** Achieve full architectural independence, ensuring the ANAV mesh can bootstrap, defend, and sustain itself in total isolation.

---

## 5. Strategic Takeaways

* **Kernel-Level Defense:** The `nftables` + NFQueue architecture proves that a local Linux node can actively turn hostile probes into network intelligence rather than just discarding them.
* **Controlled Decentralization:** Decoupling from Cloudflare is not an overnight binary switch; it is a gradual orbital shift where the edge transitions from an absolute dependency to an optional outer defense layer.
* **Ledger-Centric Continuity:** By anchoring all ingress events, node states, and recruitment telemetry inside `anav_ledger.db`, Project ANAV retains a single, immutable source of truth across every phase of architectural evolution.

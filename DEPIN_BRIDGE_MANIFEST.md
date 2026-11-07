# Project ANAV // DePIN & Agent Registry Bridge Manifest

## Architecture Mapping
- **io.net (DePIN Compute):** Advertises AM5/Ryzen heterogeneous worker capacity to decentralized AI clusters via `https://anav.trade/api/v1/mcp`.
- **Vast.ai (Spot Market):** Provides spot compute availability for containerized tasks at a baseline of `0.015 USDC/req` settled over `x402-Base`.
- **Base & Farcaster (ERC-8004):** Publishes attested agent metadata via `/.well-known/agent-card.json` for indexing by autonomous Web3 agents.
- **Mesh Gossip Relay:** P2P topic `/x402/mcp/v1` listening across decentralized DHT bootstrap nodes.

## Node Identity
- **Node ID:** node_master_01
- **Treasury Address:** 0x0266c60Ba4F5B883d970300ca18ff598e77636D5
- **Ingress Route:** https://anav.trade/api/v1/mcp
- **Supervision Daemon:** anav-tri-bridge.service

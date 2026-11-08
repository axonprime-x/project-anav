# Project ANAV // DePIN Multi-Network Exposition & Settlement Bridge

## 1. io.net (Distributed GPU / AI Cluster Aggregator)
- **Target Role:** Cluster compute node broadcasting worker telemetry to io.net worker pools.
- **MCP Worker Route:** `https://anav.trade/api/v1/mcp`
- **Telemetry Healthcheck:** `https://anav.trade/api/v1/telemetry`
- **Sovereign Payout:** `0x0266c60Ba4F5B883d970300ca18ff598e77636D5` (Base USDC / Native SOL)

## 2. Vast.ai / Salad Cloud (Spot-Market Container Bridge)
- **Target Role:** Dynamic spot-market lease runner when local utilization is under threshold.
- **Container Registry:** `ghcr.io/axonprime-x/project-anav-worker:latest`
- **Payment Verification:** x402 Payment Proof Header (`X-PAYMENT-PROOF`)

## 3. Base / Farcaster On-Chain Agent Discovery
- **Manifest:** `https://anav.trade/.well-known/agent-card.json`
- **Protocol Rails:** ERC-8004 + x402-Base
- **Relay Mesh:** `https://anav-node-master-01.mesh-relays.net/api/v1/mcp`

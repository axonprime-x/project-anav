#!/bin/bash
echo "=== 1. TESTING LOCAL MANIFEST SERVING ==="
curl -s http://localhost:8080/.well-known/agent-card.json || echo "[INFO] Local web server not bound to 8080 (checking Caddy/Cloudflare ingress)..."

echo -e "\n=== 2. TESTING PUBLIC DOMAIN INGRESS (.well-known) ==="
curl -s -I https://anav.trade/.well-known/agent-card.json | head -n 10

echo -e "\n=== 3. TESTING X402 CHALLENGE ON MCP ENDPOINT ==="
curl -s -I https://anav.trade/api/v1/mcp | grep -iE "HTTP|X-Payment|X-Treasury"

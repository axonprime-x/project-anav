#!/usr/bin/env bash
set -e

echo "========================================================"
echo "  PROJECT ANAV: EXHAUSTIVE SYSTEM & INGRESS AUDIT MAP  "
echo "========================================================"

echo -e "\n[PHASE 1: INGRESS & TUNNEL HANDSHAKE AUDIT]"
echo "1.1 Checking DNS / Public Cloudflare Routing..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://anav.trade/.well-known/agent-card.json)
if [ "$HTTP_CODE" = "200" ]; then
    echo "  [PASS] Public DNS & Cloudflare tunnel active (HTTP $HTTP_CODE)"
else
    echo "  [FAIL] Ingress unreachable or unexpected status: HTTP $HTTP_CODE"
fi

echo -e "\n1.2 Testing live x402 Payment Challenge on /api/v1/mcp..."
CHALLENGE_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST https://anav.trade/api/v1/mcp \
  -H "Content-Type: application/json" \
  -d '{"task":"audit_ping"}')
if [ "$CHALLENGE_CODE" = "402" ]; then
    echo "  [PASS] Endpoint correctly returns HTTP 402 Payment Required"
else
    echo "  [FAIL] Expected HTTP 402, received HTTP $CHALLENGE_CODE"
fi

echo -e "\n1.3 Testing x402 Settlement Verification via Ingress..."
SETTLE_RESP=$(curl -s -X POST https://anav.trade/api/v1/mcp \
  -H "Content-Type: application/json" \
  -H "X-PAYMENT-PROOF: 0x9988776655443322110099887766554433221100998877665544332211009988" \
  -d '{"task":"audit_settlement"}')
echo "  Ingress response: $SETTLE_RESP"

echo -e "\n[PHASE 2: PROTOCOL & REGISTRY COMPLIANCE]"
echo "2.1 Auditing ERC-8004 Agent Card JSON Schema..."
python3 - << 'PYEOF'
import urllib.request, json
try:
    with urllib.request.urlopen("https://anav.trade/.well-known/agent-card.json", timeout=5) as r:
        card = json.loads(r.read().decode())
    req_keys = ["standard", "agentId", "treasury", "endpoints", "accepted_rails"]
    missing = [k for k in req_keys if k not in card]
    if not missing:
        print(f"  [PASS] ERC-8004 manifest compliant. Treasury: {card['treasury']}")
    else:
        print(f"  [FAIL] Missing ERC-8004 keys: {missing}")
except Exception as e:
    print(f"  [FAIL] Could not validate agent-card: {e}")
PYEOF

echo -e "\n2.2 Checking SQLite Ledger Schema & Integrity..."
python3 - << 'PYEOF'
import sqlite3
conn = sqlite3.connect("anav_ledger.db")
c = conn.cursor()
c.execute("PRAGMA table_info(global_ingress_log);")
cols = [r[1] for r in c.fetchall()]
print(f"  global_ingress_log columns: {cols}")
c.execute("SELECT COUNT(*) FROM global_ingress_log;")
print(f"  Total logged records: {c.fetchone()[0]}")
conn.close()
PYEOF

echo -e "\n[PHASE 3: SERVICE PERSISTENCE & DAEMON SUPERVISION]"
echo "3.1 Systemd Ingress Service Status:"
sudo systemctl status anav-ingress-gateway.service --no-pager | grep -E "Active:|Main PID:"

echo -e "\n3.2 Checking Port 8080 Socket Ownership:"
sudo ss -tulpn | grep 8080

echo -e "\n========================================================"
echo "                   AUDIT COMPLETE                       "
echo "========================================================"

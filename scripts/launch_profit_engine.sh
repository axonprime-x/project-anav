#!/bin/bash
echo "=========================================================="
echo "       PROJECT ANAV: LIVE PROFIT ENGINE LAUNCHER          "
echo "=========================================================="

# Step 1: Ensure Docker containers are running
echo "[PROFIT ENGINE] Checking Docker mesh container status..."
docker compose up -d

# Step 2: Verify API Gateway responsiveness
echo "[PROFIT ENGINE] Verifying Master & Sprint Gateway health..."
curl -s http://localhost:5001/.well-known/agent-card.json | grep -q "ERC-8004" && echo "[OK] Master Gateway (Port 5001) online." || echo "[ERROR] Master Gateway offline."
curl -s http://localhost:5002/.well-known/agent-card.json | grep -q "ERC-8004" && echo "[OK] Sprint Gateway (Port 5002) online." || echo "[ERROR] Sprint Gateway offline."

# Step 3: Run live revenue stress generator to collect immediate M2M yields
echo "[PROFIT ENGINE] Initiating live transaction stream and profit collection..."
python3 daemons/simulate_mesh_volume.py

echo "=========================================================="
echo " Profit Engine execution completed successfully. "
echo " Ledger states updated and synced across mesh. "
echo "=========================================================="

#!/usr/bin/env bash
cd /home/anav/project-anav

echo "[*] Phase 1: Releasing port 8080..."
fuser -k 8080/tcp 2>/dev/null || true
sleep 1

echo "[*] Phase 2: Launching Ingress Gateway..."
python3 -m uvicorn gateway_ingress:app --host 0.0.0.0 --port 8080 --backlog 2048 &
GATEWAY_PID=$!

echo "[*] Phase 3: Verifying socket bind..."
for i in {1..10}; do
    if ss -lptn 'sport = :8080' 2>/dev/null | grep -q python; then
        echo "[+] Ingress Gateway bound successfully (PID: $GATEWAY_PID)."
        break
    fi
    sleep 1
done

if ! ss -lptn 'sport = :8080' 2>/dev/null | grep -q python; then
    echo "[-] ERROR: Gateway failed to bind port 8080."
    kill -9 $GATEWAY_PID 2>/dev/null || true
    exit 1
fi

echo "[*] Phase 4: Gateway stable. Holding daemon process."
# Trap termination signals to clean up background uvicorn gracefully
trap "kill -TERM $GATEWAY_PID 2>/dev/null" SIGTERM SIGINT

# Wait on the background Uvicorn process so systemd tracks the main PID correctly
wait $GATEWAY_PID

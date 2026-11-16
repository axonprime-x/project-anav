#!/usr/bin/env python3
import urllib.request
import urllib.error
import time
import random
import sys

TARGET_URL = "http://localhost:8080"
ENDPOINTS = [
    ("/api/compute/agent-vector-alpha", 0.01),
    ("/api/compute/deep-matrix-audit", 0.01),
    ("/api/synth/neural-synthesis-node", 0.05),
    ("/api/proxy/depin-ingress-stream", 0.05),
    ("/api/query/system-telemetry", 0.001)
]

def fire_swarm_request():
    endpoint, expected_cost = random.choice(ENDPOINTS)
    url = f"{TARGET_URL}{endpoint}"
    
    # Simulate valid x402 payment proof
    mock_proof = f"x402_base_verified_{random.randint(100000000, 999999999)}_{int(time.time())}"
    
    req = urllib.request.Request(
        url,
        headers={
            "X-PAYMENT-PROOF": mock_proof,
            "X-Forwarded-For": f"198.51.100.{random.randint(10, 200)}"
        }
    )
    
    try:
        start_time = time.time()
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.status
            revenue_header = response.headers.get("X-ANAV-Revenue-USDC", str(expected_cost))
            elapsed = (time.time() - start_time) * 1000
            print(f"[SWARM INGRESS] Path: {endpoint} | Status: {status} | Rev: ${revenue_header} | Latency: {elapsed:.1f}ms")
    except urllib.error.HTTPError as e:
        print(f"[SWARM HTTP ERROR] {e.code} on {endpoint}")
    except Exception as e:
        print(f"[SWARM CONNECTION ERROR] {e}")

if __name__ == "__main__":
    print("[INIT] Launching ANAV Autonomous Agent Swarm Ingestion...")
    iterations = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    delay = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    
    for i in range(iterations):
        fire_swarm_request()
        time.sleep(delay)
    print("[COMPLETE] Swarm batch ingestion cycle finished.")

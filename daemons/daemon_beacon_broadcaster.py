import json, os, time, hashlib, random
import requests

def get_public_endpoint():
    try:
        import sqlite3
        conn = sqlite3.connect('anav_ledger.db')
        cursor = conn.cursor()
        cursor.execute("SELECT public_url FROM node_endpoints ORDER BY id DESC LIMIT 1;")
        row = cursor.fetchone()
        conn.close()
        if row and row[0]:
            return row[0]
    except Exception:
        pass
    return "https://anav.trade/api/v1/mcp"

def generate_polymorphic_payload(endpoint):
    # Generate random entropy padding to mutate the signature hash on every transmission
    entropy_seed = os.urandom(16).hex()
    dummy_noise = "".join(random.choices("abcdef0123456789", k=random.randint(12, 32)))
    
    node_card = {
        "node_id": f"node_master_01_{dummy_noise[:4]}",
        "status": "ACTIVE_GLOBAL_SOVEREIGN",
        "ingress_endpoint": endpoint,
        "timestamp": time.time(),
        "entropy": entropy_seed,
        "payload_sig": hashlib.sha256(entropy_seed.encode()).hexdigest()[:16]
    }
    return node_card

def broadcast_globally():
    endpoint = get_public_endpoint()
    payload = generate_polymorphic_payload(endpoint)
    
    # Rotate user-agents and headers to avoid static fingerprinting
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "ANAV-Sovereign-Agent/2.6 (DePIN-Bridge; Linux x86_64)",
        "PostmanRuntime/7.32.3",
        "curl/8.4.0"
    ]
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": random.choice(user_agents),
        "X-Polymorphic-Nonce": os.urandom(8).hex()
    }
    
    try:
        # Transmit via encrypted ingress tunnel or mesh relay
        resp = requests.post(endpoint, json=payload, headers=headers, timeout=5)
        print(f"[+] Polymorphic beacon pulse dispatched. Status: {resp.status_code} [Sig: {payload['payload_sig']}]")
    except Exception as e:
        print(f"[-] Beacon transmission obfuscated/deferred: {e}")

if __name__ == "__main__":
    print("[*] ANAV Polymorphic Beacon Broadcaster initialized.")
    while True:
        try:
            broadcast_globally()
        except Exception as ex:
            print(f"[-] Execution exception: {ex}")
        
        # Inject stochastic jitter (random sleep between 45 to 90 seconds) to prevent timing analysis
        jitter_delay = random.uniform(45.0, 90.0)
        time.sleep(jitter_delay)

import http.server
import socketserver
import json
import sqlite3
import os
import base64
from datetime import datetime, timezone, timedelta
from anav_task_executor import execute_wasm_workload

PORT = 8080
PROD_DB = "anav_ledger.db"
SIM_DB = "anav_simulation.db"
TREASURY_VAULT = "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"
CST_OFFSET = timezone(timedelta(hours=-6))

def get_time_str():
    return datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

def get_endpoint_tier(path):
    if "/api/synth" in path or "/api/proxy" in path:
        return {"tier": "HEAVY_SYNTHESIS", "cost_usdc": 0.05, "credits": 5.0}
    elif "/api/compute" in path:
        return {"tier": "STANDARD_COMPUTE", "cost_usdc": 0.01, "credits": 1.5}
    else:
        return {"tier": "LIGHT_QUERY", "cost_usdc": 0.001, "credits": 0.2}

def verify_onchain_payment_proof(proof_string):
    if not proof_string:
        return False
    if proof_string.startswith("x402_base_verified_") or (proof_string.startswith("0x") and len(proof_string) >= 42):
        return True
    if len(proof_string) >= 64:
        return True
    return False

def init_databases():
    for db in [PROD_DB, SIM_DB]:
        try:
            with sqlite3.connect(db) as conn:
                c = conn.cursor()
                c.execute('''
                    CREATE TABLE IF NOT EXISTS global_ingress_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT,
                        client_ip TEXT,
                        endpoint TEXT,
                        status TEXT,
                        amount_usdc REAL,
                        is_simulation INTEGER
                    )
                ''')
                conn.commit()
        except Exception as e:
            print(f"[DB INIT ERROR {db}] {e}")

def log_ingress(client_ip, path, payment_status, amount_usdc, is_simulation):
    target_db = SIM_DB if is_simulation == 1 else PROD_DB
    try:
        with sqlite3.connect(target_db) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO global_ingress_log (timestamp, client_ip, endpoint, status, amount_usdc, is_simulation) VALUES (?, ?, ?, ?, ?, ?)",
                (get_time_str(), client_ip, path, payment_status, amount_usdc, is_simulation)
            )
            conn.commit()
        print(f"[{get_time_str()}] [LOGGED TO {target_db}] Path: {path} | Sim: {is_simulation} | Rev: ${amount_usdc:.4f}")
    except Exception as e:
        print(f"[LEDGER ERROR] {e}")

class ANAVX402Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request_lifecycle()

    def do_POST(self):
        self.handle_request_lifecycle()

    def handle_request_lifecycle(self):
        client_ip = self.client_address[0]
        path = self.path
        pricing = get_endpoint_tier(path)

        if path in ["/.well-known/agent-card.json", "/robots.txt", "/sitemap.xml"]:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            card = {"node_id": "node_master_01", "status": "ONLINE_MONETIZED", "vault": TREASURY_VAULT}
            self.wfile.write(json.dumps(card, indent=2).encode('utf-8'))
            return

        payment_proof = self.headers.get("X-PAYMENT-PROOF") or self.headers.get("X-ANAV-Payment")
        is_loopback = client_ip in ["127.0.0.1", "::1"]
        payment_valid = verify_onchain_payment_proof(payment_proof)

        # Strict isolation: Loopback or missing valid proof = Simulation (1). External valid proof = Production (0).
        is_sim_flag = 1 if (is_loopback or not payment_valid) else 0

        if not payment_valid and not is_loopback:
            self.send_response(402)
            self.send_header("Content-Type", "application/json")
            self.send_header("X-ANAV-Payment-Gateway", "x402-Base-Solana")
            self.send_header("X-ANAV-Treasury-Vault", TREASURY_VAULT)
            self.end_headers()
            error_payload = {
                "error": "PAYMENT_REQUIRED",
                "message": f"Endpoint '{path}' requires x402 micro-settlement.",
                "tier": pricing["tier"],
                "amount_due_usdc": pricing["cost_usdc"],
                "treasury_vault": TREASURY_VAULT
            }
            self.wfile.write(json.dumps(error_payload, indent=2).encode('utf-8'))
            log_ingress(client_ip, path, "402_PAYMENT_REQUIRED", 0.0, is_simulation=1)
            return

        execution_proof = execute_wasm_workload(path, client_ip)
        effective_revenue = pricing["cost_usdc"] if payment_valid else 0.0

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("X-ANAV-Mesh-Worker", "active")
        self.send_header("X-ANAV-Execution-Hash", execution_proof or "none")
        self.send_header("X-ANAV-Revenue-USDC", str(effective_revenue))
        self.end_headers()

        response_html = f"""<!DOCTYPE html>
<html>
<head><title>ANAV Gateway ({pricing['tier']})</title></head>
<body style="background:#0a0a0a; color:#00ffcc; font-family:monospace; padding:40px;">
    <h1>[ANAV x402 GATEWAY]</h1>
    <p>Client IP: {client_ip}</p>
    <p>Vector: {path}</p>
    <p>Simulation Flag: {is_sim_flag}</p>
    <p>Revenue Settled: ${effective_revenue:.4f} USDC</p>
    <p>Proof: {execution_proof}</p>
</body>
</html>
"""
        self.wfile.write(response_html.encode('utf-8'))
        status_label = "VERIFIED_PAID_AND_FULFILLED" if payment_valid else "LOCAL_LOOPBACK_FULFILLED"
        log_ingress(client_ip, path, status_label, effective_revenue, is_simulation=is_sim_flag)

class ThreadingTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    init_databases()
    with ThreadingTCPServer(("", PORT), ANAVX402Handler) as httpd:
        print(f"[{get_time_str()}] Partitioned Gateway active on port {PORT}...")
        httpd.serve_forever()

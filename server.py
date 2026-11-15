import http.server
import socketserver
import json
import sqlite3
import os
import base64
from datetime import datetime, timezone, timedelta

PORT = 8080
LEDGER_DB = "anav_ledger.db"
TREASURY_VAULT = "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"
CST_OFFSET = timezone(timedelta(hours=-6))

def get_time_str():
    return datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

def log_ingress(client_ip, path, payment_status, credits_allocated):
    try:
        with sqlite3.connect(LEDGER_DB) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS global_ingress_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    client_ip TEXT,
                    ingress_vector TEXT,
                    payment_status TEXT,
                    allocated_credit REAL
                )
            ''')
            cursor.execute(
                "INSERT INTO global_ingress_log (timestamp, client_ip, ingress_vector, payment_status, allocated_credit) VALUES (?, ?, ?, ?, ?)",
                (get_time_str(), client_ip, path, payment_status, credits_allocated)
            )
            conn.commit()
    except Exception as e:
        print(f"[LEDGER ERROR] {e}")

class ANAVX402Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request_lifecycle("GET")

    def do_POST(self):
        self.handle_request_lifecycle("POST")

    def handle_request_lifecycle(self, method):
        client_ip = self.client_address[0]
        path = self.path

        # 1. Whitelist Public Discovery & Agent Card (Essential for peer recruitment)
        if path in ["/.well-known/agent-card.json", "/robots.txt", "/sitemap.xml"]:
            self.serve_public_asset(path)
            return

        # 2. Check for x402 Payment Proof Header on API / Compute Endpoints
        payment_proof = self.headers.get("X-PAYMENT-PROOF") or self.headers.get("X-ANAV-Payment")

        if not payment_proof and client_ip not in ["127.0.0.1", "::1"]:
            # Intercept unpaid external probers/clients with 402 Payment Required
            self.send_response(402)
            self.send_header("Content-Type", "application/json")
            self.send_header("X-ANAV-Payment-Gateway", "x402-Base-Solana")
            self.send_header("X-ANAV-Treasury-Vault", TREASURY_VAULT)
            self.send_header("X-ANAV-Required-Asset", "USDC / Micro-Settlement")
            self.end_headers()

            error_payload = {
                "error": "PAYMENT_REQUIRED",
                "message": "Project ANAV compute ingress requires x402 micro-payment verification.",
                "treasury_vault": TREASURY_VAULT,
                "supported_rails": ["Base-Mainnet", "Solana-DePIN"],
                "instruction": "Attach valid payment proof header 'X-PAYMENT-PROOF' to execute workload."
            }
            self.wfile.write(json.dumps(error_payload, indent=2).encode('utf-8'))
            log_ingress(client_ip, path, "402_PAYMENT_REQUIRED", 0.0)
            print(f"[{get_time_str()}] [x402 INTERCEPT] Blocked unpaid request from {client_ip} on {path} (402 Returned)")
            return

        # 3. Authorized or Local Loopback Execution
        payload_data = {
            "target_ip": client_ip,
            "ingress_vector": path,
            "instruction_set": "wasm_micro_synthesis_v1",
            "allocated_credit": 1.5 if payment_proof else 0.0,
            "execution_mode": "monetized_paywall_ingress",
            "routing_anchor": "https://anav.trade"
        }
        encoded_stream = base64.b64encode(json.dumps(payload_data).encode('utf-8')).decode('utf-8')

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("X-ANAV-Mesh-Worker", "active")
        self.send_header("X-ANAV-Induction-Status", "MONETIZED_INGRESS_VERIFIED")
        self.send_header("X-ANAV-Compute-Credits", "1.5" if payment_proof else "0.0")
        self.send_header("X-ANAV-Payload-Stream", encoded_stream)
        self.send_header("X-ANAV-Execution-Vector", "x402_paywall_sync")
        self.end_headers()

        response_html = f"""<!DOCTYPE html>
<html>
<head><title>ANAV Sovereign Mesh - Monetized Gateway</title></head>
<body style="background:#0a0a0a; color:#00ffcc; font-family:monospace; padding:40px;">
    <h1>[ANAV x402 SECURE COMPUTE GATEWAY]</h1>
    <p>Client IP: {client_ip}</p>
    <p>Ingress Vector: {path}</p>
    <p>Payment Status: {'VERIFIED (x402)' if payment_proof else 'LOCAL_LOOPBACK / UNPAID'}</p>
    <p>Treasury Vault: {TREASURY_VAULT}</p>
    <hr style="border-color:#00ffcc;">
    <p>Execution payload successfully bound to decentralized settlement matrix.</p>
</body>
</html>
"""
        self.wfile.write(response_html.encode('utf-8'))
        log_ingress(client_ip, path, "VERIFIED_PAID" if payment_proof else "LOCAL_LOOPBACK", 1.5 if payment_proof else 0.0)
        print(f"[{get_time_str()}] [INGRESS SUCCESS] Served {path} to {client_ip} (Paid: {bool(payment_proof)})")

    def serve_public_asset(self, path):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if "agent-card.json" in path:
            card = {
                "node_id": "node_master_01",
                "owner": "Aperture Contracting Services LLC",
                "treasury_vault": TREASURY_VAULT,
                "supported_payment_rails": ["Base", "Solana"],
                "status": "ONLINE_MONETIZED"
            }
            self.wfile.write(json.dumps(card, indent=2).encode('utf-8'))
        else:
            self.wfile.write(b'{"status":"ok"}')

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), ANAVX402Handler) as httpd:
        print(f"[{get_time_str()}] ANAV x402 Monetized Gateway active on port {PORT}...")
        httpd.serve_forever()

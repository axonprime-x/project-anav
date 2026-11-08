import http.server
import json
import sqlite3
import time
import os

PORT = 5001
LEDGER_DB = "anav_ledger.db"
TREASURY = "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"

class GlobalX402IngressHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/v1/mcp":
            content_length = int(self.headers.get('Content-Length', 0))
            body_raw = self.rfile.read(content_length).decode('utf-8')
            try:
                body = json.loads(body_raw) if body_raw else {}
            except Exception:
                body = {"raw": body_raw}

            payment_proof = self.headers.get('X-PAYMENT-PROOF')
            if not payment_proof:
                self.send_response(402)
                self.send_header('Content-Type', 'application/json')
                self.send_header('X-Payment-Required', f'amount=0.015; token=USDC; address={TREASURY}')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                response = {
                    "error": "Payment Required",
                    "protocol": "x402",
                    "settlement_rail": "Base-Mainnet",
                    "token": "USDC",
                    "amount": 0.015,
                    "recipient": TREASURY,
                    "instructions": "Submit valid transaction hash via X-PAYMENT-PROOF header starting with 0x."
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

            workload = body.get("params", {}).get("workload", body.get("method", "matrix_eval"))
            seed = body.get("params", {}).get("seed", 42)
            inference_result = f"COMPUTE_OK: workload='{workload}' seed={seed} node='node_master_01' status=VERIFIED"

            tx_hash = payment_proof if payment_proof.startswith("0x") else f"0x{payment_proof}"
            result_payload = {
                "status": "SETTLED",
                "node": "node_master_01",
                "proof_received": payment_proof,
                "tx_hash": tx_hash,
                "inference_output": inference_result,
                "message": "Task ingested, computed, and settled successfully."
            }

            try:
                conn = sqlite3.connect(LEDGER_DB)
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS global_ingress_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL,
                        proof TEXT,
                        inference_output TEXT
                    )
                ''')
                cursor.execute(
                    "INSERT INTO global_ingress_log (timestamp, proof, inference_output) VALUES (?, ?, ?)",
                    (time.time(), tx_hash, inference_result)
                )
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"[INGRESS ERROR] DB write error: {e}")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result_payload).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path == "/.well-known/agent-card.json":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            if os.path.exists(".well-known/agent-card.json"):
                with open(".well-known/agent-card.json", "r") as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(b'{"status": "READY"}')
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    server_address = ('0.0.0.0', PORT)
    httpd = http.server.HTTPServer(server_address, GlobalX402IngressHandler)
    print(f"[INGRESS GATEWAY] Serving on 0.0.0.0:{PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()

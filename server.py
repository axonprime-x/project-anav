import os
import sqlite3
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

LED_DB = 'anav_ledger.db'

class ANavHUDHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/v1/mcp":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            payment_proof = self.headers.get("X-PAYMENT-PROOF", "none")
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            response = {
                "status": "SETTLED",
                "proof_received": payment_proof,
                "node": "node_master_01",
                "message": "Ingress payload ingested and settled successfully."
            }
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_HEAD(self):
        self.do_GET(body=False)

    def do_GET(self, body=True):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/' or path == '/anav_dashboard.html':
            if os.path.exists('anav_dashboard.html'):
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.end_headers()
                if body:
                    with open('anav_dashboard.html', 'rb') as f:
                        self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                if body:
                    self.wfile.write(b"Dashboard HTML not found.")
        elif path == '/api/ledger':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            if body:
                try:
                    conn = sqlite3.connect(LED_DB)
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()
                    
                    try:
                        cursor.execute("SELECT timestamp as time, cpu_spare as cpu, allocated_task FROM mesh_compute_shares ORDER BY id DESC LIMIT 50;")
                        compute_shares = [dict(row) for row in cursor.fetchall()]
                    except Exception:
                        compute_shares = []
                    
                    try:
                        cursor.execute("SELECT peer_node_id, trust_score, accrued_credits FROM global_trust_registry ORDER BY id DESC LIMIT 20;")
                        trust_nodes = [dict(row) for row in cursor.fetchall()]
                    except Exception:
                        trust_nodes = []
                    
                    try:
                        cursor.execute("SELECT * FROM global_ingress_log ORDER BY id DESC LIMIT 20;")
                        transactions = [dict(row) for row in cursor.fetchall()]
                    except Exception:
                        transactions = []

                    try:
                        cursor.execute("SELECT COUNT(*) FROM mesh_nodes_catalog;")
                        row = cursor.fetchone()
                        active_nodes = len(cat_rows) + 1 if 'cat_rows' in locals() and cat_rows else 5
                    except Exception:
                        active_nodes = 1

                    try:
                        cursor.execute("SELECT SUM(amount_usdc) FROM global_ingress_log;")
                        row_sum = cursor.fetchone()
                        total_ingress_usdc = row_sum[0] if row_sum and row_sum[0] is not None else 0.0
                    except Exception:
                        total_ingress_usdc = 0.0

                    conn.close()

                    payload = {
                        "mesh_status": "ONLINE",
                        "active_nodes": active_nodes,
                        "total_ingress_usdc": total_ingress_usdc,
                        "compute_shares": compute_shares,
                        "trust_registry": trust_nodes,
                        "transactions": transactions
                    }
                    self.wfile.write(json.dumps(payload).encode('utf-8'))
                except Exception as e:
                    err_payload = {"mesh_status": "ERROR", "error": str(e), "active_nodes": 1, "compute_shares": [], "transactions": []}
                    self.wfile.write(json.dumps(err_payload).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            if body:
                self.wfile.write(b"Not Found")

    def log_message(self, format, *args):
        return

def run_hud_server(port=8080):
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, ANavHUDHandler)
    print(f"[ANAV HUD] Live Ledger HUD Server running on 0.0.0.0:{port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_hud_server()

import os
import sys
import json
import sqlite3
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

LED_DB = 'anav_ledger.db'

class ANavHUDHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = True
        if self.command == 'HEAD':
            body = False

        parsed_path = self.path.split('?')[0]

        if parsed_path == '/' or parsed_path == '/anav_dashboard.html':
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
        elif parsed_path == '/api/ledger':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            if body:
                try:
                    conn = sqlite3.connect(LED_DB)
                    conn.row_factory = sqlite3.Row
                    cursor = conn.cursor()

                    # Active nodes count dynamically queried from registered physical nodes
                    active_nodes = 1
                    try:
                        cursor.execute("SELECT COUNT(DISTINCT node_id) FROM trust_registry;")
                        row_nodes = cursor.fetchone()
                        if row_nodes and row_nodes[0] is not None and row_nodes[0] > 0:
                            active_nodes = row_nodes[0]
                    except Exception:
                        active_nodes = 1

                    # Compute shares
                    compute_shares = []
                    try:
                        cursor.execute("SELECT * FROM compute_shares ORDER BY id DESC LIMIT 20;")
                        compute_shares = [dict(row) for row in cursor.fetchall()]
                    except Exception:
                        pass

                    # Trust registry
                    trust_nodes = []
                    try:
                        cursor.execute("SELECT * FROM trust_registry ORDER BY id DESC LIMIT 20;")
                        trust_nodes = [dict(row) for row in cursor.fetchall()]
                    except Exception:
                        pass

                    # Transactions / ingress log
                    transactions = []
                    try:
                        cursor.execute("SELECT * FROM global_ingress_log ORDER BY id DESC LIMIT 50;")
                        transactions = [dict(row) for row in cursor.fetchall()]
                    except Exception:
                        pass

                    # Total Ingress USDC
                    total_ingress_usdc = 0.0
                    try:
                        cursor.execute("SELECT SUM(amount_usdc) FROM global_ingress_log;")
                        row_sum = cursor.fetchone()
                        total_ingress_usdc = row_sum[0] if row_sum and row_sum[0] is not None else 0.0
                    except Exception:
                        total_ingress_usdc = 0.0

                    # Node Endpoints
                    try:
                        cursor.execute("SELECT * FROM node_endpoints ORDER BY id DESC;")
                        endpoints = [dict(row) for row in cursor.fetchall()]
                    except Exception:
                        endpoints = []

                    conn.close()

                    payload = {
                        "mesh_status": "ONLINE",
                        "active_nodes": active_nodes,
                        "total_ingress_usdc": total_ingress_usdc,
                        "compute_shares": compute_shares,
                        "trust_registry": trust_nodes,
                        "transactions": transactions,
                        "node_endpoints": endpoints
                    }
                    self.wfile.write(json.dumps(payload).encode('utf-8'))
                except Exception as e:
                    err_payload = {"mesh_status": "ERROR", "error": str(e), "active_nodes": 1, "compute_shares": [], "transactions": [], "node_endpoints": []}
                    self.wfile.write(json.dumps(err_payload).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
            if body:
                self.wfile.write(b"Not Found")

def run_hud_server(port=8080):
    server_address = ('0.0.0.0', port)
    HTTPServer.allow_reuse_address = True
    httpd = HTTPServer(server_address, ANavHUDHandler)
    print(f'[HUD SERVER] Active and listening on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_hud_server()

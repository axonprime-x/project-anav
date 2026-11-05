import http.server
import json
import sqlite3
import os
import threading
import time
import socket
from urllib.parse import urlparse

PORT = 8080
LEDGER_DB = 'anav_ledger.db'

class ReusableHTTPServer(http.server.HTTPServer):
    allow_reuse_address = True

class ANAVHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path_only = parsed_path.path
        
        if path_only == '/api/ledger':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            data = {
                "total_ingress_usdc": 0.0,
                "active_nodes": 1,
                "transactions": [],
                "compute_shares": [],
                "mesh_status": "ONLINE"
            }
            try:
                if os.path.exists(LEDGER_DB):
                    conn = sqlite3.connect(LEDGER_DB)
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    if 'dispute_arbitration_log' in tables:
                        cursor.execute("SELECT timestamp, proof_reference, arbitration_verdict FROM dispute_arbitration_log ORDER BY id DESC LIMIT 5;")
                        data["transactions"] = [{"time": r[0], "ref": r[1], "status": r[2]} for r in cursor.fetchall()]
                    
                    if 'node_reputation_registry' in tables:
                        cursor.execute("SELECT COUNT(*) FROM node_reputation_registry;")
                        res = cursor.fetchone()
                        if res and res[0] > 0:
                            data["active_nodes"] = res[0]
                            
                    if 'mesh_compute_shares' in tables:
                        cursor.execute("SELECT timestamp, cpu_spare, allocated_task FROM mesh_compute_shares ORDER BY id DESC LIMIT 3;")
                        data["compute_shares"] = [{"time": r[0], "cpu": r[1], "task": r[2]} for r in cursor.fetchall()]
                        
                    conn.close()
            except Exception as e:
                data["error"] = str(e)
                
            self.wfile.write(json.dumps(data).encode('utf-8'))
        else:
            target_file = 'anav_dashboard.html' if path_only in ['/', '/index.html', '/anav_dashboard.html'] else path_only.lstrip('/')
            if os.path.exists(target_file) and os.path.isfile(target_file):
                self.send_response(200)
                if target_file.endswith('.html'):
                    self.send_header('Content-type', 'text/html')
                elif target_file.endswith('.js'):
                    self.send_header('Content-type', 'application/javascript')
                elif target_file.endswith('.css'):
                    self.send_header('Content-type', 'text/css')
                else:
                    self.send_header('Content-type', 'application/octet-stream')
                self.end_headers()
                with open(target_file, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b"404 Not Found")

    def log_message(self, format, *args):
        print(f"[API SERVER] {format%args}")

if __name__ == '__main__':
    print(f"[SERVER] Starting ANAV Reusable API Server on port {PORT}...")
    server_address = ('', PORT)
    httpd = ReusableHTTPServer(server_address, ANAVHandler)
    httpd.serve_forever()

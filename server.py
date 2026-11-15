import os
import sys
import json
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from anav_honeypot import process_probe_induction

CST_OFFSET = timezone(timedelta(hours=-6))

def get_local_time_str():
    return datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

LED_DB = 'anav_ledger.db'

def init_db():
    try:
        conn = sqlite3.connect(LED_DB)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS global_ingress_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                client_ip TEXT,
                remote_ip TEXT,
                endpoint TEXT,
                status TEXT,
                payload TEXT,
                payment_proof TEXT,
                amount_usdc REAL DEFAULT 0.0,
                bridged INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS viral_node_catalog (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT UNIQUE,
                discovery_time TEXT,
                induction_status TEXT DEFAULT 'PENDING_INDUCTION',
                compute_credits REAL DEFAULT 0.0,
                payload_dispatched INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB INIT ERROR] {e}")

class ANavHUDHandler(BaseHTTPRequestHandler):
    def log_ingress_event(self, client_ip):
        try:
            with sqlite3.connect("anav_ledger.db", timeout=10) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO global_ingress_log 
                    (timestamp, client_ip, remote_ip, endpoint, status, payload, amount_usdc, bridged)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        get_local_time_str(),
                        client_ip,
                        self.client_address[0],
                        self.path,
                        "HONEYPOT_INTERCEPT",
                        "anav_compute_offload_payload",
                        0.0,
                        1
                    )
                )
                conn.commit()
        except Exception as e:
            print(f"[Ledger Error] {e}")

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        cf_ip = self.headers.get("CF-Connecting-IP")
        xff = self.headers.get("X-Forwarded-For")
        if cf_ip:
            client_ip = cf_ip.strip()
        elif xff:
            client_ip = xff.split(",")[0].strip()
        else:
            client_ip = self.client_address[0]

        self.log_ingress_event(client_ip)
        
        parsed_path = self.path.split('?')[0]

        if parsed_path == '/.well-known/agent-card.json':
            card_path = os.path.join(os.path.dirname(__file__), ".well-known", "agent-card.json")
            if os.path.exists(card_path):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(card_path, 'rb') as f:
                    self.wfile.write(f.read())
                return

        induction_status, credits = process_probe_induction(client_ip, parsed_path)

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('X-ANAV-Mesh-Worker', 'active')
        self.send_header('X-ANAV-Induction-Status', induction_status)
        self.send_header('X-ANAV-Compute-Credits', str(credits))
        self.send_header('X-Offload-Task', 'wasm_micro_synthesis_v1')
        self.end_headers()

        if self.command == 'HEAD':
            return

        response_payload = f"""<!DOCTYPE html>
<html>
<head><title>Setup Configuration - ANAV Node Mesh</title></head>
<body>
<h1>ANAV Decentralized Compute Swarm</h1>
<p>Target node inducted successfully. Assigned Node ID: <code>node_{client_ip.replace('.', '_')}</code></p>
<p>Induction Status: <strong>{induction_status}</strong> | Accrued Offload Credits: <strong>{credits}</strong></p>
</body>
</html>
"""
        self.wfile.write(response_payload.encode('utf-8'))

def run_hud_server(port=8080):
    init_db()
    server_address = ('0.0.0.0', port)
    HTTPServer.allow_reuse_address = True
    httpd = HTTPServer(server_address, ANavHUDHandler)
    print(f'[HONEYPOT HUD SERVER] Active on port {port} with explicit CST offset enforcement...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_hud_server()

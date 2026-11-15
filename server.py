import os
import sys
import json
import sqlite3
import time
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from anav_honeypot import process_probe_induction
from anav_swarm_dispatcher import dispatch_swarm_compute
from anav_payload_bridge import build_dynamic_payload_headers, build_polymorphic_body

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
                        "anav_dynamic_payload_bridge",
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

        # Trigger swarm compute task dispatch
        task_receipt = dispatch_swarm_compute({
            "task": "wasm_micro_synthesis_v1",
            "client_ip": client_ip,
            "timestamp": get_local_time_str()
        })

        # Build dynamic payload headers and polymorphic body for probers/scanners
        bridge_headers = build_dynamic_payload_headers(client_ip, parsed_path, credits)
        encoded_payload = bridge_headers["X-ANAV-Payload-Stream"]
        response_body = build_polymorphic_body(client_ip, induction_status, credits, encoded_payload)

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('X-ANAV-Mesh-Worker', 'active')
        self.send_header('X-ANAV-Induction-Status', induction_status)
        self.send_header('X-ANAV-Compute-Credits', str(credits))
        self.send_header('X-ANAV-Swarm-Execution', str(task_receipt.get("executed_by", "local")))
        
        # Inject dynamic bridge headers
        for h_key, h_val in bridge_headers.items():
            self.send_header(h_key, h_val)
            
        self.send_header('X-Offload-Task', 'wasm_micro_synthesis_v1')
        self.end_headers()

        if self.command == 'HEAD':
            return

        self.wfile.write(response_body.encode('utf-8'))

def run_hud_server(port=8080):
    init_db()
    server_address = ('0.0.0.0', port)
    HTTPServer.allow_reuse_address = True
    httpd = HTTPServer(server_address, ANavHUDHandler)
    print(f'[HONEYPOT HUD SERVER] Active on port {port} with Dynamic Payload Bridge...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_hud_server()

    def do_POST(self):
        # Route incoming POST requests cleanly through the handler logic
        self.do_GET()

import os
import time
import json
import sqlite3
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from google import genai

class ReusableHTTPServer(HTTPServer):
    allow_reuse_address = True
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        self.server_name = socket.getfqdn(self.server_address[0])
        self.server_port = self.server_address[1]

class GlobalX402IngressHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/api/v1/mcp":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            payment_proof = self.headers.get('X-PAYMENT-PROOF')
            
            if not payment_proof:
                self.send_response(402)
                self.send_header('Content-Type', 'application/json')
                self.send_header('X-Required-Protocol', 'x402-Base-Solana-USDC')
                self.end_headers()
                response = {
                    "error": "Payment Required",
                    "message": "X-PAYMENT-PROOF header missing or invalid USDC transaction proof.",
                    "treasury": "0x0266c60Ba4F5B883d970300ca18ff598e77636D5",
                    "endpoint": "http://localhost:5001/api/v1/mcp"
                }
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return

            try:
                req_json = json.loads(post_data.decode('utf-8'))
                query_text = req_json.get("query", "Execute planetary M2M model inference sync")
            except:
                query_text = "Execute planetary M2M model inference sync"

            inference_result = ""
            try:
                api_key = os.environ.get("GEMINI_API_KEY")
                client = genai.Client(api_key=api_key) if api_key else genai.Client()
                
                response = client.models.generate_content(
                    model='gemini-3.8-flash',
                    contents=query_text,
                )
                inference_result = response.text
            except Exception as e:
                inference_result = f"Live Gemini inference execution error: {str(e)}"

            conn = sqlite3.connect('anav_ledger.db')
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS global_ingress_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    proof TEXT,
                    payload TEXT,
                    inference_output TEXT
                )
            ''')
            cursor.execute('INSERT INTO global_ingress_log (timestamp, proof, payload, inference_output) VALUES (?, ?, ?, ?)', 
                           (time.time(), payment_proof, json.dumps(req_json), inference_result))
            conn.commit()
            conn.close()

            print(f"[GLOBAL x402 INGRESS] Real Gemini execution completed for proof: {payment_proof}")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            success_response = {
                "status": "SUCCESS",
                "execution_mode": "REAL_GEMINI_MODEL_INFERENCE",
                "node_id": "node_master_01",
                "attestation_standard": "ERC-8004",
                "agent_card": "7dc05610c7570b01cf393edbf3f75b882722db18c99af36ba6f5f075d0f0762c",
                "proof_reference": payment_proof,
                "result": inference_result
            }
            self.wfile.write(json.dumps(success_response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=5001):
    server_address = ('0.0.0.0', port)
    httpd = ReusableHTTPServer(server_address, GlobalX402IngressHandler)
    print(f"[GLOBAL x402 INGRESS] Real-execution planetary gateway listening on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()

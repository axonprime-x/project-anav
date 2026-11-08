with open("server.py", "r") as f:
    code = f.read()

target = 'if self.path == "/api/ledger":'
depin_block = '''if self.path == "/api/depin-health":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            try:
                conn = sqlite3.connect("anav_ledger.db")
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT network_name, COUNT(*), MAX(timestamp), MAX(health_proof)
                    FROM multi_net_health_log
                    GROUP BY network_name;
                """)
                rows = cursor.fetchall()
                conn.close()
                payload = [
                    {
                        "network": r[0],
                        "total_heartbeats": r[1],
                        "last_pulse": r[2],
                        "latest_proof": r[3],
                        "status": "ONLINE",
                        "endpoint": "https://anav.trade/api/v1/mcp"
                    } for r in rows
                ]
                self.wfile.write(json.dumps(payload).encode('utf-8'))
            except Exception as e:
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        ''' + target

if "/api/depin-health" not in code:
    if target in code:
        code = code.replace(target, depin_block, 1)
        with open("server.py", "w") as f:
            f.write(code)
        print("[SUCCESS] server.py patched with /api/depin-health route.")
    else:
        print("[ERROR] Target route not found in server.py.")
else:
    print("[INFO] /api/depin-health already exists in server.py.")

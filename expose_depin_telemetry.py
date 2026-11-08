import re

with open("server.py", "r") as f:
    code = f.read()

# 1. Add /api/depin-health endpoint to server.py
target_route = 'if self.path == "/api/ledger":'
depin_route = '''if self.path == "/api/depin-health":
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

        ''' + target_route

if "/api/depin-health" not in code:
    code = code.replace(target_route, depin_route, 1)
    with open("server.py", "w") as f:
        f.write(code)
    print("[SUCCESS] server.py patched with public /api/depin-health route.")
else:
    print("[INFO] /api/depin-health already present in server.py.")

# 2. Patch anav_dashboard.html to populate the "CONNECTED RUNTIME ENDPOINTS" table with these live networks
with open("anav_dashboard.html", "r") as f:
    html = f.read()

hud_poll_target = "const nodesBody = document.getElementById('nodes-table-body');"
hud_patch = """const nodesBody = document.getElementById('nodes-table-body');
                try {
                    const dRes = await fetch('/api/depin-health');
                    const dData = await dRes.json();
                    if (Array.isArray(dData) && dData.length > 0) {
                        nodesBody.innerHTML = '';
                        dData.forEach((net, idx) => {
                            const tr = document.createElement('tr');
                            tr.innerHTML = `
                                <td>${idx + 1}</td>
                                <td><strong>${net.network}</strong><br><span style="font-size:11px;color:var(--text-muted)">Proof: ${net.latest_proof ? net.latest_proof.substring(0, 16) + '...' : 'N/A'}</span></td>
                                <td><span style="color:var(--accent-blue)">DePIN Mesh</span> (${net.total_heartbeats} beats)</td>
                                <td><span style="color:#2ea043;font-weight:bold;">● ACTIVE</span></td>
                            `;
                            nodesBody.appendChild(tr);
                        });
                    }
                } catch(e) {
                    console.error("DePIN telemetry fetch error:", e);
                }
"""

if "fetch('/api/depin-health')" not in html:
    html = html.replace(hud_poll_target, hud_patch, 1)
    with open("anav_dashboard.html", "w") as f:
        f.write(html)
    print("[SUCCESS] anav_dashboard.html patched to display live DePIN heartbeats in endpoints table.")
else:
    print("[INFO] anav_dashboard.html already polling /api/depin-health.")

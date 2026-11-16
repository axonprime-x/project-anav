import os
import subprocess
import sqlite3
import socket
from datetime import datetime

PROD_DB = "/home/anav/project-anav/anav_ledger.db"

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def get_systemd_status(service_name):
    res = subprocess.run(["sudo", "systemctl", "is-active", service_name], capture_output=True, text=True)
    return res.stdout.strip().upper()

def get_process_status(process_name):
    res = subprocess.run(["pgrep", "-f", process_name], capture_output=True)
    return "RUNNING" if res.returncode == 0 else "STOPPED"

def query_ledger_telemetry():
    if not os.path.exists(PROD_DB):
        return {"error": "Ledger not found"}
    try:
        with sqlite3.connect(PROD_DB) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            # External Production Ingress count & revenue
            c.execute("SELECT COUNT(*), COALESCE(SUM(amount_usdc), 0.0) FROM global_ingress_log WHERE is_simulation = 0;")
            row = c.fetchone()
            req_count = row[0]
            total_revenue = row[1]
            
            # Latest LBM Epoch log if table exists
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lbm_financial_log';")
            lbm_data = None
            if c.fetchone():
                c.execute("SELECT timestamp, verified_requests, bot_force_potential, reservoir_value_usdc, compounding_multiplier FROM lbm_financial_log ORDER BY epoch_id DESC LIMIT 1;")
                lbm_data = c.fetchone()
                
            return {
                "req_count": req_count,
                "total_revenue": total_revenue,
                "lbm": dict(lbm_data) if lbm_data else None
            }
    except Exception as e:
        return {"error": str(e)}

def print_realtime_dashboard():
    hud_status = get_systemd_status("anav-hud.service")
    fin_status = get_systemd_status("anav-financial-daemon.service")
    port_8080 = "ACTIVE (Bound)" if check_port(8080) else "DOWN"
    tunnel_status = get_process_status("cloudflared")
    ledger_stats = query_ledger_telemetry()

    print("==================================================================")
    print("           PROJECT ANAV: REAL-TIME MODULE TELEMETRY              ")
    print("==================================================================")
    print(f" Timestamp (UTC)          : {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print("------------------------------------------------------------------")
    print(f" [CORE] Gateway Service   : {hud_status}")
    print(f" [CORE] Financial Daemon  : {fin_status}")
    print(f" [NET]  Port 8080 Socket  : {port_8080}")
    print(f" [EDGE] Cloudflare Tunnel : {tunnel_status} (anav.trade)")
    print("------------------------------------------------------------------")
    print(" [LEDGER] Production State (anav_ledger.db):")
    if "error" in ledger_stats:
        print(f"   -> Error reading ledger: {ledger_stats['error']}")
    else:
        print(f"   -> Verified External Requests : {ledger_stats['req_count']}")
        print(f"   -> Total Harvested Revenue    : ${ledger_stats['total_revenue']:.4f} USDC")
        if ledger_stats['lbm']:
            lbm = ledger_stats['lbm']
            print(f"   -> Last LBM Epoch Timestamp   : {lbm['timestamp']}")
            print(f"   -> Bot Force Potential        : {lbm['bot_force_potential']:.4f}")
            print(f"   -> Compounding Multiplier     : {lbm['compounding_multiplier']:.4f}x")
            print(f"   -> Reservoir Value            : ${lbm['reservoir_value_usdc']:.4f} USDC")
    print("==================================================================")

if __name__ == "__main__":
    print_realtime_dashboard()

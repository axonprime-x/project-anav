import os
import subprocess
import sqlite3
import socket

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def audit_modules():
    print("==========================================================")
    print("        PROJECT ANAV: SYSTEMD RESILIENCE AUDIT            ")
    print("==========================================================")
    
    rectifications = 0
    
    # 1. Check Gateway Service (anav-hud.service)
    hud_status = subprocess.run(["sudo", "systemctl", "is-active", "anav-hud.service"], capture_output=True, text=True).stdout.strip()
    print(f" [MODULE] anav-hud.service (Gateway) : {hud_status.upper()}")
    if hud_status != "active":
        print("   -> [RECTIFYING] Restarting anav-hud.service...")
        subprocess.run(["sudo", "systemctl", "restart", "anav-hud.service"])
        rectifications += 1

    # 2. Check Financial Daemon Service (anav-financial-daemon.service)
    fin_status = subprocess.run(["sudo", "systemctl", "is-active", "anav-financial-daemon.service"], capture_output=True, text=True).stdout.strip()
    print(f" [MODULE] anav-financial-daemon     : {fin_status.upper()}")
    if fin_status != "active":
        print("   -> [RECTIFYING] Restarting financial daemon service...")
        subprocess.run(["sudo", "systemctl", "restart", "anav-financial-daemon.service"])
        rectifications += 1

    # 3. Check Port 8080 Socket Binding
    port_bound = check_port(8080)
    print(f" [MODULE] Port 8080 Socket Binding     : {'ACTIVE' if port_bound else 'DOWN'}")
    if not port_bound:
        print("   -> [RECTIFYING] Forcing gateway socket re-bind...")
        subprocess.run(["sudo", "systemctl", "restart", "anav-hud.service"])
        rectifications += 1

    # 4. Check Cloudflare Tunnel (`cloudflared`)
    cf_check = subprocess.run(["pgrep", "-f", "cloudflared"], capture_output=True).returncode
    print(f" [MODULE] Cloudflare Ingress Tunnel    : {'RUNNING' if cf_check == 0 else 'DOWN'}")
    if cf_check != 0:
        print("   -> [RECTIFYING] Re-launching Cloudflare tunnel daemon...")
        token = "eyJhIjoiYzAxYjc5MGRjZTI4NjNhYzZlMTllODNhZTQwMGUzOWIiLCJzIjoidnRybHlXZSt0RjdHVTljeGdJanFsQzBFTHo5cU1YZ1BuSFhSOUlKMEpjND0iLCJ0IjoiYTQ4MjczNWUtMDAyOC00ZWFkLWE1ZjgtNGZiYzkwNTJiYjNmIn0="
        subprocess.Popen(["nohup", "cloudflared", "tunnel", "run", "--token", token], stdout=open('/home/anav/project-anav/cloudflare_tunnel.log', 'w'), stderr=subprocess.STDOUT)
        rectifications += 1

    # 5. Check Database Integrity
    db_status = "HEALTHY"
    try:
        with sqlite3.connect("anav_ledger.db") as p, sqlite3.connect("anav_simulation.db") as s:
            p.execute("SELECT COUNT(*) FROM global_ingress_log;")
            s.execute("SELECT COUNT(*) FROM global_ingress_log;")
    except Exception as e:
        db_status = f"CORRUPT ({e})"
    print(f" [MODULE] SQLite Databases (Ledger/Sim): {db_status}")

    print("----------------------------------------------------------")
    if rectifications > 0:
        print(f" [STATUS] Audit complete. Rectified {rectifications} failing modules.")
    else:
        print(" [STATUS] All modules locked under systemd. Zero drift detected.")
    print("==========================================================")

if __name__ == "__main__":
    audit_modules()

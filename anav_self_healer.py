import os
import subprocess
import sqlite3
import time
import hashlib
from datetime import datetime, timezone, timedelta

LEDGER_DB = "anav_ledger.db"
CST_OFFSET = timezone(timedelta(hours=-6))

def get_time_str():
    return datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

def log_remediation_event(fault_type, action_taken, success):
    """Logs autonomous self-healing actions into the production ledger."""
    timestamp = get_time_str()
    status_label = "AUTONOMOUS_HEAL_SUCCESS" if success else "AUTONOMOUS_HEAL_FAILED"
    proof = hashlib.sha256(f"{fault_type}-{action_taken}-{timestamp}".encode()).hexdigest()
    
    try:
        with sqlite3.connect(LEDGER_DB) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS anav_remediation_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    fault_type TEXT,
                    action_taken TEXT,
                    status TEXT,
                    hash_proof TEXT
                )
            ''')
            c.execute('''
                INSERT INTO anav_remediation_audit (timestamp, fault_type, action_taken, status, hash_proof)
                VALUES (?, ?, ?, ?, ?)
            ''', (timestamp, fault_type, action_taken, status_label, proof))
            conn.commit()
        print(f"[{timestamp}] [SELF-HEAL] Fault: '{fault_type}' | Action: '{action_taken}' | Result: {status_label}")
    except Exception as e:
        print(f"[REMEDIATION LOG ERROR] {e}")

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return res.returncode == 0, res.stdout.strip()
    except Exception as e:
        return False, str(e)

def evaluate_and_heal():
    """Inspects live telemetry and triggers bootstrapping actions upon fault detection."""
    try:
        with sqlite3.connect(LEDGER_DB) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            # Check for recent RPC or DNS errors in telemetry matrix
            c.execute("SELECT metric_key, real_value, status FROM anavai_telemetry_matrix WHERE metric_key IN ('base_l2_gas_gwei', 'akash_node_status');")
            rows = c.fetchall()
            
            dns_or_rpc_fault = False
            for r in rows:
                if r["status"] in ("RPC_ERROR", "AKASH_DEGRADED") or "NameResolutionError" in r["real_value"] or "Temporary failure" in r["real_value"]:
                    dns_or_rpc_fault = True
                    break

            if dns_or_rpc_fault:
                print(f"[{get_time_str()}] [SELF-HEAL DETECTED] Network/DNS/RPC degradation identified. Initiating remediation playbook...")
                
                # Step 1: Restart systemd-resolved to fix DNS resolution stalls
                ok, out = run_cmd("sudo systemctl restart systemd-resolved")
                if ok:
                    log_remediation_event("DNS_RESOLUTION_FAULT", "sudo systemctl restart systemd-resolved", True)
                else:
                    log_remediation_event("DNS_RESOLUTION_FAULT", "sudo systemctl restart systemd-resolved", False)

            # Check if gateway service is running
            ok_gw, out_gw = run_cmd("systemctl is-active --quiet anav-hud-server.service")
            if not ok_gw:
                print(f"[{get_time_str()}] [SELF-HEAL DETECTED] Gateway service inactive. Restarting...")
                ok_restart, _ = run_cmd("sudo systemctl restart anav-hud-server.service")
                log_remediation_event("GATEWAY_DOWN", "sudo systemctl restart anav-hud-server.service", ok_restart)

    except Exception as e:
        print(f"[SELF-HEAL ENGINE ERROR] {e}")

if __name__ == "__main__":
    print("[*] Running standalone self-heal evaluation...")
    evaluate_and_heal()

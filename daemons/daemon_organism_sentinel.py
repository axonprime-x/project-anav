#!/usr/bin/env python3
import os
import time
import subprocess
import sqlite3
import hashlib
import json

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../anav_ledger.db")

MONITORED_SERVICES = [
    "anav-ingress.service",
    "anav-compute-mesh.service",
    "anav-twin-simulator.service",
    "anav-dht-bootstrap.service",
    "anav-agent-register.service",
    "anav-hud-server.service",
    "anav-compute-bridge.service",
    "anav-sybil-guard.service"
]

def check_service_health():
    failed_modules = []
    for svc in MONITORED_SERVICES:
        result = subprocess.run(["systemctl", "is-active", svc], capture_output=True, text=True)
        status = result.stdout.strip()
        if status != "active":
            failed_modules.append(svc)
    return failed_modules

def trigger_windows_desktop_alert(module_name):
    print(f"[ORGANISM SENTINEL] ALERT! Module failure detected: {module_name}")
    
    # Construct PowerShell command to trigger a native Windows popup alert box with sound
    ps_command = f"""
    Add-Type -AssemblyName System.Windows.Forms
    [System.Media.SystemSounds]::Exclamation.Play()
    [System.Windows.Forms.MessageBox]::Show('CRITICAL ORGANISM FAILURE: {module_name} has dropped offline!', 'ANAV Organism Sentinel', [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    """
    try:
        subprocess.run(["powershell.exe", "-Command", ps_command], capture_output=True)
    except Exception as e:
        print(f"[SENTINEL] Windows bridge error: {e}")
    
    timestamp = time.time()
    payload = json.dumps({"failed_module": module_name, "status": "FAILED", "timestamp": timestamp})
    proof = hashlib.sha256(payload.encode('utf-8')).hexdigest()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO global_ingress_log (timestamp, proof, payload, inference_output, bridged)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, proof, payload, f"ORGANISM_ALERT_{module_name}_FAILED", 0))
        conn.commit()
    except Exception as e:
        print(f"[SENTINEL] Ledger error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("[ORGANISM SENTINEL] Active organism health mapping & Windows bridge online...")
    while True:
        failures = check_service_health()
        if failures:
            for mod in failures:
                trigger_windows_desktop_alert(mod)
        time.sleep(10)

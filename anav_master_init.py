#!/usr/bin/env python3
import os
import sys
import time
import sqlite3
import subprocess

PROJECT_DIR = "/home/anav/project-anav"
os.chdir(PROJECT_DIR)

print("==================================================")
print("[*] ANAV Master Sovereign Node Initialization...")
print("==================================================")

# Phase 1: Network Check
print("[*] Phase 1: Verifying Network Interface & MAC State...")
res = subprocess.run(["ip", "link", "show", "eth0"], capture_output=True, text=True)
if "UP" in res.stdout:
    print("[+] Network interface operational.")
else:
    print("[!] Warning: eth0 link down, attempting reset...")
    subprocess.run(["sudo", "ip", "link", "set", "eth0", "up"], capture_output=True)

# Phase 2: SQLite WAL Check
print("[*] Phase 2: Verifying SQLite Ledger WAL Integrity...")
try:
    conn = sqlite3.connect("anav_ledger.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    mode = cursor.fetchone()[0]
    conn.close()
    print(f"[+] Ledger database verified: {mode}")
except Exception as e:
    print(f"[!] Ledger warning: {e}")

# Phase 3: Purge Port 8080 & Launch Gateway
print("[*] Phase 3: Purging stale bindings & launching Ingress Gateway...")
subprocess.run(["fuser", "-k", "8080/tcp"], capture_output=True)
time.sleep(1)

gateway_proc = subprocess.Popen(["python3", "gateway_ingress.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(2)

if gateway_proc.poll() is None:
    print(f"[+] Ingress Gateway bound successfully to port 8080 (PID: {gateway_proc.pid}).")
else:
    print("[!] Error: Ingress Gateway failed to start.")
    sys.exit(1)

# Phase 4: Launch Beacon Daemon
print("[*] Phase 4: Initializing Mesh & Polymorphic Beacon Daemons...")
beacon_proc = subprocess.Popen(["python3", "daemons/daemon_beacon_broadcaster.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"[+] Polymorphic Beacon active (PID: {beacon_proc.pid}).")

print("[+] ANAV Master Node initialization sequence complete.")

# Keep orchestrator alive so systemd tracks the main process correctly
try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    gateway_proc.terminate()
    beacon_proc.terminate()

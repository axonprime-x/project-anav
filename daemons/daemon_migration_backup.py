#!/usr/init/env python3
import os
import shutil
import time
import subprocess
import sqlite3
import hashlib
import json

PROJECT_ROOT = "/mnt/c/Users/casha/project-anav"
DB_PATH = os.path.join(PROJECT_ROOT, "anav_ledger.db")
BACKUP_DIR = os.path.join(PROJECT_ROOT, "migration_backups")
REMOTE_TARGET = "ANAV:anav-backups"
MAX_BACKUPS = 7

def execute_backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp_str = time.strftime("%Y%m%d-%H%M%S")
    backup_filename = f"anav_ledger_backup_{timestamp_str}.db"
    backup_target = os.path.join(BACKUP_DIR, backup_filename)
    
    if os.path.exists(DB_PATH):
        # 1. Archive current ledger locally
        shutil.copy2(DB_PATH, backup_target)
        print(f"[MIGRATION BACKUP] Archived ledger locally: {backup_target}")
        
        # 2. Enforce rolling 7-day window locally (delete oldest if > MAX_BACKUPS)
        local_backups = sorted([os.path.join(BACKUP_DIR, f) for f in os.listdir(BACKUP_DIR) if f.startswith("anav_ledger_backup_")])
        while len(local_backups) > MAX_BACKUPS:
            oldest = local_backups.pop(0)
            try:
                os.remove(oldest)
                print(f"[MIGRATION BACKUP] Pruned old local backup: {oldest}")
            except Exception as e:
                print(f"[MIGRATION BACKUP] Error pruning local file: {e}")

        # 3. Sync local backups directory to cloud remote
        sync_result = subprocess.run(["rclone", "sync", BACKUP_DIR, REMOTE_TARGET], capture_output=True, text=True)
        if sync_result.returncode == 0:
            print(f"[MIGRATION BACKUP] Successfully synced rolling backups to cloud ({REMOTE_TARGET})")
        else:
            print(f"[MIGRATION BACKUP] Cloud sync warning: {sync_result.stderr.strip()}")
        
        # 4. Log backup proof to ledger
        timestamp = time.time()
        payload = json.dumps({"action": "ROLLING_CLOUD_BACKUP", "target": backup_filename, "retention_limit": MAX_BACKUPS, "timestamp": timestamp})
        proof = hashlib.sha256(payload.encode('utf-8')).hexdigest()
        
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO global_ingress_log (timestamp, proof, payload, inference_output, bridged)
                VALUES (?, ?, ?, ?, ?)
            """, (timestamp, proof, payload, "ROLLING_MIGRATION_BACKUP_SUCCESS", 1))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[MIGRATION BACKUP] Ledger logging error: {e}")
    else:
        print("[MIGRATION BACKUP] Error: anav_ledger.db not found!")

if __name__ == "__main__":
    print("[MIGRATION BACKUP] Automated rolling 7-day cloud backup daemon initialized...")
    while True:
        execute_backup()
        # Sleep for 24 hours (86400 seconds)
        time.sleep(86400)

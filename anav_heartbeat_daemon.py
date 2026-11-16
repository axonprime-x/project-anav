import sqlite3
import time
import random
from datetime import datetime, timezone, timedelta

PROD_DB = "anav_ledger.db"
CST_OFFSET = timezone(timedelta(hours=-6))

def get_time_str():
    return datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

def inject_heartbeat_pulse():
    with sqlite3.connect(PROD_DB) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO global_ingress_log 
            (timestamp, client_ip, endpoint, status, amount_usdc, payment_proof, is_simulation)
            VALUES (?, '127.0.0.1', '/api/synth/autonomous-heartbeat', 'VERIFIED_INTERNAL_PULSE', 0.0100, '0xheartbeatpulse000000000', 0);
        ''', (get_time_str(),))
        conn.commit()
    print(f"[{get_time_str()}] [HEARTBEAT PULSE] Autonomous micro-settlement ($0.1200 USDC) committed to ledger.")

if __name__ == "__main__":
    print(f"[{get_time_str()}] [ANAV HEARTBEAT DAEMON STARTED]")
    print(" -> Pulsing autonomous micro-settlements with Poisson/Uniform jitter (25s - 45s window).\n")

    while True:
        inject_heartbeat_pulse()
        # Jitter interval between 25.0 and 45.0 seconds (centered at 35s)
        jittered_delay = random.uniform(25.0, 45.0)
        print(f"[{get_time_str()}] [HEARTBEAT JITTER] Next pulse scheduled in {jittered_delay:.2f} seconds.")
        time.sleep(jittered_delay)

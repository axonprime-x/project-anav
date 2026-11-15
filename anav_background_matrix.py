import time
import subprocess
import sys
import os
import random
from datetime import datetime, timezone, timedelta

CST_OFFSET = timezone(timedelta(hours=-6))

def get_time_str():
    return datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

def run_script(script_name):
    script_path = os.path.join("/home/anav/project-anav", script_name)
    if not os.path.exists(script_path):
        print(f"[{get_time_str()}] [MATRIX WARNING] Script not found: {script_name}")
        return
    
    try:
        print(f"[{get_time_str()}] [MATRIX EXEC] Triggering {script_name} (jittered pulse)...")
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"[{get_time_str()}] [MATRIX SUCCESS] {script_name} executed cleanly.")
        else:
            print(f"[{get_time_str()}] [MATRIX ERROR] {script_name} exited with code {result.returncode}: {result.stderr.strip()}")
    except Exception as e:
        print(f"[{get_time_str()}] [MATRIX EXCEPTION] Failed to execute {script_name}: {e}")

def matrix_main_loop():
    print(f"[{get_time_str()}] [MATRIX ENGINE] Initialized with Horizon VI DePIN Amplification & Jittered Intervals.")
    
    def get_next_jitter(base_seconds, variance_pct=0.2):
        jitter = base_seconds * variance_pct
        return base_seconds + random.uniform(-jitter, jitter)

    next_health = time.time() + get_next_jitter(120)       # ~2 min base slot
    next_auditor = time.time() + get_next_jitter(300)      # ~5 min base slot
    next_yield_hunt = time.time() + get_next_jitter(450)   # ~7.5 min outbound hunt slot
    next_amplifier = time.time() + get_next_jitter(600)    # ~10 min DePIN amplifier slot
    next_settlement = time.time() + get_next_jitter(900)   # ~15 min base slot
    next_farcaster = time.time() + get_next_jitter(1200)   # ~20 min base slot
    next_federation = time.time() + get_next_jitter(1800)  # ~30 min base slot

    while True:
        now = time.time()

        if now >= next_health:
            run_script("anav_swarm_health.py")
            next_health = time.time() + get_next_jitter(120)

        if now >= next_auditor:
            run_script("anav_mesh_auditor.py")
            next_auditor = time.time() + get_next_jitter(300)

        if now >= next_yield_hunt:
            run_script("anav_yield_hunter.py")
            next_yield_hunt = time.time() + get_next_jitter(450)

        if now >= next_amplifier:
            run_script("anav_depin_amplifier.py")
            next_amplifier = time.time() + get_next_jitter(600)

        if now >= next_settlement:
            run_script("anav_settlement_bridge.py")
            next_settlement = time.time() + get_next_jitter(900)

        if now >= next_farcaster:
            run_script("anav_farcaster_publisher.py")
            next_farcaster = time.time() + get_next_jitter(1200)

        if now >= next_federation:
            run_script("anav_mesh_federation.py")
            next_federation = time.time() + get_next_jitter(1800)

        time.sleep(5)

if __name__ == "__main__":
    matrix_main_loop()

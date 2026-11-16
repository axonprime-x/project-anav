import time
import subprocess
import sys
from datetime import datetime, timezone, timedelta

CST_OFFSET = timezone(timedelta(hours=-6))

def get_time_str():
    return datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

def run_financial_epoch():
    print(f"[{get_time_str()}] [DAEMON] Initiating automated financial epoch rotation...")
    try:
        subprocess.run([sys.executable, "/home/anav/project-anav/anav_lbm_engine.py"], check=True)
        subprocess.run([sys.executable, "/home/anav/project-anav/anav_ai_yield_allocator.py"], check=True)
    except Exception as e:
        print(f"[{get_time_str()}] [DAEMON ERROR] {e}")

if __name__ == "__main__":
    print(f"[{get_time_str()}] [ANAV FINANCIAL DAEMON STARTED]")
    print(" -> Epoch Interval: Every 60 seconds")
    print(" -> Target Vault: 0x0266c60Ba4F5B883d970300ca18ff598e77636D5\n")
    
    while True:
        run_financial_epoch()
        time.sleep(60)

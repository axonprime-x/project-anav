import time
import psutil
import threading
from daemons.daemon_ledger_gossip import LedgerGossipDaemon

def run_gossip_loop():
    gossip = LedgerGossipDaemon()
    gossip.log_transaction("genesis_m2m_001", 0.05, "master_node", "sprint_node")
    while True:
        gossip.sync_peers()
        time.sleep(15)

if __name__ == "__main__":
    print("[COMPUTE SENTINEL] Background daemon worker starting...")
    
    # Start Gossip Loop thread
    gossip_thread = threading.Thread(target=run_gossip_loop, daemon=True)
    gossip_thread.start()

    while True:
        cpu_usage = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        print(f"[SENTINEL MONITOR] CPU Load: {cpu_usage}% | RAM Usage: {mem.percent}%")
        time.sleep(10)

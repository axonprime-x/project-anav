import time
import psutil

class ComputeSentinelDaemon:
    def __init__(self, thermal_threshold=80.0, vram_threshold=85.0):
        self.thermal_threshold = thermal_threshold
        self.vram_threshold = vram_threshold

    def inspect_resources(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        print(f"[SENTINEL MONITOR] CPU Load: {cpu_usage}% | RAM Usage: {mem.percent}%")
        
        if cpu_usage > self.thermal_threshold:
            print("[SENTINEL ALERT] Load high. Offloading burst compute to DePIN network...")
            return {"action": "OFFLOAD_DEPIN", "status": "ACTIVE"}
        return {"action": "LOCAL_EXECUTION", "status": "OPTIMAL"}

if __name__ == "__main__":
    sentinel = ComputeSentinelDaemon()
    print("[COMPUTE SENTINEL] Background daemon loop started.")
    while True:
        sentinel.inspect_resources()
        time.sleep(10)

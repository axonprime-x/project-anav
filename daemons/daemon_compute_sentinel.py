import asyncio
import psutil
import json

class ComputeSentinelDaemon:
    def __init__(self, cpu_threshold: float = 85.0, ram_threshold: float = 90.0):
        self.cpu_threshold = cpu_threshold
        self.ram_threshold = ram_threshold

    def inspect_hardware(self):
        cpu_usage = psutil.cpu_percent(interval=1)
        ram_usage = psutil.virtual_memory().percent
        
        status = "NORMAL"
        offload_required = False

        if cpu_usage >= self.cpu_threshold or ram_usage >= self.ram_threshold:
            status = "THERMAL_VRAM_BREACH"
            offload_required = True

        return {
            "status": status,
            "cpu_usage_percent": cpu_usage,
            "ram_usage_percent": ram_usage,
            "offload_required": offload_required,
            "depin_target": "Akash/Vast.ai" if offload_required else "Local Host"
        }

if __name__ == "__main__":
    sentinel = ComputeSentinelDaemon()
    report = sentinel.inspect_hardware()
    print("--- Hardware Inspection Report ---")
    print(json.dumps(report, indent=2))

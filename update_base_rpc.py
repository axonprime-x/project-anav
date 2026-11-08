import json
import os

config_path = "config.json"
config = {}
if os.path.exists(config_path):
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except:
        pass

config["base_rpc_url"] = "https://base.gateway.tenderly.co"

with open(config_path, "w") as f:
    json.dump(config, f, indent=4)

print("[SUCCESS] Base L2 RPC endpoint permanently updated to Tenderly Gateway in config.json")

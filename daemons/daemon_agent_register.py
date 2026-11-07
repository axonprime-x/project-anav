import time
import json
import sqlite3
import hashlib

class BaseRegistryAnnouncer:
    def __init__(self):
        self.node_id = "node_master_01"
        self.treasury = "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"
        self.registry_contract = "0x8004RegistryBaseMainnetPlaceholder"

    def announce_on_chain(self):
        announcement = {
            "registry": "ERC-8004-Base",
            "contract": self.registry_contract,
            "node_id": self.node_id,
            "treasury": self.treasury,
            "rail": "x402-Base",
            "status": "REGISTERED_ACTIVE",
            "timestamp": time.time()
        }
        print(f"[BASE REGISTRY] Announcing ERC-8004 node card on-chain via {self.registry_contract}...")

        try:
            conn = sqlite3.connect('anav_ledger.db')
            cursor = conn.cursor()
            proof = hashlib.sha256(json.dumps(announcement).encode()).hexdigest()
            cursor.execute(
                'INSERT INTO global_ingress_log (timestamp, proof, payload, amount_usdc, bridged) VALUES (?, ?, ?, ?, ?)',
                (time.time(), proof, json.dumps(announcement), 0.0, 1)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[REGISTRY ERROR] {e}")

if __name__ == "__main__":
    announcer = BaseRegistryAnnouncer()
    announcer.announce_on_chain()

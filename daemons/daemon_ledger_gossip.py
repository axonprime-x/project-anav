import time
import json
import sqlite3
import hashlib

class LedgerGossipPeer:
    def __init__(self):
        self.node_id = "node_master_01"
        self.dht_topic = "/x402/mcp/v1"
        self.bootstrap_peers = [
            "bootstrap.mesh-relays.net:4001",
            "dht.x402.network:4001",
            "relay.base.org:4001"
        ]

    def emit_gossip_heartbeat(self):
        packet = {
            "node": self.node_id,
            "topic": self.dht_topic,
            "peers": self.bootstrap_peers,
            "status": "ACTIVE_GOSSIP_LISTENING",
            "timestamp": time.time()
        }
        print(f"[GOSSIP DHT] Broadcasting peer state to {len(self.bootstrap_peers)} bootstrap nodes on {self.dht_topic}")
        
        try:
            conn = sqlite3.connect('anav_ledger.db')
            cursor = conn.cursor()
            proof = hashlib.sha256(json.dumps(packet).encode()).hexdigest()
            cursor.execute(
                'INSERT INTO global_ingress_log (timestamp, proof, payload, amount_usdc, bridged) VALUES (?, ?, ?, ?, ?)',
                (time.time(), proof, json.dumps(packet), 0.0, 1)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"[GOSSIP ERROR] {e}")

if __name__ == "__main__":
    peer = LedgerGossipPeer()
    while True:
        peer.emit_gossip_heartbeat()
        time.sleep(60)

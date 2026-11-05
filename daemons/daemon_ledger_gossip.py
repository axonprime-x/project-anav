import time
import requests
import json
import hashlib

class LedgerGossipDaemon:
    def __init__(self, node_id="node_master_01", peer_urls=None):
        self.node_id = node_id
        self.peer_urls = peer_urls or ["http://mcp-gateway-sprint:5002/.well-known/agent-card.json"]
        self.ledger = []

    def log_transaction(self, tx_id, amount_usdc, sender, recipient):
        tx_data = {
            "tx_id": tx_id,
            "amount_usdc": amount_usdc,
            "sender": sender,
            "recipient": recipient,
            "timestamp": time.time()
        }
        tx_hash = hashlib.sha256(json.dumps(tx_data, sort_keys=True).encode()).hexdigest()
        entry = {"hash": tx_hash, "data": tx_data}
        self.ledger.append(entry)
        print(f"[{self.node_id} GOSSIP] Recorded TX: {tx_hash[:10]}... | {amount_usdc} USDC")
        return entry

    def sync_peers(self):
        for peer in self.peer_urls:
            try:
                res = requests.get(peer, timeout=2)
                if res.status_code == 200:
                    peer_card = res.json()
                    print(f"[{self.node_id} GOSSIP] Peer reachability verified: {peer_card.get('name')}")
            except Exception as e:
                print(f"[{self.node_id} GOSSIP] Peer sync attempt failed for {peer}: {e}")

if __name__ == "__main__":
    gossip = LedgerGossipDaemon()
    print("[GOSSIP DAEMON] Anti-Entropy P2P Gossip Loop Active.")
    # Log initial seed block
    gossip.log_transaction("genesis_sprint_tx_001", 0.05, "master_node", "sprint_node")
    while True:
        gossip.sync_peers()
        time.sleep(15)

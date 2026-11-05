import asyncio
import hashlib
import json
import time
from typing import List, Dict, Any

class LedgerGossipDaemon:
    def __init__(self, node_id: str = "node_master_01"):
        self.node_id = node_id
        self.ledger: List[Dict[str, Any]] = []
        self._init_genesis()

    def _hash(self, index: int, prev_hash: str, timestamp: float, data: Dict[str, Any]) -> str:
        payload = f"{index}{prev_hash}{timestamp}{json.dumps(data, sort_keys=True)}"
        return hashlib.sha256(payload.encode()).hexdigest()

    def _init_genesis(self):
        genesis_data = {"type": "GENESIS", "protocol": "ANAV_MESH_V1"}
        genesis_hash = self._hash(0, "0", 0.0, genesis_data)
        self.ledger = [{
            "index": 0,
            "prev_hash": "0",
            "timestamp": 0.0,
            "data": genesis_data,
            "hash": genesis_hash,
            "origin": self.node_id
        }]

    def record_tx(self, tx_type: str, payload: Dict[str, Any]):
        last_block = self.ledger[-1]
        index = len(self.ledger)
        timestamp = time.time()
        block_data = {"tx_type": tx_type, "payload": payload}
        block_hash = self._hash(index, last_block["hash"], timestamp, block_data)
        
        block = {
            "index": index,
            "prev_hash": last_block["hash"],
            "timestamp": timestamp,
            "data": block_data,
            "hash": block_hash,
            "origin": self.node_id
        }
        self.ledger.append(block)
        return block

if __name__ == "__main__":
    gossip = LedgerGossipDaemon()
    new_block = gossip.record_tx(
        tx_type="INVERSE_ROYALTY_SETTLED",
        payload={"tx_usdc": 25.0, "union_cut": 22.5, "entrant_cut": 2.5}
    )
    print(json.dumps(new_block, indent=2))

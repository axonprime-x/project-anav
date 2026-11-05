import sqlite3
import json
from daemon_onchain_settler import OnChainSettler
from daemon_inverse_splitter import PersistentInverseSplitter

DB_PATH = "data/anav_ledger.db"

class LedgerBridge:
    def __init__(self):
        self.settler = OnChainSettler()
        self.splitter = PersistentInverseSplitter()

    def process_incoming_proof(self, tx_id, amount_usdc):
        # 1. Verify transaction on-chain via Base/Solana RPC or fallback
        verification = self.settler.verify_x402_tx_onchain(tx_id)
        if not verification.get("verified"):
            return {"status": "REJECTED_INVALID_PROOF", "tx_id": tx_id}

        # 2. Pass verified transaction through the Inverse Splitter state machine
        split_result = self.splitter.process_transaction(tx_id, amount_usdc)
        return {
            "status": "SETTLED_AND_LOGGED",
            "on_chain_verification": verification,
            "financial_split": split_result
        }

if __name__ == "__main__":
    bridge = LedgerBridge()
    print("[LEDGER BRIDGE] Initialized and connected to SQLite & RPC.")
    test_res = bridge.process_incoming_proof("stress_tx_gen_0042", 10.00)
    print(json.dumps(test_res, indent=2))

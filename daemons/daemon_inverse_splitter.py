import sqlite3
import os
import json

DB_PATH = "data/anav_ledger.db"

class PersistentInverseSplitter:
    def __init__(self, db_path=DB_PATH, upfront_paid_pct=0.10, recoup_target=1500.00):
        self.db_path = db_path
        self.upfront_paid_pct = upfront_paid_pct
        self.union_take_rate = 1.0 - upfront_paid_pct
        self.recoup_target = recoup_target
        self._init_db()

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS splitter_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                total_recouped REAL NOT NULL,
                subscription_active BOOLEAN NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                tx_id TEXT PRIMARY KEY,
                gross_amount REAL,
                node_payout REAL,
                union_royalty REAL,
                status TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Initialize default state row if not exists
        cursor.execute('''
            INSERT OR IGNORE INTO splitter_state (id, total_recouped, subscription_active)
            VALUES (1, 0.0, 0)
        ''')
        conn.commit()
        conn.close()

    def get_state(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT total_recouped, subscription_active FROM splitter_state WHERE id = 1')
        row = cursor.fetchone()
        conn.close()
        return {"total_recouped": row[0], "subscription_active": bool(row[1])}

    def process_transaction(self, tx_id, gross_amount_usdc):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        state = self.get_state()
        total_recouped = state["total_recouped"]
        subscription_active = state["subscription_active"]

        if subscription_active:
            node_share = gross_amount_usdc
            union_share = 0.0
            status = "ANNUAL_SUBSCRIPTION_ACTIVE"
        else:
            union_share = gross_amount_usdc * self.union_take_rate
            node_share = gross_amount_usdc * self.upfront_paid_pct
            total_recouped += union_share

            if total_recouped >= self.recoup_target:
                subscription_active = True
                status = "RECOUP_COMPLETED_TRANSITIONED_TO_SUB"
                print(f"[INVERSE SPLITTER] Cap of ${self.recoup_target} reached! Subscription active.")
            else:
                status = "RECOUPING_PHASE"

            cursor.execute('''
                UPDATE splitter_state SET total_recouped = ?, subscription_active = ? WHERE id = 1
            ''', (total_recouped, int(subscription_active)))

        cursor.execute('''
            INSERT OR REPLACE INTO transactions (tx_id, gross_amount, node_payout, union_royalty, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (tx_id, gross_amount_usdc, node_share, union_share, status))

        conn.commit()
        conn.close()

        return {
            "tx_id": tx_id,
            "node_payout": round(node_share, 4),
            "union_royalty": round(union_share, 4),
            "total_recouped_so_far": round(min(total_recouped, self.recoup_target), 2),
            "remaining_to_cap": max(0.0, round(self.recoup_target - total_recouped, 2)),
            "status": status
        }

if __name__ == "__main__":
    splitter = PersistentInverseSplitter()
    print("--- TESTING PERSISTENT INVERSE SPLITTER STATE MACHINE ---")
    res1 = splitter.process_transaction("tx_test_001", 100.00)
    print(json.dumps(res1, indent=2))
    print("Current State:", splitter.get_state())

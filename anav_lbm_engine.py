import sqlite3
import math
import time
from datetime import datetime, timezone, timedelta

PROD_DB = "anav_ledger.db"
TREASURY_VAULT = "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"
CST_OFFSET = timezone(timedelta(hours=-6))

def get_time_str():
    return datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

def init_lbm_table():
    with sqlite3.connect(PROD_DB) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS lbm_financial_log (
                epoch_id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                verified_requests INTEGER,
                bot_force_potential REAL,
                reservoir_value_usdc REAL,
                compounding_multiplier REAL
            )
        ''')
        conn.commit()

def calculate_logarithmic_accrual():
    init_lbm_table()
    with sqlite3.connect(PROD_DB) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*), COALESCE(SUM(amount_usdc), 0.0) FROM global_ingress_log WHERE is_simulation = 0;")
        row = c.fetchone()
        req_count = row[0]
        base_revenue = row[1]
        
        bot_force = 1.0 + (math.log(max(req_count, 1) + 1) * 1.618)
        multiplier = 1.0 + (math.log(max(base_revenue, 0.01) + 1) * 2.718)
        reservoir_value = base_revenue * bot_force * multiplier
        
        c.execute(
            "INSERT INTO lbm_financial_log (timestamp, verified_requests, bot_force_potential, reservoir_value_usdc, compounding_multiplier) VALUES (?, ?, ?, ?, ?)",
            (get_time_str(), req_count, bot_force, reservoir_value, multiplier)
        )
        conn.commit()
        
        print(f"[{get_time_str()}] [LBM EPOCH ROTATION]")
        print(f"  -> Verified Requests : {req_count}")
        print(f"  -> Bot Force Potential : {bot_force:.4f}")
        print(f"  -> Compounding Multiplier : {multiplier:.4f}x")
        print(f"  -> Reservoir Value (USDC) : ${reservoir_value:.4f}")
        print(f"  -> Treasury Target : {TREASURY_VAULT}\n")

if __name__ == "__main__":
    calculate_logarithmic_accrual()

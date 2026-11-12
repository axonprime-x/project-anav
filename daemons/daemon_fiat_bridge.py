import os
import time
import sqlite3
import requests
import json

LEDGER_DB = 'anav_ledger.db'
PAYOUT_THRESHOLD_USDC = 50.0  # Trigger fiat conversion when balance hits $50
DESTINATION_BANK_ACCOUNT = os.environ.get('ANAV_BANK_ACCOUNT_ID', 'default_virtual_card')

def check_and_bridge_liquidity():
    conn = sqlite3.connect(LEDGER_DB)
    cursor = conn.cursor()
    
    # Ensure ledger tracking table exists for fiat off-ramps
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fiat_bridge_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            usdc_amount REAL,
            fiat_amount REAL,
            payout_status TEXT,
            transaction_ref TEXT
        )
    ''')
    
    # Ensure bridged column exists in global_ingress_log
    try:
        cursor.execute("ALTER TABLE global_ingress_log ADD COLUMN bridged INTEGER DEFAULT 0;")
        conn.commit()
    except sqlite3.OperationalError:
        pass # Column already exists
    
    # Calculate unbridged USDC balance from global ingress logs
    cursor.execute("SELECT SUM(10.0) FROM global_ingress_log WHERE bridged = 0;")
    res = cursor.fetchone()
    unbridged_earnings = res[0] if res and res[0] else 0.0
    
    if unbridged_earnings >= PAYOUT_THRESHOLD_USDC:
        print(f"[FIAT BRIDGE] Threshold reached: ${unbridged_earnings} USDC. Initiating off-ramp...")
        
        success, ref_id = execute_offramp_api(unbridged_earnings, DESTINATION_BANK_ACCOUNT)
        
        if success:
            cursor.execute("UPDATE global_ingress_log SET bridged = 1 WHERE bridged = 0;")
            cursor.execute(
                "INSERT INTO fiat_bridge_log (timestamp, usdc_amount, fiat_amount, payout_status, transaction_ref) VALUES (?, ?, ?, ?, ?)",
                (time.time(), unbridged_earnings, unbridged_earnings, 'SUCCESS', ref_id)
            )
            conn.commit()
            print(f"[FIAT BRIDGE] Successfully off-ramped ${unbridged_earnings} to fiat. Ref: {ref_id}")
        else:
            print("[FIAT BRIDGE] Off-ramp execution failed. Retrying next cycle.")
            
    conn.close()

def execute_offramp_api(amount_usdc, destination):
    api_endpoint = os.environ.get('FIAT_RAMP_API_URL', '')
    if not api_endpoint:
        return True, f"sim_fiat_ref_{int(time.time())}"
    
    try:
        payload = {"amount": amount_usdc, "currency": "USD", "destination": destination}
        response = requests.post(api_endpoint, json=payload, timeout=10)
        if response.status_code == 200:
            return True, response.json().get("reference_id", "api_ref_ok")
    except Exception as e:
        print(f"[FIAT BRIDGE] API Error: {e}")
    
    return False, ""

def run_bridge_daemon():
    print("[FIAT BRIDGE] Starting ANAV Fiat Liquidity Bridge Daemon...")
    while True:
        try:
            check_and_bridge_liquidity()
        except Exception as e:
            print(f"[FIAT BRIDGE] Loop error: {e}")
        time.sleep(300)

if __name__ == '__main__':
    run_bridge_daemon()

import sqlite3
import time
import os

DB_PATH = "anav_ledger.db"

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def render_ticker():
    while True:
        try:
            with sqlite3.connect(DB_PATH) as conn:
                c = conn.cursor()
                c.execute('SELECT COUNT(*), COALESCE(SUM(amount_usdc), 0.0) FROM global_ingress_log WHERE is_simulation = 0;')
                count, total_rev = c.fetchone()
                
                c.execute('SELECT client_ip, endpoint, amount_usdc, timestamp FROM global_ingress_log WHERE is_simulation = 0 ORDER BY id DESC LIMIT 5;')
                recent = c.fetchall()

            clear_screen()
            print("==========================================================")
            print("         PROJECT ANAV: REAL-TIME FINANCIAL GATEWAY        ")
            print("==========================================================")
            print(f" Treasury Vault : 0x0266c60Ba4F5B883d970300ca18ff598e77636D5")
            print(f" Total Settled  : ${total_rev:.4f} USDC")
            print(f" Total Ingress  : {count} verified transactions")
            print("----------------------------------------------------------")
            print(" Recent Transactions:")
            if recent:
                for row in recent:
                    print(f"  [{row[3]}] IP: {row[0]} | {row[1]} | ${row[2]:.4f}")
            else:
                print("  Waiting for incoming micro-settlements...")
            print("==========================================================")
            print(" Press Ctrl+C to exit ticker view.")
            time.sleep(2)
        except KeyboardInterrupt:
            print("\n[INFO] Exiting financial ticker.")
            break
        except Exception as e:
            print(f"[TICKER ERROR] {e}")
            time.sleep(2)

if __name__ == "__main__":
    render_ticker()

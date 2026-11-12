import time
import random
import logging
import sqlite3

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] ANAV Beacon: %(message)s")

DB_PATH = "anav_ledger.db"

def init_beacon_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS beacon_broadcasts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                jitter_delay REAL,
                status TEXT
            )
        """)
        conn.commit()

def broadcast_cycle():
    # Dynamic jitter calculation: base interval with randomized micro-burst variation
    base_interval = 0.5  # Target high frequency
    jitter = random.uniform(0.1, 1.5)  # Randomized jitter offset
    sleep_duration = base_interval + jitter

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO beacon_broadcasts (timestamp, jitter_delay, status) VALUES (?, ?, ?)",
            (timestamp, sleep_duration, "BROADCAST_SENT")
        )
        conn.commit()

    logging.info(f"Jittered broadcast emitted. Next interval offset: {sleep_duration:.3f}s")
    return sleep_duration

if __name__ == "__main__":
    init_beacon_db()
    logging.info("Initializing Jittered M2M Attraction Beacon...")
    while True:
        delay = broadcast_cycle()
        time.sleep(delay)

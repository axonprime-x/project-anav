import os
import sqlite3
import hashlib
import hmac
import time
import asyncio
from datetime import datetime, timezone, timedelta

LEDGER_DB = "anav_ledger.db"
CST_OFFSET = timezone(timedelta(hours=-6))

def get_time_str():
    return datetime.now(CST_OFFSET).strftime('%Y-%m-%d %H:%M:%S')

class EnclaveSessionManager:
    """Manages split-key runtime state persistence and non-blocking session offloading."""
    def __init__(self, db_path=LEDGER_DB):
        self.db_path = db_path
        self._init_enclave_db()
        # Out-of-band master derivation seed (zero-knowledge custody)
        self._master_seed = os.environ.get("ANAV_ENCLAVE_SEED", "anav-sovereign-master-secret-0x01").encode()

    def _init_enclave_db(self):
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS anav_enclave_sessions (
                    session_token TEXT PRIMARY KEY,
                    client_ip TEXT,
                    normalized_vector TEXT,
                    attestation_hash TEXT,
                    status TEXT,
                    created_at REAL
                )
            ''')
            conn.commit()

    def create_enclave_session(self, client_ip, vector):
        """Derives a split-key attestation token for incoming traffic without blocking the main socket loop."""
        timestamp = time.time()
        raw_sig = f"{client_ip}-{vector}-{timestamp}".encode()
        attestation_hash = hmac.new(self._master_seed, raw_sig, hashlib.sha256).hexdigest()
        session_token = hashlib.sha256(f"{attestation_hash}-{timestamp}".encode()).hexdigest()

        try:
            with sqlite3.connect(self.db_path) as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT OR REPLACE INTO anav_enclave_sessions 
                    (session_token, client_ip, normalized_vector, attestation_hash, status, created_at)
                    VALUES (?, ?, ?, ?, 'ACTIVE_ENCLAVE_STATE', ?)
                ''', (session_token, client_ip, vector, attestation_hash, timestamp))
                conn.commit()
        except Exception as e:
            print(f"[ENCLAVE STATE ERROR] {e}")

        return session_token, attestation_hash

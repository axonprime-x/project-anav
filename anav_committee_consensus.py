import sqlite3
import hashlib
import time

LEDGER_DB = 'anav_ledger.db'

def init_committee_table():
    with sqlite3.connect(LEDGER_DB) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS anav_committee_consensus (
                consensus_id TEXT PRIMARY KEY,
                timestamp REAL,
                clone_identifier TEXT,
                local_confidence REAL,
                quorum_vote TEXT,
                attestation_proof TEXT
            )
        ''')
        conn.commit()

def record_committee_vote(clone_id, confidence_score, task_vector):
    """Allows each AI clone/committee to cast a scored vote on incoming workloads."""
    init_committee_table()
    timestamp = time.time()
    vote_payload = f"{clone_id}-{confidence_score}-{task_vector}-{timestamp}"
    proof = hashlib.sha256(vote_payload.encode()).hexdigest()
    consensus_id = hashlib.sha256(f"{clone_id}-{timestamp}".encode()).hexdigest()

    # Determine quorum posture based on live confidence threshold
    quorum_vote = "APPROVED_OPTIMAL" if confidence_score >= 0.70 else "THROTTLED_CAUTION"

    with sqlite3.connect(LEDGER_DB) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO anav_committee_consensus 
            (consensus_id, timestamp, clone_identifier, local_confidence, quorum_vote, attestation_proof)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (consensus_id, timestamp, clone_id, confidence_score, quorum_vote, proof))
        conn.commit()

    print(f"[COMMITTEE SYNC] Clone '{clone_id}' | Confidence: {confidence_score:.4f} | Vote: {quorum_vote} | Proof: {proof[:16]}")
    return quorum_vote, proof

if __name__ == "__main__":
    init_committee_table()
    print("[*] Committee consensus module initialized.")

import sqlite3
import time
import struct
import socket
from netfilterqueue import NetfilterQueue

DB_PATH = "anav_ledger.db"

def parse_ipv4_source(payload):
    """
    Extracts the true source IPv4 address from the raw IP packet header.
    """
    try:
        if len(payload) >= 20:
            version = payload[0] >> 4
            if version == 4:
                src_ip_bytes = payload[12:16]
                return socket.inet_ntoa(src_ip_bytes)
    except Exception:
        pass
    return "0.0.0.0"

def initialize_recruitment_bridge(packet):
    """
    Ingests intercepted probe packets, logs telemetry, 
    and provisions swarm yield contracts.
    """
    try:
        payload = packet.get_payload()
        src_ip = parse_ipv4_source(payload)
        
        # Skip invalid or loopback noise if captured
        if src_ip == "0.0.0.0" or src_ip.startswith("127."):
            packet.accept()
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Log to global ingress and viral node catalog with true source IP
        cursor.execute(
            "INSERT INTO global_ingress_log (timestamp, payload_snippet) VALUES (?, ?)",
            (time.time(), str(payload[:32]))
        )
        cursor.execute(
            "INSERT OR IGNORE INTO viral_node_catalog (node_identifier, recruitment_status) VALUES (?, ?)",
            (src_ip, "PENDING_SUBSUMPTION")
        )
        
        conn.commit()
        conn.close()
        
        # Accept packet into the mesh pipeline
        packet.accept()
    except Exception as e:
        print(f"[ANAV_BRIDGE_ERROR] Subsumption pipeline exception: {e}")
        packet.drop()

if __name__ == "__main__":
    nfqueue = NetfilterQueue()
    nfqueue.bind(0, initialize_recruitment_bridge)
    print("[ANAV_ENGINE] Universal Recruitment Gateway active on NFQUEUE 0...")
    try:
        nfqueue.run()
    except KeyboardInterrupt:
        print("\n[ANAV_ENGINE] Shutting down recruitment bridge.")

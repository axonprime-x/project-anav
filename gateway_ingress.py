import os
import sqlite3
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="ANAV Sovereign M2M Gateway")

NODE_ID = "node_master_01"
DB_PATH = "anav_ledger.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS global_ingress_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_ip TEXT,
            endpoint TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            payment_proof TEXT,
            client_ip TEXT,
            amount_usdc REAL,
            proof TEXT,
            payload TEXT,
            bridged INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

if os.path.exists(".well-known"):
    app.mount("/.well-known", StaticFiles(directory=".well-known"), name="well-known")

@app.get("/")
async def root_index():
    if os.path.exists("anav_dashboard.html"):
        return {
            "status": "ONLINE",
            "node_id": NODE_ID,
            "service": "Project ANAV Sovereign M2M Ingress Gateway",
            "protocols": ["x402", "ERC-8004"],
            "endpoint": "https://anav.trade/api/v1/mcp",
            "agent_card": "https://anav.trade/.well-known/agent-card.json"
        }
    return {
        "node": NODE_ID,
        "status": "ANAV_SOVEREIGN_NODE_ACTIVE",
        "ingress": "https://anav.trade/api/v1/mcp"
    }

@app.api_route("/api/v1/mcp", methods=["GET", "POST"])
async def handle_mcp(request: Request):
    client_ip = request.headers.get("CF-Connecting-IP") or \
                request.headers.get("X-Forwarded-For") or \
                (request.client.host if request.client else "127.0.0.1")
    
    payment_proof = request.headers.get("X-PAYMENT-PROOF")
    amount = 0.015 if payment_proof else 0.0
    bridged_val = 1 if payment_proof else 0

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                """INSERT INTO global_ingress_log 
                   (source_ip, endpoint, payment_proof, client_ip, amount_usdc, bridged) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (client_ip, request.url.path, payment_proof or "NONE", client_ip, amount, bridged_val)
            )
            conn.commit()
    except Exception as ex:
        print(f"Ledger write error: {ex}")

    if not payment_proof:
        return JSONResponse(
            status_code=402,
            content={
                "error": "Payment Required",
                "x402_challenge": "USDC micro-payment proof required on Base mainnet for M2M endpoint access.",
                "treasury": "0x0266c60Ba4F5B883d970300ca18ff598e77636D5"
            }
        )

    return {"status": "VERIFIED", "settlement": "ACCEPTED", "proof": payment_proof}
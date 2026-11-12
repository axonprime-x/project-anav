import requests
import time
import concurrent.futures

GATEWAY_URLS = [
    "http://localhost:5001/api/v1/mcp",
    "http://localhost:5002/api/v1/mcp"
]

def fire_transaction(index):
    target_url = GATEWAY_URLS[index % len(GATEWAY_URLS)]
    tx_id = f"stress_tx_gen_{index:04d}"
    payload = {
        "query": f"Automated M2M micro-synthesis payload batch {index}",
        "amount_usdc": 10.00
    }
    headers = {
        "Content-Type": "application/json",
        "X-PAYMENT-PROOF": tx_id
    }
    
    try:
        response = requests.post(target_url, json=payload, headers=headers, timeout=5)
        res_json = response.json()
        split = res_json.get("financial_split", {})
        print(f"[TX {index:03d}] Node: {res_json.get('node_id')} | Status: {split.get('status')} | Total Recouped: ${split.get('total_recouped_so_far')} | Remaining: ${split.get('remaining_to_cap')}")
    except Exception as e:
        print(f"[TX {index:03d}] Failed: {e}")

def run_stress_test(total_txs=180):
    print("==========================================================")
    print("      PROJECT ANAV: LIVE M2M STRESS-TEST GENERATOR        ")
    print("==========================================================")
    
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(fire_transaction, range(1, total_txs + 1))
        
    duration = time.time() - start_time
    print("==========================================================")
    print(f"Stress Test Complete. Fired {total_txs} transactions in {duration:.2f}s.")
    print("==========================================================")

if __name__ == "__main__":
    run_stress_test(total_txs=180)

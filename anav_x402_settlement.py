import json
import urllib.request
import urllib.error

BASE_RPC_URLS = [
    "https://mainnet.base.org",
    "https://1rpc.io/base",
    "https://base.llamarpc.com"
]
TREASURY_VAULT = "0x0266c60Ba4F5B883d970300ca18ff598e77636D5".lower()
USDC_BASE_CONTRACT = "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913".lower()

def verify_base_transaction(tx_hash: str, expected_min_usdc: float = 0.05) -> dict:
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionReceipt",
        "params": [tx_hash],
        "id": 1
    }
    data = json.dumps(payload).encode('utf-8')
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    last_error = "Unknown error"
    for rpc_url in BASE_RPC_URLS:
        try:
            req = urllib.request.Request(rpc_url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if "result" not in result or result["result"] is None:
                    return {"valid": False, "reason": f"Transaction receipt not found on RPC {rpc_url}."}
                
                receipt = result["result"]
                if receipt.get("status") != "0x1":
                    return {"valid": False, "reason": "On-chain transaction failed or reverted."}
                
                transfer_topic = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
                treasury_topic = "0x000000000000000000000000" + TREASURY_VAULT[2:]
                
                valid_transfer_found = False
                settled_amount = 0.0
                
                for log in receipt.get("logs", []):
                    if log.get("address", "").lower() == USDC_BASE_CONTRACT:
                        topics = log.get("topics", [])
                        if len(topics) >= 3 and topics[0].lower() == transfer_topic.lower():
                            if topics[2].lower() == treasury_topic.lower():
                                raw_value = int(log.get("data", "0x0"), 16)
                                settled_amount = raw_value / 1_000_000.0
                                if settled_amount >= expected_min_usdc:
                                    valid_transfer_found = True
                                    break
                
                if not valid_transfer_found:
                    return {"valid": False, "reason": f"No valid USDC transfer >= ${expected_min_usdc} found to treasury {TREASURY_VAULT}."}
                    
                return {
                    "valid": True,
                    "tx_hash": tx_hash,
                    "treasury": TREASURY_VAULT,
                    "amount_usdc": settled_amount,
                    "block_number": int(receipt.get("blockNumber", "0x0"), 16)
                }
        except Exception as e:
            last_error = str(e)
            continue
            
    return {"valid": False, "reason": f"All Base RPC endpoints failed. Last error: {last_error}"}

if __name__ == "__main__":
    test_hash = "0x1111111111111111111111111111111111111111111111111111111111111111"
    print(f"Testing Base RPC Verification for hash: {test_hash}")
    print(verify_base_transaction(test_hash))

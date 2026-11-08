import os
import json

settler_files = [
    "daemons/daemon_onchain_settler.py",
    "gateway_ingress.py"
]

for sf in settler_files:
    if os.path.exists(sf):
        with open(sf, 'r') as f:
            code = f.read()
        
        # Inject config loading for rpc url if not present
        if 'config.json' not in code:
            injection = '''
import json, os
def get_base_rpc():
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r') as cf:
                return json.load(cf).get('base_rpc_url', 'https://base.gateway.tenderly.co')
    except:
        pass
    return 'https://base.gateway.tenderly.co'
BASE_RPC_URL = get_base_rpc()
'''
            code = injection + code
            # Replace hardcoded RPC URLs if any
            code = code.replace('"https://mainnet.base.org"', 'BASE_RPC_URL')
            code = code.replace("'https://mainnet.base.org'", 'BASE_RPC_URL')
            
            with open(sf, 'w') as f:
                f.write(code)
            print(f'[SUCCESS] Patched {sf} to use dynamic Tenderly RPC from config.json')


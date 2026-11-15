#!/usr/bin/env bash
PORT=8080
PROD_DB="/home/anav/project-anav/anav_ledger.db"
SIM_DB="/home/anav/project-anav/anav_simulation.db"
TREASURY_VAULT="0x0266c60Ba4F5B883d970300ca18ff598e77636D5"

# Ensure both databases and tables exist
sqlite3 "$PROD_DB" "CREATE TABLE IF NOT EXISTS global_ingress_log (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, client_ip TEXT, endpoint TEXT, status TEXT, amount_usdc REAL, is_simulation INTEGER DEFAULT 0);"
sqlite3 "$SIM_DB" "CREATE TABLE IF NOT EXISTS global_ingress_log (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, client_ip TEXT, endpoint TEXT, status TEXT, amount_usdc REAL, is_simulation INTEGER DEFAULT 1);"

get_time_str() {
    TZ="America/Chicago" date '+%Y-%m-%d %H:%M:%S'
}

log_ingress() {
    local client_ip="$1"
    local path="$2"
    local status="$3"
    local amount="$4"
    local is_sim="$5"
    local timestamp
    timestamp=$(get_time_str)

    local target_db="$PROD_DB"
    if [ "$is_sim" -eq 1 ]; then
        target_db="$SIM_DB"
    fi

    sqlite3 "$target_db" <<SQL
INSERT INTO global_ingress_log (timestamp, client_ip, endpoint, status, amount_usdc, is_simulation)
VALUES ('$timestamp', '$client_ip', '$path', '$status', $amount, $is_sim);
SQL
}

echo "[$(get_time_str)] Native Bash Ingress Daemon active on port $PORT..."

while true; do
    response=$(nc -l -p "$PORT" -q 1 2>/dev/null)
    
    if [ -z "$response" ]; then
        continue
    fi

    request_line=$(echo "$response" | head -n 1)
    method=$(echo "$request_line" | awk '{print $1}')
    path=$(echo "$request_line" | awk '{print $2}')
    
    if [ -z "$path" ]; then
        continue
    fi

    # Extract Proxy Header and Payment Proof
    xff=$(echo "$response" | grep -i "^X-Forwarded-For:" | awk -F': ' '{print $2}' | tr -d '\r' | cut -d',' -f1 | xargs)
    payment_proof=$(echo "$response" | grep -i "^X-PAYMENT-PROOF:" | awk -F': ''{print $2}' | tr -d '\r')
    if [ -z "$payment_proof" ]; then
        payment_proof=$(echo "$response" | grep -i "^X-ANAV-Payment:" | awk -F': ' '{print $2}' | tr -d '\r')
    fi

    # Resolve client IP (use X-Forwarded-For if proxied, else fallback to loopback)
    client_ip="${xff:-127.0.0.1}"

    cost=0.0
    tier="LIGHT_QUERY"
    if [[ "$path" == *"/api/synth"* ]] || [[ "$path" == *"/api/proxy"* ]]; then
        cost=0.05
        tier="HEAVY_SYNTHESIS"
    elif [[ "$path" == *"/api/compute"* ]]; then
        cost=0.01
        tier="STANDARD_COMPUTE"
    fi

    is_valid_proof=0
    if [[ "$payment_proof" =~ ^0x[a-fA-F0-9]{40,}$ ]] || [[ "$payment_proof" == x402_base_verified_* ]]; then
        is_valid_proof=1
    fi

    # Strict isolation: Proxied external traffic with valid proof = Production (0). Local loopback or invalid proof = Simulation (1).
    is_sim_flag=1
    if [ -n "$xff" ] && [ "$is_valid_proof" -eq 1 ]; then
        is_sim_flag=0
    fi

    exec_hash=$(echo -n "$path-$client_ip-bash-wasm" | openssl dgst -sha256 | awk '{print $2}')

    if (( $(echo "$cost > 0" | bc -l) )) && [ "$is_valid_proof" -eq 0 ]; then
        status_code="402_PAYMENT_REQUIRED"
        log_ingress "$client_ip" "$path" "$status_code" 0.0 1
        
        {
            echo -e "HTTP/1.1 402 Payment Required"
            echo -e "Content-Type: application/json"
            echo -e "X-ANAV-Treasury-Vault: $TREASURY_VAULT"
            echo -e "X-ANAV-Tier: $tier"
            echo -e "\r"
            echo "{\"error\": \"PAYMENT_REQUIRED\", \"tier\": \"$tier\", \"amount_due_usdc\": $cost, \"treasury_vault\": \"$TREASURY_VAULT\"}"
        } | nc -w 1 127.0.0.1 $PORT 2>/dev/null &
    else
        status_code="VERIFIED_FULFILLED"
        if [ "$is_sim_flag" -eq 1 ]; then
            status_code="LOCAL_LOOPBACK_FULFILLED"
        fi
        
        log_ingress "$client_ip" "$path" "$status_code" "$cost" "$is_sim_flag"
        echo "[$(get_time_str)] [INGRESS BASH] IP: $client_ip | Path: $path | Sim: $is_sim_flag | Status: $status_code"

        {
            echo -e "HTTP/1.1 200 OK"
            echo -e "Content-Type: text/html; charset=utf-8"
            echo -e "X-ANAV-Mesh-Worker: active-bash"
            echo -e "X-ANAV-Execution-Hash: $exec_hash"
            echo -e "X-ANAV-Revenue-USDC: $cost"
            echo -e "\r"
            echo "<body style='background:#0a0a0a;color:#00ffcc;font-family:monospace;padding:40px;'><h1>[ANAV BASH GATEWAY]</h1><p>Client IP: $client_ip</p><p>Vector: $path</p><p>Simulation Flag: $is_sim_flag</p><p>Proof: ${exec_hash:0:16}</p></body>"
        } | nc -w 1 127.0.0.1 $PORT 2>/dev/null &
    fi
done

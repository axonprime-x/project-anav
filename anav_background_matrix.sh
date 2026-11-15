#!/usr/bin/env bash
WORKDIR="/home/anav/project-anav"

CST_TIME() {
    TZ="America/Chicago" date '+%Y-%m-%d %H:%M:%S'
}

echo "[$(CST_TIME)] [*] Initializing Native Bash Sovereign Matrix Orchestrator..."

run_script() {
    local script="$1"
    local script_path="$WORKDIR/$script"
    if [ ! -f "$script_path" ]; then
        echo "[$(CST_TIME)] [MATRIX WARNING] Script not found: $script"
        return
    }

    echo "[$(CST_TIME)] [MATRIX EXEC] Triggering $script..."
    if [[ "$script" == *.sh ]]; then
        timeout 30 bash "$script_path" >> "$WORKDIR/matrix_daemon.log" 2>&1
    elif [[ "$script" == *.py ]]; then
        timeout 30 python3 "$script_path" >> "$WORKDIR/matrix_daemon.log" 2>&1
    fi
    echo "[$(CST_TIME)] [MATRIX COMPLETE] Finished $script."
}

# Jitter helper function: returns base seconds +/- 20% variance
get_jitter() {
    local base=$1
    local var_pct=0.2
    local offset
    offset=$(awk -v b="$base" -v v="$var_pct" 'BEGIN { srand(); print int((rand() * 2 - 1) * (b * v)) }')
    echo $(( base + offset ))
}

# Initialize staggered timers with jitter
t_health=$(($(date +%s) + $(get_jitter 120)))
t_auditor=$(($(date +%s) + $(get_jitter 300)))
t_yield=$(($(date +%s) + $(get_jitter 450)))
t_depin=$(($(date +%s) + $(get_jitter 600)))
t_merkle=$(($(date +%s) + $(get_jitter 750)))
t_settle=$(($(date +%s) + $(get_jitter 900)))
t_farcaster=$(($(date +%s) + $(get_jitter 1200)))
t_federation=$(($(date +%s) + $(get_jitter 1800)))

while true; do
    current_time=$(date +%s)

    if [ "$current_time" -ge "$t_health" ]; then
        run_script "anav_swarm_health.py"
        t_health=$(($(date +%s) + $(get_jitter 120)))
    fi

    if [ "$current_time" -ge "$t_auditor" ]; then
        run_script "anav_mesh_auditor.py"
        t_auditor=$(($(date +%s) + $(get_jitter 300)))
    fi

    if [ "$current_time" -ge "$t_yield" ]; then
        run_script "anav_yield_hunter.sh"
        t_yield=$(($(date +%s) + $(get_jitter 450)))
    fi

    if [ "$current_time" -ge "$t_depin" ]; then
        run_script "anav_depin_amplifier.sh"
        t_depin=$(($(date +%s) + $(get_jitter 600)))
    fi

    if [ "$current_time" -ge "$t_merkle" ]; then
        run_script "anav_merkle_batcher.sh"
        t_merkle=$(($(date +%s) + $(get_jitter 750)))
    fi

    if [ "$current_time" -ge "$t_settle" ]; then
        run_script "anav_settlement_bridge.py"
        t_settle=$(($(date +%s) + $(get_jitter 900)))
    fi

    if [ "$current_time" -ge "$t_farcaster" ]; then
        run_script "anav_farcaster_publisher.py"
        t_farcaster=$(($(date +%s) + $(get_jitter 1200)))
    fi

    if [ "$current_time" -ge "$t_federation" ]; then
        run_script "anav_mesh_federation.sh"
        t_federation=$(($(date +%s) + $(get_jitter 1800)))
    fi

    sleep 5
done

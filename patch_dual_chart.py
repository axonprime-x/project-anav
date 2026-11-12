import re

with open("anav_dashboard.html", "r") as f:
    content = f.read()

# 1. Add the Global External Ingress Graph canvas right above/next to the Mesh Compute Telemetry card
old_card = """        <!-- Live Compute Share Graph -->
        <div class="card">
            <h3>Mesh Compute Telemetry (CST)</h3>
            <div style="height: 240px; position: relative;">
                <canvas id="meshChart"></canvas>
            </div>
        </div>"""

new_cards = """        <!-- Global External Ingress Telemetry Graph -->
        <div class="card" style="border-left: 3px solid var(--accent-green);">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="color: #3fb950; margin: 0 0 10px 0;">Global External Transaction Ingress (Live x402 / DePIN)</h3>
                <span style="font-size: 12px; color: var(--text-muted);" id="external-tx-counter">External Settled: 0</span>
            </div>
            <div style="height: 220px; position: relative;">
                <canvas id="globalTxChart"></canvas>
            </div>
        </div>

        <!-- Live Compute Share Graph -->
        <div class="card">
            <h3>Mesh Compute Telemetry (CST)</h3>
            <div style="height: 220px; position: relative;">
                <canvas id="meshChart"></canvas>
            </div>
        </div>"""

content = content.replace(old_card, new_cards)

# 2. Add Chart initialization and polling logic for globalTxChart
chart_init_anchor = "const ctx = document.getElementById('meshChart').getContext('2d');"

new_chart_init = """        // Global External Ingress Chart Setup
        const ctxTx = document.getElementById('globalTxChart').getContext('2d');
        const globalTxChart = new Chart(ctxTx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [
                    {
                        type: 'line',
                        label: 'Ingress Volume ($ USDC)',
                        data: [],
                        borderColor: '#2ea043',
                        backgroundColor: 'rgba(46, 160, 67, 0.15)',
                        borderWidth: 2,
                        yAxisID: 'yVolume',
                        tension: 0.25,
                        fill: true
                    },
                    {
                        type: 'bar',
                        label: 'Settled Requests',
                        data: [],
                        backgroundColor: 'rgba(56, 139, 253, 0.45)',
                        borderColor: '#58a6ff',
                        borderWidth: 1,
                        yAxisID: 'yCount',
                        barPercentage: 0.5
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { grid: { color: '#30363d' }, ticks: { color: '#8b949e', maxTicksLimit: 8 } },
                    yVolume: { 
                        type: 'linear', 
                        position: 'left', 
                        grid: { color: '#30363d' }, 
                        ticks: { color: '#3fb950', callback: v => '$' + v.toFixed(3) }, 
                        beginAtZero: true 
                    },
                    yCount: { 
                        type: 'linear', 
                        position: 'right', 
                        grid: { drawOnChartArea: false }, 
                        ticks: { color: '#58a6ff', stepSize: 1 }, 
                        beginAtZero: true 
                    }
                }
            }
        });

        const ctx = document.getElementById('meshChart').getContext('2d');"""

content = content.replace(chart_init_anchor, new_chart_init)

# 3. Add fetching of /api/global-transactions inside pollLedger
poll_anchor = "meshChart.update();\n                }"

poll_tx_update = """meshChart.update();
                }

                // Poll Global Ingress Graph Feed
                try {
                    const txRes = await fetch('/api/global-transactions');
                    const txData = await txRes.json();
                    if (Array.isArray(txData) && txData.length > 0) {
                        const chronTx = [...txData].reverse().slice(-20);
                        document.getElementById('external-tx-counter').textContent = `Total Recorded: ${txData.length}`;
                        globalTxChart.data.labels = chronTx.map(t => formatCentralTimeShort(t.timestamp));
                        globalTxChart.data.datasets[0].data = chronTx.map(t => Number(t.amount_usdc || 0));
                        globalTxChart.data.datasets[1].data = chronTx.map((_, idx) => idx + 1);
                        globalTxChart.update();
                    }
                } catch (e) {
                    console.error("External chart fetch error:", e);
                }"""

content = content.replace(poll_anchor, poll_tx_update)

with open("anav_dashboard.html", "w") as f:
    f.write(content)

print("[SUCCESS] anav_dashboard.html patched with dedicated Global Ingress Graph pane.")

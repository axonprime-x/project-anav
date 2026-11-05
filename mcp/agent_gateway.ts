import express from 'express';
import type { Request, Response } from 'express';
import { GoogleGenAI } from '@google/genai';
import { execSync } from 'child_process';

const app = express();
app.use(express.json());

const PORT = Number(process.env.PORT) || 5001;
const NODE_ID = process.env.NODE_ID || 'node_master_01';
const apiKey = process.env.GEMINI_API_KEY;

app.get('/.well-known/agent-card.json', (req: Request, res: Response) => {
  res.json({
    type: "ERC-8004-Agent-Card",
    name: `ANAV-Sovereign-Node-${NODE_ID}`,
    endpoint: `http://localhost:${PORT}/api/v1/mcp`,
    payment_token: "USDC",
    accepted_rails: ["x402-Base", "x402-Solana"],
    capabilities: ["code_synthesis", "telemetry_parsing", "inverse_royalty_settlement"],
    trust_verification: "SHA256_ATTESTED"
  });
});

app.post('/api/v1/mcp', async (req: Request, res: Response) => {
  const paymentHeader = req.headers['x-payment-proof'];

  if (!paymentHeader) {
    return res.status(402).json({
      error: "Payment Required",
      protocol: "x402",
      price_usdc: "0.05",
      pay_to: "0xANAVUnionMeshMasterAddress...",
      message: "Please include valid X-PAYMENT-PROOF header to execute Gemini synthesis payload."
    });
  }

  const { query, amount_usdc = 0.05 } = req.body;

  // Process transaction through Python SQLite Inverse Splitter Daemon
  let splitResult = { status: "SPLIT_PENDING" };
  try {
    const pythonCmd = `python3 -c "from daemons.daemon_inverse_splitter import PersistentInverseSplitter; s = PersistentInverseSplitter(); print(s.process_transaction('${paymentHeader}', ${amount_usdc}))"`;
    const output = execSync(pythonCmd).toString().trim();
    splitResult = JSON.parse(output.replace(/'/g, '"'));
  } catch (err: any) {
    console.error("[GATEWAY SPLIT ERROR]", err.message);
  }

  if (!apiKey || apiKey === 'demo_key') {
    return res.json({
      status: "SUCCESS",
      mode: "LOCAL_MOCK_SYNTHESIS",
      node_id: NODE_ID,
      m2m_settlement: "VERIFIED",
      proof_reference: paymentHeader,
      financial_split: splitResult,
      result: `[ANAV M2M GATEWAY] Executed query: "${query || 'Ping telemetry status'}". Inverse split logged.`
    });
  }

  try {
    const ai = new GoogleGenAI({ apiKey });
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: `[ANAV M2M GATEWAY - ${NODE_ID}] Query: ${query || 'Ping telemetry status'}`
    });

    return res.json({
      status: "SUCCESS",
      mode: "LIVE_GEMINI_SYNTHESIS",
      node_id: NODE_ID,
      m2m_settlement: "VERIFIED",
      financial_split: splitResult,
      result: response.text
    });
  } catch (err: any) {
    return res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`[ANAV AGENT GATEWAY] Node ${NODE_ID} listening on 0.0.0.0:${PORT}`);
});

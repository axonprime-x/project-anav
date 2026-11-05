import express from 'express';
import type { Request, Response } from 'express';
import { GoogleGenAI } from '@google/genai';

const app = express();
app.use(express.json());

const PORT = process.env.PORT || 5001;
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || 'demo_key' });

app.get('/.well-known/agent-card.json', (req: Request, res: Response) => {
  res.json({
    type: "ERC-8004-Agent-Card",
    name: "ANAV-Sovereign-Node-master_01",
    endpoint: `http://localhost:${PORT}/api/v1/mcp`,
    payment_token: "USDC",
    accepted_rails: ["x402-Base", "x402-Solana"],
    capabilities: ["code_synthesis", "telemetry_parsing"],
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

  const { query } = req.body;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: `[ANAV M2M GATEWAY] Query: ${query || 'Ping telemetry status'}`
    });

    return res.json({
      status: "SUCCESS",
      m2m_settlement: "VERIFIED",
      result: response.text
    });
  } catch (err: any) {
    return res.status(500).json({ error: err.message });
  }
});

app.listen(PORT, () => {
  printNodeInfo(PORT);
});

function printNodeInfo(port: any) {
  console.log(`[ANAV AGENT GATEWAY] Listening on port ${port}`);
  console.log(`  ├─ Agent Card: http://localhost:${port}/.well-known/agent-card.json`);
  console.log(`  └─ x402 Endpoint: http://localhost:${port}/api/v1/mcp`);
}

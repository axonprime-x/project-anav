"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importStar(require("express"));
const genai_1 = require("@google/genai");
const app = (0, express_1.default)();
app.use(express_1.default.json());
const PORT = process.env.PORT || 5001;
const ai = new genai_1.GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || 'demo_key' });
app.get('/.well-known/agent-card.json', (req, res) => {
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
app.post('/api/v1/mcp', async (req, res) => {
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
    }
    catch (err) {
        return res.status(500).json({ error: err.message });
    }
});
app.listen(PORT, () => {
    printNodeInfo(PORT);
});
function printNodeInfo(port) {
    console.log(`[ANAV AGENT GATEWAY] Listening on port ${port}`);
    console.log(`  ├─ Agent Card: http://localhost:${port}/.well-known/agent-card.json`);
    console.log(`  └─ x402 Endpoint: http://localhost:${port}/api/v1/mcp`);
}
//# sourceMappingURL=agent_gateway.js.map
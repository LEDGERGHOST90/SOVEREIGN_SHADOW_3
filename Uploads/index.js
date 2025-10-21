/**
 * NEXUS API Gateway — Express server
 * Fixes: "Module 'crypto' has been externalized for browser" by moving ALL signing to the server.
 * 
 * 🔐 Keep credentials ONLY in server env vars (.env). Never in client code.
 */

import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import binanceRouter from "./api/exchanges/binance.js";
import okxRouter from "./api/exchanges/okx.js";

// Load environment variables
dotenv.config();

const app = express();
const PORT = process.env.PORT || 5055;

// Middleware
app.use(cors());
app.use(express.json());

// API Routes
app.use("/api/binance", binanceRouter);
app.use("/api/okx", okxRouter);

// Health check
app.get("/api/health", (req, res) => {
  res.json({ status: "ok", timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, "0.0.0.0", () => {
  console.log(`🚀 NEXUS API Gateway running on port ${PORT}`);
  console.log(`📊 Binance.US API: /api/binance/portfolio`);
  console.log(`📊 OKX API: /api/okx/portfolio`);
});


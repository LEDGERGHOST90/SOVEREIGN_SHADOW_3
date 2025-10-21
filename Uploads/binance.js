import crypto from "crypto";
import express from "express";

const router = express.Router();

router.get("/portfolio", async (req, res) => {
  try {
    // Read credentials from env on server
    const apiKey = process.env.BINANCE_API_KEY;
    const secret = process.env.BINANCE_SECRET_KEY;
    
    if (!apiKey || !secret) {
      return res.status(500).json({ 
        ok: false, 
        error: "Binance.US API credentials not configured" 
      });
    }

    const timestamp = Date.now();
    const query = `timestamp=${timestamp}`;

    // Server-side HMAC signing
    const signature = crypto
      .createHmac("sha256", secret)
      .update(query)
      .digest("hex");

    const url = `https://api.binance.us/api/v3/account?${query}&signature=${signature}`;

    const response = await fetch(url, {
      headers: { 
        "X-MBX-APIKEY": apiKey,
        "Content-Type": "application/json"
      }
    });

    const data = await response.json();
    
    if (!response.ok) {
      return res.status(response.status).json({ 
        ok: false, 
        error: data.msg || "Binance.US API error" 
      });
    }

    res.json({ ok: true, data });
  } catch (error) {
    console.error("Binance.US API error:", error);
    res.status(500).json({ 
      ok: false, 
      error: error.message || "Internal server error" 
    });
  }
});

router.post("/hedge", async (req, res) => {
  try {
    const { symbol, side, quantity } = req.body;
    const apiKey = process.env.BINANCE_API_KEY;
    const secret = process.env.BINANCE_SECRET_KEY;
    
    if (!apiKey || !secret) {
      return res.status(500).json({ 
        ok: false, 
        error: "Binance.US API credentials not configured" 
      });
    }

    const timestamp = Date.now();
    const params = new URLSearchParams({
      symbol,
      side,
      type: "MARKET",
      quantity: quantity.toString(),
      timestamp: timestamp.toString()
    });

    // Server-side HMAC signing for trade execution
    const signature = crypto
      .createHmac("sha256", secret)
      .update(params.toString())
      .digest("hex");

    params.append("signature", signature);

    const url = `https://api.binance.us/api/v3/order`;

    const response = await fetch(url, {
      method: "POST",
      headers: { 
        "X-MBX-APIKEY": apiKey,
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: params
    });

    const data = await response.json();
    
    if (!response.ok) {
      return res.status(response.status).json({ 
        ok: false, 
        error: data.msg || "Binance.US trade execution error" 
      });
    }

    res.json({ ok: true, data });
  } catch (error) {
    console.error("Binance.US hedge error:", error);
    res.status(500).json({ 
      ok: false, 
      error: error.message || "Internal server error" 
    });
  }
});

export default router;


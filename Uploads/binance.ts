import crypto from "crypto";
import express from "express";

const router = express.Router();

router.get("/portfolio", async (_req, res) => {
  try {
    const key = process.env.BINANCE_US_KEY!;
    const secret = process.env.BINANCE_US_SECRET!;
    if (!key || !secret) return res.status(500).json({ ok:false, error:"Missing BINANCE_US_KEY/SECRET" });
    
    const ts = Date.now();
    const q = `timestamp=${ts}`;
    const sig = crypto.createHmac("sha256", secret).update(q).digest("hex");
    const url = `https://api.binance.us/api/v3/account?${q}&signature=${sig}`;
    
    const r = await fetch(url, { headers: { "X-MBX-APIKEY": key } });
    const data = await r.json();
    res.json({ ok: true, data });
  } catch (e: any) { 
    res.status(500).json({ ok:false, error: e?.message || String(e) }); 
  }
});

export default router;


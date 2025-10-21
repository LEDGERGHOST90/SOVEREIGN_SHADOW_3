import express from "express";

const router = express.Router();

router.get("/portfolio", async (_req, res) => {
  // TODO: Implement real OKX signing server-side
  res.json({ ok: true, data: { items: [], note: "OKX stub" } });
});

export default router;


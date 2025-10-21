import express from "express";
import binance from "./api/exchanges/binance";
import okx from "./api/exchanges/okx";

const app = express();
app.use(express.json());
app.use("/api/binance", binance);
app.use("/api/okx", okx);

const port = Number(process.env.PORT || 5174);
app.listen(port, () => console.log(`[server] listening on :${port}`));


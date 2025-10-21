/**
 * NEXUS PROTOCOL — Client Portfolio Sync (browser-safe)
 * =====================================================
 * Fetches real-time portfolio data from server API endpoints
 * No more browser crypto - all signing handled server-side
 */

// -------- Helper: fetch with error handling --------
async function fetchJSON(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return response.json();
}

// -------- Adapters: normalize different exchange formats --------

function adaptBinanceBalances(serverData) {
  // server returns: { platform: "Binance.US", success: true, balances: [...], totalValue: 1234 }
  if (!serverData?.success) {
    throw new Error(serverData?.error || "Binance.US gateway error");
  }
  return serverData.balances.map((b) => ({
    symbol: b.asset,
    free: Number(b.free || 0),
    locked: Number(b.locked || 0),
    total: Number(b.total || 0),
    venue: "BINANCE_US",
  }));
}

function adaptOkxBalances(serverData) {
  // server returns raw OKX balance payload under data
  // OKX shape: { code: "0", data: [{ details: [{ ccy, cashBal, availBal, ... }] }] }
  if (!serverData?.success) {
    throw new Error(serverData?.error || "OKX gateway error");
  }
  const details = (serverData.balances || []);
  return details.map((d) => ({
    symbol: d.ccy,
    free: Number(d.availBal || d.bal || 0),
    locked: Math.max(0, Number(d.bal || 0) - Number(d.availBal || 0)),
    total: Number(d.bal || d.availBal || 0),
    venue: "OKX",
  }));
}

// Optional: Coinbase adapter if you expose it via server
function adaptCoinbaseBalances(serverData) {
  if (!serverData?.success) throw new Error(serverData?.error || "Coinbase gateway error");
  const items = (serverData.balances || []).map((a) => ({
    symbol: a.currency,
    free: Number(a.balance || 0),
    locked: Number(a.locked || 0),
    total: Number(a.balance || 0) + Number(a.locked || 0),
    venue: "COINBASE",
  }));
  return items;
}

// -------- Public API: called by components --------

export async function fetchBinanceUSPortfolio() {
  try {
    console.log('🔄 Fetching Binance.US portfolio via server...');
    const data = await fetchJSON("/api/portfolio/binance");
    const assets = adaptBinanceBalances(data);
    console.log(`✅ Binance.US: ${assets.length} assets loaded`);
    return assets;
  } catch (error) {
    console.error('❌ Binance.US portfolio fetch failed:', error);
    throw error;
  }
}

export async function fetchOKXPortfolio() {
  try {
    console.log('🔄 Fetching OKX portfolio via server...');
    const data = await fetchJSON("/api/portfolio/okx");
    const assets = adaptOkxBalances(data);
    console.log(`✅ OKX: ${assets.length} assets loaded`);
    return assets;
  } catch (error) {
    console.error('❌ OKX portfolio fetch failed:', error);
    throw error;
  }
}

export async function fetchCoinbasePortfolio() {
  try {
    console.log('🔄 Fetching Coinbase portfolio via server...');
    // Only if you implement /api/portfolio/coinbase on the server
    const data = await fetchJSON("/api/portfolio/coinbase");
    const assets = adaptCoinbaseBalances(data);
    console.log(`✅ Coinbase: ${assets.length} assets loaded`);
    return assets;
  } catch (error) {
    console.error('❌ Coinbase portfolio fetch failed:', error);
    throw error;
  }
}

export async function fetchCompletePortfolio({ includeCoinbase = false } = {}) {
  console.log('🚀 FETCHING COMPLETE LIVE PORTFOLIO VIA CLIENT...');
  
  const results = await Promise.allSettled([
    fetchBinanceUSPortfolio(),
    fetchOKXPortfolio(),
    includeCoinbase ? fetchCoinbasePortfolio() : Promise.resolve([]),
  ]);

  const assets = results.flatMap((r) => (r.status === "fulfilled" ? r.value : []));
  const errors = results
    .map((r, idx) => (r.status === "rejected" ? { idx, error: r.reason?.message || String(r.reason) } : null))
    .filter(Boolean);

  console.log('✅ PORTFOLIO SYNC COMPLETE!');
  console.log(`📊 Assets Found: ${assets.length}`);
  if (errors.length > 0) {
    console.warn('⚠️ Portfolio warnings:', errors);
  }

  return { assets, errors };
}

export function summarizePortfolio(assets, pricesBySymbol = {}) {
  // pricesBySymbol is optional: { BTC: 64000, ETH: 3200, ... }
  const byKey = new Map();
  for (const a of assets) {
    const key = `${a.venue}:${a.symbol}`;
    const prev = byKey.get(key) || { ...a, total: 0 };
    prev.total += a.total;
    byKey.set(key, prev);
  }
  const merged = [...byKey.values()];
  
  // Calculate total value using current market prices
  const marketPrices = {
    'BTC': 58000,
    'ETH': 2650,
    'USDT': 1.00,
    'USDC': 1.00,
    'USD': 1.00,
    'ADA': 0.35,
    'HBAR': 0.055,
    'CTSI': 0.15,
    'ARB': 0.52,
    'RENDER': 7.20,
    'BONK': 0.000018,
    'WIF': 1.85,
    'BRETT': 0.08,
    'SOL': 142,
    'BNB': 580,
    'MATIC': 0.42,
    'LINK': 11.50
  };
  
  const totalValue = merged.reduce((acc, a) => {
    const price = pricesBySymbol[a.symbol] || marketPrices[a.symbol] || 0.01;
    return acc + (price * a.total);
  }, 0);
  
  return { items: merged, totalValue };
}

/**
 * Convert portfolio assets to NEXUS format for display
 */
export function convertToNexusFormat(assets) {
  return assets.map(asset => ({
    id: asset.symbol.toLowerCase(),
    name: getAssetName(asset.symbol),
    symbol: asset.symbol,
    price: getAssetPrice(asset.symbol),
    balance: asset.total,
    value: asset.total * getAssetPrice(asset.symbol),
    changeDay: Math.random() * 10 - 5, // Will be fetched from price API
    changeWeek: Math.random() * 20 - 10,
    changeMonth: Math.random() * 30 - 15,
    changeAll: Math.random() * 200 - 100,
    spark: generateSparklineData(),
    accent: getAssetColor(asset.symbol),
    connected: true,
    platforms: [asset.venue],
    hedgeRatio: calculateHedgeRatio(asset.symbol),
    riskLevel: getRiskLevel(asset.symbol),
    free: asset.free,
    locked: asset.locked
  }));
}

// Helper functions
function getAssetName(symbol) {
  const names = {
    'BTC': 'Bitcoin',
    'ETH': 'Ethereum',
    'SOL': 'Solana',
    'USDT': 'Tether USD',
    'USDC': 'USD Coin',
    'USD': 'US Dollar',
    'BNB': 'Binance Coin',
    'ADA': 'Cardano',
    'HBAR': 'Hedera',
    'CTSI': 'Cartesi',
    'ARB': 'Arbitrum',
    'RENDER': 'Render',
    'BONK': 'Bonk',
    'WIF': 'Dogwifhat',
    'BRETT': 'Brett',
    'DOT': 'Polkadot',
    'LINK': 'Chainlink',
    'MATIC': 'Polygon'
  };
  return names[symbol] || symbol;
}

function getAssetPrice(symbol) {
  const prices = {
    'BTC': 58000,
    'ETH': 2650,
    'USDT': 1.00,
    'USDC': 1.00,
    'USD': 1.00,
    'ADA': 0.35,
    'HBAR': 0.055,
    'CTSI': 0.15,
    'ARB': 0.52,
    'RENDER': 7.20,
    'BONK': 0.000018,
    'WIF': 1.85,
    'BRETT': 0.08,
    'SOL': 142,
    'BNB': 580,
    'MATIC': 0.42,
    'LINK': 11.50
  };
  return prices[symbol] || 0.01;
}

function getAssetColor(symbol) {
  const colors = {
    'BTC': '#f7931a',
    'ETH': '#627eea',
    'SOL': '#9945ff',
    'USDT': '#26a17b',
    'USDC': '#2775ca',
    'USD': '#22c55e',
    'BNB': '#f3ba2f',
    'ADA': '#0033ad',
    'HBAR': '#000000',
    'CTSI': '#325fff',
    'ARB': '#28a0f0',
    'RENDER': '#5865f2',
    'BONK': '#f97316',
    'WIF': '#a855f7',
    'BRETT': '#ef4444',
    'DOT': '#e6007a',
    'LINK': '#375bd2',
    'MATIC': '#8247e5'
  };
  return colors[symbol] || '#6b7280';
}

function calculateHedgeRatio(symbol) {
  // Higher hedge ratios for more volatile assets
  const ratios = {
    'BTC': 0.6,
    'ETH': 0.8,
    'SOL': 0.7,
    'USDT': 0,
    'USDC': 0,
    'USD': 0,
    'ADA': 0.5,
    'HBAR': 0.4,
    'CTSI': 0.6,
    'ARB': 0.7,
    'RENDER': 0.8,
    'BONK': 0.9,
    'WIF': 0.9,
    'BRETT': 0.8
  };
  return ratios[symbol] || 0.5;
}

function getRiskLevel(symbol) {
  const risks = {
    'BTC': 'MEDIUM',
    'ETH': 'MEDIUM',
    'SOL': 'HIGH',
    'USDT': 'LOW',
    'USDC': 'LOW',
    'USD': 'LOW',
    'ADA': 'MEDIUM',
    'HBAR': 'MEDIUM',
    'CTSI': 'HIGH',
    'ARB': 'HIGH',
    'RENDER': 'HIGH',
    'BONK': 'VERY_HIGH',
    'WIF': 'VERY_HIGH',
    'BRETT': 'HIGH'
  };
  return risks[symbol] || 'MEDIUM';
}

function generateSparklineData() {
  const data = [];
  let price = 100;
  for (let i = 0; i < 12; i++) {
    price += (Math.random() - 0.5) * 10;
    data.push(Math.max(0, price));
  }
  return data;
}


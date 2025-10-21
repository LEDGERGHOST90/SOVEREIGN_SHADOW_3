/**
 * NEXUS PROTOCOL - Real Portfolio Data
 * 
 * Integrated from fut_purp_spot_Aug19 trading system
 * Live portfolio positions and hedge data
 */

// Real portfolio data from hedge execution system
export const PORTFOLIO_SUMMARY = {
  totalValue: 12725.0,
  ethExposure: 6500.0,
  hedgeRatio: 0.8,
  protectionAmount: 5200.0,
  lastUpdate: "2025-08-19T19:28:17.955836"
};

// Active hedge positions
export const ACTIVE_HEDGES = [
  {
    id: "eth-perp-hedge",
    symbol: "ETH-PERP",
    action: "SHORT",
    size: 1.2381,
    value: 5200.0,
    purpose: "STETH_HEDGE",
    platform: "COINBASE_FUTURES",
    status: "READY_FOR_MANUAL_EXECUTION",
    timestamp: "2025-08-19T19:28:17.955836"
  }
];

// Real asset positions based on portfolio data
export const REAL_ASSETS = [
  {
    id: "ethereum",
    name: "Ethereum",
    symbol: "ETH",
    price: 2650.45, // Calculated from $6500 exposure
    balance: 2.4528, // ETH balance
    value: 6500.0,
    changeDay: 2.34,
    changeWeek: 8.12,
    changeMonth: -4.61,
    changeAll: 12.5,
    spark: [2580, 2610, 2590, 2620, 2640, 2635, 2650, 2630, 2645, 2650, 2648, 2665],
    accent: "#627eea",
    connected: true,
    hedgeRatio: 80,
    hedgeValue: 5200.0,
    platform: "Coinbase Futures",
    riskLevel: "MEDIUM"
  },
  {
    id: "staked-ethereum",
    name: "Staked Ethereum",
    symbol: "STETH",
    price: 2645.20,
    balance: 2.4580,
    value: 6500.0, // Part of ETH exposure
    changeDay: 2.28,
    changeWeek: 8.05,
    changeMonth: -4.55,
    changeAll: 12.2,
    spark: [2575, 2605, 2585, 2615, 2635, 2630, 2645, 2625, 2640, 2645, 2643, 2660],
    accent: "#00d4ff",
    connected: true,
    hedgeRatio: 80,
    hedgeValue: 5200.0,
    platform: "Ledger Vault",
    riskLevel: "MEDIUM"
  },
  {
    id: "usdt",
    name: "Tether USD",
    symbol: "USDT",
    price: 1.0,
    balance: 6225.0,
    value: 6225.0,
    changeDay: 0.01,
    changeWeek: -0.02,
    changeMonth: 0.05,
    changeAll: 0.1,
    spark: [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    accent: "#26a17b",
    connected: true,
    hedgeRatio: 0,
    hedgeValue: 0,
    platform: "Multiple",
    riskLevel: "LOW"
  },
  {
    id: "bitcoin",
    name: "Bitcoin",
    symbol: "BTC",
    price: 58420.50,
    balance: 0.0342,
    value: 1998.0,
    changeDay: 1.85,
    changeWeek: 4.22,
    changeMonth: -2.15,
    changeAll: 45.8,
    spark: [57200, 57800, 57500, 58100, 58300, 58200, 58400, 58100, 58350, 58420, 58380, 58500],
    accent: "#f7931a",
    connected: true,
    hedgeRatio: 0,
    hedgeValue: 0,
    platform: "Coinbase",
    riskLevel: "MEDIUM"
  },
  {
    id: "solana",
    name: "Solana",
    symbol: "SOL",
    price: 142.85,
    balance: 7.0245,
    value: 1003.5,
    changeDay: 3.45,
    changeWeek: 12.8,
    changeMonth: 8.92,
    changeAll: 285.4,
    spark: [135, 138, 140, 142, 144, 143, 145, 142, 144, 143, 142, 145],
    accent: "#9945ff",
    connected: true,
    hedgeRatio: 0,
    hedgeValue: 0,
    platform: "Multiple",
    riskLevel: "HIGH"
  }
];

// Risk management configuration
export const RISK_CONFIG = {
  maxPositionSize: 10000,
  stopLossPct: 0.05,
  rebalanceThreshold: 0.10,
  autoMonitoring: true,
  tradingAuthorized: true
};

// API credentials status
export const API_STATUS = {
  coinbase: {
    connected: true,
    permissions: ["trade", "transfer"],
    status: "FULLY_AUTHORIZED"
  },
  binanceUS: {
    connected: true,
    permissions: ["read", "trade"],
    status: "CONFIGURED"
  },
  okx: {
    connected: true,
    permissions: ["read", "trade"],
    status: "CONFIGURED"
  },
  ledgerVault: {
    connected: true,
    permissions: ["read"],
    status: "VAULT_CONNECTED"
  }
};


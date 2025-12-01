/**
 * Neural Hub API Client
 * Connects SS_III Dashboard to AURORA (Neural Hub) backend
 */

const NEURAL_HUB_URL = "http://localhost:8000";

export interface MarketData {
  symbol: string;
  price: number;
  change_24h: number;
  rsi: number;
  volume_24h: number;
}

export interface Signal {
  symbol: string;
  action: "BUY" | "SELL" | "HOLD";
  confidence: number;
  reasoning: string;
  entry_price: number;
  stop_loss: number;
  take_profit_1: number;
  take_profit_2: number;
  risk_level: string;
  timeframe: string;
  timestamp: string;
}

export interface Analysis {
  symbol: string;
  trend: string;
  strength: number;
  support_levels: number[];
  resistance_levels: number[];
  patterns_detected: string[];
  key_insights: string[];
  recommendation: string;
  timestamp: string;
}

export interface CouncilState {
  status: string;
  timestamp: string;
  council: Record<string, unknown>;
  last_trade: Record<string, unknown>;
  portfolio_snapshot: {
    net_worth: number;
    debt: number;
    health_factor: number;
  };
  december_campaign: Record<string, unknown>;
  active_motions: unknown[];
}

export interface PortfolioData {
  net_worth: number;
  ledger: Record<string, unknown>;
  exchanges: Record<string, unknown>;
  aave: {
    collateral: number;
    debt: number;
    health_factor: number;
  };
}

// Health check
export async function checkHealth(): Promise<{ status: string; timestamp: string }> {
  const res = await fetch(`${NEURAL_HUB_URL}/api/`);
  return res.json();
}

// Get portfolio data
export async function getPortfolio(): Promise<PortfolioData> {
  const res = await fetch(`${NEURAL_HUB_URL}/api/portfolio`);
  return res.json();
}

// Get council state (from BRAIN.json)
export async function getCouncilState(): Promise<CouncilState> {
  const res = await fetch(`${NEURAL_HUB_URL}/api/council/state`);
  return res.json();
}

// Generate a trading signal
export async function generateSignal(symbol: string): Promise<{ status: string; signal: Signal }> {
  const res = await fetch(`${NEURAL_HUB_URL}/api/signals/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symbol }),
  });
  return res.json();
}

// Get all signals
export async function getSignals(status?: string): Promise<Signal[]> {
  const url = status
    ? `${NEURAL_HUB_URL}/api/signals?status=${status}`
    : `${NEURAL_HUB_URL}/api/signals`;
  const res = await fetch(url);
  return res.json();
}

// Deep analyze a symbol
export async function analyzeSymbol(symbol: string): Promise<Analysis> {
  const res = await fetch(`${NEURAL_HUB_URL}/api/neural/analyze/${symbol}`);
  return res.json();
}

// Chat with neural agent (Oracle)
export async function oracleChat(message: string, context?: Record<string, unknown>): Promise<{ response: string }> {
  const res = await fetch(`${NEURAL_HUB_URL}/api/neural/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, context }),
  });
  return res.json();
}

// Get strategy recommendation
export async function getStrategyRecommendation(): Promise<Record<string, unknown>> {
  const res = await fetch(`${NEURAL_HUB_URL}/api/neural/strategy`);
  return res.json();
}

// Run market scanner
export async function runScanner(params?: {
  minVolume?: number;
  minChange?: number;
  sortBy?: string;
}): Promise<{
  scan_time: string;
  symbols_scanned: number;
  signals_found: number;
  tokens: Array<{
    symbol: string;
    action: string;
    confidence: number;
    reasoning: string;
    price: number;
    rsi: number;
    change_24h: number;
  }>;
}> {
  const searchParams = new URLSearchParams();
  if (params?.minVolume) searchParams.set("minVolume", String(params.minVolume));
  if (params?.minChange) searchParams.set("minChange", String(params.minChange));
  if (params?.sortBy) searchParams.set("sortBy", params.sortBy);

  const url = `${NEURAL_HUB_URL}/api/scanner${searchParams.toString() ? `?${searchParams}` : ""}`;
  const res = await fetch(url);
  return res.json();
}

// Get positions
export async function getPositions(): Promise<{
  positions: Array<{
    id: string;
    symbol: string;
    entry_price: number;
    current_price: number;
    quantity: number;
    position_value: number;
    stop_loss: number;
    take_profit_1: number;
    take_profit_2: number;
    status: string;
  }>;
  count: number;
}> {
  const res = await fetch(`${NEURAL_HUB_URL}/api/positions`);
  return res.json();
}

// Get automation status
export async function getAutomationStatus(): Promise<{
  enabled: boolean;
  mode: string;
  trades_today: number;
  max_trades: number;
  min_confidence: number;
  last_scan: string;
}> {
  const res = await fetch(`${NEURAL_HUB_URL}/api/automation/status`);
  return res.json();
}

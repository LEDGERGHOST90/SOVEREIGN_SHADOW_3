/**
 * SovereignShadow API Service
 * Connects Gemini frontend to Python backend
 *
 * Usage:
 *   import { sovereignApi } from './services/sovereignApi';
 *   const portfolio = await sovereignApi.getPortfolio();
 */

// API base URL - switch between local dev and production
const API_BASE = import.meta.env.PROD
  ? 'https://sovereignnshadowii.abacusai.app/api'
  : 'http://localhost:8000/api';

interface ApiResponse<T> {
  data?: T;
  error?: string;
}

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
      return { error: error.detail || `HTTP ${response.status}` };
    }

    const data = await response.json();
    return { data };
  } catch (err) {
    return { error: err instanceof Error ? err.message : 'Network error' };
  }
}

// =============================================================================
// PORTFOLIO
// =============================================================================

export interface Portfolio {
  timestamp: string;
  total_value_usd: number;
  exchanges: Record<string, any>;
  defi: Record<string, any>;
  summary: Record<string, any>;
}

export interface AaveStatus {
  health_factor: number;
  total_debt_usd: number;
  collateral_usd: number;
  collateral_asset: string;
  borrow_apy: number;
  annual_cost: number;
  status: string;
  last_updated: string;
}

// =============================================================================
// STRATEGIES
// =============================================================================

export interface Strategy {
  id?: string;
  name: string;
  description: string;
  category: 'Vault' | 'Sniper' | 'Ladder' | 'MENACE';
  risk_level: 'Low' | 'Medium' | 'High' | 'Degen';
  timeframe: string;
  assets: string[];
  buy_conditions: string[];
  sell_conditions: string[];
  stop_loss: string;
  take_profit: string;
  indicators: string[];
  sentiment: number;
  source?: string;
  created_at?: string;
}

// =============================================================================
// TRADES
// =============================================================================

export interface Trade {
  asset: string;
  side: 'buy' | 'sell';
  amount: number;
  price?: number;
  strategy_id?: string;
}

export interface TradeRecord extends Trade {
  id: string;
  status: string;
  requested_at: string;
  executed_at?: string;
  profit?: number;
}

// =============================================================================
// SCANNER
// =============================================================================

export interface BreakoutCandidate {
  token: string;
  score: number;
  volume_24h: number;
  price_change: number;
  smart_money_score: number;
}

// =============================================================================
// API SERVICE
// =============================================================================

export const sovereignApi = {
  // Health check
  async healthCheck() {
    return fetchApi<{ status: string; timestamp: string }>('/health');
  },

  // Portfolio
  async getPortfolio() {
    return fetchApi<Portfolio>('/portfolio');
  },

  async getAaveStatus() {
    return fetchApi<AaveStatus>('/portfolio/aave');
  },

  // Strategies
  async listStrategies() {
    return fetchApi<{ strategies: Strategy[]; count: number }>('/strategies');
  },

  async getStrategy(id: string) {
    return fetchApi<Strategy>(`/strategies/${id}`);
  },

  async saveStrategy(strategy: Strategy) {
    return fetchApi<{ status: string; strategy_id: string }>('/strategies', {
      method: 'POST',
      body: JSON.stringify(strategy),
    });
  },

  async deleteStrategy(id: string) {
    return fetchApi<{ status: string }>(`/strategies/${id}`, {
      method: 'DELETE',
    });
  },

  // Scanner
  async getBreakoutCandidates() {
    return fetchApi<{ candidates: BreakoutCandidate[]; scanned_at: string }>('/scanner/breakout');
  },

  async scanDexTokens() {
    return fetchApi<{ tokens: any[]; scanned_at: string }>('/scanner/dex');
  },

  // Trading
  async executeTrade(trade: Trade) {
    return fetchApi<{ status: string; trade_id: string; message: string }>('/trades/execute', {
      method: 'POST',
      body: JSON.stringify(trade),
    });
  },

  async listTrades() {
    return fetchApi<{ trades: TradeRecord[]; count: number }>('/trades');
  },

  // Session
  async getCurrentSession() {
    return fetchApi<any>('/session');
  },

  async saveSession(state: any) {
    return fetchApi<{ status: string }>('/session', {
      method: 'POST',
      body: JSON.stringify(state),
    });
  },
};

// =============================================================================
// HYBRID MODE: Use API when available, fall back to localStorage
// =============================================================================

export async function syncStrategiesToBackend(localStrategies: Strategy[]) {
  const { data, error } = await sovereignApi.listStrategies();

  if (error) {
    console.warn('Backend unavailable, using localStorage only');
    return { synced: false, error };
  }

  // Find strategies that exist locally but not in backend
  const backendIds = new Set(data?.strategies.map(s => s.id));
  const toSync = localStrategies.filter(s => !backendIds.has(s.id));

  // Sync each missing strategy
  for (const strategy of toSync) {
    await sovereignApi.saveStrategy(strategy);
  }

  return { synced: true, count: toSync.length };
}

export default sovereignApi;

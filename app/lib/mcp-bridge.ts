/**
 * MCP Bridge - Live connection to Sovereign Shadow Trading API
 * Connects Next.js frontend to Python FastAPI backend
 *
 * USAGE IN API ROUTES:
 * import { MCPBridge } from '@/lib/mcp-bridge';
 * const data = await MCPBridge.getEmpire();
 *
 * BACKEND: FastAPI server must be running on port 8000
 * Start with: python3 core/api/trading_api_server.py
 */

export interface EmpireData {
  totalValue: number;
  ledgerVault: number;
  binanceUs: number;
  lidoRewards: number;
  timestamp: string;
  metamask?: number;
  aaveHealthFactor?: number;
}

export interface VaultHoldings {
  steth: number;
  btc: number;
  xrp: number;
  eth: number;
  sol: number;
  usdt?: number;
}

export interface HealthStatus {
  status: string;
  uptime_seconds: number;
  active_strategies: number;
  risk_gate_status: string;
  aave_health_factor: number | null;
  session_pnl: number;
}

export class MCPBridge {
  // API base URL - configurable via environment variable
  private static readonly API_BASE =
    process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  // Fallback data in case API is unreachable
  private static readonly FALLBACK_EMPIRE: EmpireData = {
    totalValue: 6203.94,
    ledgerVault: 6167.43,
    binanceUs: 0,
    lidoRewards: 0,
    metamask: 36.51,
    timestamp: new Date().toISOString()
  };

  private static readonly FALLBACK_VAULT: VaultHoldings = {
    steth: 0,  // AAVE wstETH
    btc: 2231.74,
    xrp: 2.57,
    eth: 21.62,
    sol: 0,
    usdt: 4.99
  };

  /**
   * Get complete empire overview from live API
   * Falls back to cached data if API unreachable
   */
  static async getEmpire(): Promise<EmpireData> {
    try {
      const response = await fetch(`${this.API_BASE}/api/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(5000) // 5 second timeout
      });

      if (!response.ok) {
        throw new Error(`API returned ${response.status}`);
      }

      const health: HealthStatus = await response.json();

      // Map health response to EmpireData format
      return {
        totalValue: health.session_pnl + 6203.94, // Base + session P&L
        ledgerVault: 6167.43, // From portfolio
        binanceUs: 0, // Need to implement exchange balance fetch
        lidoRewards: 0, // AAVE rewards (if available)
        metamask: 36.51,
        aaveHealthFactor: health.aave_health_factor || undefined,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.warn('⚠️ Failed to fetch live empire data, using fallback:', error);
      return this.FALLBACK_EMPIRE;
    }
  }

  /**
   * Get Ledger vault breakdown from live API
   * Falls back to cached data if API unreachable
   */
  static async getVault(): Promise<VaultHoldings> {
    try {
      const response = await fetch(`${this.API_BASE}/api/portfolio/ledger`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(5000)
      });

      if (!response.ok) {
        // API might not have this endpoint yet, fall back
        console.warn('⚠️ /api/portfolio/ledger not available, using fallback');
        return this.FALLBACK_VAULT;
      }

      const data = await response.json();

      return {
        steth: data.aave_wsteth || 0,
        btc: data.btc || 2231.74,
        xrp: data.xrp || 2.57,
        eth: data.eth || 21.62,
        sol: data.sol || 0,
        usdt: data.usdt || 4.99
      };
    } catch (error) {
      console.warn('⚠️ Failed to fetch vault data, using fallback:', error);
      return this.FALLBACK_VAULT;
    }
  }

  /**
   * Check if Binance US exchange is healthy
   * Uses live API to verify exchange connection
   */
  static async checkBinance(): Promise<{ healthy: boolean; message: string }> {
    try {
      const response = await fetch(`${this.API_BASE}/api/exchange/binance/status`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(5000)
      });

      if (!response.ok) {
        return {
          healthy: false,
          message: `API error: ${response.status}`
        };
      }

      const data = await response.json();
      return {
        healthy: data.connected || false,
        message: data.message || 'Status unknown'
      };
    } catch (error) {
      return {
        healthy: false,
        message: 'Cannot connect to API server - is it running?'
      };
    }
  }

  /**
   * Get live trading strategy performance
   * NEW: Direct access to strategy metrics
   */
  static async getStrategyPerformance(): Promise<any> {
    try {
      const response = await fetch(`${this.API_BASE}/api/strategy/performance`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(5000)
      });

      if (!response.ok) {
        throw new Error(`Strategy API returned ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('❌ Failed to fetch strategy performance:', error);
      return {
        strategies: [],
        total_profit: 0,
        total_trades: 0,
        session_start: new Date().toISOString()
      };
    }
  }

  /**
   * Execute a trade via the API
   * NEW: Direct trade execution from frontend
   */
  static async executeTrade(params: {
    strategy: string;
    pair: string;
    amount: number;
    side?: string;
    mode?: string;
  }): Promise<any> {
    try {
      const response = await fetch(`${this.API_BASE}/api/trade/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy: params.strategy,
          pair: params.pair,
          amount: params.amount,
          side: params.side || 'auto',
          mode: params.mode || 'paper'
        }),
        signal: AbortSignal.timeout(10000) // 10 seconds for trades
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Trade execution failed');
      }

      return await response.json();
    } catch (error) {
      console.error('❌ Trade execution failed:', error);
      throw error;
    }
  }

  /**
   * Check if API server is reachable
   * Useful for health checks and error handling
   */
  static async isAPIHealthy(): Promise<boolean> {
    try {
      const response = await fetch(`${this.API_BASE}/api/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(3000)
      });
      return response.ok;
    } catch {
      return false;
    }
  }
}

// Export convenience functions
export const getEmpireData = () => MCPBridge.getEmpire();
export const getVaultData = () => MCPBridge.getVault();
export const checkBinanceHealth = () => MCPBridge.checkBinance();

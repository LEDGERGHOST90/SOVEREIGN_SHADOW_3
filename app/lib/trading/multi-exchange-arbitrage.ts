import { EventEmitter } from 'events';

export interface ArbitrageOpportunity {
  id: string;
  symbol: string;
  buyExchange: string;
  sellExchange: string;
  buyPrice: number;
  sellPrice: number;
  profitPercentage: number;
  profitAmount: number;
  maxQuantity: number;
  timestamp: string;
  confidence: number;
  riskLevel: 'low' | 'medium' | 'high';
}

export interface ExchangePrice {
  exchange: string;
  symbol: string;
  bid: number;
  ask: number;
  volume: number;
  timestamp: string;
  spread: number;
}

export interface ArbitrageConfig {
  minProfitPercentage: number;
  maxPositionSize: number;
  maxDailyTrades: number;
  riskManagement: {
    maxLossPerTrade: number;
    stopLossPercentage: number;
    takeProfitPercentage: number;
  };
  exchanges: string[];
  symbols: string[];
}

export class MultiExchangeArbitrage extends EventEmitter {
  private config: ArbitrageConfig;
  private opportunities: Map<string, ArbitrageOpportunity> = new Map();
  private exchangePrices: Map<string, ExchangePrice[]> = new Map();
  private dailyTradeCount: number = 0;
  private dailyPnL: number = 0;
  private isRunning: boolean = false;

  constructor() {
    super();
    
    this.config = {
      minProfitPercentage: 0.5, // 0.5% minimum profit
      maxPositionSize: 1000, // $1000 max position
      maxDailyTrades: 50,
      riskManagement: {
        maxLossPerTrade: 50, // $50 max loss per trade
        stopLossPercentage: 1, // 1% stop loss
        takeProfitPercentage: 2 // 2% take profit
      },
      exchanges: ['binance_us', 'okx', 'kraken'],
      symbols: ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'ADA/USDT', 'SOL/USDT']
    };

    this.startArbitrageMonitoring();
  }

  // Start continuous arbitrage monitoring
  private startArbitrageMonitoring(): void {
    this.isRunning = true;
    
    // Monitor prices every 5 seconds
    setInterval(() => {
      if (this.isRunning) {
        this.scanForOpportunities();
      }
    }, 5000);

    // Clean up old opportunities every minute
    setInterval(() => {
      this.cleanupOldOpportunities();
    }, 60000);

    console.log('🔍 Multi-exchange arbitrage monitoring started');
  }

  // Scan for arbitrage opportunities across exchanges
  private async scanForOpportunities(): Promise<void> {
    try {
      for (const symbol of this.config.symbols) {
        await this.checkSymbolArbitrage(symbol);
      }
    } catch (error) {
      console.error('Error scanning for arbitrage opportunities:', error);
    }
  }

  // Check arbitrage opportunities for a specific symbol
  private async checkSymbolArbitrage(symbol: string): Promise<void> {
    const prices = await this.fetchExchangePrices(symbol);
    if (prices.length < 2) return;

    // Sort by ask price (buy price)
    const sortedByAsk = [...prices].sort((a, b) => a.ask - b.ask);
    
    // Find best arbitrage opportunity
    for (let i = 0; i < sortedByAsk.length; i++) {
      const buyExchange = sortedByAsk[i];
      
      for (let j = i + 1; j < sortedByAsk.length; j++) {
        const sellExchange = sortedByAsk[j];
        
        // Calculate profit potential
        const profitPercentage = ((sellExchange.bid - buyExchange.ask) / buyExchange.ask) * 100;
        
        if (profitPercentage >= this.config.minProfitPercentage) {
          const maxQuantity = Math.min(
            buyExchange.volume * 0.1, // Max 10% of exchange volume
            this.config.maxPositionSize / buyExchange.ask
          );
          
          const profitAmount = (sellExchange.bid - buyExchange.ask) * maxQuantity;
          
          const opportunity: ArbitrageOpportunity = {
            id: this.generateOpportunityId(),
            symbol,
            buyExchange: buyExchange.exchange,
            sellExchange: sellExchange.exchange,
            buyPrice: buyExchange.ask,
            sellPrice: sellExchange.bid,
            profitPercentage,
            profitAmount,
            maxQuantity,
            timestamp: new Date().toISOString(),
            confidence: this.calculateConfidence(buyExchange, sellExchange),
            riskLevel: this.assessRiskLevel(profitPercentage, maxQuantity)
          };

          // Store opportunity
          this.opportunities.set(opportunity.id, opportunity);
          
          // Emit opportunity found event
          this.emit('opportunityFound', opportunity);
          
          console.log(`💰 Arbitrage opportunity: ${symbol} - ${opportunity.profitPercentage.toFixed(2)}% profit ($${opportunity.profitAmount.toFixed(2)})`);
        }
      }
    }
  }

  // Fetch prices from all exchanges for a symbol
  private async fetchExchangePrices(symbol: string): Promise<ExchangePrice[]> {
    const prices: ExchangePrice[] = [];
    
    for (const exchange of this.config.exchanges) {
      try {
        const price = await this.fetchExchangePrice(exchange, symbol);
        if (price) {
          prices.push(price);
        }
      } catch (error) {
        console.warn(`Failed to fetch price from ${exchange} for ${symbol}:`, error);
      }
    }
    
    return prices;
  }

  // Fetch price from a specific exchange
  private async fetchExchangePrice(exchange: string, symbol: string): Promise<ExchangePrice | null> {
    // Simulate API calls to different exchanges
    const basePrice = this.getBasePrice(symbol);
    const spread = 0.001; // 0.1% spread
    
    // Add some randomness to simulate real market conditions
    const variation = (Math.random() - 0.5) * 0.002; // ±0.2% variation
    const adjustedPrice = basePrice * (1 + variation);
    
    return {
      exchange,
      symbol,
      bid: adjustedPrice * (1 - spread / 2),
      ask: adjustedPrice * (1 + spread / 2),
      volume: Math.random() * 1000000 + 100000, // $100k - $1.1M volume
      timestamp: new Date().toISOString(),
      spread: spread * 100
    };
  }

  // Get base price for a symbol (simulated)
  private getBasePrice(symbol: string): number {
    const basePrices: { [key: string]: number } = {
      'BTC/USDT': 95000,
      'ETH/USDT': 3200,
      'XRP/USDT': 0.65,
      'ADA/USDT': 0.45,
      'SOL/USDT': 180
    };
    
    return basePrices[symbol] || 100;
  }

  // Calculate confidence score for an opportunity
  private calculateConfidence(buyExchange: ExchangePrice, sellExchange: ExchangePrice): number {
    let confidence = 70; // Base confidence
    
    // Adjust based on volume
    const minVolume = Math.min(buyExchange.volume, sellExchange.volume);
    if (minVolume > 500000) confidence += 20; // High volume = higher confidence
    else if (minVolume > 100000) confidence += 10;
    
    // Adjust based on spread
    const avgSpread = (buyExchange.spread + sellExchange.spread) / 2;
    if (avgSpread < 0.05) confidence += 10; // Tight spread = higher confidence
    
    return Math.min(100, confidence);
  }

  // Assess risk level for an opportunity
  private assessRiskLevel(profitPercentage: number, quantity: number): 'low' | 'medium' | 'high' {
    if (profitPercentage > 2 && quantity > 10000) return 'low';
    if (profitPercentage > 1 && quantity > 5000) return 'medium';
    return 'high';
  }

  // Execute arbitrage trade
  async executeArbitrage(opportunityId: string, quantity: number): Promise<{
    success: boolean;
    tradeId?: string;
    profit?: number;
    error?: string;
  }> {
    const opportunity = this.opportunities.get(opportunityId);
    if (!opportunity) {
      return { success: false, error: 'Opportunity not found' };
    }

    // Check daily limits
    if (this.dailyTradeCount >= this.config.maxDailyTrades) {
      return { success: false, error: 'Daily trade limit reached' };
    }

    // Check position size
    if (quantity > opportunity.maxQuantity) {
      return { success: false, error: 'Position size exceeds maximum' };
    }

    try {
      // Simulate trade execution
      const tradeId = this.generateTradeId();
      const profit = (opportunity.sellPrice - opportunity.buyPrice) * quantity;
      
      // Update counters
      this.dailyTradeCount++;
      this.dailyPnL += profit;
      
      // Remove opportunity
      this.opportunities.delete(opportunityId);
      
      console.log(`✅ Arbitrage executed: ${opportunity.symbol} - Profit: $${profit.toFixed(2)}`);
      
      // Emit trade executed event
      this.emit('tradeExecuted', {
        tradeId,
        opportunity,
        quantity,
        profit,
        timestamp: new Date().toISOString()
      });
      
      return {
        success: true,
        tradeId,
        profit
      };
      
    } catch (error) {
      console.error('Failed to execute arbitrage:', error);
      return {
        success: false,
        error: 'Trade execution failed'
      };
    }
  }

  // Get current arbitrage opportunities
  getOpportunities(): ArbitrageOpportunity[] {
    return Array.from(this.opportunities.values())
      .sort((a, b) => b.profitPercentage - a.profitPercentage);
  }

  // Get arbitrage statistics
  getStatistics(): {
    totalOpportunities: number;
    dailyTrades: number;
    dailyPnL: number;
    averageProfit: number;
    topSymbol: string;
    topExchange: string;
  } {
    const opportunities = Array.from(this.opportunities.values());
    
    const symbolCounts = opportunities.reduce((acc, opp) => {
      acc[opp.symbol] = (acc[opp.symbol] || 0) + 1;
      return acc;
    }, {} as { [key: string]: number });
    
    const exchangeCounts = opportunities.reduce((acc, opp) => {
      acc[opp.buyExchange] = (acc[opp.buyExchange] || 0) + 1;
      return acc;
    }, {} as { [key: string]: number });
    
    const topSymbol = Object.entries(symbolCounts).sort(([,a], [,b]) => b - a)[0]?.[0] || 'N/A';
    const topExchange = Object.entries(exchangeCounts).sort(([,a], [,b]) => b - a)[0]?.[0] || 'N/A';
    
    const averageProfit = opportunities.length > 0 
      ? opportunities.reduce((sum, opp) => sum + opp.profitAmount, 0) / opportunities.length
      : 0;
    
    return {
      totalOpportunities: opportunities.length,
      dailyTrades: this.dailyTradeCount,
      dailyPnL: this.dailyPnL,
      averageProfit,
      topSymbol,
      topExchange
    };
  }

  // Clean up old opportunities
  private cleanupOldOpportunities(): void {
    const fiveMinutesAgo = Date.now() - (5 * 60 * 1000);
    
    for (const [id, opportunity] of this.opportunities.entries()) {
      if (new Date(opportunity.timestamp).getTime() < fiveMinutesAgo) {
        this.opportunities.delete(id);
      }
    }
  }

  // Generate unique opportunity ID
  private generateOpportunityId(): string {
    return `arb_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
  }

  // Generate unique trade ID
  private generateTradeId(): string {
    return `trade_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
  }

  // Update configuration
  updateConfig(newConfig: Partial<ArbitrageConfig>): void {
    this.config = { ...this.config, ...newConfig };
    console.log('⚙️ Arbitrage configuration updated:', newConfig);
  }

  // Get current configuration
  getConfig(): ArbitrageConfig {
    return { ...this.config };
  }

  // Stop arbitrage monitoring
  stop(): void {
    this.isRunning = false;
    console.log('🛑 Arbitrage monitoring stopped');
  }

  // Start arbitrage monitoring
  start(): void {
    this.isRunning = true;
    console.log('▶️ Arbitrage monitoring started');
  }

  // Reset daily counters (call at start of new day)
  resetDailyCounters(): void {
    this.dailyTradeCount = 0;
    this.dailyPnL = 0;
    console.log('🔄 Daily arbitrage counters reset');
  }
}

// Export singleton instance
export const multiExchangeArbitrage = new MultiExchangeArbitrage();

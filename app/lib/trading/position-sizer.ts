import { EventEmitter } from 'events';

export interface PositionSizingConfig {
  initialAllocation: number; // percentage of total wealth
  confidenceScaling: boolean;
  maxPositionSize: number; // percentage of total wealth
  stopLoss: number; // percentage
  takeProfit: number; // percentage
  riskPerTrade: number; // percentage of total wealth
  maxDailyLoss: number; // percentage of total wealth
}

export interface PositionSizeResult {
  recommendedSize: number;
  dollarAmount: number;
  confidence: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  reasoning: string;
  stopLossPrice: number;
  takeProfitPrice: number;
  maxLoss: number;
  maxGain: number;
  positionPercent: number;
  warnings: string[];
}

export interface ConfidenceMetrics {
  technicalScore: number; // 0-100
  fundamentalScore: number; // 0-100
  marketConditionScore: number; // 0-100
  historicalPerformanceScore: number; // 0-100
  riskAssessmentScore: number; // 0-100
}

export class PositionSizer extends EventEmitter {
  private config: PositionSizingConfig;
  private totalWealth: number;
  private currentPositions: Map<string, any> = new Map();
  private dailyPnL: number = 0;
  private tradeHistory: any[] = [];

  constructor(totalWealth: number = 7716.23) {
    super();
    
    this.totalWealth = totalWealth;
    
    this.config = {
      initialAllocation: 10, // 10% of total wealth
      confidenceScaling: true,
      maxPositionSize: 25, // 25% of total wealth
      stopLoss: 2, // 2% stop loss
      takeProfit: 5, // 5% take profit
      riskPerTrade: 1, // 1% of total wealth risk per trade
      maxDailyLoss: 2 // 2% of total wealth max daily loss
    };
  }

  // Calculate position size based on confidence and risk
  calculatePositionSize(
    symbol: string,
    currentPrice: number,
    confidence: ConfidenceMetrics,
    marketCondition: 'bullish' | 'bearish' | 'sideways' | 'volatile'
  ): PositionSizeResult {
    
    // Calculate overall confidence score
    const overallConfidence = this.calculateOverallConfidence(confidence, marketCondition);
    
    // Check daily loss limits
    const dailyLossLimit = this.totalWealth * (this.config.maxDailyLoss / 100);
    if (Math.abs(this.dailyPnL) >= dailyLossLimit) {
      return this.createZeroPositionResult(
        'Daily loss limit reached',
        ['Daily loss limit exceeded - no new positions allowed']
      );
    }

    // Check if we already have a position in this symbol
    const existingPosition = this.currentPositions.get(symbol);
    if (existingPosition) {
      return this.createZeroPositionResult(
        'Position already exists',
        [`Already holding ${existingPosition.quantity} ${symbol}`]
      );
    }

    // Calculate base position size
    let basePositionPercent = this.config.initialAllocation;
    
    // Apply confidence scaling
    if (this.config.confidenceScaling) {
      basePositionPercent = this.applyConfidenceScaling(basePositionPercent, overallConfidence);
    }

    // Apply market condition adjustments
    basePositionPercent = this.applyMarketConditionAdjustment(basePositionPercent, marketCondition);

    // Ensure we don't exceed maximum position size
    basePositionPercent = Math.min(basePositionPercent, this.config.maxPositionSize);

    // Calculate dollar amount
    const dollarAmount = this.totalWealth * (basePositionPercent / 100);
    const recommendedSize = dollarAmount / currentPrice;

    // Calculate stop loss and take profit prices
    const stopLossPrice = currentPrice * (1 - this.config.stopLoss / 100);
    const takeProfitPrice = currentPrice * (1 + this.config.takeProfit / 100);

    // Calculate potential loss and gain
    const maxLoss = dollarAmount * (this.config.stopLoss / 100);
    const maxGain = dollarAmount * (this.config.takeProfit / 100);

    // Determine risk level
    const riskLevel = this.determineRiskLevel(overallConfidence, basePositionPercent, maxLoss);

    // Generate warnings
    const warnings = this.generateWarnings(overallConfidence, basePositionPercent, maxLoss);

    // Generate reasoning
    const reasoning = this.generateReasoning(overallConfidence, basePositionPercent, marketCondition);

    const result: PositionSizeResult = {
      recommendedSize,
      dollarAmount,
      confidence: overallConfidence,
      riskLevel,
      reasoning,
      stopLossPrice,
      takeProfitPrice,
      maxLoss,
      maxGain,
      positionPercent: basePositionPercent,
      warnings
    };

    // Log the position sizing decision
    this.logPositionDecision(symbol, currentPrice, result, confidence);

    this.emit('positionCalculated', { symbol, result });

    return result;
  }

  // Update position tracking
  updatePosition(symbol: string, quantity: number, price: number, side: 'buy' | 'sell'): void {
    const existingPosition = this.currentPositions.get(symbol) || { quantity: 0, avgPrice: 0 };
    
    if (side === 'buy') {
      const totalQuantity = existingPosition.quantity + quantity;
      const totalValue = (existingPosition.quantity * existingPosition.avgPrice) + (quantity * price);
      const newAvgPrice = totalQuantity > 0 ? totalValue / totalQuantity : price;
      
      this.currentPositions.set(symbol, {
        quantity: totalQuantity,
        avgPrice: newAvgPrice,
        lastUpdate: new Date().toISOString()
      });
    } else {
      const newQuantity = existingPosition.quantity - quantity;
      if (newQuantity <= 0) {
        this.currentPositions.delete(symbol);
      } else {
        this.currentPositions.set(symbol, {
          quantity: newQuantity,
          avgPrice: existingPosition.avgPrice,
          lastUpdate: new Date().toISOString()
        });
      }
    }

    // Update daily P&L
    this.updateDailyPnL(symbol, quantity, price, side, existingPosition.avgPrice);
  }

  // Get current portfolio allocation
  getPortfolioAllocation(): {
    totalValue: number;
    positions: Array<{
      symbol: string;
      quantity: number;
      avgPrice: number;
      currentValue: number;
      percentOfPortfolio: number;
      unrealizedPnL: number;
    }>;
    availableCash: number;
    totalAllocated: number;
  } {
    const positions = Array.from(this.currentPositions.entries()).map(([symbol, position]) => {
      // Simulate current price (in real system, this would come from market data)
      const currentPrice = this.getCurrentPrice(symbol);
      const currentValue = position.quantity * currentPrice;
      const unrealizedPnL = currentValue - (position.quantity * position.avgPrice);
      
      return {
        symbol,
        quantity: position.quantity,
        avgPrice: position.avgPrice,
        currentValue,
        percentOfPortfolio: (currentValue / this.totalWealth) * 100,
        unrealizedPnL
      };
    });

    const totalAllocated = positions.reduce((sum, pos) => sum + pos.currentValue, 0);
    const availableCash = this.totalWealth - totalAllocated;

    return {
      totalValue: this.totalWealth,
      positions,
      availableCash,
      totalAllocated
    };
  }

  private calculateOverallConfidence(confidence: ConfidenceMetrics, marketCondition: string): number {
    // Weighted average of confidence metrics
    const weights = {
      technicalScore: 0.25,
      fundamentalScore: 0.20,
      marketConditionScore: 0.20,
      historicalPerformanceScore: 0.15,
      riskAssessmentScore: 0.20
    };

    let weightedSum = 0;
    let totalWeight = 0;

    Object.entries(weights).forEach(([key, weight]) => {
      const score = confidence[key as keyof ConfidenceMetrics];
      if (score !== undefined) {
        weightedSum += score * weight;
        totalWeight += weight;
      }
    });

    let overallConfidence = totalWeight > 0 ? weightedSum / totalWeight : 0;

    // Apply market condition adjustment
    switch (marketCondition) {
      case 'bullish':
        overallConfidence *= 1.1; // Boost confidence in bullish markets
        break;
      case 'bearish':
        overallConfidence *= 0.9; // Reduce confidence in bearish markets
        break;
      case 'volatile':
        overallConfidence *= 0.8; // Significantly reduce confidence in volatile markets
        break;
      case 'sideways':
        overallConfidence *= 0.95; // Slightly reduce confidence in sideways markets
        break;
    }

    return Math.max(0, Math.min(100, overallConfidence));
  }

  private applyConfidenceScaling(basePercent: number, confidence: number): number {
    // Scale position size based on confidence (50-100% confidence range)
    if (confidence < 50) {
      return basePercent * 0.5; // Reduce position size for low confidence
    } else if (confidence < 70) {
      return basePercent * 0.75; // Slightly reduce for medium confidence
    } else if (confidence < 85) {
      return basePercent; // Normal size for good confidence
    } else {
      return basePercent * 1.25; // Increase size for high confidence (up to max)
    }
  }

  private applyMarketConditionAdjustment(basePercent: number, marketCondition: string): number {
    switch (marketCondition) {
      case 'bullish':
        return basePercent * 1.1; // Slightly increase in bullish markets
      case 'bearish':
        return basePercent * 0.7; // Reduce in bearish markets
      case 'volatile':
        return basePercent * 0.6; // Significantly reduce in volatile markets
      case 'sideways':
        return basePercent * 0.9; // Slightly reduce in sideways markets
      default:
        return basePercent;
    }
  }

  private determineRiskLevel(confidence: number, positionPercent: number, maxLoss: number): 'low' | 'medium' | 'high' | 'critical' {
    const riskScore = (100 - confidence) + (positionPercent * 2) + (maxLoss / this.totalWealth * 100);
    
    if (riskScore < 30) return 'low';
    if (riskScore < 50) return 'medium';
    if (riskScore < 70) return 'high';
    return 'critical';
  }

  private generateWarnings(confidence: number, positionPercent: number, maxLoss: number): string[] {
    const warnings: string[] = [];

    if (confidence < 60) {
      warnings.push('Low confidence trade - consider reducing position size');
    }

    if (positionPercent > this.config.maxPositionSize * 0.8) {
      warnings.push('Large position size - approaching maximum allocation');
    }

    if (maxLoss > this.totalWealth * 0.02) {
      warnings.push('High potential loss - exceeds 2% of total wealth');
    }

    if (Math.abs(this.dailyPnL) > this.totalWealth * 0.01) {
      warnings.push('Significant daily P&L movement - monitor closely');
    }

    return warnings;
  }

  private generateReasoning(confidence: number, positionPercent: number, marketCondition: string): string {
    const reasoning: string[] = [];

    reasoning.push(`Confidence level: ${confidence.toFixed(1)}%`);
    reasoning.push(`Position size: ${positionPercent.toFixed(1)}% of total wealth`);
    reasoning.push(`Market condition: ${marketCondition}`);

    if (confidence >= 80) {
      reasoning.push('High confidence trade - optimal position size applied');
    } else if (confidence >= 60) {
      reasoning.push('Moderate confidence - standard position sizing');
    } else {
      reasoning.push('Low confidence - reduced position size for risk management');
    }

    return reasoning.join('; ');
  }

  private createZeroPositionResult(reason: string, warnings: string[]): PositionSizeResult {
    return {
      recommendedSize: 0,
      dollarAmount: 0,
      confidence: 0,
      riskLevel: 'critical',
      reasoning: reason,
      stopLossPrice: 0,
      takeProfitPrice: 0,
      maxLoss: 0,
      maxGain: 0,
      positionPercent: 0,
      warnings
    };
  }

  private getCurrentPrice(symbol: string): number {
    // Simulate current prices (in real system, this would come from market data)
    const prices: { [key: string]: number } = {
      'BTC': 95000,
      'ETH': 3200,
      'XRP': 0.65,
      'ADA': 0.45,
      'SOL': 180
    };
    
    return prices[symbol] || 100;
  }

  private updateDailyPnL(symbol: string, quantity: number, price: number, side: 'buy' | 'sell', avgPrice: number): void {
    if (side === 'sell') {
      const pnl = (price - avgPrice) * quantity;
      this.dailyPnL += pnl;
    }
  }

  private logPositionDecision(symbol: string, price: number, result: PositionSizeResult, confidence: ConfidenceMetrics): void {
    const logEntry = {
      timestamp: new Date().toISOString(),
      symbol,
      price,
      result,
      confidence,
      totalWealth: this.totalWealth,
      dailyPnL: this.dailyPnL
    };

    this.tradeHistory.push(logEntry);
    
    // Keep only last 1000 entries
    if (this.tradeHistory.length > 1000) {
      this.tradeHistory = this.tradeHistory.slice(-1000);
    }

    console.log(`📊 Position sizing for ${symbol}: ${result.positionPercent.toFixed(1)}% ($${result.dollarAmount.toFixed(2)}) - ${result.riskLevel} risk`);
  }

  // Reset daily P&L (call at start of new trading day)
  resetDailyPnL(): void {
    this.dailyPnL = 0;
    console.log('🔄 Daily P&L reset');
  }

  // Update total wealth
  updateTotalWealth(newWealth: number): void {
    this.totalWealth = newWealth;
    console.log(`💰 Total wealth updated to $${newWealth.toFixed(2)}`);
  }

  // Get position sizing statistics
  getStats(): {
    totalWealth: number;
    dailyPnL: number;
    totalPositions: number;
    totalAllocated: number;
    availableCash: number;
    averageConfidence: number;
    totalTrades: number;
  } {
    const allocation = this.getPortfolioAllocation();
    const averageConfidence = this.tradeHistory.length > 0 
      ? this.tradeHistory.reduce((sum, trade) => sum + trade.result.confidence, 0) / this.tradeHistory.length
      : 0;

    return {
      totalWealth: this.totalWealth,
      dailyPnL: this.dailyPnL,
      totalPositions: this.currentPositions.size,
      totalAllocated: allocation.totalAllocated,
      availableCash: allocation.availableCash,
      averageConfidence,
      totalTrades: this.tradeHistory.length
    };
  }

  // Update configuration
  updateConfig(newConfig: Partial<PositionSizingConfig>): void {
    this.config = { ...this.config, ...newConfig };
    console.log('⚙️ Position sizing configuration updated:', newConfig);
  }

  // Get current configuration
  getConfig(): PositionSizingConfig {
    return { ...this.config };
  }
}

// Export singleton instance
export const positionSizer = new PositionSizer();

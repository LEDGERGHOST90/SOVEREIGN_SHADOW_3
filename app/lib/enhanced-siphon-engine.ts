
/**
 * 💎 ENHANCED HYBRID AI SIPHON LOGIC - REAL-TIME ENGINE  
 * Advanced wealth preservation with real-time profit tracking and fee optimization
 */

import { prisma } from './db';
import { ShadowAI } from './shadow-ai';
import { BinanceClient } from './binance';
import cron from 'node-cron';

// Initialize Binance US client with real credentials
const binanceClient = new BinanceClient({
  apiKey: process.env.BINANCE_US_API_KEY!,
  apiSecret: process.env.BINANCE_US_SECRET_KEY!
});

// Import base interfaces
interface SiphonConfig {
  thresholdAmount: number;
  baseSiphonRatio: number;
  baseRetentionRatio: number;
  volatilityAdjustment: number;
  userId: string;
}

interface SiphonResult {
  triggered: boolean;
  profitAmount: number;
  siphonedAmount: number;
  retainedAmount: number;
  adjustedSiphonRatio: number;
  volatilityFactor: number;
  reasoning: {
    sage: string;
    tactical: string;
  };
}

export interface EnhancedSiphonConfig extends SiphonConfig {
  realTimeTracking: boolean;
  feeOptimization: boolean;
  autoTrigger: boolean;
  minProfitThreshold: number;
  maxHotRetention: number;
  emergencyVaultRatio: number;
}

export interface RealTimePortfolioData {
  totalValue: number;
  totalProfit: number;
  unrealizedPnL: number;
  realizedPnL: number;
  positions: PortfolioPosition[];
  lastUpdated: Date;
}

export interface PortfolioPosition {
  asset: string;
  symbol: string;
  quantity: number;
  avgPrice: number;
  currentPrice: number;
  unrealizedPnL: number;
  realizedPnL: number;
  percentChange: number;
}

export interface FeeOptimization {
  tradingFees: number;
  gasFees: number;
  bridgeFees: number;
  totalFeesSaved: number;
  feeStrategy: 'MAKER' | 'TAKER' | 'HYBRID';
  optimalTiming: Date;
}

export class EnhancedHybridSiphonEngine {
  private shadowAI: ShadowAI;
  private binanceClient: BinanceClient;
  private realTimeInterval: NodeJS.Timeout | null = null;
  private websocketConnection: WebSocket | null = null;
  
  constructor() {
    this.shadowAI = new ShadowAI();
    this.binanceClient = new BinanceClient({
      apiKey: process.env.BINANCE_US_API_KEY!,
      apiSecret: process.env.BINANCE_US_SECRET_KEY!
    });
    
    this.initializeCronJobs();
  }

  /**
   * ENHANCED REAL-TIME SIPHON EXECUTION
   * Monitors portfolio and executes intelligent siphoning based on real-time data
   */
  async executeEnhancedSiphon(
    userId: string,
    config: EnhancedSiphonConfig
  ): Promise<SiphonResult & { feeOptimization: FeeOptimization; realTimeData: RealTimePortfolioData }> {
    
    // 1. Get real-time portfolio data
    const portfolioData = await this.getRealTimePortfolioData(userId);
    
    // 2. Calculate fee optimizations
    const feeOptimization = await this.calculateFeeOptimization(portfolioData);
    
    // 3. Get Shadow.AI enhanced market intelligence
    const marketIntel = await this.shadowAI.getMarketIntelligence();
    
    // 4. Determine optimal siphon strategy
    const siphonStrategy = await this.determineOptimalSiphonStrategy(
      portfolioData,
      marketIntel,
      feeOptimization,
      config
    );
    
    // 5. Execute siphon if triggered
    let siphonResult: SiphonResult;
    
    if (siphonStrategy.shouldExecute) {
      siphonResult = await this.executePrecisionSiphon(
        portfolioData.totalProfit,
        siphonStrategy,
        config,
        userId
      );
      
      // 6. Log enhanced siphon execution
      await this.logEnhancedSiphonExecution(userId, {
        portfolioData,
        feeOptimization,
        siphonResult,
        strategy: siphonStrategy
      });
      
    } else {
      siphonResult = {
        triggered: false,
        profitAmount: portfolioData.totalProfit,
        siphonedAmount: 0,
        retainedAmount: portfolioData.totalProfit,
        adjustedSiphonRatio: config.baseSiphonRatio,
        volatilityFactor: 1.0,
        reasoning: {
          sage: "The river flows steady, but the dam awaits the perfect moment. Patience sharpens the blade of wisdom.",
          tactical: `Conditions not optimal for siphon. Profit: $${portfolioData.totalProfit.toFixed(2)}, Market: ${marketIntel.volatilityRegime}`
        }
      };
    }
    
    return {
      ...siphonResult,
      feeOptimization,
      realTimeData: portfolioData
    };
  }

  /**
   * REAL-TIME PORTFOLIO DATA AGGREGATION
   * Combines data from all exchanges and wallets for complete picture
   */
  async getRealTimePortfolioData(userId: string): Promise<RealTimePortfolioData> {
    try {
      // 1. Get Binance US account data
      const binanceAccount = await this.binanceClient.getAccountInfo();
      const binancePrices = await this.binanceClient.get24hrTicker();
      
      // 2. Get stored portfolio data
      const storedPortfolio = await prisma.portfolio.findMany({
        where: { userId },
        include: { trades: { take: 100, orderBy: { createdAt: 'desc' } } }
      });
      
      // 3. Calculate positions and P&L
      const positions: PortfolioPosition[] = [];
      let totalValue = 0;
      let totalRealizedPnL = 0;
      let totalUnrealizedPnL = 0;
      
      for (const asset of storedPortfolio) {
        const binanceBalance = binanceAccount.balances.find((b: any) => b.asset === asset.asset);
        const priceData = Array.isArray(binancePrices) 
          ? binancePrices.find((p: any) => p.symbol === `${asset.asset}USDT`)
          : binancePrices.symbol === `${asset.asset}USDT` ? binancePrices : null;
        
        const currentPrice = priceData ? parseFloat(priceData.lastPrice) : asset.currentPrice;
        const quantity = binanceBalance 
          ? parseFloat(binanceBalance.free) + parseFloat(binanceBalance.locked)
          : Number(asset.hotBalance) + Number(asset.coldBalance);
        
        const unrealizedPnL = (Number(currentPrice) - Number(asset.averagePrice)) * quantity;
        const realizedPnL = asset.trades.reduce((sum: number, trade: any) => 
          sum + (trade.type === 'SELL' ? trade.profit || 0 : 0), 0
        );
        
        if (quantity > 0) {
          positions.push({
            asset: asset.asset,
            symbol: `${asset.asset}USDT`,
            quantity,
            avgPrice: Number(asset.averagePrice),
            currentPrice: Number(currentPrice),
            unrealizedPnL,
            realizedPnL,
            percentChange: ((Number(currentPrice) - Number(asset.averagePrice)) / Number(asset.averagePrice)) * 100
          });
          
          totalValue += quantity * Number(currentPrice);
          totalRealizedPnL += realizedPnL;
          totalUnrealizedPnL += unrealizedPnL;
        }
      }
      
      return {
        totalValue,
        totalProfit: Number(totalRealizedPnL) + Number(totalUnrealizedPnL),
        unrealizedPnL: totalUnrealizedPnL,
        realizedPnL: totalRealizedPnL,
        positions,
        lastUpdated: new Date()
      };
      
    } catch (error) {
      console.error('Real-time portfolio data error:', error);
      throw new Error('Failed to fetch real-time portfolio data');
    }
  }

  /**
   * ADVANCED FEE OPTIMIZATION CALCULATOR
   * Analyzes trading patterns and optimizes fee structures
   */
  async calculateFeeOptimization(portfolioData: RealTimePortfolioData): Promise<FeeOptimization> {
    try {
      // 1. Get trading volume for fee tier calculation
      const last30DaysTrades = await prisma.trade.findMany({
        where: {
          createdAt: {
            gte: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)
          }
        }
      });
      
      const totalVolume30Days = last30DaysTrades.reduce((sum, trade) => 
        sum + (Number(trade.quantity) * Number(trade.price)), 0
      );
      
      // 2. Calculate fee savings based on volume
      const baseFeeRate = 0.001; // 0.1%
      const vipFeeRate = totalVolume30Days > 100000 ? 0.0006 : // VIP 1
                        totalVolume30Days > 50000 ? 0.0008 :   // Regular+ 
                        baseFeeRate; // Base
      
      const tradingFees = totalVolume30Days * vipFeeRate;
      const potentialSavings = totalVolume30Days * (baseFeeRate - vipFeeRate);
      
      // 3. Calculate optimal trading strategy
      const feeStrategy: 'MAKER' | 'TAKER' | 'HYBRID' = 
        totalVolume30Days > 50000 ? 'MAKER' : // Use maker orders for large volume
        portfolioData.totalValue > 100000 ? 'HYBRID' : // Mixed strategy for large portfolios
        'TAKER'; // Simple market orders for small accounts
      
      // 4. Determine optimal timing for trades (low network congestion)
      const optimalTiming = new Date();
      optimalTiming.setHours(6, 0, 0, 0); // 6 AM UTC typically has lower fees
      
      return {
        tradingFees,
        gasFees: 0, // Not applicable for centralized exchange
        bridgeFees: 0, // Calculate if cross-chain operations needed
        totalFeesSaved: potentialSavings,
        feeStrategy,
        optimalTiming
      };
      
    } catch (error) {
      console.error('Fee optimization calculation error:', error);
      return {
        tradingFees: 0,
        gasFees: 0,
        bridgeFees: 0,
        totalFeesSaved: 0,
        feeStrategy: 'TAKER',
        optimalTiming: new Date()
      };
    }
  }

  /**
   * INTELLIGENT SIPHON STRATEGY DETERMINATION
   * Uses AI and market data to determine optimal siphon execution
   */
  async determineOptimalSiphonStrategy(
    portfolioData: RealTimePortfolioData,
    marketIntel: any,
    feeOptimization: FeeOptimization,
    config: EnhancedSiphonConfig
  ): Promise<{ shouldExecute: boolean; reason: string; urgency: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' }> {
    
    // 1. Check profit thresholds
    if (portfolioData.realizedPnL < config.thresholdAmount) {
      return {
        shouldExecute: false,
        reason: `Realized profit $${portfolioData.realizedPnL.toFixed(2)} below threshold $${config.thresholdAmount}`,
        urgency: 'LOW'
      };
    }
    
    // 2. Analyze market conditions
    let urgencyScore = 0;
    
    if (marketIntel.volatilityRegime === 'HIGH' || marketIntel.volatilityRegime === 'EXTREME') {
      urgencyScore += 2; // Higher urgency in volatile markets
    }
    
    if (marketIntel.riskSignals.level === 'ORANGE' || marketIntel.riskSignals.level === 'RED') {
      urgencyScore += 3; // High urgency if risk signals elevated
    }
    
    if (portfolioData.unrealizedPnL < 0 && Math.abs(portfolioData.unrealizedPnL) > portfolioData.realizedPnL * 0.3) {
      urgencyScore += 2; // Unrealized losses threaten realized gains
    }
    
    // 3. Check if hot balance is getting too large
    const hotBalance = portfolioData.totalValue - (portfolioData.totalValue * 0.3); // Assuming 30% in cold storage
    if (hotBalance > config.maxHotRetention) {
      urgencyScore += 1;
    }
    
    // 4. Determine execution decision and urgency
    const urgency: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' = 
      urgencyScore >= 5 ? 'CRITICAL' :
      urgencyScore >= 3 ? 'HIGH' :
      urgencyScore >= 1 ? 'MEDIUM' : 'LOW';
    
    const shouldExecute = config.autoTrigger && (urgency === 'HIGH' || urgency === 'CRITICAL');
    
    return {
      shouldExecute,
      reason: `Market conditions: ${marketIntel.volatilityRegime}, Risk: ${marketIntel.riskSignals.level}, Urgency: ${urgency}`,
      urgency
    };
  }

  /**
   * PRECISION SIPHON EXECUTION
   * Enhanced siphon with intelligent timing and fee optimization
   */
  async executePrecisionSiphon(
    profitAmount: number,
    strategy: any,
    config: EnhancedSiphonConfig,
    userId: string
  ): Promise<SiphonResult> {
    
    // Use emergency vault ratio if urgency is critical
    const siphonRatio = strategy.urgency === 'CRITICAL' 
      ? config.emergencyVaultRatio 
      : config.baseSiphonRatio;
    
    const siphonedAmount = profitAmount * siphonRatio;
    const retainedAmount = profitAmount - siphonedAmount;
    
    const reasoning = {
      sage: strategy.urgency === 'CRITICAL'
        ? `⚡ The storm approaches - emergency protocols engaged. $${siphonedAmount.toFixed(2)} secured in the fortress of time, while $${retainedAmount.toFixed(2)} stands guard against the chaos.`
        : `🎯 Precision strikes true. $${siphonedAmount.toFixed(2)} flows to the eternal vault as $${retainedAmount.toFixed(2)} fuels the engine of opportunity. Balance achieved.`,
      tactical: `Enhanced siphon: ${(siphonRatio * 100).toFixed(1)}% secured ($${siphonedAmount.toFixed(2)}). Strategy: ${strategy.urgency} urgency, optimized for ${strategy.reason}`
    };
    
    return {
      triggered: true,
      profitAmount,
      siphonedAmount,
      retainedAmount,
      adjustedSiphonRatio: siphonRatio,
      volatilityFactor: 1.0,
      reasoning
    };
  }

  /**
   * ENHANCED LOGGING WITH ANALYTICS
   */
  async logEnhancedSiphonExecution(userId: string, data: any): Promise<void> {
    try {
      // Standard siphon log
      await prisma.vaultLog.create({
        data: {
          userId,
          asset: 'USD_PROFIT',
          amount: data.siphonResult.siphonedAmount,
          type: 'SIPHON',
          fromWallet: 'hot',
          toWallet: 'cold',
          status: 'COMPLETED',
          completedAt: new Date()
        }
      });
      
      // Enhanced analytics log
      await prisma.siphonAnalytics.create({
        data: {
          userId,
          executionDate: new Date(),
          totalPortfolioValue: data.portfolioData.totalValue,
          realizedPnL: data.portfolioData.realizedPnL,
          unrealizedPnL: data.portfolioData.unrealizedPnL,
          siphonedAmount: data.siphonResult.siphonedAmount,
          retainedAmount: data.siphonResult.retainedAmount,
          siphonRatio: data.siphonResult.siphonedAmount / data.portfolioData.totalValue, // Add required field
          feesSaved: data.feeOptimization.totalFeesSaved,
          urgencyLevel: data.strategy.urgency,
          marketConditions: data.strategy.reason
        }
      });
      
    } catch (error) {
      console.error('Enhanced logging failed:', error);
    }
  }

  /**
   * INITIALIZE CRON JOBS FOR AUTOMATED MONITORING
   */
  initializeCronJobs(): void {
    // Monitor every 15 minutes for siphon opportunities
    cron.schedule('*/15 * * * *', async () => {
      try {
        const users = await prisma.user.findMany({
          include: { settings: true }
        });
        
        for (const user of users) {
          const config = await EnhancedHybridSiphonEngine.getEnhancedConfig(user.id);
          if (config.autoTrigger) {
            await this.executeEnhancedSiphon(user.id, config);
          }
        }
      } catch (error) {
        console.error('Automated siphon monitoring error:', error);
      }
    });
  }

  /**
   * GET ENHANCED CONFIGURATION
   */
  static async getEnhancedConfig(userId: string): Promise<EnhancedSiphonConfig> {
    const settings = await prisma.userSettings.findFirst({
      where: { userId }
    });

    return {
      thresholdAmount: settings?.siphonThreshold ? Number(settings.siphonThreshold) : 3500,
      baseSiphonRatio: settings?.siphonRatio ? Number(settings.siphonRatio) : 0.30,
      baseRetentionRatio: settings?.retentionRatio ? Number(settings.retentionRatio) : 0.70,
      volatilityAdjustment: settings?.volatilityAdjustment ? Number(settings.volatilityAdjustment) : 0.10,
      userId,
      realTimeTracking: true,
      feeOptimization: true,
      autoTrigger: settings?.autoSiphon || false,
      minProfitThreshold: 1000,
      maxHotRetention: 50000,
      emergencyVaultRatio: 0.80 // 80% to vault in emergency
    };
  }
}

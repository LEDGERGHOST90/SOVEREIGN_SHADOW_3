
/**
 * 💎 HYBRID AI SIPHON LOGIC - CORE ENGINE
 * The sovereign discipline that preserves wealth while keeping hot capital alive
 */

import { prisma } from './db';
import { ShadowAI } from './shadow-ai';

export interface SiphonConfig {
  thresholdAmount: number;      // Default: $3,500
  baseSiphonRatio: number;      // Default: 0.30 (30% to vault)
  baseRetentionRatio: number;   // Default: 0.70 (70% retained hot)
  volatilityAdjustment: number; // ±10% based on market conditions
  userId: string;
}

export interface SiphonResult {
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

export class HybridSiphonEngine {
  private shadowAI: ShadowAI;

  constructor() {
    this.shadowAI = new ShadowAI();
  }

  /**
   * CORE HYBRID SIPHON LOGIC
   * Executes the discipline that builds sovereign wealth
   */
  async executeSiphon(
    realizedProfit: number,
    config: SiphonConfig
  ): Promise<SiphonResult> {
    // 1. Check threshold trigger
    const thresholdMet = realizedProfit >= config.thresholdAmount;
    
    if (!thresholdMet) {
      return {
        triggered: false,
        profitAmount: realizedProfit,
        siphonedAmount: 0,
        retainedAmount: realizedProfit,
        adjustedSiphonRatio: config.baseSiphonRatio,
        volatilityFactor: 1.0,
        reasoning: {
          sage: "The seed has not yet grown to harvest. Patience builds the foundation of empire.",
          tactical: `Profit $${realizedProfit.toFixed(2)} below threshold $${config.thresholdAmount}. No siphon triggered.`
        }
      };
    }

    // 2. Get volatility adjustment from Shadow.AI
    const marketIntelligence = await this.shadowAI.getMarketIntelligence();
    const volatilityFactor = this.calculateVolatilityAdjustment(
      marketIntelligence.volatilityRegime,
      config.volatilityAdjustment
    );

    // 3. Calculate dynamic ratios
    const adjustedSiphonRatio = Math.min(
      Math.max(config.baseSiphonRatio * volatilityFactor, 0.20), // Min 20%
      0.80 // Max 80%
    );
    
    const adjustedRetentionRatio = 1 - adjustedSiphonRatio;

    // 4. Execute hybrid calculation
    const siphonedAmount = realizedProfit * adjustedSiphonRatio;
    const retainedAmount = realizedProfit * adjustedRetentionRatio;

    // 5. Generate AI reasoning
    const reasoning = this.generateReasoning(
      realizedProfit,
      siphonedAmount,
      retainedAmount,
      adjustedSiphonRatio,
      marketIntelligence.volatilityRegime
    );

    // 6. Log the siphon execution
    await this.logSiphonExecution(config.userId, {
      profitAmount: realizedProfit,
      siphonedAmount,
      retainedAmount,
      volatilityFactor,
      marketConditions: marketIntelligence.volatilityRegime
    });

    return {
      triggered: true,
      profitAmount: realizedProfit,
      siphonedAmount,
      retainedAmount,
      adjustedSiphonRatio,
      volatilityFactor,
      reasoning
    };
  }

  /**
   * Calculate volatility-based adjustment factor
   */
  private calculateVolatilityAdjustment(
    volatilityRegime: 'LOW' | 'MEDIUM' | 'HIGH' | 'EXTREME',
    maxAdjustment: number
  ): number {
    switch (volatilityRegime) {
      case 'LOW':
        // Low volatility = more aggressive siphoning (less hot retention needed)
        return 1 + (maxAdjustment * 0.5); // +5% more to vault
      case 'MEDIUM':
        return 1.0; // Base ratios
      case 'HIGH':
        // High volatility = more hot retention needed
        return 1 - (maxAdjustment * 0.5); // -5% to vault, +5% hot retention
      case 'EXTREME':
        // Extreme volatility = maximum hot retention
        return 1 - maxAdjustment; // -10% to vault, +10% hot retention
      default:
        return 1.0;
    }
  }

  /**
   * Generate AI-powered reasoning for siphon decisions
   */
  private generateReasoning(
    profit: number,
    siphoned: number,
    retained: number,
    ratio: number,
    volatility: string
  ): { sage: string; tactical: string } {
    const sageMessages = [
      `Legacy strengthens as $${siphoned.toFixed(2)} flows to the vault, yet the furnace burns bright with $${retained.toFixed(2)} retained. Balance is the art of the sovereign.`,
      `The river of profit divides: $${siphoned.toFixed(2)} to the eternal vault, $${retained.toFixed(2)} to the living fire. Thus grows the empire that never sleeps.`,
      `Discipline carves prosperity from chaos. $${siphoned.toFixed(2)} preserved, $${retained.toFixed(2)} empowered. The cycle perpetuates itself.`,
      `As water finds its level, so wealth finds its purpose: $${siphoned.toFixed(2)} to safety, $${retained.toFixed(2)} to opportunity. The wheel turns onward.`
    ];

    const tacticalMessage = `Hybrid siphon executed: $${siphoned.toFixed(2)} preserved (${(ratio * 100).toFixed(1)}%), $${retained.toFixed(2)} hot retained. Ratio adjusted for ${volatility.toLowerCase()} volatility.`;

    const randomSage = sageMessages[Math.floor(Math.random() * sageMessages.length)];

    return {
      sage: randomSage,
      tactical: tacticalMessage
    };
  }

  /**
   * Log siphon execution to database
   */
  private async logSiphonExecution(
    userId: string,
    data: {
      profitAmount: number;
      siphonedAmount: number;
      retainedAmount: number;
      volatilityFactor: number;
      marketConditions: string;
    }
  ): Promise<void> {
    try {
      await prisma.vaultLog.create({
        data: {
          userId,
          asset: 'USD_PROFIT',
          amount: data.siphonedAmount,
          type: 'SIPHON',
          fromWallet: 'hot',
          toWallet: 'cold',
          status: 'COMPLETED',
          completedAt: new Date()
        }
      });

      // Create agent reflection for this siphon
      await prisma.agentReflection.create({
        data: {
          userId,
          content: `Hybrid siphon executed: $${data.profitAmount.toFixed(2)} profit → $${data.siphonedAmount.toFixed(2)} preserved, $${data.retainedAmount.toFixed(2)} retained. Volatility factor: ${data.volatilityFactor.toFixed(2)} (${data.marketConditions})`,
          mood: 'disciplined',
          tags: ['siphon', 'discipline', 'wealth-building', 'hybrid-logic']
        }
      });
    } catch (error) {
      console.error('Failed to log siphon execution:', error);
    }
  }

  /**
   * Get default siphon configuration for user
   */
  static async getDefaultConfig(userId: string): Promise<SiphonConfig> {
    const settings = await prisma.userSettings.findFirst({
      where: { userId }
    });

    return {
      thresholdAmount: settings?.siphonThreshold ? Number(settings.siphonThreshold) : 3500,
      baseSiphonRatio: settings?.siphonRatio ? Number(settings.siphonRatio) : 0.30, // 30% to vault
      baseRetentionRatio: settings?.retentionRatio ? Number(settings.retentionRatio) : 0.70, // 70% retained hot
      volatilityAdjustment: settings?.volatilityAdjustment ? Number(settings.volatilityAdjustment) : 0.10, // ±10% adjustment range
      userId
    };
  }
}

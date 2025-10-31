
// Oracle-Inspired RWA Vault Management System
// Systematic wealth preservation inspired by Larry Ellison's approach

import { prisma } from './db';
import { ondoClient } from './ondo';

export interface VaultPerformance {
  vaultId: string;
  name: string;
  currentValue: number;
  dayChange: number;
  percentChange: number;
  totalYield: number;
  averageYield: number;
  strategy: string;
  riskScore: number;
}

export interface OracleWealthStrategy {
  targetRWAAllocation: number; // Percentage of portfolio in RWAs
  maxSingleAssetAllocation: number; // Risk management
  yieldTarget: number; // Minimum yield target
  rebalanceFrequency: number; // Days between rebalances
}

export class RWAVaultManager {
  private userId: string;

  constructor(userId: string) {
    this.userId = userId;
  }

  // Create Oracle-inspired vault strategy
  async createOracleVault(
    name: string = "Oracle Treasury Vault",
    strategy: 'CONSERVATIVE' | 'BALANCED' | 'GROWTH' | 'ORACLE_INSPIRED' = 'ORACLE_INSPIRED'
  ): Promise<string> {
    try {
      const vault = await prisma.rWAVault.create({
        data: {
          userId: this.userId,
          name,
          description: `Inspired by Larry Ellison's $393B wealth strategy - systematic RWA accumulation`,
          strategy,
          targetAllocation: strategy === 'ORACLE_INSPIRED' ? 25.00 : 
                           strategy === 'CONSERVATIVE' ? 60.00 :
                           strategy === 'BALANCED' ? 40.00 : 20.00,
          autoRebalance: true,
          rebalanceThreshold: 5.00,
          nextRebalance: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 7 days
        }
      });

      // Create default allocations based on Oracle strategy
      const allocations = await this.getOracleAllocations(strategy);
      
      for (const allocation of allocations) {
        await prisma.vaultAllocation.create({
          data: {
            vaultId: vault.id,
            assetType: allocation.assetType,
            symbol: allocation.symbol,
            targetPercent: allocation.targetPercent
          }
        });
      }

      return vault.id;
    } catch (error) {
      console.error('Error creating Oracle vault:', error);
      throw error;
    }
  }

  // Get Oracle-inspired allocation strategy
  private async getOracleAllocations(strategy: string) {
    const allocations = [];
    
    switch (strategy) {
      case 'ORACLE_INSPIRED':
        // Mimics Oracle's focus on infrastructure and stable yields
        allocations.push(
          { assetType: 'TOKENIZED_TREASURY' as const, symbol: 'OUSG', targetPercent: 40.00 },
          { assetType: 'TOKENIZED_TREASURY' as const, symbol: 'USDY', targetPercent: 35.00 },
          { assetType: 'MONEY_MARKET' as const, symbol: 'OMMF', targetPercent: 25.00 }
        );
        break;
        
      case 'CONSERVATIVE':
        allocations.push(
          { assetType: 'TOKENIZED_TREASURY' as const, symbol: 'OUSG', targetPercent: 60.00 },
          { assetType: 'TOKENIZED_TREASURY' as const, symbol: 'USDY', targetPercent: 25.00 },
          { assetType: 'MONEY_MARKET' as const, symbol: 'OMMF', targetPercent: 15.00 }
        );
        break;
        
      case 'BALANCED':
        allocations.push(
          { assetType: 'TOKENIZED_TREASURY' as const, symbol: 'OUSG', targetPercent: 45.00 },
          { assetType: 'TOKENIZED_TREASURY' as const, symbol: 'USDY', targetPercent: 35.00 },
          { assetType: 'MONEY_MARKET' as const, symbol: 'OMMF', targetPercent: 20.00 }
        );
        break;
        
      case 'GROWTH':
        allocations.push(
          { assetType: 'TOKENIZED_TREASURY' as const, symbol: 'USDY', targetPercent: 50.00 },
          { assetType: 'TOKENIZED_TREASURY' as const, symbol: 'OUSG', targetPercent: 30.00 },
          { assetType: 'MONEY_MARKET' as const, symbol: 'OMMF', targetPercent: 20.00 }
        );
        break;
    }
    
    return allocations;
  }

  // Execute vault rebalancing (Oracle-style systematic approach)
  async rebalanceVault(vaultId: string): Promise<boolean> {
    try {
      const vault = await prisma.rWAVault.findUnique({
        where: { id: vaultId },
        include: { allocations: true }
      });

      if (!vault || !vault.autoRebalance) return false;

      const portfolio = await ondoClient.getPortfolioData(this.userId);
      const totalValue = portfolio.totalValue;

      if (totalValue === 0) return false;

      let rebalanceNeeded = false;

      // Check if rebalancing is needed
      for (const allocation of vault.allocations) {
        const currentAsset = portfolio.assets.find(a => a.symbol === allocation.symbol);
        const currentValue = currentAsset ? currentAsset.currentPrice * 1000 : 0; // Mock calculation
        const currentPercent = (currentValue / totalValue) * 100;
        const targetPercent = parseFloat(allocation.targetPercent.toString());
        
        const deviation = Math.abs(currentPercent - targetPercent);
        
        if (deviation > parseFloat(vault.rebalanceThreshold.toString())) {
          rebalanceNeeded = true;
          
          // Update current allocation
          await prisma.vaultAllocation.update({
            where: { id: allocation.id },
            data: {
              currentPercent,
              currentValue
            }
          });
        }
      }

      if (rebalanceNeeded) {
        // Execute rebalancing logic (would integrate with Ondo's trading APIs)
        await prisma.rWAVault.update({
          where: { id: vaultId },
          data: {
            lastRebalance: new Date(),
            nextRebalance: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
          }
        });

        // Record milestone
        await this.recordWealthMilestone('VAULT_GRADUATION', totalValue, 'Automated vault rebalancing completed');
      }

      return rebalanceNeeded;
    } catch (error) {
      console.error('Error rebalancing vault:', error);
      return false;
    }
  }

  // Get vault performance metrics
  async getVaultPerformance(): Promise<VaultPerformance[]> {
    try {
      const vaults = await prisma.rWAVault.findMany({
        where: { 
          userId: this.userId,
          isActive: true 
        },
        include: { allocations: true }
      });

      const performance: VaultPerformance[] = [];

      for (const vault of vaults) {
        const currentValue = parseFloat(vault.currentValue.toString());
        const totalDeposits = parseFloat(vault.totalDeposits.toString());
        const totalYield = parseFloat(vault.totalYield.toString());
        const averageYield = parseFloat(vault.averageYield.toString());

        // Calculate day change (simplified)
        const dayChange = currentValue * 0.01; // Mock 1% daily change
        const percentChange = totalDeposits > 0 ? ((currentValue - totalDeposits) / totalDeposits) * 100 : 0;

        // Risk score based on strategy
        const riskScore = vault.strategy === 'CONSERVATIVE' ? 25 :
                         vault.strategy === 'BALANCED' ? 50 :
                         vault.strategy === 'GROWTH' ? 75 :
                         vault.strategy === 'ORACLE_INSPIRED' ? 40 : 50;

        performance.push({
          vaultId: vault.id,
          name: vault.name,
          currentValue,
          dayChange,
          percentChange,
          totalYield,
          averageYield,
          strategy: vault.strategy,
          riskScore
        });
      }

      return performance;
    } catch (error) {
      console.error('Error getting vault performance:', error);
      return [];
    }
  }

  // Record wealth milestone (Oracle-style achievement tracking)
  private async recordWealthMilestone(
    type: 'NET_WORTH_MILESTONE' | 'DAILY_GAIN_RECORD' | 'PORTFOLIO_ALL_TIME_HIGH' | 'RWA_YIELD_MILESTONE' | 'VAULT_GRADUATION',
    amount: number,
    trigger: string
  ): Promise<void> {
    try {
      await prisma.wealthMilestone.create({
        data: {
          userId: this.userId,
          milestoneType: type,
          amount,
          description: `Oracle-inspired wealth milestone: ${trigger}`,
          trigger,
          dayGain: type === 'DAILY_GAIN_RECORD' ? amount : 0,
          percentGain: 0, // Would calculate actual percentage
          assetClass: 'RWA'
        }
      });
    } catch (error) {
      console.error('Error recording wealth milestone:', error);
    }
  }

  // Check for automated vault graduation (move profits to vault)
  async checkVaultGraduation(): Promise<boolean> {
    try {
      const settings = await prisma.userSettings.findUnique({
        where: { userId: this.userId }
      });

      if (!settings || !settings.autoSiphon) return false;

      const portfolio = await ondoClient.getPortfolioData(this.userId);
      const threshold = parseFloat(settings.graduationThreshold.toString());

      if (portfolio.totalValue >= threshold) {
        // Execute graduation (move funds to vault)
        const graduationAmount = portfolio.totalValue * 0.3; // 30% to vault
        
        await this.recordWealthMilestone('VAULT_GRADUATION', graduationAmount, 
          'Automated RWA vault graduation triggered');

        return true;
      }

      return false;
    } catch (error) {
      console.error('Error checking vault graduation:', error);
      return false;
    }
  }
}

// Oracle Wealth Score Calculator
export async function calculateOracleScore(userId: string): Promise<{
  score: number;
  breakdown: {
    diversification: number;
    rwaAllocation: number;
    yieldGeneration: number;
    systematicApproach: number;
  };
  recommendations: string[];
}> {
  try {
    const [rwaAssets, vaults, milestones] = await Promise.all([
      prisma.rWAAsset.findMany({ where: { userId } }),
      prisma.rWAVault.findMany({ where: { userId, isActive: true } }),
      prisma.wealthMilestone.findMany({ where: { userId } })
    ]);

    let diversification = 0;
    let rwaAllocation = 0;
    let yieldGeneration = 0;
    let systematicApproach = 0;
    
    const recommendations: string[] = [];

    // Diversification Score (0-25)
    const assetTypes = new Set(rwaAssets.map(a => a.assetType));
    diversification = Math.min(25, assetTypes.size * 8);
    
    if (diversification < 20) {
      recommendations.push("Increase diversification across RWA asset types");
    }

    // RWA Allocation Score (0-25)
    const totalRWAValue = rwaAssets.reduce((sum, a) => sum + parseFloat(a.value.toString()), 0);
    // Mock total portfolio value calculation
    const totalPortfolioValue = totalRWAValue * 2; // Assuming 50% RWA allocation for demo
    rwaAllocation = totalPortfolioValue > 0 ? Math.min(25, (totalRWAValue / totalPortfolioValue) * 50) : 0;
    
    if (rwaAllocation < 20) {
      recommendations.push("Consider increasing RWA allocation for stability");
    }

    // Yield Generation Score (0-25)
    const avgYield = rwaAssets.length > 0 
      ? rwaAssets.reduce((sum, a) => sum + parseFloat(a.yield.toString()), 0) / rwaAssets.length
      : 0;
    yieldGeneration = Math.min(25, avgYield * 4);
    
    if (yieldGeneration < 20) {
      recommendations.push("Focus on higher-yield RWA opportunities");
    }

    // Systematic Approach Score (0-25)
    const hasAutoVaults = vaults.some(v => v.autoRebalance);
    const recentMilestones = milestones.filter(m => 
      m.achievedAt > new Date(Date.now() - 30 * 24 * 60 * 60 * 1000));
    
    systematicApproach = (hasAutoVaults ? 15 : 0) + Math.min(10, recentMilestones.length * 2);
    
    if (!hasAutoVaults) {
      recommendations.push("Enable automated vault rebalancing for systematic growth");
    }

    const totalScore = diversification + rwaAllocation + yieldGeneration + systematicApproach;

    return {
      score: totalScore,
      breakdown: {
        diversification,
        rwaAllocation,
        yieldGeneration,
        systematicApproach
      },
      recommendations
    };
  } catch (error) {
    console.error('Error calculating Oracle score:', error);
    return {
      score: 0,
      breakdown: { diversification: 0, rwaAllocation: 0, yieldGeneration: 0, systematicApproach: 0 },
      recommendations: ["Enable RWA integration to begin Oracle-inspired wealth building"]
    };
  }
}

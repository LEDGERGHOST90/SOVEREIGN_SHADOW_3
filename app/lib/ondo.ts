
// Oracle-inspired RWA Integration - Ondo Finance
// Inspired by Larry Ellison's $393B wealth surge through systematic asset management

import axios from 'axios';
import { prisma } from './db';

export interface OndoAsset {
  symbol: string;
  name: string;
  type: 'TOKENIZED_TREASURY' | 'MONEY_MARKET' | 'TOKENIZED_STOCK';
  currentPrice: number;
  nav: number; // Net Asset Value
  yield: number;
  aum: number; // Assets Under Management
  chain: string;
  contractAddress: string;
}

export interface OndoPortfolio {
  totalValue: number;
  assets: OndoAsset[];
  dayChange: number;
  dayChangePercent: number;
}

// Core Ondo Finance Assets - Production Ready
export const ONDO_ASSETS: Record<string, OndoAsset> = {
  OUSG: {
    symbol: 'OUSG',
    name: 'Ondo Short-Term US Government Bond Fund',
    type: 'TOKENIZED_TREASURY',
    currentPrice: 105.23,
    nav: 105.23,
    yield: 5.15,
    aum: 200000000, // $200M AUM
    chain: 'ethereum',
    contractAddress: '0x1B19C19393e2d034D8Ff31ff34c81252FcBbee92'
  },
  USDY: {
    symbol: 'USDY',
    name: 'US Dollar Yield Token',
    type: 'TOKENIZED_TREASURY',
    currentPrice: 1.0521,
    nav: 1.0521,
    yield: 5.21,
    aum: 350000000, // $350M AUM
    chain: 'ethereum',
    contractAddress: '0x96F6eF951840721AdBF46Ac996b59E0235CB985C'
  },
  OMMF: {
    symbol: 'OMMF',
    name: 'Ondo Money Market Fund',
    type: 'MONEY_MARKET',
    currentPrice: 1.0235,
    nav: 1.0235,
    yield: 4.85,
    aum: 180000000, // $180M AUM
    chain: 'ethereum',
    contractAddress: '0x087D01d8F495fFA4a22cA2F46E3Bb2D40E5FD4a8'
  }
};

export class OndoFinanceClient {
  private apiKey?: string;
  private baseURL = 'https://api.ondo.finance/v1';

  constructor(apiKey?: string) {
    this.apiKey = apiKey || process.env.ONDO_API_KEY;
  }

  // Get real-time asset data (with fallback to mock data for demo)
  async getAssetData(symbol: string): Promise<OndoAsset | null> {
    try {
      if (!this.apiKey) {
        // Return mock data for demo purposes
        return ONDO_ASSETS[symbol] || null;
      }

      const response = await axios.get(`${this.baseURL}/assets/${symbol}`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        }
      });

      return response.data;
    } catch (error) {
      console.error(`Error fetching Ondo asset data for ${symbol}:`, error);
      // Fallback to static data
      return ONDO_ASSETS[symbol] || null;
    }
  }

  // Get portfolio overview
  async getPortfolioData(userId: string): Promise<OndoPortfolio> {
    try {
      // Fetch user's RWA assets from database
      const userRWAAssets = await prisma.rWAAsset.findMany({
        where: { userId }
      });

      const assets: OndoAsset[] = [];
      let totalValue = 0;
      let dayChange = 0;

      for (const asset of userRWAAssets) {
        const ondoAsset = await this.getAssetData(asset.symbol);
        if (ondoAsset) {
          assets.push(ondoAsset);
          const assetValue = parseFloat(asset.balance.toString()) * ondoAsset.currentPrice;
          totalValue += assetValue;
          dayChange += parseFloat(asset.dayChange.toString());
        }
      }

      const dayChangePercent = totalValue > 0 ? (dayChange / (totalValue - dayChange)) * 100 : 0;

      return {
        totalValue,
        assets,
        dayChange,
        dayChangePercent
      };
    } catch (error) {
      console.error('Error fetching Ondo portfolio data:', error);
      return {
        totalValue: 0,
        assets: [],
        dayChange: 0,
        dayChangePercent: 0
      };
    }
  }

  // Mint tokenized asset (simulated for demo)
  async mintAsset(userId: string, symbol: string, amount: number): Promise<string | null> {
    try {
      const asset = await this.getAssetData(symbol);
      if (!asset) throw new Error(`Asset ${symbol} not found`);

      // In production, this would interact with Ondo's smart contracts
      // For demo, we'll create a database record
      const value = amount * asset.currentPrice;

      await prisma.rWATransaction.create({
        data: {
          userId,
          rwaAssetId: (await this.ensureAssetExists(userId, symbol)).id,
          type: 'MINT',
          amount,
          price: asset.currentPrice,
          value,
          status: 'CONFIRMED',
          executedAt: new Date()
        }
      });

      // Update or create RWA asset holding
      await prisma.rWAAsset.upsert({
        where: {
          userId_symbol: { userId, symbol }
        },
        update: {
          balance: {
            increment: amount
          },
          value: {
            increment: value
          },
          lastUpdated: new Date()
        },
        create: {
          userId,
          assetType: asset.type,
          symbol,
          name: asset.name,
          balance: amount,
          value,
          yield: asset.yield,
          issuer: 'Ondo Finance',
          underlying: asset.type === 'TOKENIZED_TREASURY' ? 'US Treasuries' : 'Money Market'
        }
      });

      return `mint_${Date.now()}`;
    } catch (error) {
      console.error('Error minting Ondo asset:', error);
      return null;
    }
  }

  // Redeem tokenized asset
  async redeemAsset(userId: string, symbol: string, amount: number): Promise<string | null> {
    try {
      const asset = await this.getAssetData(symbol);
      if (!asset) throw new Error(`Asset ${symbol} not found`);

      const userAsset = await prisma.rWAAsset.findUnique({
        where: { userId_symbol: { userId, symbol } }
      });

      if (!userAsset || parseFloat(userAsset.balance.toString()) < amount) {
        throw new Error('Insufficient balance');
      }

      const value = amount * asset.currentPrice;

      await prisma.rWATransaction.create({
        data: {
          userId,
          rwaAssetId: userAsset.id,
          type: 'REDEEM',
          amount,
          price: asset.currentPrice,
          value: -value,
          status: 'CONFIRMED',
          executedAt: new Date()
        }
      });

      await prisma.rWAAsset.update({
        where: { id: userAsset.id },
        data: {
          balance: {
            decrement: amount
          },
          value: {
            decrement: value
          },
          lastUpdated: new Date()
        }
      });

      return `redeem_${Date.now()}`;
    } catch (error) {
      console.error('Error redeeming Ondo asset:', error);
      return null;
    }
  }

  private async ensureAssetExists(userId: string, symbol: string) {
    const asset = await this.getAssetData(symbol);
    if (!asset) throw new Error(`Asset ${symbol} not found`);

    return await prisma.rWAAsset.upsert({
      where: { userId_symbol: { userId, symbol } },
      update: {},
      create: {
        userId,
        assetType: asset.type,
        symbol,
        name: asset.name,
        balance: 0,
        value: 0,
        yield: asset.yield,
        issuer: 'Ondo Finance',
        underlying: asset.type === 'TOKENIZED_TREASURY' ? 'US Treasuries' : 'Money Market'
      }
    });
  }

  // Update all asset prices and yields (scheduled job)
  async updateAssetPrices(): Promise<void> {
    try {
      for (const [symbol, assetData] of Object.entries(ONDO_ASSETS)) {
        const latestData = await this.getAssetData(symbol);
        if (latestData) {
          // Update all user assets with latest pricing
          await prisma.rWAAsset.updateMany({
            where: { symbol },
            data: {
              yield: latestData.yield,
              lastUpdated: new Date()
            }
          });
        }
      }
    } catch (error) {
      console.error('Error updating Ondo asset prices:', error);
    }
  }
}

// Oracle Wealth Engine - Calculate wealth surge metrics
export async function calculateWealthSurge(userId: string): Promise<{
  netWorth: number;
  dayChange: number;
  percentChange: number;
  largestSingleDayGain: number;
  oracleInspiredScore: number; // 0-100 score based on Ellison's strategy
}> {
  try {
    const [cryptoAssets, rwaAssets, wealthMilestones] = await Promise.all([
      prisma.portfolio.findMany({ where: { userId } }),
      prisma.rWAAsset.findMany({ where: { userId } }),
      prisma.wealthMilestone.findMany({ 
        where: { userId },
        orderBy: { achievedAt: 'desc' }
      })
    ]);

    // Calculate crypto net worth
    const cryptoValue = cryptoAssets.reduce((total, asset) => 
      total + parseFloat(asset.totalInvested.toString()), 0);

    // Calculate RWA net worth
    const rwaValue = rwaAssets.reduce((total, asset) => 
      total + parseFloat(asset.value.toString()), 0);

    const netWorth = cryptoValue + rwaValue;

    // Calculate day changes
    const cryptoDayChange = 0; // Would calculate from price changes
    const rwaDayChange = rwaAssets.reduce((total, asset) => 
      total + parseFloat(asset.dayChange.toString()), 0);
    
    const dayChange = cryptoDayChange + rwaDayChange;
    const percentChange = netWorth > 0 ? (dayChange / (netWorth - dayChange)) * 100 : 0;

    // Find largest single-day gain
    const largestGain = wealthMilestones
      .filter(m => m.milestoneType === 'DAILY_GAIN_RECORD')
      .reduce((max, milestone) => 
        Math.max(max, parseFloat(milestone.dayGain.toString())), 0);

    // Oracle-inspired score (diversification, yield focus, systematic approach)
    let oracleScore = 0;
    
    // Diversification (40 points max)
    const assetCount = cryptoAssets.length + rwaAssets.length;
    oracleScore += Math.min(40, assetCount * 8);
    
    // RWA allocation (30 points max)
    const rwaAllocation = netWorth > 0 ? (rwaValue / netWorth) * 100 : 0;
    oracleScore += Math.min(30, rwaAllocation);
    
    // Yield generation (30 points max)
    const avgYield = rwaAssets.length > 0 
      ? rwaAssets.reduce((sum, a) => sum + parseFloat(a.yield.toString()), 0) / rwaAssets.length
      : 0;
    oracleScore += Math.min(30, avgYield * 6);

    return {
      netWorth,
      dayChange,
      percentChange,
      largestSingleDayGain: largestGain,
      oracleInspiredScore: Math.round(oracleScore)
    };
  } catch (error) {
    console.error('Error calculating wealth surge:', error);
    return {
      netWorth: 0,
      dayChange: 0,
      percentChange: 0,
      largestSingleDayGain: 0,
      oracleInspiredScore: 0
    };
  }
}

export const ondoClient = new OndoFinanceClient();

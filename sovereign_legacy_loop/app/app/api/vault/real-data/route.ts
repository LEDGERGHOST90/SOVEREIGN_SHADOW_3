export const dynamic = 'force-dynamic';

import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { prisma } from '@/lib/db';
import { TradeDataProcessor } from '@/lib/trade-data-processor';
import fs from 'fs';
import path from 'path';

interface PortfolioData {
  totalValue: number;
  hotWalletValue: number;
  coldVaultValue: number;
  assets: Array<{
    symbol: string;
    amount: number;
    usdValue: number;
    percentage: number;
  }>;
  recentActivity: Array<{
    id: string;
    asset: string;
    amount: number;
    type: string;
    fromWallet: string;
    toWallet: string;
    status: string;
    createdAt: string;
    completedAt?: string;
  }>;
}

// Use enhanced trade data processor

// Calculate vault allocation based on real data
function calculateVaultAllocation(totalValue: number, tradeData: any) {
  // Siphon logic: 75% stays hot for trading, 25% moves to cold vault
  const hotWalletValue = totalValue * 0.75;
  const coldVaultValue = totalValue * 0.25;
  
  return {
    hotWalletValue,
    coldVaultValue,
    siphonRatio: 0.25,
    lastSiphon: new Date().toISOString(),
    nextGraduation: Math.max(0, 1000 - (totalValue % 1000)) // Next $1000 milestone
  };
}

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Process real trade history using enhanced processor
    const csvPath = path.join(process.cwd(), 'data', '202509211751.csv');
    const tradeData = TradeDataProcessor.processCSVTradeHistory(csvPath);
    const analysis = TradeDataProcessor.analyzePortfolioPerformance(tradeData);
    
    // Use processed data
    const totalValue = tradeData.totalValue;
    
    // Calculate vault allocation
    const vaultAllocation = calculateVaultAllocation(totalValue, tradeData);
    
    // Convert asset breakdown to portfolio format
    const assets = Object.entries(tradeData.assetBreakdown)
      .filter(([symbol, data]) => data.usdValue > 0.01) // Filter out dust
      .map(([symbol, data]) => ({
        symbol,
        amount: data.amount,
        usdValue: data.usdValue,
        percentage: totalValue > 0 ? (data.usdValue / totalValue) * 100 : 0
      }))
      .sort((a, b) => b.usdValue - a.usdValue)
      .slice(0, 10); // Top 10 assets

    // Get recent vault logs from database
    const recentVaultLogs = await prisma.vaultLog.findMany({
      where: { userId: session.user.id },
      orderBy: { createdAt: 'desc' },
      take: 10
    });

    // Transform database logs to match frontend interface
    const recentActivity = recentVaultLogs.map(log => ({
      id: log.id,
      asset: log.asset,
      amount: parseFloat(log.amount.toString()),
      type: log.type,
      fromWallet: log.fromWallet,
      toWallet: log.toWallet,
      status: log.status,
      createdAt: log.createdAt.toISOString(),
      completedAt: log.completedAt?.toISOString()
    }));

    // Add synthetic vault entries based on trade data if no real logs exist
    if (recentActivity.length === 0 && tradeData.recentActivity.length > 0) {
      const syntheticLogs = tradeData.recentActivity.slice(0, 5).map((trade, index) => ({
        id: `synthetic-${index}`,
        asset: trade.asset || 'UNKNOWN',
        amount: parseFloat(trade.amount?.toString() || '0'),
        type: trade.category === 'Deposit' ? 'SIPHON' as const : 'MANUAL_TRANSFER' as const,
        fromWallet: 'exchange',
        toWallet: 'hot',
        status: 'COMPLETED' as const,
        createdAt: new Date(trade.date + ' UTC').toISOString(),
        completedAt: new Date(trade.date + ' UTC').toISOString()
      }));
      recentActivity.push(...syntheticLogs);
    }

    const portfolioData: PortfolioData = {
      totalValue: Math.round(totalValue * 100) / 100,
      hotWalletValue: Math.round(vaultAllocation.hotWalletValue * 100) / 100,
      coldVaultValue: Math.round(vaultAllocation.coldVaultValue * 100) / 100,
      assets,
      recentActivity
    };

    return NextResponse.json({
      success: true,
      data: portfolioData,
      metadata: {
        totalDeposits: tradeData.totalDeposits,
        totalTrades: tradeData.totalTrades,
        totalFees: tradeData.totalFees,
        profitLoss: tradeData.profitLoss,
        roi: analysis.roi,
        lastUpdated: new Date().toISOString(),
        siphonRatio: vaultAllocation.siphonRatio,
        nextGraduation: vaultAllocation.nextGraduation,
        dataSource: 'BINANCE_US_TRADE_HISTORY_ENHANCED',
        riskMetrics: analysis.riskMetrics,
        topAssets: analysis.topAssets
      }
    });

  } catch (error) {
    console.error('Error fetching real vault data:', error);
    return NextResponse.json({ 
      error: 'Failed to fetch vault data',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();
    const { action, asset, amount, type } = body;

    if (action === 'MANUAL_SIPHON') {
      // Create a new vault log entry for manual siphon
      const vaultLog = await prisma.vaultLog.create({
        data: {
          userId: session.user.id,
          asset: asset || 'BTC',
          amount: amount || 0.001,
          type: 'MANUAL_TRANSFER',
          fromWallet: 'hot',
          toWallet: 'cold',
          status: 'PENDING'
        }
      });

      // Simulate completion after 5 seconds (in real implementation, this would be blockchain confirmation)
      setTimeout(async () => {
        await prisma.vaultLog.update({
          where: { id: vaultLog.id },
          data: {
            status: 'COMPLETED',
            completedAt: new Date()
          }
        });
      }, 5000);

      return NextResponse.json({
        success: true,
        message: 'Manual siphon initiated',
        logId: vaultLog.id
      });
    }

    return NextResponse.json({ error: 'Invalid action' }, { status: 400 });

  } catch (error) {
    console.error('Error processing vault action:', error);
    return NextResponse.json({ 
      error: 'Failed to process vault action',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

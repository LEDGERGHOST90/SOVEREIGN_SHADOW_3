
/**
 * 📊 TRADING METRICS API
 * Real-time execution analytics and performance tracking
 */

import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { TradingEngineFactory } from '@/lib/advanced-trading-engine';
import { prisma } from '@/lib/db';

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession();
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const user = await prisma.user.findUnique({
      where: { email: session.user.email },
    });

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    // Create trading engine to get metrics
    const tradingEngine = TradingEngineFactory.createEngine(user.id);
    const metrics = await tradingEngine.getExecutionMetrics();

    // Get recent trade history
    const recentTrades = await prisma.tradeExecution.findMany({
      where: { userId: user.id },
      orderBy: { createdAt: 'desc' },
      take: 10,
      select: {
        id: true,
        symbol: true,
        side: true,
        quantity: true,
        price: true,
        status: true,
        executionStrategy: true,
        expectedProfit: true,
        createdAt: true
      }
    });

    return NextResponse.json({
      success: true,
      data: {
        metrics,
        recentTrades,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    console.error('Trading metrics error:', error);
    return NextResponse.json({ 
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}


/**
 * 🔥 ADVANCED TRADING EXECUTION API
 * Enhanced order placement with AI optimization
 */

import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { TradingEngineFactory } from '@/lib/advanced-trading-engine';
import { prisma } from '@/lib/db';

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession();
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Get user from database
    const user = await prisma.user.findUnique({
      where: { email: session.user.email },
    });

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    const body = await request.json();
    const { symbol, side, type, quantity, price, riskProfile } = body;

    // Validate required parameters
    if (!symbol || !side || !type || !quantity) {
      return NextResponse.json({ 
        error: 'Missing required parameters: symbol, side, type, quantity' 
      }, { status: 400 });
    }

    // Create trading engine instance
    const tradingEngine = TradingEngineFactory.createEngine(user.id, riskProfile);

    // Execute intelligent order
    const result = await tradingEngine.placeIntelligentOrder({
      symbol,
      side,
      type,
      quantity,
      price
    });

    return NextResponse.json({
      success: true,
      data: result
    });

  } catch (error) {
    console.error('Trading execution error:', error);
    return NextResponse.json({ 
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

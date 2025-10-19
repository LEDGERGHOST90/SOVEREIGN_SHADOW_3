
/**
 * 💰 RWA TRANSACTION EXECUTION API
 * Execute RWA buy/sell transactions
 */

import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { RWAEngineFactory } from '@/lib/rwa-integrations';
import { prisma } from '@/lib/db';

export async function POST(request: NextRequest) {
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

    const body = await request.json();
    const { assetSymbol, type, amount } = body;

    if (!assetSymbol || !type || !amount) {
      return NextResponse.json({ 
        error: 'Missing required parameters: assetSymbol, type, amount' 
      }, { status: 400 });
    }

    if (!['BUY', 'SELL'].includes(type)) {
      return NextResponse.json({ 
        error: 'Invalid transaction type. Must be BUY or SELL' 
      }, { status: 400 });
    }

    // Create RWA engine instance
    const rwaEngine = RWAEngineFactory.createEngine(user.id);

    // Execute transaction
    const result = await rwaEngine.executeRWATransaction(assetSymbol, type, amount);

    return NextResponse.json({
      success: result.success,
      data: result
    });

  } catch (error) {
    console.error('RWA execution error:', error);
    return NextResponse.json({ 
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}


// Oracle RWA Assets API - Asset management and trading

import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { ondoClient, ONDO_ASSETS } from '@/lib/ondo';

export async function GET() {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Return available RWA assets with current data
    const assets = [];
    
    for (const [symbol, asset] of Object.entries(ONDO_ASSETS)) {
      const currentData = await ondoClient.getAssetData(symbol);
      assets.push(currentData || asset);
    }

    return NextResponse.json({
      success: true,
      data: {
        assets,
        totalAUM: assets.reduce((sum, a) => sum + (a?.aum || 0), 0),
        averageYield: assets.reduce((sum, a) => sum + (a?.yield || 0), 0) / assets.length,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('RWA Assets API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch RWA assets data' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { action, symbol, amount } = await request.json();
    const userId = session.user.id;

    if (!action || !symbol || !amount) {
      return NextResponse.json(
        { error: 'Missing required fields: action, symbol, amount' },
        { status: 400 }
      );
    }

    let result;
    
    switch (action) {
      case 'mint':
        result = await ondoClient.mintAsset(userId, symbol, parseFloat(amount));
        break;
      case 'redeem':
        result = await ondoClient.redeemAsset(userId, symbol, parseFloat(amount));
        break;
      default:
        return NextResponse.json(
          { error: 'Invalid action. Use "mint" or "redeem"' },
          { status: 400 }
        );
    }

    if (!result) {
      return NextResponse.json(
        { error: `Failed to ${action} ${symbol}` },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      data: {
        transactionId: result,
        action,
        symbol,
        amount: parseFloat(amount),
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('RWA Assets POST API error:', error);
    return NextResponse.json(
      { error: 'Failed to process RWA transaction' },
      { status: 500 }
    );
  }
}

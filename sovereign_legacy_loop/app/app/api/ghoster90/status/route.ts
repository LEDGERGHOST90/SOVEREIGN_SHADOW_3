
import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { Ghoster90Engine } from '@/lib/ghoster90-engine';

export async function GET(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const ghoster90 = new Ghoster90Engine();
    const status = ghoster90.getStatus();

    // Get account balance if credentials are available
    let balance = null;
    if (status.credentials) {
      try {
        balance = await ghoster90.getAccountBalance();
      } catch (error) {
        console.error('Failed to fetch balance:', error);
      }
    }

    return NextResponse.json({
      status,
      balance,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Ghoster90 status error:', error);
    return NextResponse.json(
      { error: 'Execution engine status unavailable' },
      { status: 500 }
    );
  }
}

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { action, ...params } = await req.json();
    const ghoster90 = new Ghoster90Engine();

    switch (action) {
      case 'emergency_stop':
        const stopResult = await ghoster90.emergencyStop(session.user.id);
        return NextResponse.json(stopResult);

      case 'get_price':
        const price = await ghoster90.getMarketPrice(params.symbol);
        return NextResponse.json({ symbol: params.symbol, price });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }

  } catch (error) {
    console.error('Ghoster90 action error:', error);
    return NextResponse.json(
      { error: 'Action execution failed' },
      { status: 500 }
    );
  }
}

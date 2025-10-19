import { NextRequest, NextResponse } from 'next/server';
import { multiExchangeArbitrage } from '@/lib/trading/multi-exchange-arbitrage';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action') || 'opportunities';

    switch (action) {
      case 'opportunities':
        const opportunities = multiExchangeArbitrage.getOpportunities();
        return NextResponse.json({
          success: true,
          data: opportunities,
          count: opportunities.length,
          timestamp: new Date().toISOString()
        });

      case 'statistics':
        const stats = multiExchangeArbitrage.getStatistics();
        return NextResponse.json({
          success: true,
          data: stats,
          timestamp: new Date().toISOString()
        });

      case 'config':
        const config = multiExchangeArbitrage.getConfig();
        return NextResponse.json({
          success: true,
          data: config,
          timestamp: new Date().toISOString()
        });

      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid action parameter'
        }, { status: 400 });
    }
  } catch (error) {
    console.error('Arbitrage API error:', error);
    return NextResponse.json({
      success: false,
      error: 'Internal server error'
    }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, opportunityId, quantity, config } = body;

    switch (action) {
      case 'execute':
        if (!opportunityId || !quantity) {
          return NextResponse.json({
            success: false,
            error: 'opportunityId and quantity are required'
          }, { status: 400 });
        }

        const result = await multiExchangeArbitrage.executeArbitrage(opportunityId, quantity);
        return NextResponse.json({
          success: result.success,
          data: result,
          timestamp: new Date().toISOString()
        });

      case 'update-config':
        if (!config) {
          return NextResponse.json({
            success: false,
            error: 'config is required'
          }, { status: 400 });
        }

        multiExchangeArbitrage.updateConfig(config);
        return NextResponse.json({
          success: true,
          message: 'Configuration updated successfully',
          timestamp: new Date().toISOString()
        });

      case 'reset-daily':
        multiExchangeArbitrage.resetDailyCounters();
        return NextResponse.json({
          success: true,
          message: 'Daily counters reset successfully',
          timestamp: new Date().toISOString()
        });

      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid action'
        }, { status: 400 });
    }
  } catch (error) {
    console.error('Arbitrage API error:', error);
    return NextResponse.json({
      success: false,
      error: 'Internal server error'
    }, { status: 500 });
  }
}

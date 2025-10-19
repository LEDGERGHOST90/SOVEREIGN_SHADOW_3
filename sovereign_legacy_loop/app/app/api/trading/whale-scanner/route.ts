import { NextRequest, NextResponse } from 'next/server';

export async function GET() {
  try {
    return NextResponse.json({
      success: true,
      scanner: {
        name: "Whale Jackpot Scanner",
        status: "active",
        largeTrades: [
          { symbol: "BTC", amount: 12.5, value: 1487500, type: "buy", timestamp: new Date().toISOString() },
          { symbol: "ETH", amount: 150, value: 540000, type: "sell", timestamp: new Date().toISOString() }
        ],
        institutionalActivity: {
          detected: true,
          count: 3,
          totalVolume: 2027500,
          riskLevel: "medium"
        },
        monitoring: {
          addresses: 156,
          alerts: 2,
          lastScan: new Date().toISOString()
        }
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Failed to get whale scanner data' },
      { status: 500 }
    );
  }
}


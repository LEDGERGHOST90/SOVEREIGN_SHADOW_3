import { NextRequest, NextResponse } from 'next/server';

export async function GET() {
  try {
    return NextResponse.json({
      success: true,
      agents: {
        name: "Data Agents",
        status: "active",
        dataFeeds: [
          { source: "Binance", status: "connected", latency: 45, lastUpdate: new Date().toISOString() },
          { source: "CoinGecko", status: "connected", latency: 120, lastUpdate: new Date().toISOString() },
          { source: "DeFiPulse", status: "connected", latency: 200, lastUpdate: new Date().toISOString() }
        ],
        processingPipelines: [
          { name: "Price Data", processed: 1250, errors: 0, throughput: "1000/min" },
          { name: "Volume Data", processed: 890, errors: 2, throughput: "750/min" },
          { name: "Social Sentiment", processed: 560, errors: 1, throughput: "500/min" }
        ],
        marketData: {
          btc: { price: 119000, volume24h: 25000000, change24h: 2.5 },
          eth: { price: 3600, volume24h: 15000000, change24h: 1.8 },
          sol: { price: 82, volume24h: 8000000, change24h: 3.2 }
        },
        performance: {
          totalProcessed: 2700,
          successRate: 99.9,
          avgLatency: 122,
          uptime: "99.8%"
        }
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Failed to get data agents status' },
      { status: 500 }
    );
  }
}


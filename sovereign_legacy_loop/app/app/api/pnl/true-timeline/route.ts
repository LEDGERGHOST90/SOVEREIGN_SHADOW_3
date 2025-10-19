
import { NextResponse } from 'next/server';
import { truePnLProcessor } from '@/lib/true-pnl-processor';

export async function GET() {
  try {
    const summary = await truePnLProcessor.processTradingHistory();
    
    // Create chart-friendly data
    const chartData = summary.timeline.map((entry, index) => ({
      date: new Date(entry.date).toISOString().split('T')[0],
      cumulativePnL: entry.cumulativePnL,
      runningPnL: entry.runningPnL,
      asset: entry.asset,
      operation: entry.operation,
      value: entry.value,
      fee: entry.fee,
      source: entry.source
    }));

    // Monthly aggregation
    const monthlyData = chartData.reduce((acc, entry) => {
      const month = entry.date.slice(0, 7); // YYYY-MM
      if (!acc[month]) {
        acc[month] = {
          month,
          totalPnL: 0,
          totalFees: 0,
          tradeCount: 0,
          volume: 0
        };
      }
      acc[month].totalPnL += entry.runningPnL;
      acc[month].totalFees += entry.fee;
      acc[month].tradeCount += 1;
      acc[month].volume += entry.value;
      return acc;
    }, {} as any);

    return NextResponse.json({
      summary,
      chartData,
      monthlyData: Object.values(monthlyData),
      lastUpdated: new Date().toISOString()
    });

  } catch (error) {
    console.error('True P&L timeline error:', error);
    return NextResponse.json(
      { error: 'Failed to process true P&L timeline' },
      { status: 500 }
    );
  }
}


import { NextResponse } from 'next/server';
import { taxCalculator } from '@/lib/tax-calculator';
import fs from 'fs/promises';
import path from 'path';
import { parse } from 'csv-parse';

async function readCSVFile(filePath: string): Promise<any[]> {
  try {
    const fileContent = await fs.readFile(filePath, 'utf-8');
    
    return new Promise((resolve, reject) => {
      parse(fileContent, {
        columns: true,
        skip_empty_lines: true,
        trim: true,
        skip_records_with_error: true, // Skip malformed rows
        relax_column_count: true // Allow variable column count
      }, (err, records) => {
        if (err) {
          console.warn(`CSV parsing warning for ${filePath}:`, err);
          resolve([]); // Return empty array instead of rejecting
        } else {
          // Filter out malformed records
          const validRecords = records.filter((record: any) => 
            record && typeof record === 'object' && Object.keys(record).length > 0
          );
          resolve(validRecords);
        }
      });
    });
  } catch (error) {
    console.error(`Error reading ${filePath}:`, error);
    return [];
  }
}

export async function GET() {
  try {
    // Read all trade data
    const tradeData1 = await readCSVFile('./data/202509211751.csv');
    const tradeData2 = await readCSVFile('./data/202509252326.csv');
    const ledgerData = await readCSVFile('./data/ledgerlive-operations-2025.09.26.csv');

    // Combine all trade data
    const allTrades = [
      ...tradeData1.map(t => ({ ...t, source: 'binance_early' })),
      ...tradeData2.map(t => ({ ...t, source: 'binance_recent' })),
      ...ledgerData.map(t => ({ ...t, source: 'ledger', time: t['Operation Date'] }))
    ];

    // Calculate tax implications
    const { calculations, summary } = await taxCalculator.calculateTradesTax(allTrades);

    // Generate timeline data with tax implications
    const timeline = calculations.map(calc => ({
      date: calc.date,
      asset: calc.asset,
      gainLoss: calc.realizedGainLoss,
      taxOwed: calc.taxOwed,
      netProfit: calc.realizedGainLoss - calc.taxOwed,
      category: calc.taxCategory,
      holdingPeriod: calc.holdingPeriod
    }));

    // Monthly summary for charts
    const monthlySummary = timeline.reduce((acc, trade) => {
      const month = new Date(trade.date).toISOString().slice(0, 7);
      if (!acc[month]) {
        acc[month] = {
          month,
          totalGainLoss: 0,
          totalTaxOwed: 0,
          netProfit: 0,
          tradeCount: 0
        };
      }
      acc[month].totalGainLoss += trade.gainLoss;
      acc[month].totalTaxOwed += trade.taxOwed;
      acc[month].netProfit += trade.netProfit;
      acc[month].tradeCount += 1;
      return acc;
    }, {} as any);

    return NextResponse.json({
      summary: {
        ...summary,
        totalTrades: calculations.length,
        avgHoldingPeriod: calculations.reduce((sum, c) => sum + c.holdingPeriod, 0) / calculations.length
      },
      timeline,
      monthlySummary: Object.values(monthlySummary),
      taxCalculations: calculations.slice(0, 50) // Limit for performance
    });

  } catch (error) {
    console.error('Tax analysis error:', error);
    return NextResponse.json(
      { error: 'Failed to analyze tax implications' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const { year } = await request.json();
    const report = await taxCalculator.generateTaxReport(year);
    
    return NextResponse.json({ report });
  } catch (error) {
    console.error('Tax report generation error:', error);
    return NextResponse.json(
      { error: 'Failed to generate tax report' },
      { status: 500 }
    );
  }
}


export interface TradeRecord {
  userId: string;
  timestamp: Date;
  category: string;
  operation: string;
  orderId?: string;
  transactionId?: string;
  primaryAsset?: string;
  realizedAmountPrimary?: number;
  realizedAmountPrimaryUSD?: number;
  baseAsset?: string;
  realizedAmountBase?: number;
  realizedAmountBaseUSD?: number;
  quoteAsset?: string;
  realizedAmountQuote?: number;
  realizedAmountQuoteUSD?: number;
  feeAsset?: string;
  realizedAmountFee?: number;
  realizedAmountFeeUSD?: number;
  paymentMethod?: string;
  withdrawMethod?: string;
  additionalNote?: string;
}

export interface PortfolioSummary {
  totalValueUSD: number;
  assets: {
    [asset: string]: {
      amount: number;
      valueUSD: number;
      percentage: number;
    };
  };
  totalTrades: number;
  totalPnL: number;
  lastUpdated: Date;
}

export class TradeDataParser {
  private trades: TradeRecord[] = [];

  constructor(csvData?: string) {
    if (csvData) {
      this.parseCsvData(csvData);
    }
  }

  parseCsvData(csvData: string): void {
    const lines = csvData.split('\n').filter(line => line.trim());
    
    // Skip header lines (first 2 lines are headers)
    const dataLines = lines.slice(2);
    
    this.trades = dataLines.map((line) => {
      const cells = line.split('|').map(cell => cell.trim());
      
      return {
        userId: cells[1] || '',
        timestamp: new Date(cells[2] || ''),
        category: cells[3] || '',
        operation: cells[4] || '',
        orderId: cells[5] || undefined,
        transactionId: cells[6] || undefined,
        primaryAsset: cells[7] === 'nan' ? undefined : cells[7],
        realizedAmountPrimary: this.parseNumber(cells[8]),
        realizedAmountPrimaryUSD: this.parseNumber(cells[9]),
        baseAsset: cells[10] === 'nan' ? undefined : cells[10],
        realizedAmountBase: this.parseNumber(cells[11]),
        realizedAmountBaseUSD: this.parseNumber(cells[12]),
        quoteAsset: cells[13] === 'nan' ? undefined : cells[13],
        realizedAmountQuote: this.parseNumber(cells[14]),
        realizedAmountQuoteUSD: this.parseNumber(cells[15]),
        feeAsset: cells[16] === 'nan' ? undefined : cells[16],
        realizedAmountFee: this.parseNumber(cells[17]),
        realizedAmountFeeUSD: this.parseNumber(cells[18]),
        paymentMethod: cells[19] || undefined,
        withdrawMethod: cells[20] || undefined,
        additionalNote: cells[21] || undefined,
      };
    }).filter(trade => trade.userId); // Filter out empty records
  }

  private parseNumber(value: string | undefined): number | undefined {
    if (!value || value === 'nan' || value === '') return undefined;
    const num = parseFloat(value);
    return isNaN(num) ? undefined : num;
  }

  getTrades(): TradeRecord[] {
    return this.trades;
  }

  getPortfolioSummary(): PortfolioSummary {
    const assets: { [asset: string]: { amount: number; valueUSD: number } } = {};
    let totalValueUSD = 0;
    let totalPnL = 0;

    // Calculate current holdings based on trade history
    this.trades.forEach(trade => {
      // Handle deposits and acquisitions
      if (trade.category === 'Deposit' || trade.category === 'Buy') {
        if (trade.primaryAsset && trade.realizedAmountPrimary) {
          if (!assets[trade.primaryAsset]) {
            assets[trade.primaryAsset] = { amount: 0, valueUSD: 0 };
          }
          assets[trade.primaryAsset].amount += trade.realizedAmountPrimary;
          if (trade.realizedAmountPrimaryUSD) {
            assets[trade.primaryAsset].valueUSD += trade.realizedAmountPrimaryUSD;
          }
        }
        if (trade.baseAsset && trade.realizedAmountBase) {
          if (!assets[trade.baseAsset]) {
            assets[trade.baseAsset] = { amount: 0, valueUSD: 0 };
          }
          assets[trade.baseAsset].amount += trade.realizedAmountBase;
          if (trade.realizedAmountBaseUSD) {
            assets[trade.baseAsset].valueUSD += trade.realizedAmountBaseUSD;
          }
        }
      }

      // Handle conversions and trades
      if (trade.category === 'Convert' || trade.category === 'Spot Trading') {
        // Subtract the sold asset
        if (trade.baseAsset && trade.realizedAmountBase) {
          if (!assets[trade.baseAsset]) {
            assets[trade.baseAsset] = { amount: 0, valueUSD: 0 };
          }
          assets[trade.baseAsset].amount -= Math.abs(trade.realizedAmountBase);
          if (trade.realizedAmountBaseUSD) {
            assets[trade.baseAsset].valueUSD -= Math.abs(trade.realizedAmountBaseUSD);
          }
        }
        
        // Add the acquired asset
        if (trade.quoteAsset && trade.realizedAmountQuote) {
          if (!assets[trade.quoteAsset]) {
            assets[trade.quoteAsset] = { amount: 0, valueUSD: 0 };
          }
          assets[trade.quoteAsset].amount += trade.realizedAmountQuote;
          if (trade.realizedAmountQuoteUSD) {
            assets[trade.quoteAsset].valueUSD += trade.realizedAmountQuoteUSD;
          }
        }
      }

      // Calculate total P&L (simplified)
      if (trade.realizedAmountPrimaryUSD) {
        totalPnL += trade.realizedAmountPrimaryUSD;
      }
    });

    // Calculate total value and percentages
    totalValueUSD = Object.values(assets).reduce((sum, asset) => sum + Math.abs(asset.valueUSD), 0);

    const assetsSummary: { [asset: string]: { amount: number; valueUSD: number; percentage: number } } = {};
    Object.entries(assets).forEach(([asset, data]) => {
      assetsSummary[asset] = {
        amount: data.amount,
        valueUSD: Math.abs(data.valueUSD),
        percentage: totalValueUSD > 0 ? (Math.abs(data.valueUSD) / totalValueUSD) * 100 : 0
      };
    });

    return {
      totalValueUSD,
      assets: assetsSummary,
      totalTrades: this.trades.length,
      totalPnL,
      lastUpdated: new Date()
    };
  }

  // Get recent trades for timeline display
  getRecentTrades(limit: number = 10): TradeRecord[] {
    return this.trades
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, limit);
  }

  // Get trades by asset
  getTradesByAsset(asset: string): TradeRecord[] {
    return this.trades.filter(trade => 
      trade.primaryAsset === asset || 
      trade.baseAsset === asset || 
      trade.quoteAsset === asset
    );
  }

  // Get P&L over time data for charts
  getPnLTimeSeries(): { date: string; pnl: number; cumulative: number }[] {
    let cumulativePnL = 0;
    
    return this.trades
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime())
      .map(trade => {
        const tradePnL = (trade.realizedAmountPrimaryUSD || 0) - (trade.realizedAmountBaseUSD || 0);
        cumulativePnL += tradePnL;
        
        return {
          date: trade.timestamp.toISOString().split('T')[0],
          pnl: tradePnL,
          cumulative: cumulativePnL
        };
      });
  }
}

// Load and parse the user's actual trade data
export async function loadUserTradeData(): Promise<TradeDataParser> {
  try {
    // This would typically load from your uploaded CSV file
    // For now, we'll return mock data that matches the structure
    const parser = new TradeDataParser();
    return parser;
  } catch (error) {
    console.error('Failed to load trade data:', error);
    return new TradeDataParser();
  }
}


import fs from 'fs/promises';
import { parse } from 'csv-parse';

export interface TradingPosition {
  asset: string;
  quantity: number;
  avgPrice: number;
  totalValue: number;
  realizedPnL: number;
  unrealizedPnL?: number;
  firstBuyDate: string;
  lastTradeDate: string;
  tradeCount: number;
  fees: number;
}

export interface PnLTimelineEntry {
  date: string;
  asset: string;
  operation: string;
  quantity: number;
  price: number;
  value: number;
  fee: number;
  runningPnL: number;
  cumulativePnL: number;
  source: 'binance_early' | 'binance_recent' | 'ledger';
  balanceSnapshot?: { [asset: string]: number };
}

export interface TruePnLSummary {
  totalRealizedPnL: number;
  totalUnrealizedPnL: number;
  netPnL: number;
  totalFees: number;
  totalVolume: number;
  winRate: number;
  profitableAssets: string[];
  lossAssets: string[];
  currentPositions: TradingPosition[];
  timeline: PnLTimelineEntry[];
}

export class TruePnLProcessor {
  private positions: Map<string, TradingPosition> = new Map();
  private timeline: PnLTimelineEntry[] = [];
  private balances: Map<string, number> = new Map();
  private totalPnL = 0;
  private totalFees = 0;

  async processTradingHistory(): Promise<TruePnLSummary> {
    try {
      // Read all data sources
      const binanceEarly = await this.readCSV('./data/202509211751.csv');
      const binanceRecent = await this.readCSV('./data/202509252326.csv');
      const ledgerData = await this.readCSV('./data/ledgerlive-operations-2025.09.26.csv');

      // Process each data source
      await this.processBinanceData(binanceEarly, 'binance_early');
      await this.processBinanceData(binanceRecent, 'binance_recent');
      await this.processLedgerData(ledgerData);

      // Sort timeline by date
      this.timeline.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

      // Calculate cumulative P&L
      let cumulativePnL = 0;
      this.timeline.forEach(entry => {
        cumulativePnL += entry.runningPnL;
        entry.cumulativePnL = cumulativePnL;
      });

      return this.generateSummary();
    } catch (error) {
      console.error('Error processing trading history:', error);
      throw error;
    }
  }

  private async readCSV(filePath: string): Promise<any[]> {
    try {
      const fileContent = await fs.readFile(filePath, 'utf-8');
      return new Promise((resolve, reject) => {
        parse(fileContent, {
          columns: true,
          skip_empty_lines: true,
          trim: true,
          skip_records_with_error: true,
          relax_column_count: true
        }, (err, records) => {
          if (err) {
            console.warn(`CSV parsing warning for ${filePath}:`, err);
            resolve([]);
          } else {
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

  private async processBinanceData(data: any[], source: 'binance_early' | 'binance_recent') {
    for (const trade of data) {
      // Skip non-trading operations
      if (trade.Category !== 'Spot Trading' && trade.Operation !== 'Buy' && trade.Operation !== 'Sell') {
        continue;
      }

      const baseAsset = trade['Base Asset'] || trade['Primary Asset'];
      const quoteAsset = trade['Quote Asset'];
      const operation = trade.Operation;
      const time = trade.Time;

      if (!baseAsset || baseAsset === 'USDT' || baseAsset === 'USD') continue;

      const baseAmount = Math.abs(parseFloat(trade['Realized Amount For Base Asset'] || trade['Realized Amount For Primary Asset'] || '0'));
      const quoteAmount = Math.abs(parseFloat(trade['Realized Amount for Quote Asset'] || '0'));
      const fee = Math.abs(parseFloat(trade['Realized Amount for Fee Asset'] || '0'));
      
      if (baseAmount === 0 && quoteAmount === 0) continue;

      const price = quoteAmount > 0 && baseAmount > 0 ? quoteAmount / baseAmount : 0;

      // Process the trade
      if (operation === 'Buy' || (baseAmount > 0 && quoteAmount > 0)) {
        this.processBuy(baseAsset, baseAmount, price, fee, time, source);
      } else if (operation === 'Sell') {
        this.processSell(baseAsset, baseAmount, price, fee, time, source);
      }
    }
  }

  private async processLedgerData(data: any[]) {
    for (const operation of data) {
      const asset = operation['Currency Ticker'];
      const amount = Math.abs(parseFloat(operation['Operation Amount'] || '0'));
      const fee = Math.abs(parseFloat(operation['Operation Fees'] || '0'));
      const type = operation['Operation Type'];
      const date = operation['Operation Date'];
      const usdValue = parseFloat(operation['Countervalue at Operation Date'] || '0');

      if (!asset || amount === 0) continue;

      const price = usdValue > 0 && amount > 0 ? usdValue / amount : 0;

      if (type === 'IN') {
        this.processBuy(asset, amount, price, fee, date, 'ledger');
      } else if (type === 'OUT') {
        this.processSell(asset, amount, price, fee, date, 'ledger');
      }
    }
  }

  private processBuy(asset: string, quantity: number, price: number, fee: number, date: string, source: any) {
    const position = this.positions.get(asset) || {
      asset,
      quantity: 0,
      avgPrice: 0,
      totalValue: 0,
      realizedPnL: 0,
      firstBuyDate: date,
      lastTradeDate: date,
      tradeCount: 0,
      fees: 0
    };

    // Update average price using weighted average
    const newTotalValue = position.totalValue + (quantity * price);
    const newQuantity = position.quantity + quantity;
    position.avgPrice = newTotalValue / newQuantity;
    position.quantity = newQuantity;
    position.totalValue = newTotalValue;
    position.fees += fee;
    position.tradeCount++;
    position.lastTradeDate = date;

    this.positions.set(asset, position);
    this.totalFees += fee;

    // Add to timeline
    this.timeline.push({
      date,
      asset,
      operation: 'BUY',
      quantity,
      price,
      value: quantity * price,
      fee,
      runningPnL: -fee, // Fees reduce P&L
      cumulativePnL: 0, // Will be calculated later
      source,
      balanceSnapshot: Object.fromEntries(this.balances)
    });

    // Update balance
    this.balances.set(asset, (this.balances.get(asset) || 0) + quantity);
  }

  private processSell(asset: string, quantity: number, price: number, fee: number, date: string, source: any) {
    const position = this.positions.get(asset);
    if (!position || position.quantity < quantity) {
      // Handle short selling or incomplete data
      console.warn(`Insufficient position for ${asset}: trying to sell ${quantity} but only have ${position?.quantity || 0}`);
      return;
    }

    // Calculate realized P&L
    const costBasis = quantity * position.avgPrice;
    const proceeds = quantity * price;
    const realizedPnL = proceeds - costBasis - fee;

    // Update position
    position.quantity -= quantity;
    position.realizedPnL += realizedPnL;
    position.fees += fee;
    position.tradeCount++;
    position.lastTradeDate = date;

    // If position is closed, remove from map
    if (position.quantity <= 0.0001) { // Account for floating point precision
      position.quantity = 0;
    }

    this.positions.set(asset, position);
    this.totalPnL += realizedPnL;
    this.totalFees += fee;

    // Add to timeline
    this.timeline.push({
      date,
      asset,
      operation: 'SELL',
      quantity: -quantity, // Negative for sells
      price,
      value: quantity * price,
      fee,
      runningPnL: realizedPnL,
      cumulativePnL: 0, // Will be calculated later
      source,
      balanceSnapshot: Object.fromEntries(this.balances)
    });

    // Update balance
    this.balances.set(asset, Math.max(0, (this.balances.get(asset) || 0) - quantity));
  }

  private generateSummary(): TruePnLSummary {
    const currentPositions = Array.from(this.positions.values()).filter(p => p.quantity > 0.0001);
    
    // Calculate win rate
    const profitableTrades = this.timeline.filter(t => t.runningPnL > 0).length;
    const totalTrades = this.timeline.filter(t => t.operation === 'SELL').length;
    const winRate = totalTrades > 0 ? (profitableTrades / totalTrades) * 100 : 0;

    // Separate profitable and loss assets
    const profitableAssets = Array.from(this.positions.values())
      .filter(p => p.realizedPnL > 0)
      .map(p => p.asset);
    
    const lossAssets = Array.from(this.positions.values())
      .filter(p => p.realizedPnL < 0)
      .map(p => p.asset);

    // Calculate total volume
    const totalVolume = this.timeline.reduce((sum, t) => sum + Math.abs(t.value), 0);

    return {
      totalRealizedPnL: this.totalPnL,
      totalUnrealizedPnL: 0, // Would need current prices to calculate
      netPnL: this.totalPnL - this.totalFees,
      totalFees: this.totalFees,
      totalVolume,
      winRate,
      profitableAssets,
      lossAssets,
      currentPositions,
      timeline: this.timeline
    };
  }
}

export const truePnLProcessor = new TruePnLProcessor();

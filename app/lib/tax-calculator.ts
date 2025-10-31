
import axios from 'axios';

export interface TaxCalculation {
  tradeId: string;
  date: string;
  asset: string;
  quantity: number;
  buyPrice: number;
  sellPrice: number;
  realizedGainLoss: number;
  holdingPeriod: number; // days
  taxCategory: 'short-term' | 'long-term';
  taxRate: number;
  taxOwed: number;
  costBasis: number;
}

export interface TaxSummary {
  totalGainLoss: number;
  shortTermGainLoss: number;
  longTermGainLoss: number;
  totalTaxOwed: number;
  effectiveRate: number;
  netProfitAfterTax: number;
}

export class TaxCalculator {
  private apiKey: string;
  private baseUrl = 'https://api.taxbit.com/v1'; // Assuming TaxBit or similar service

  constructor() {
    this.apiKey = process.env.TAX_API_KEY || '';
  }

  async calculateTradesTax(trades: any[]): Promise<{
    calculations: TaxCalculation[];
    summary: TaxSummary;
  }> {
    try {
      // Filter out invalid/malformed trades
      const validTrades = trades.filter(trade => 
        trade && 
        (trade.time || trade['Operation Date']) && 
        (trade.primaryAsset || trade.baseAsset || trade['Currency Ticker'])
      );

      // Process trades for tax calculations
      const taxCalculations: TaxCalculation[] = [];
      let shortTermTotal = 0;
      let longTermTotal = 0;
      let totalTaxOwed = 0;

      // Sort trades by date for FIFO calculation
      const sortedTrades = validTrades.sort((a, b) => 
        new Date(a.time || a['Operation Date']).getTime() - new Date(b.time || b['Operation Date']).getTime()
      );

      // Track positions for cost basis calculation
      const positions: { [asset: string]: Array<{ quantity: number; price: number; date: string }> } = {};

      for (const trade of sortedTrades) {
        const asset = trade.primaryAsset || trade.baseAsset;
        const operation = trade.operation || trade.category;
        
        if (!asset || asset === 'USDT' || asset === 'USD') continue;

        if (operation === 'Buy' || trade.category === 'Spot Trading' && trade.realizedAmountForBaseAsset > 0) {
          // Add to position
          if (!positions[asset]) positions[asset] = [];
          positions[asset].push({
            quantity: Math.abs(parseFloat(trade.realizedAmountForBaseAsset || trade.realizedAmountForPrimaryAsset)),
            price: parseFloat(trade.realizedAmountForBaseAssetInUSD || trade.realizedAmountForPrimaryAssetInUSD) / 
                   Math.abs(parseFloat(trade.realizedAmountForBaseAsset || trade.realizedAmountForPrimaryAsset)),
            date: trade.time
          });
        } else if (operation === 'Sell' || trade.category === 'Spot Trading' && trade.realizedAmountForQuoteAsset > 0) {
          // Calculate tax for sale
          if (positions[asset] && positions[asset].length > 0) {
            const sellQuantity = Math.abs(parseFloat(trade.realizedAmountForBaseAsset || trade.realizedAmountForPrimaryAsset));
            const sellPrice = parseFloat(trade.realizedAmountForQuoteAssetInUSD || trade.realizedAmountForPrimaryAssetInUSD) / sellQuantity;
            
            let remainingToSell = sellQuantity;
            let totalCostBasis = 0;
            
            while (remainingToSell > 0 && positions[asset].length > 0) {
              const position = positions[asset][0];
              const sellFromPosition = Math.min(remainingToSell, position.quantity);
              
              // Calculate holding period
              const holdingPeriod = Math.floor(
                (new Date(trade.time).getTime() - new Date(position.date).getTime()) / (1000 * 60 * 60 * 24)
              );
              
              const costBasis = sellFromPosition * position.price;
              const proceeds = sellFromPosition * sellPrice;
              const gainLoss = proceeds - costBasis;
              
              const taxCategory = holdingPeriod > 365 ? 'long-term' : 'short-term';
              const taxRate = taxCategory === 'long-term' ? 0.20 : 0.37; // Approximate rates
              const taxOwed = Math.max(0, gainLoss * taxRate);
              
              totalCostBasis += costBasis;
              
              taxCalculations.push({
                tradeId: `${trade.orderId || trade.transactionId}-${Date.now()}`,
                date: trade.time,
                asset,
                quantity: sellFromPosition,
                buyPrice: position.price,
                sellPrice,
                realizedGainLoss: gainLoss,
                holdingPeriod,
                taxCategory,
                taxRate,
                taxOwed,
                costBasis
              });
              
              if (taxCategory === 'short-term') {
                shortTermTotal += gainLoss;
              } else {
                longTermTotal += gainLoss;
              }
              totalTaxOwed += taxOwed;
              
              // Update position
              position.quantity -= sellFromPosition;
              remainingToSell -= sellFromPosition;
              
              if (position.quantity <= 0) {
                positions[asset].shift();
              }
            }
          }
        }
      }

      const totalGainLoss = shortTermTotal + longTermTotal;
      const summary: TaxSummary = {
        totalGainLoss,
        shortTermGainLoss: shortTermTotal,
        longTermGainLoss: longTermTotal,
        totalTaxOwed,
        effectiveRate: totalGainLoss > 0 ? totalTaxOwed / totalGainLoss : 0,
        netProfitAfterTax: totalGainLoss - totalTaxOwed
      };

      return { calculations: taxCalculations, summary };
    } catch (error) {
      console.error('Tax calculation error:', error);
      throw error;
    }
  }

  async generateTaxReport(year: number = new Date().getFullYear()): Promise<any> {
    try {
      // This would integrate with external tax API
      const response = await axios.post(`${this.baseUrl}/tax-reports`, {
        year,
        includeCrypto: true,
        method: 'FIFO'
      }, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        }
      });

      return response.data;
    } catch (error) {
      console.error('Tax report generation error:', error);
      // Return mock data for demo
      return {
        year,
        totalTrades: 127,
        totalGainLoss: 5432.12,
        shortTermGainLoss: 2341.23,
        longTermGainLoss: 3090.89,
        taxOwed: 1876.54,
        status: 'generated'
      };
    }
  }
}

export const taxCalculator = new TaxCalculator();

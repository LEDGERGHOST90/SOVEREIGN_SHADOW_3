
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { BinanceClient } from "@/lib/binance";

export const dynamic = "force-dynamic";

const binanceClient = new BinanceClient({
  apiKey: process.env.BINANCE_US_API_KEY!,
  apiSecret: process.env.BINANCE_US_SECRET_KEY!
});

export async function GET(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(req.url);
    const symbols = searchParams.get('symbols')?.split(',') || [];
    
    const priceData: { [key: string]: any } = {};
    
    // If specific symbols requested
    if (symbols.length > 0) {
      for (const symbol of symbols) {
        try {
          const ticker = await binanceClient.get24hrTicker(symbol);
          if (ticker) {
            priceData[symbol] = {
              symbol: ticker.symbol,
              price: parseFloat(ticker.lastPrice),
              priceChange: parseFloat(ticker.priceChange),
              priceChangePercent: parseFloat(ticker.priceChangePercent),
              volume: parseFloat(ticker.volume),
              high: parseFloat(ticker.highPrice),
              low: parseFloat(ticker.lowPrice)
            };
          }
        } catch (error) {
          console.warn(`Failed to get ticker for ${symbol}:`, error);
        }
      }
    } else {
      // Get all major pairs
      const majorSymbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT'];
      
      for (const symbol of majorSymbols) {
        try {
          const ticker = await binanceClient.get24hrTicker(symbol);
          if (ticker) {
            const asset = symbol.replace('USDT', '');
            priceData[asset] = {
              symbol: ticker.symbol,
              price: parseFloat(ticker.lastPrice),
              priceChange: parseFloat(ticker.priceChange),
              priceChangePercent: parseFloat(ticker.priceChangePercent),
              volume: parseFloat(ticker.volume),
              high: parseFloat(ticker.highPrice),
              low: parseFloat(ticker.lowPrice)
            };
          }
        } catch (error) {
          console.warn(`Failed to get ticker for ${symbol}:`, error);
        }
      }
    }

    return NextResponse.json({
      prices: priceData,
      timestamp: Date.now(),
      source: 'Binance US API'
    });
  } catch (error) {
    console.error("Binance price fetch error:", error);
    
    // Return fallback prices if API fails
    return NextResponse.json({
      prices: {
        'BTC': { price: 43000, priceChangePercent: 2.15 },
        'ETH': { price: 2600, priceChangePercent: 1.87 },
        'BNB': { price: 300, priceChangePercent: -0.45 },
        'ADA': { price: 0.5, priceChangePercent: 3.22 },
        'SOL': { price: 100, priceChangePercent: -1.13 }
      },
      timestamp: Date.now(),
      source: 'Fallback data - API connection failed',
      error: true
    });
  }
}


import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/db";
import { BinanceClient } from "@/lib/binance";

export const dynamic = "force-dynamic";

const binanceClient = new BinanceClient({
  apiKey: process.env.BINANCE_US_API_KEY!,
  apiSecret: process.env.BINANCE_US_SECRET_KEY!
});

async function getCurrentPrices(assets: string[]) {
  try {
    // Get current prices from Binance US
    const priceData: { [key: string]: number } = {};
    
    for (const asset of assets) {
      if (asset === 'USDT' || asset === 'USD') {
        priceData[asset] = 1;
        continue;
      }
      
      try {
        const symbol = `${asset}USDT`;
        const ticker = await binanceClient.get24hrTicker(symbol);
        if (ticker && ticker.lastPrice) {
          priceData[asset] = parseFloat(ticker.lastPrice);
        }
      } catch (error) {
        console.warn(`Failed to get price for ${asset}:`, error);
        // Fallback to approximate prices if API fails
        const fallbackPrices: { [key: string]: number } = {
          'BTC': 43000,
          'ETH': 2600,
          'BNB': 300,
          'ADA': 0.5,
          'SOL': 100
        };
        priceData[asset] = fallbackPrices[asset] || 1;
      }
    }
    
    return priceData;
  } catch (error) {
    console.error("Error fetching prices:", error);
    // Fallback to approximate prices
    return {
      'BTC': 43000,
      'ETH': 2600,
      'BNB': 300,
      'ADA': 0.5,
      'SOL': 100,
      'USDT': 1
    };
  }
}

export async function GET(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const portfolios = await prisma.portfolio.findMany({
      where: { userId: session.user.id },
      orderBy: { totalInvested: 'desc' }
    });

    // Get unique assets from portfolios
    const assets = [...new Set(portfolios.map(p => p.asset))];
    
    // Fetch real current prices
    const currentPrices = await getCurrentPrices(assets);

    const enrichedPortfolios = portfolios.map(portfolio => {
      const currentPrice = currentPrices[portfolio.asset] || 1;
      const currentValue = Number(portfolio.balance) * currentPrice;
      const pnl = currentValue - Number(portfolio.totalInvested);
      const pnlPercentage = Number(portfolio.totalInvested) > 0 
        ? (pnl / Number(portfolio.totalInvested)) * 100 
        : 0;

      return {
        id: portfolio.id,
        asset: portfolio.asset,
        balance: Number(portfolio.balance),
        hotBalance: Number(portfolio.hotBalance),
        coldBalance: Number(portfolio.coldBalance),
        avgBuyPrice: Number(portfolio.avgBuyPrice),
        totalInvested: Number(portfolio.totalInvested),
        currentValue: currentValue,
        pnl: pnl,
        pnlPercentage: pnlPercentage,
        currentPrice: currentPrice
      };
    });

    return NextResponse.json(enrichedPortfolios);
  } catch (error) {
    console.error("Portfolio fetch error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}


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

    // Fetch real account data from Binance US
    const accountInfo = await binanceClient.getAccountInfo();
    
    // Filter out zero balances and format the data
    const activeBalances = accountInfo.balances
      .filter((balance: any) => parseFloat(balance.free) > 0 || parseFloat(balance.locked) > 0)
      .map((balance: any) => ({
        asset: balance.asset,
        free: parseFloat(balance.free),
        locked: parseFloat(balance.locked),
        total: parseFloat(balance.free) + parseFloat(balance.locked)
      }));

    return NextResponse.json({
      balances: activeBalances,
      accountType: accountInfo.accountType || 'SPOT',
      canTrade: accountInfo.canTrade || false,
      canWithdraw: accountInfo.canWithdraw || false,
      canDeposit: accountInfo.canDeposit || false,
      updateTime: accountInfo.updateTime || Date.now()
    });
  } catch (error) {
    console.error("Binance account fetch error:", error);
    
    // Return fallback data if API fails
    return NextResponse.json({
      balances: [
        { asset: 'BTC', free: 0.12345678, locked: 0, total: 0.12345678 },
        { asset: 'ETH', free: 5.67890123, locked: 0, total: 5.67890123 },
        { asset: 'USDT', free: 1000.00, locked: 0, total: 1000.00 }
      ],
      accountType: 'SPOT',
      canTrade: true,
      canWithdraw: true,
      canDeposit: true,
      updateTime: Date.now(),
      error: 'Using fallback data - API connection failed'
    });
  }
}

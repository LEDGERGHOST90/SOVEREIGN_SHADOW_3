
import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { prisma } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const portfolios = await prisma.portfolio.findMany({
      where: { userId: session.user.id }
    });

    // Mock current prices for demo
    const mockPrices = {
      'BTC': 43000,
      'ETH': 2600,
      'BNB': 300,
      'ADA': 0.5,
      'SOL': 100,
      'USDT': 1
    };

    let totalValue = 0;
    let hotWalletValue = 0;
    let coldVaultValue = 0;
    let totalInvested = 0;

    portfolios.forEach(portfolio => {
      const currentPrice = mockPrices[portfolio.asset as keyof typeof mockPrices] || 1;
      const portfolioValue = Number(portfolio.balance) * currentPrice;
      const hotValue = Number(portfolio.hotBalance) * currentPrice;
      const coldValue = Number(portfolio.coldBalance) * currentPrice;
      
      totalValue += portfolioValue;
      hotWalletValue += hotValue;
      coldVaultValue += coldValue;
      totalInvested += Number(portfolio.totalInvested);
    });

    const totalPnL = totalValue - totalInvested;
    const totalPnLPercentage = totalInvested > 0 ? (totalPnL / totalInvested) * 100 : 0;

    // Mock daily change (would come from price history)
    const dailyChange = totalValue * 0.023; // Mock 2.3% daily gain
    const dailyChangePercentage = 2.3;

    const wealthSummary = {
      totalValue: Math.round(totalValue * 100) / 100,
      hotWalletValue: Math.round(hotWalletValue * 100) / 100,
      coldVaultValue: Math.round(coldVaultValue * 100) / 100,
      totalPnL: Math.round(totalPnL * 100) / 100,
      totalPnLPercentage: Math.round(totalPnLPercentage * 100) / 100,
      dailyChange: Math.round(dailyChange * 100) / 100,
      dailyChangePercentage: dailyChangePercentage
    };

    return NextResponse.json(wealthSummary);
  } catch (error) {
    console.error("Wealth fetch error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

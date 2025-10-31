
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

    const trades = await prisma.trade.findMany({
      where: { userId: session.user.id },
      orderBy: { createdAt: 'desc' },
      take: 50
    });

    const formattedTrades = trades.map(trade => ({
      id: trade.id,
      asset: trade.asset,
      type: trade.type,
      side: trade.side,
      amount: Number(trade.amount),
      price: Number(trade.price),
      fee: Number(trade.fee),
      pnl: trade.pnl ? Number(trade.pnl) : null,
      strategy: trade.strategy,
      status: trade.status,
      executedAt: trade.executedAt?.toISOString(),
      createdAt: trade.createdAt.toISOString()
    }));

    return NextResponse.json(formattedTrades);
  } catch (error) {
    console.error("Trades fetch error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { asset, type, side, amount, price, strategy } = await req.json();

    if (!asset || !type || !side || !amount) {
      return NextResponse.json(
        { error: "Missing required fields" },
        { status: 400 }
      );
    }

    const trade = await prisma.trade.create({
      data: {
        userId: session.user.id,
        asset,
        type,
        side,
        amount,
        quantity: amount, // Add required quantity field
        price: price || 0,
        strategy: strategy || 'MANUAL',
        status: 'PENDING'
      }
    });

    return NextResponse.json({
      id: trade.id,
      asset: trade.asset,
      type: trade.type,
      side: trade.side,
      amount: Number(trade.amount),
      price: Number(trade.price),
      strategy: trade.strategy,
      status: trade.status,
      createdAt: trade.createdAt.toISOString()
    });
  } catch (error) {
    console.error("Trade creation error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

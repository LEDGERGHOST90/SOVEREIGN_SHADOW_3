
import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { prisma } from '@/lib/db';
import { HybridSiphonEngine } from '@/lib/siphon-engine';

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { profitAmount, assetSymbol, source } = await req.json();

    if (!profitAmount || profitAmount <= 0) {
      return NextResponse.json({ error: 'Invalid profit amount' }, { status: 400 });
    }

    const siphonEngine = new HybridSiphonEngine();
    const config = await HybridSiphonEngine.getDefaultConfig(session.user.id);

    // Execute the hybrid siphon logic
    const result = await siphonEngine.executeSiphon(profitAmount, config);

    // Update portfolio balances if siphon was triggered
    if (result.triggered && assetSymbol) {
      const portfolio = await prisma.portfolio.findFirst({
        where: {
          userId: session.user.id,
          asset: assetSymbol
        }
      });

      if (portfolio) {
        // Move siphoned amount from hot to cold balance
        await prisma.portfolio.update({
          where: { id: portfolio.id },
          data: {
            hotBalance: {
              decrement: result.siphonedAmount
            },
            coldBalance: {
              increment: result.siphonedAmount
            }
          }
        });
      }
    }

    return NextResponse.json({
      success: true,
      result
    });

  } catch (error) {
    console.error('Siphon execution error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Get siphon configuration and recent logs
    const config = await HybridSiphonEngine.getDefaultConfig(session.user.id);
    
    const recentSiphons = await prisma.vaultLog.findMany({
      where: {
        userId: session.user.id,
        type: 'SIPHON'
      },
      orderBy: { createdAt: 'desc' },
      take: 10
    });

    const totalSiphoned = await prisma.vaultLog.aggregate({
      where: {
        userId: session.user.id,
        type: 'SIPHON',
        status: 'COMPLETED'
      },
      _sum: { amount: true }
    });

    return NextResponse.json({
      config,
      recentSiphons,
      totalSiphoned: totalSiphoned._sum.amount || 0,
      status: 'ARMED'
    });

  } catch (error) {
    console.error('Siphon status error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}


/**
 * 🎯 RWA STRATEGY GENERATION API
 * Oracle-inspired strategic allocation recommendations
 */

import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { RWAEngineFactory } from '@/lib/rwa-integrations';
import { prisma } from '@/lib/db';

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession();
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const user = await prisma.user.findUnique({
      where: { email: session.user.email },
    });

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    const body = await request.json();
    const { portfolioValue, riskTolerance } = body;

    if (!portfolioValue || !riskTolerance) {
      return NextResponse.json({ 
        error: 'Missing required parameters: portfolioValue, riskTolerance' 
      }, { status: 400 });
    }

    // Create RWA engine instance
    const rwaEngine = RWAEngineFactory.createEngine(user.id);

    // Generate Oracle-inspired strategy
    const strategy = await rwaEngine.generateOracleStrategy(portfolioValue, riskTolerance);

    // Generate rebalancing plan
    const rebalancePlan = await rwaEngine.generateRebalancingPlan(strategy);

    return NextResponse.json({
      success: true,
      data: {
        strategy,
        rebalancePlan,
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    console.error('RWA strategy error:', error);
    return NextResponse.json({ 
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

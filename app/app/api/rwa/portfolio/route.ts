
// Oracle-Inspired RWA Portfolio API
// Real-World Asset portfolio management inspired by Larry Ellison's systematic approach

import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { ondoClient, calculateWealthSurge } from '@/lib/ondo';
import { RWAVaultManager, calculateOracleScore } from '@/lib/rwa-vault-manager';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const userId = session.user.id;
    
    // Get RWA portfolio data
    const portfolio = await ondoClient.getPortfolioData(userId);
    
    // Get wealth surge metrics (Oracle-inspired)
    const wealthMetrics = await calculateWealthSurge(userId);
    
    // Get Oracle score
    const oracleScore = await calculateOracleScore(userId);
    
    // Get vault performance
    const vaultManager = new RWAVaultManager(userId);
    const vaultPerformance = await vaultManager.getVaultPerformance();

    return NextResponse.json({
      success: true,
      data: {
        portfolio,
        wealthMetrics,
        oracleScore,
        vaultPerformance,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('RWA Portfolio API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch RWA portfolio data' },
      { status: 500 }
    );
  }
}

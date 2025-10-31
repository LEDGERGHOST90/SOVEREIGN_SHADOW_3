
// Oracle Wealth Metrics API - Inspired by Larry Ellison's $393B milestone

import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';

export const dynamic = 'force-dynamic';
import { calculateWealthSurge } from '@/lib/ondo';
import { calculateOracleScore } from '@/lib/rwa-vault-manager';
import { prisma } from '@/lib/db';

export async function GET() {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const userId = session.user.id;
    
    // Get Oracle-inspired wealth metrics
    const wealthSurge = await calculateWealthSurge(userId);
    const oracleScore = await calculateOracleScore(userId);
    
    // Get wealth milestones (recent achievements)
    const milestones = await prisma.wealthMilestone.findMany({
      where: { userId },
      orderBy: { achievedAt: 'desc' },
      take: 10
    });

    // Calculate Oracle comparison metrics
    const oracleComparison = {
      // Larry Ellison's historic metrics for comparison
      ellisonNetWorth: 393000000000, // $393B at peak
      ellisonDayGain: 101000000000,  // $101B single-day gain
      ellisonGainPercent: 34.7,      // 34.7% single-day gain
      
      // User's metrics vs Oracle
      netWorthRatio: wealthSurge.netWorth / 393000000000,
      dayGainRatio: wealthSurge.largestSingleDayGain / 101000000000,
      efficiencyScore: oracleScore.score,
      
      // Progress milestones
      nextMilestone: getNextWealthMilestone(wealthSurge.netWorth),
      daysToMilestone: estimateDaysToMilestone(wealthSurge.netWorth, wealthSurge.dayChange)
    };

    return NextResponse.json({
      success: true,
      data: {
        wealthSurge,
        oracleScore,
        milestones: milestones.map(m => ({
          id: m.id,
          type: m.milestoneType,
          amount: parseFloat(m.amount.toString()),
          trigger: m.trigger,
          achievedAt: m.achievedAt,
          dayGain: parseFloat(m.dayGain.toString()),
          percentGain: parseFloat(m.percentGain.toString())
        })),
        oracleComparison,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('Oracle Metrics API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch Oracle metrics' },
      { status: 500 }
    );
  }
}

function getNextWealthMilestone(currentNetWorth: number): { amount: number; name: string } {
  const milestones = [
    { amount: 100000, name: "$100K Sovereign" },
    { amount: 500000, name: "$500K Commander" },
    { amount: 1000000, name: "$1M Millionaire" },
    { amount: 5000000, name: "$5M Elite" },
    { amount: 10000000, name: "$10M Decamillionaire" },
    { amount: 50000000, name: "$50M Ultra High Net Worth" },
    { amount: 100000000, name: "$100M Centimillionaire" },
    { amount: 1000000000, name: "$1B Billionaire" },
    { amount: 10000000000, name: "$10B Oracle Apprentice" },
    { amount: 100000000000, name: "$100B Oracle Elite" },
    { amount: 393000000000, name: "$393B Oracle Master (Ellison Level)" }
  ];

  return milestones.find(m => m.amount > currentNetWorth) || 
         { amount: 393000000000, name: "Oracle Master Level" };
}

function estimateDaysToMilestone(currentValue: number, dailyGain: number): number {
  if (dailyGain <= 0) return Infinity;
  
  const nextMilestone = getNextWealthMilestone(currentValue);
  const remaining = nextMilestone.amount - currentValue;
  
  return Math.ceil(remaining / dailyGain);
}

import { NextRequest, NextResponse } from 'next/server';
import { ledgerLiveMetrics } from '@/lib/ledger/ledger-live-metrics';
import { multiExchangeArbitrage } from '@/lib/trading/multi-exchange-arbitrage';
import { positionSizer } from '@/lib/trading/position-sizer';
import { sessionManager } from '@/lib/auth/session-manager';
import { complianceLogger } from '@/lib/logging/compliance-logger';

export async function GET(request: NextRequest) {
  try {
    // Get comprehensive system status
    const ledgerMetrics = ledgerLiveMetrics.getMetrics();
    const ledgerSecurity = ledgerLiveMetrics.getSecuritySummary();
    const arbitrageStats = multiExchangeArbitrage.getStatistics();
    const positionStats = positionSizer.getStats();
    const sessionStats = sessionManager.getSessionStats();
    const loggingStats = complianceLogger.getStats();

    // Calculate overall sovereign status
    const sovereignStatus = calculateSovereignStatus({
      ledgerSecurity,
      arbitrageStats,
      positionStats,
      sessionStats,
      loggingStats
    });

    return NextResponse.json({
      success: true,
      sovereignStatus: {
        level: sovereignStatus.level,
        score: sovereignStatus.score,
        message: sovereignStatus.message,
        timestamp: new Date().toISOString()
      },
      components: {
        ledgerLive: {
          security: ledgerSecurity,
          metrics: {
            totalValue: ledgerMetrics.wealthProtection.assetsUnderManagement,
            coldStoragePercentage: ledgerMetrics.wealthProtection.coldStoragePercentage,
            connectedDevices: ledgerLiveMetrics.getConnectedDevices().length,
            hardwareConfirmationRate: ledgerMetrics.security.hardwareConfirmationRate
          }
        },
        trading: {
          arbitrage: {
            opportunities: arbitrageStats.totalOpportunities,
            dailyPnL: arbitrageStats.dailyPnL,
            averageProfit: arbitrageStats.averageProfit
          },
          positionSizing: {
            totalWealth: positionStats.totalWealth,
            totalPositions: positionStats.totalPositions,
            averageConfidence: positionStats.averageConfidence
          }
        },
        security: {
          sessions: {
            active: sessionStats.activeSessions,
            averageAge: sessionStats.averageSessionAge
          },
          logging: {
            totalLogs: loggingStats.totalLogs,
            tradingDecisions: loggingStats.tradingDecisions
          }
        }
      },
      recommendations: sovereignStatus.recommendations,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Sovereign status error:', error);
    return NextResponse.json({
      success: false,
      error: 'Failed to retrieve sovereign status',
      timestamp: new Date().toISOString()
    }, { status: 500 });
  }
}

function calculateSovereignStatus(components: any) {
  let score = 0;
  let maxScore = 0;
  const recommendations: string[] = [];

  // Ledger Live Security (40% weight)
  const ledgerScore = components.ledgerSecurity.overallScore;
  score += (ledgerScore / 100) * 40;
  maxScore += 40;

  if (ledgerScore < 100) {
    recommendations.push('Optimize Ledger Live security configuration');
  }

  // Arbitrage System (25% weight)
  const arbitrageScore = Math.min(100, (components.arbitrageStats.totalOpportunities * 10) + 50);
  score += (arbitrageScore / 100) * 25;
  maxScore += 25;

  if (components.arbitrageStats.dailyPnL < 0) {
    recommendations.push('Review arbitrage strategy - negative daily P&L detected');
  }

  // Position Sizing (20% weight)
  const positionScore = Math.min(100, (components.positionStats.averageConfidence || 75));
  score += (positionScore / 100) * 20;
  maxScore += 20;

  if (components.positionStats.averageConfidence < 70) {
    recommendations.push('Improve trading confidence - consider strategy optimization');
  }

  // Session Security (15% weight)
  const sessionScore = components.sessionStats.activeSessions > 0 ? 100 : 0;
  score += (sessionScore / 100) * 15;
  maxScore += 15;

  // Calculate final percentage
  const finalScore = maxScore > 0 ? Math.round((score / maxScore) * 100) : 0;

  // Determine sovereign level
  let level: string;
  let message: string;

  if (finalScore >= 95) {
    level = 'SOVEREIGN';
    message = 'Ultimate crypto trading sovereignty achieved - all systems optimal';
  } else if (finalScore >= 85) {
    level = 'EXCELLENT';
    message = 'High-performance trading system with robust security';
  } else if (finalScore >= 70) {
    level = 'GOOD';
    message = 'Solid trading system with room for optimization';
  } else if (finalScore >= 50) {
    level = 'FAIR';
    message = 'Basic trading system - improvements recommended';
  } else {
    level = 'NEEDS_ATTENTION';
    message = 'System requires immediate attention and optimization';
  }

  return {
    level,
    score: finalScore,
    message,
    recommendations
  };
}

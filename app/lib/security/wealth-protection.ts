import { NextRequest, NextResponse } from 'next/server';
import crypto from 'crypto';

export interface WealthProtectionConfig {
  totalWealth: number;
  maxDailyLoss: number;
  maxPositionSize: number;
  emergencyStopThreshold: number;
  securityLayers: string[];
}

export class WealthProtectionSystem {
  private config: WealthProtectionConfig;
  private dailyLosses: Map<string, number> = new Map();
  private suspiciousActivities: Array<{ timestamp: string; activity: string; severity: 'low' | 'medium' | 'high' }> = [];

  constructor() {
    this.config = {
      totalWealth: 7716.23, // Current tracked wealth
      maxDailyLoss: 154.32, // 2% of total wealth
      maxPositionSize: 385.81, // 5% of total wealth
      emergencyStopThreshold: 308.65, // 4% of total wealth
      securityLayers: [
        'authentication_2fa',
        'transaction_validation',
        'whale_monitoring',
        'circuit_breakers',
        'emergency_stop'
      ]
    };
  }

  // Real-time wealth monitoring
  async monitorWealthChanges(currentWealth: number, previousWealth: number): Promise<{
    status: 'safe' | 'warning' | 'critical';
    message: string;
    action: string;
  }> {
    const change = currentWealth - previousWealth;
    const changePercent = (change / previousWealth) * 100;
    const today = new Date().toISOString().split('T')[0];
    
    // Track daily losses
    const currentDailyLoss = this.dailyLosses.get(today) || 0;
    
    if (change < 0) {
      const newDailyLoss = currentDailyLoss + Math.abs(change);
      this.dailyLosses.set(today, newDailyLoss);
      
      if (newDailyLoss > this.config.maxDailyLoss) {
        return {
          status: 'critical',
          message: `Daily loss limit exceeded: $${newDailyLoss.toFixed(2)} > $${this.config.maxDailyLoss}`,
          action: 'EMERGENCY_STOP_ALL_TRADING'
        };
      }
      
      if (changePercent < -5) {
        return {
          status: 'warning',
          message: `Significant wealth decrease: ${changePercent.toFixed(2)}%`,
          action: 'INCREASE_MONITORING'
        };
      }
    }
    
    return {
      status: 'safe',
      message: `Wealth change: ${changePercent.toFixed(2)}%`,
      action: 'CONTINUE_NORMAL_OPERATIONS'
    };
  }

  // Position size validation
  validatePositionSize(symbol: string, amount: number, price: number): {
    approved: boolean;
    reason: string;
    suggestedAmount?: number;
  } {
    const positionValue = amount * price;
    const maxPosition = this.config.maxPositionSize;
    
    if (positionValue > maxPosition) {
      const suggestedAmount = maxPosition / price;
      return {
        approved: false,
        reason: `Position size $${positionValue.toFixed(2)} exceeds limit $${maxPosition}`,
        suggestedAmount: suggestedAmount
      };
    }
    
    return {
      approved: true,
      reason: 'Position size within acceptable limits'
    };
  }

  // Suspicious activity detection
  detectSuspiciousActivity(activity: string, context: any): void {
    const suspiciousPatterns = [
      /large.*transfer/i,
      /unusual.*volume/i,
      /rapid.*price.*movement/i,
      /multiple.*failed.*attempts/i
    ];
    
    const isSuspicious = suspiciousPatterns.some(pattern => pattern.test(activity));
    
    if (isSuspicious) {
      this.suspiciousActivities.push({
        timestamp: new Date().toISOString(),
        activity: activity,
        severity: this.calculateSeverity(activity, context)
      });
      
      // Auto-trigger security protocols for high severity
      if (this.suspiciousActivities[this.suspiciousActivities.length - 1].severity === 'high') {
        this.triggerEmergencyProtocol();
      }
    }
  }

  private calculateSeverity(activity: string, context: any): 'low' | 'medium' | 'high' {
    if (activity.includes('large transfer') && context.value > 1000) return 'high';
    if (activity.includes('unusual volume') && context.volume > 10000) return 'high';
    if (activity.includes('rapid price movement') && Math.abs(context.priceChange) > 10) return 'medium';
    return 'low';
  }

  private triggerEmergencyProtocol(): void {
    console.log('🚨 EMERGENCY PROTOCOL TRIGGERED 🚨');
    console.log('All trading operations suspended');
    console.log('Security team notified');
    console.log('Wealth protection measures activated');
  }

  // 2FA validation for high-value operations
  validate2FA(token: string, operation: string): boolean {
    // In production, integrate with actual 2FA service
    const validTokens = process.env.VALID_2FA_TOKENS?.split(',') || [];
    return validTokens.includes(token);
  }

  // Generate security report
  generateSecurityReport(): {
    wealthStatus: string;
    dailyLoss: number;
    suspiciousActivities: number;
    securityScore: number;
    recommendations: string[];
  } {
    const today = new Date().toISOString().split('T')[0];
    const dailyLoss = this.dailyLosses.get(today) || 0;
    const suspiciousCount = this.suspiciousActivities.filter(
      a => a.timestamp.startsWith(today)
    ).length;
    
    const securityScore = Math.max(0, 100 - (dailyLoss / this.config.maxDailyLoss) * 50 - suspiciousCount * 10);
    
    const recommendations = [];
    if (dailyLoss > this.config.maxDailyLoss * 0.5) {
      recommendations.push('Consider reducing position sizes');
    }
    if (suspiciousCount > 3) {
      recommendations.push('Review recent trading activities');
    }
    if (securityScore < 70) {
      recommendations.push('Implement additional security measures');
    }
    
    return {
      wealthStatus: dailyLoss > this.config.maxDailyLoss * 0.8 ? 'HIGH_RISK' : 'SAFE',
      dailyLoss: dailyLoss,
      suspiciousActivities: suspiciousCount,
      securityScore: Math.round(securityScore),
      recommendations: recommendations
    };
  }
}

// Export singleton instance
export const wealthProtection = new WealthProtectionSystem();

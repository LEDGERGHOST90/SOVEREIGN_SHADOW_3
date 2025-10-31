
'use client';

// Oracle Metrics Display Component - Ellison's $393B Inspired Tracking

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Crown, 
  TrendingUp, 
  Target, 
  Zap, 
  Calendar,
  Award
} from 'lucide-react';
import { formatCurrency, formatPercent } from '@/lib/utils';

interface OracleMetrics {
  wealthSurge: {
    netWorth: number;
    dayChange: number;
    percentChange: number;
    largestSingleDayGain: number;
    oracleInspiredScore: number;
  };
  oracleComparison: {
    ellisonNetWorth: number;
    ellisonDayGain: number;
    ellisonGainPercent: number;
    netWorthRatio: number;
    dayGainRatio: number;
    nextMilestone: {
      amount: number;
      name: string;
    };
    daysToMilestone: number;
  };
  milestones: Array<{
    id: string;
    type: string;
    amount: number;
    trigger: string;
    achievedAt: string;
    dayGain: number;
    percentGain: number;
  }>;
}

export default function OracleMetricsCard() {
  const [metrics, setMetrics] = useState<OracleMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOracleMetrics();
  }, []);

  const fetchOracleMetrics = async () => {
    try {
      const response = await fetch('/api/rwa/oracle-metrics');
      const data = await response.json();
      
      if (data.success) {
        setMetrics(data.data);
      }
    } catch (error) {
      console.error('Error fetching Oracle metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-8 bg-gray-200 rounded w-3/4"></div>
            <div className="space-y-2">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!metrics) return null;

  const progressToOracle = (metrics.oracleComparison.netWorthRatio * 100);
  const milestoneProgress = metrics.oracleComparison.daysToMilestone === Infinity ? 0 : 
    Math.max(0, 100 - (metrics.oracleComparison.daysToMilestone / 365) * 100);

  return (
    <div className="space-y-6">
      {/* Oracle Progress Card */}
      <Card className="border-2 border-yellow-200 bg-gradient-to-br from-yellow-50 to-amber-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-amber-800">
            <Crown className="h-6 w-6" />
            Oracle Wealth Progress
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="text-sm text-gray-600 mb-2">Net Worth vs Oracle ($393B)</div>
              <Progress 
                value={Math.min(100, progressToOracle)} 
                className="h-3"
              />
              <div className="text-xs text-gray-500 mt-1">
                {progressToOracle.toFixed(6)}% of Oracle's peak
              </div>
            </div>
            
            <div>
              <div className="text-sm text-gray-600 mb-2">Next Milestone Progress</div>
              <Progress 
                value={milestoneProgress} 
                className="h-3"
              />
              <div className="text-xs text-gray-500 mt-1">
                {metrics.oracleComparison.nextMilestone.name}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-green-600">
                ${formatCurrency(metrics.wealthSurge.netWorth)}
              </div>
              <div className="text-sm text-gray-600">Your Net Worth</div>
            </div>
            
            <div>
              <div className="text-2xl font-bold text-blue-600">
                ${formatCurrency(metrics.wealthSurge.largestSingleDayGain)}
              </div>
              <div className="text-sm text-gray-600">Best Single Day</div>
              <div className="text-xs text-gray-500">
                vs Oracle's $101B record
              </div>
            </div>
            
            <div>
              <div className="text-2xl font-bold text-purple-600">
                {metrics.oracleComparison.daysToMilestone === Infinity ? '∞' : metrics.oracleComparison.daysToMilestone}
              </div>
              <div className="text-sm text-gray-600">
                Days to {metrics.oracleComparison.nextMilestone.name}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Recent Milestones */}
      {metrics.milestones.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Award className="h-5 w-5" />
              Recent Achievements
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {metrics.milestones.slice(0, 5).map((milestone) => (
                <div key={milestone.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                      {milestone.type === 'DAILY_GAIN_RECORD' && <Zap className="h-4 w-4 text-blue-600" />}
                      {milestone.type === 'NET_WORTH_MILESTONE' && <Target className="h-4 w-4 text-green-600" />}
                      {milestone.type === 'RWA_YIELD_MILESTONE' && <TrendingUp className="h-4 w-4 text-purple-600" />}
                      {!['DAILY_GAIN_RECORD', 'NET_WORTH_MILESTONE', 'RWA_YIELD_MILESTONE'].includes(milestone.type) && 
                        <Award className="h-4 w-4 text-gray-600" />}
                    </div>
                    <div>
                      <div className="font-medium text-sm">
                        {milestone.type.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                      </div>
                      <div className="text-xs text-gray-600">
                        {milestone.trigger}
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="font-semibold text-sm">
                      ${formatCurrency(milestone.amount)}
                    </div>
                    <div className="text-xs text-gray-500">
                      {new Date(milestone.achievedAt).toLocaleDateString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Oracle Comparison Stats */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Crown className="h-5 w-5 text-yellow-600" />
            Oracle Benchmarks
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
              <div className="text-lg font-bold text-blue-600">
                ${formatCurrency(metrics.oracleComparison.ellisonNetWorth)}
              </div>
              <div className="text-sm text-gray-600">Larry Ellison's Peak</div>
              <div className="text-xs text-gray-500">September 2025</div>
            </div>
            
            <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
              <div className="text-lg font-bold text-green-600">
                ${formatCurrency(metrics.oracleComparison.ellisonDayGain)}
              </div>
              <div className="text-sm text-gray-600">Historic Single Day</div>
              <div className="text-xs text-gray-500">Largest gain ever recorded</div>
            </div>
            
            <div className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
              <div className="text-lg font-bold text-purple-600">
                +{formatPercent(metrics.oracleComparison.ellisonGainPercent)}%
              </div>
              <div className="text-sm text-gray-600">Peak Day Percentage</div>
              <div className="text-xs text-gray-500">Oracle AI Infrastructure boom</div>
            </div>
          </div>
          
          <div className="mt-4 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
            <div className="flex items-center gap-2 mb-2">
              <Crown className="h-4 w-4 text-yellow-600" />
              <span className="font-semibold text-yellow-800">Oracle Strategy Insights</span>
            </div>
            <div className="text-sm text-yellow-700 space-y-1">
              <div>• Systematic infrastructure focus (AI, cloud, database)</div>
              <div>• Long-term asset accumulation strategy</div>
              <div>• Diversified real-world asset allocation</div>
              <div>• Automated wealth preservation systems</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

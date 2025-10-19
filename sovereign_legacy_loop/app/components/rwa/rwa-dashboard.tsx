
'use client';

// Oracle-Inspired RWA Dashboard Component
// Real-World Asset management inspired by Larry Ellison's $393B wealth strategy

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Target, 
  Crown, 
  Zap,
  Building2,
  Shield,
  BarChart3,
  Trophy,
  ArrowUpRight,
  Coins
} from 'lucide-react';
import { formatCurrency, formatPercent } from '@/lib/utils';
import toast from 'react-hot-toast';

interface RWAMetrics {
  portfolio: {
    totalValue: number;
    assets: any[];
    dayChange: number;
    dayChangePercent: number;
  };
  wealthMetrics: {
    netWorth: number;
    dayChange: number;
    percentChange: number;
    largestSingleDayGain: number;
    oracleInspiredScore: number;
  };
  oracleScore: {
    score: number;
    breakdown: {
      diversification: number;
      rwaAllocation: number;
      yieldGeneration: number;
      systematicApproach: number;
    };
    recommendations: string[];
  };
  vaultPerformance: any[];
}

interface OracleComparison {
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
}

export default function RWADashboard() {
  const [metrics, setMetrics] = useState<RWAMetrics | null>(null);
  const [oracleComparison, setOracleComparison] = useState<OracleComparison | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchRWAData();
    fetchOracleMetrics();
  }, []);

  const fetchRWAData = async () => {
    try {
      const response = await fetch('/api/rwa/portfolio');
      const data = await response.json();
      
      if (data.success) {
        setMetrics(data.data);
      } else {
        toast.error('Failed to load RWA data');
      }
    } catch (error) {
      console.error('Error fetching RWA data:', error);
      toast.error('Error loading RWA portfolio');
    }
  };

  const fetchOracleMetrics = async () => {
    try {
      const response = await fetch('/api/rwa/oracle-metrics');
      const data = await response.json();
      
      if (data.success) {
        setOracleComparison(data.data.oracleComparison);
      }
    } catch (error) {
      console.error('Error fetching Oracle metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  const createOracleVault = async (strategy: string) => {
    try {
      const response = await fetch('/api/rwa/vaults', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'create',
          name: `Oracle ${strategy} Vault`,
          strategy: strategy.toUpperCase()
        })
      });

      const data = await response.json();
      
      if (data.success) {
        toast.success(`Oracle ${strategy} Vault created successfully!`);
        fetchRWAData(); // Refresh data
      } else {
        toast.error('Failed to create vault');
      }
    } catch (error) {
      console.error('Error creating vault:', error);
      toast.error('Error creating Oracle vault');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Loading Oracle RWA Engine...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Oracle Header */}
      <div className="bg-gradient-to-r from-blue-900 to-purple-900 p-6 rounded-xl text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold flex items-center gap-3">
              <Crown className="h-8 w-8 text-yellow-400" />
              Oracle RWA Engine
            </h1>
            <p className="text-blue-200 mt-2">
              Real-World Asset management inspired by Larry Ellison's $393B wealth strategy
            </p>
          </div>
          {oracleComparison && (
            <div className="text-right">
              <div className="text-sm text-blue-200">Progress to Oracle Level</div>
              <div className="text-2xl font-bold">
                {(oracleComparison.netWorthRatio * 100).toFixed(6)}%
              </div>
              <div className="text-xs text-blue-300">
                ${formatCurrency(oracleComparison.nextMilestone.amount)} next milestone
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Oracle Score Card */}
      {metrics?.oracleScore && (
        <Card className="border-2 border-yellow-200 bg-gradient-to-br from-yellow-50 to-amber-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-amber-800">
              <Trophy className="h-6 w-6" />
              Oracle Wealth Score: {metrics.oracleScore.score}/100
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {metrics.oracleScore.breakdown.diversification}
                </div>
                <div className="text-sm text-gray-600">Diversification</div>
                <Progress 
                  value={(metrics.oracleScore.breakdown.diversification / 25) * 100} 
                  className="mt-2"
                />
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {metrics.oracleScore.breakdown.rwaAllocation}
                </div>
                <div className="text-sm text-gray-600">RWA Allocation</div>
                <Progress 
                  value={(metrics.oracleScore.breakdown.rwaAllocation / 25) * 100} 
                  className="mt-2"
                />
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {metrics.oracleScore.breakdown.yieldGeneration}
                </div>
                <div className="text-sm text-gray-600">Yield Generation</div>
                <Progress 
                  value={(metrics.oracleScore.breakdown.yieldGeneration / 25) * 100} 
                  className="mt-2"
                />
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {metrics.oracleScore.breakdown.systematicApproach}
                </div>
                <div className="text-sm text-gray-600">Systematic Approach</div>
                <Progress 
                  value={(metrics.oracleScore.breakdown.systematicApproach / 25) * 100} 
                  className="mt-2"
                />
              </div>
            </div>
            
            {metrics.oracleScore.recommendations.length > 0 && (
              <div className="bg-amber-100 p-4 rounded-lg">
                <h4 className="font-semibold text-amber-800 mb-2">Oracle Recommendations:</h4>
                <ul className="space-y-1">
                  {metrics.oracleScore.recommendations.map((rec, idx) => (
                    <li key={idx} className="text-sm text-amber-700 flex items-center gap-2">
                      <ArrowUpRight className="h-4 w-4" />
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Portfolio Overview</TabsTrigger>
          <TabsTrigger value="assets">RWA Assets</TabsTrigger>
          <TabsTrigger value="vaults">Oracle Vaults</TabsTrigger>
          <TabsTrigger value="analytics">Wealth Analytics</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {/* Wealth Metrics */}
          {metrics?.wealthMetrics && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total Net Worth</CardTitle>
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    ${formatCurrency(metrics.wealthMetrics.netWorth)}
                  </div>
                  <div className={`text-xs flex items-center ${
                    metrics.wealthMetrics.dayChange >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {metrics.wealthMetrics.dayChange >= 0 ? (
                      <TrendingUp className="h-3 w-3 mr-1" />
                    ) : (
                      <TrendingDown className="h-3 w-3 mr-1" />
                    )}
                    ${formatCurrency(Math.abs(metrics.wealthMetrics.dayChange))} today
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">RWA Portfolio Value</CardTitle>
                  <Building2 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    ${formatCurrency(metrics.portfolio.totalValue)}
                  </div>
                  <div className={`text-xs flex items-center ${
                    metrics.portfolio.dayChange >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {metrics.portfolio.dayChange >= 0 ? (
                      <TrendingUp className="h-3 w-3 mr-1" />
                    ) : (
                      <TrendingDown className="h-3 w-3 mr-1" />
                    )}
                    {formatPercent(metrics.portfolio.dayChangePercent)}% today
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Largest Daily Gain</CardTitle>
                  <Zap className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">
                    ${formatCurrency(metrics.wealthMetrics.largestSingleDayGain)}
                  </div>
                  <div className="text-xs text-gray-600">
                    Personal best vs Ellison's $101B
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Oracle Score</CardTitle>
                  <Target className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-purple-600">
                    {metrics.wealthMetrics.oracleInspiredScore}/100
                  </div>
                  <Progress 
                    value={metrics.wealthMetrics.oracleInspiredScore} 
                    className="mt-2"
                  />
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        <TabsContent value="assets" className="space-y-6">
          {/* RWA Assets */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Coins className="h-6 w-6" />
                Ondo Finance Assets
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!metrics || metrics.portfolio.assets.length === 0 ? (
                <div className="text-center py-12">
                  <Building2 className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-600 mb-2">No RWA Assets Yet</h3>
                  <p className="text-gray-500 mb-6">
                    Start building your Oracle-inspired portfolio with tokenized real-world assets
                  </p>
                  <div className="flex gap-4 justify-center">
                    <Button 
                      onClick={() => createOracleVault('Conservative')}
                      className="bg-blue-600 hover:bg-blue-700"
                    >
                      <Shield className="h-4 w-4 mr-2" />
                      Conservative Vault
                    </Button>
                    <Button 
                      onClick={() => createOracleVault('Oracle_Inspired')}
                      className="bg-purple-600 hover:bg-purple-700"
                    >
                      <Crown className="h-4 w-4 mr-2" />
                      Oracle Strategy
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {metrics.portfolio.assets.map((asset, idx) => (
                    <div key={idx} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                          <Building2 className="h-6 w-6 text-blue-600" />
                        </div>
                        <div>
                          <div className="font-semibold">{asset.name}</div>
                          <div className="text-sm text-gray-500">
                            {asset.symbol} • {formatPercent(asset.yield)}% yield
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">
                          ${formatCurrency(asset.currentPrice)}
                        </div>
                        <Badge variant="secondary">
                          {asset.type.replace('_', ' ')}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="vaults" className="space-y-6">
          {/* Vault Performance */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-6 w-6" />
                Oracle RWA Vaults
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!metrics || metrics.vaultPerformance.length === 0 ? (
                <div className="text-center py-12">
                  <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-600 mb-2">No Active Vaults</h3>
                  <p className="text-gray-500 mb-6">
                    Create your first Oracle-inspired RWA vault for systematic wealth preservation
                  </p>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    {['Conservative', 'Balanced', 'Growth', 'Oracle_Inspired'].map((strategy) => (
                      <Button
                        key={strategy}
                        onClick={() => createOracleVault(strategy)}
                        variant="outline"
                        className="p-4 h-auto flex flex-col items-center gap-2"
                      >
                        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                          {strategy === 'Conservative' && <Shield className="h-4 w-4 text-white" />}
                          {strategy === 'Balanced' && <Target className="h-4 w-4 text-white" />}
                          {strategy === 'Growth' && <TrendingUp className="h-4 w-4 text-white" />}
                          {strategy === 'Oracle_Inspired' && <Crown className="h-4 w-4 text-white" />}
                        </div>
                        <div className="text-sm font-medium">
                          {strategy.replace('_', ' ')}
                        </div>
                      </Button>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {metrics.vaultPerformance.map((vault) => (
                    <div key={vault.vaultId} className="p-4 border rounded-lg">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h4 className="font-semibold">{vault.name}</h4>
                          <div className="text-sm text-gray-500">
                            {vault.strategy.replace('_', ' ')} Strategy
                          </div>
                        </div>
                        <Badge 
                          variant={vault.riskScore < 40 ? 'secondary' : vault.riskScore < 70 ? 'default' : 'destructive'}
                        >
                          Risk: {vault.riskScore}/100
                        </Badge>
                      </div>
                      
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <div className="text-sm text-gray-500">Current Value</div>
                          <div className="font-semibold">
                            ${formatCurrency(vault.currentValue)}
                          </div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-500">Day Change</div>
                          <div className={`font-semibold ${
                            vault.dayChange >= 0 ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {vault.dayChange >= 0 ? '+' : ''}${formatCurrency(vault.dayChange)}
                          </div>
                        </div>
                        <div>
                          <div className="text-sm text-gray-500">Average Yield</div>
                          <div className="font-semibold text-purple-600">
                            {formatPercent(vault.averageYield)}%
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-6">
          {/* Oracle Comparison */}
          {oracleComparison && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-6 w-6" />
                  Oracle Wealth Comparison
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div>
                      <div className="text-sm text-gray-500">Larry Ellison's Peak Net Worth</div>
                      <div className="text-2xl font-bold">
                        ${formatCurrency(oracleComparison.ellisonNetWorth)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Historic Single-Day Gain</div>
                      <div className="text-xl font-bold text-green-600">
                        ${formatCurrency(oracleComparison.ellisonDayGain)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Peak Daily Gain %</div>
                      <div className="text-xl font-bold text-green-600">
                        +{formatPercent(oracleComparison.ellisonGainPercent)}%
                      </div>
                    </div>
                  </div>
                  
                  <div className="space-y-4">
                    <div>
                      <div className="text-sm text-gray-500">Your Next Milestone</div>
                      <div className="text-lg font-bold text-purple-600">
                        {oracleComparison.nextMilestone.name}
                      </div>
                      <div className="text-sm text-gray-500">
                        ${formatCurrency(oracleComparison.nextMilestone.amount)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Estimated Days to Milestone</div>
                      <div className="text-xl font-bold">
                        {oracleComparison.daysToMilestone === Infinity ? '∞' : oracleComparison.daysToMilestone} days
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

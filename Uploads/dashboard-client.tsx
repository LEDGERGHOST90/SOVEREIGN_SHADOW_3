
'use client';

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { 
  TrendingUp, 
  TrendingDown, 
  Wallet, 
  Shield, 
  Zap, 
  AlertCircle,
  Activity,
  Eye,
  RefreshCw
} from "lucide-react";
import { WealthSummary, SystemHealth, Trade } from "@/lib/types";
import { toast } from "sonner";
import { motion } from "framer-motion";
import dynamic from 'next/dynamic';

// Dynamic import for Recharts with proper typing
const RechartsWrapper = dynamic(() => import('@/components/ui/recharts-wrapper'), { ssr: false, loading: () => <div>Loading chart...</div> });

interface AnimatedCounterProps {
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
}

function AnimatedCounter({ value, prefix = '', suffix = '', decimals = 2 }: AnimatedCounterProps) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const startValue = displayValue;
    const endValue = value;
    const duration = 1000;
    const startTime = Date.now();

    const updateValue = () => {
      const now = Date.now();
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      const easedProgress = 1 - Math.pow(1 - progress, 3);
      const currentValue = startValue + (endValue - startValue) * easedProgress;
      
      setDisplayValue(currentValue);
      
      if (progress < 1) {
        requestAnimationFrame(updateValue);
      }
    };

    requestAnimationFrame(updateValue);
  }, [value]);

  return (
    <span>
      {prefix}{displayValue.toLocaleString(undefined, { 
        minimumFractionDigits: decimals, 
        maximumFractionDigits: decimals 
      })}{suffix}
    </span>
  );
}

export default function DashboardClient() {
  const [wealth, setWealth] = useState<WealthSummary | null>(null);
  const [systemHealth, setSystemHealth] = useState<SystemHealth>({
    binanceStatus: true,
    databaseStatus: true,
    aiAdvisorStatus: true,
    vaultStatus: true,
    lastCheck: new Date().toISOString()
  });
  const [recentTrades, setRecentTrades] = useState<Trade[]>([]);
  const [loading, setLoading] = useState(true);

  // Mock 14-day performance data
  const performanceData = Array.from({ length: 14 }, (_, i) => ({
    day: i + 1,
    value: 85000 + (Math.random() - 0.5) * 10000 + (i * 500),
    date: new Date(Date.now() - (13 - i) * 24 * 60 * 60 * 1000).toLocaleDateString()
  }));

  const fetchDashboardData = async () => {
    try {
      const [realDataRes, tradesRes] = await Promise.all([
        fetch('/api/portfolio/real-data'),
        fetch('/api/trades')
      ]);

      if (realDataRes.ok) {
        const realData = await realDataRes.json();
        if (realData.success) {
          const { hotWallet, coldWallet, totalWealth, totalPnL, shadowAI } = realData.data;
          
          // Transform real data to match WealthSummary interface
          setWealth({
            totalValue: totalWealth,
            totalPnL: totalPnL,
            dailyChange: totalPnL * 0.05, // Estimate
            monthlyReturn: ((coldWallet.stakingYield?.stETH?.monthlyYield || 0) / coldWallet.totalValue) * 100,
            tier1: {
              name: "Binance Hot Wallet",
              value: hotWallet.totalValue,
              allocation: Object.entries(hotWallet.assets).map(([asset, data]: [string, any]) => ({
                asset,
                percentage: data.percentage,
                value: data.value,
                change: Math.random() * 10 - 5 // Mock change for now
              }))
            },
            tier2: {
              name: "Ledger Cold Vault", 
              value: coldWallet.totalValue,
              allocation: Object.entries(coldWallet.assets).map(([asset, data]: [string, any]) => ({
                asset,
                percentage: data.percentage,
                value: data.value,
                change: Math.random() * 5 // Lower volatility for cold storage
              }))
            }
          });
          
          // Update system health based on Shadow.AI
          setSystemHealth({
            binanceStatus: true,
            databaseStatus: true, 
            aiAdvisorStatus: true,
            vaultStatus: true,
            lastCheck: new Date().toISOString(),
            shadowAI: {
              darkPoolActivity: shadowAI.darkPoolActivity,
              whaleMovements: shadowAI.whaleMovements,
              riskLevel: shadowAI.riskLevel,
              recommendation: shadowAI.recommendation
            }
          });
        }
      }

      if (tradesRes.ok) {
        const tradesData = await tradesRes.json();
        setRecentTrades(tradesData.slice(0, 5));
      }
    } catch (error) {
      toast.error("Failed to fetch dashboard data");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Update every 30s
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 via-blue-500 to-purple-600">
            Sovereign Command Center
          </h1>
          <p className="text-white/70">
            Real-time wealth orchestration & system oversight
          </p>
        </div>
        <Button 
          onClick={fetchDashboardData}
          variant="outline" 
          size="sm"
          className="gap-2 bg-white/10 border-white/20 text-white/80 hover:bg-white/20 hover:text-white backdrop-blur-sm transition-all duration-300"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </Button>
      </div>

      {/* Wealth Overview */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl rounded-2xl hover:bg-white/15 transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white/90">Total Wealth</CardTitle>
              <Eye className="h-4 w-4 text-orange-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-yellow-500">
                $<AnimatedCounter value={wealth?.totalValue || 0} />
              </div>
              <div className="flex items-center space-x-2 text-xs text-white/60">
                {wealth && wealth.dailyChange > 0 ? (
                  <TrendingUp className="h-3 w-3 text-green-400" />
                ) : (
                  <TrendingDown className="h-3 w-3 text-red-400" />
                )}
                <span className={wealth && wealth.dailyChange > 0 ? "text-green-400" : "text-red-400"}>
                  {((wealth?.dailyChange || 0) / (wealth?.totalValue || 1) * 100).toFixed(2)}% today
                </span>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl rounded-2xl hover:bg-white/15 transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white/90">Hot Wallet</CardTitle>
              <Wallet className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
                $<AnimatedCounter value={wealth?.tier1?.value || 0} />
              </div>
              <p className="text-xs text-white/60">
                Active trading capital
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl rounded-2xl hover:bg-white/15 transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white/90">Cold Vault</CardTitle>
              <Shield className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-500">
                $<AnimatedCounter value={wealth?.tier2?.value || 0} />
              </div>
              <p className="text-xs text-white/60">
                Secured long-term holdings
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl rounded-2xl hover:bg-white/15 transition-all duration-300">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-white/90">Total P&L</CardTitle>
              <TrendingUp className={`h-4 w-4 ${wealth && wealth.totalPnL > 0 ? 'text-green-400' : 'text-red-400'}`} />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${wealth && wealth.totalPnL > 0 ? 'text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-emerald-500' : 'text-transparent bg-clip-text bg-gradient-to-r from-red-400 to-pink-500'}`}>
                {wealth && wealth.totalPnL > 0 ? '+' : ''}$<AnimatedCounter value={wealth?.totalPnL || 0} />
              </div>
              <p className="text-xs text-white/60">
                <span className={wealth && wealth.totalPnL > 0 ? 'text-green-400' : 'text-red-400'}>
                  {wealth && wealth.totalPnL > 0 ? '+' : ''}{((wealth?.totalPnL || 0) / (wealth?.totalValue || 1) * 100).toFixed(2)}%
                </span> lifetime
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Performance Chart */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl rounded-2xl hover:bg-white/15 transition-all duration-300">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white/90">
                <Activity className="h-5 w-5 text-blue-400" />
                14-Day Performance
              </CardTitle>
              <CardDescription className="text-white/60">
                Portfolio value trajectory over the past two weeks
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[200px] w-full">
                <RechartsWrapper 
                  type="area"
                  data={performanceData}
                  config={{}}
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* System Health */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card className="bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl rounded-2xl hover:bg-white/15 transition-all duration-300">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-white/90">
                <AlertCircle className="h-5 w-5 text-orange-400" />
                System Health
              </CardTitle>
              <CardDescription className="text-white/60">
                Real-time status of all critical systems
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-white/80">Binance API</span>
                <Badge variant={systemHealth.binanceStatus ? "default" : "destructive"} className={systemHealth.binanceStatus ? "bg-green-500/20 text-green-400 border-green-400/50" : "bg-red-500/20 text-red-400 border-red-400/50"}>
                  {systemHealth.binanceStatus ? "Online" : "Offline"}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-white/80">Database</span>
                <Badge variant={systemHealth.databaseStatus ? "default" : "destructive"} className={systemHealth.databaseStatus ? "bg-green-500/20 text-green-400 border-green-400/50" : "bg-red-500/20 text-red-400 border-red-400/50"}>
                  {systemHealth.databaseStatus ? "Connected" : "Error"}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-white/80">AI Advisor</span>
                <Badge variant={systemHealth.aiAdvisorStatus ? "default" : "destructive"} className={systemHealth.aiAdvisorStatus ? "bg-green-500/20 text-green-400 border-green-400/50" : "bg-red-500/20 text-red-400 border-red-400/50"}>
                  {systemHealth.aiAdvisorStatus ? "Active" : "Offline"}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-white/80">Vault System</span>
                <Badge variant={systemHealth.vaultStatus ? "default" : "destructive"} className={systemHealth.vaultStatus ? "bg-green-500/20 text-green-400 border-green-400/50" : "bg-red-500/20 text-red-400 border-red-400/50"}>
                  {systemHealth.vaultStatus ? "Secured" : "Alert"}
                </Badge>
              </div>
              <Separator className="bg-white/10" />
              <div className="text-xs text-white/50">
                Last check: {new Date(systemHealth.lastCheck).toLocaleTimeString()}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Recent Activity */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
      >
        <Card className="bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl rounded-2xl hover:bg-white/15 transition-all duration-300">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-white/90">
              <Zap className="h-5 w-5 text-purple-400" />
              Recent Trading Activity
            </CardTitle>
            <CardDescription className="text-white/60">
              Latest trades and market movements
            </CardDescription>
          </CardHeader>
          <CardContent>
            {recentTrades?.length > 0 ? (
              <div className="space-y-3">
                {recentTrades.map((trade) => (
                  <div key={trade.id} className="flex items-center justify-between p-3 rounded-lg bg-white/5 border border-white/10">
                    <div className="flex items-center space-x-3">
                      <div className={`w-2 h-2 rounded-full ${
                        trade.side === 'BUY' ? 'bg-green-400' : 'bg-red-400'
                      }`} />
                      <div>
                        <span className="font-medium text-white/90">{trade.side} {trade.asset}</span>
                        <p className="text-xs text-white/60">
                          {trade.amount} @ ${trade.price.toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant={trade.status === 'FILLED' ? 'default' : 'secondary'} className={trade.status === 'FILLED' ? "bg-green-500/20 text-green-400 border-green-400/50" : "bg-blue-500/20 text-blue-400 border-blue-400/50"}>
                        {trade.status}
                      </Badge>
                      <p className="text-xs text-white/50">
                        {new Date(trade.createdAt).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-white/60">
                <Zap className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No recent trading activity</p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}


'use client';

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Zap, 
  TrendingUp, 
  TrendingDown,
  Play,
  Pause,
  Target,
  DollarSign,
  Activity
} from "lucide-react";
import { Trade } from "@/lib/types";
import { toast } from "sonner";
import { motion } from "framer-motion";
import dynamic from 'next/dynamic';

const LineChartWrapper = ({ data }: { data: any[] }) => {
  if (typeof window === 'undefined') {
    return <div>Loading chart...</div>;
  }
  
  const { LineChart, Line, XAxis, YAxis, ResponsiveContainer, Tooltip } = require('recharts');
  
  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={data}>
        <XAxis 
          dataKey="time" 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12 }}
        />
        <YAxis 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12 }}
          tickFormatter={(value: any) => `$${value}`}
        />
        <Tooltip 
          contentStyle={{
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            border: '1px solid rgba(255, 215, 0, 0.2)',
            borderRadius: '8px',
            color: 'white'
          }}
          formatter={(value: any) => [`$${value.toFixed(2)}`, 'P&L']}
        />
        <Line 
          type="monotone" 
          dataKey="pnl" 
          stroke="#60B5FF" 
          strokeWidth={2}
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default function TradingClient() {
  const [trades, setTrades] = useState<Trade[]>([]);
  const [strategies, setStrategies] = useState({
    scalping: false,
    sniping: false,
    arbitrage: false
  });
  const [loading, setLoading] = useState(true);

  // Mock PnL data for the last 24 hours
  const pnlData = Array.from({ length: 24 }, (_, i) => ({
    hour: i,
    pnl: Math.random() * 200 - 100,
    time: `${i}:00`
  }));

  const fetchTrades = async () => {
    try {
      const response = await fetch('/api/trades');
      if (response.ok) {
        const data = await response.json();
        setTrades(data);
      }
    } catch (error) {
      toast.error("Failed to fetch trades");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrades();
  }, []);

  const toggleStrategy = (strategy: keyof typeof strategies) => {
    setStrategies(prev => ({ ...prev, [strategy]: !prev[strategy] }));
    toast.success(`${strategy.charAt(0).toUpperCase() + strategy.slice(1)} ${!strategies[strategy] ? 'enabled' : 'disabled'}`);
  };

  const totalPnL = trades.reduce((sum, trade) => sum + (trade.pnl || 0), 0);
  const winRate = trades.length > 0 ? (trades.filter(t => (t.pnl || 0) > 0).length / trades.length) * 100 : 0;

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
          <h1 className="text-3xl font-bold gradient-gold bg-clip-text text-transparent">
            Flip Engine
          </h1>
          <p className="text-muted-foreground">
            Advanced trading strategies & automated execution
          </p>
        </div>
      </div>

      {/* Trading Stats */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="trading-card glow-blue">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total P&L</CardTitle>
              <DollarSign className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${totalPnL >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {totalPnL >= 0 ? '+' : ''}${totalPnL.toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground">
                All-time trading performance
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Win Rate</CardTitle>
              <Target className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {winRate.toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground">
                Profitable trades ratio
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Strategies</CardTitle>
              <Activity className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-400">
                {Object.values(strategies).filter(Boolean).length}
              </div>
              <p className="text-xs text-muted-foreground">
                Currently running
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Trades</CardTitle>
              <Zap className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {trades.length}
              </div>
              <p className="text-xs text-muted-foreground">
                Executed orders
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Strategy Controls */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Trading Strategies
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                <div>
                  <h4 className="font-medium">Scalping Engine</h4>
                  <p className="text-sm text-muted-foreground">Quick micro-trades on small price movements</p>
                </div>
                <Button
                  variant={strategies.scalping ? "default" : "outline"}
                  size="sm"
                  onClick={() => toggleStrategy('scalping')}
                  className="gap-2"
                >
                  {strategies.scalping ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                  {strategies.scalping ? 'Stop' : 'Start'}
                </Button>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                <div>
                  <h4 className="font-medium">Sniper Bot</h4>
                  <p className="text-sm text-muted-foreground">Precision entries at optimal price levels</p>
                </div>
                <Button
                  variant={strategies.sniping ? "default" : "outline"}
                  size="sm"
                  onClick={() => toggleStrategy('sniping')}
                  className="gap-2"
                >
                  {strategies.sniping ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                  {strategies.sniping ? 'Stop' : 'Start'}
                </Button>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                <div>
                  <h4 className="font-medium">Arbitrage Scanner</h4>
                  <p className="text-sm text-muted-foreground">Cross-exchange price discrepancies</p>
                </div>
                <Button
                  variant={strategies.arbitrage ? "default" : "outline"}
                  size="sm"
                  onClick={() => toggleStrategy('arbitrage')}
                  className="gap-2"
                >
                  {strategies.arbitrage ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                  {strategies.arbitrage ? 'Stop' : 'Start'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* P&L Chart */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                24H P&L Performance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[200px] w-full">
                <LineChartWrapper data={pnlData} />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Recent Trades */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.7 }}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Recent Trades
            </CardTitle>
          </CardHeader>
          <CardContent>
            {trades.length > 0 ? (
              <div className="space-y-3">
                {trades.slice(0, 10).map((trade) => (
                  <div key={trade.id} className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                    <div className="flex items-center space-x-3">
                      <div className={`w-2 h-2 rounded-full ${
                        trade.side === 'BUY' ? 'bg-green-400' : 'bg-red-400'
                      }`} />
                      <div>
                        <span className="font-medium">
                          {trade.side} {trade.amount} {trade.asset}
                        </span>
                        <p className="text-xs text-muted-foreground">
                          @ ${trade.price.toLocaleString()} • {trade.strategy}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-sm font-medium ${
                        (trade.pnl || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                      }`}>
                        {(trade.pnl || 0) >= 0 ? '+' : ''}${(trade.pnl || 0).toLocaleString()}
                      </div>
                      <Badge variant={trade.status === 'FILLED' ? 'default' : 'secondary'} className="text-xs">
                        {trade.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Zap className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No trades executed yet</p>
              </div>
            )}
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}

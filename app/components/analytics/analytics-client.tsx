
'use client';

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { BarChart3, Shield, AlertTriangle, TrendingUp } from "lucide-react";
import { motion } from "framer-motion";
import dynamic from 'next/dynamic';

const BarChartWrapper = ({ data }: { data: any[] }) => {
  if (typeof window === 'undefined') {
    return <div>Loading chart...</div>;
  }
  
  const { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip } = require('recharts');
  
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data}>
        <XAxis 
          dataKey="month" 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12 }}
        />
        <YAxis 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12 }}
          tickFormatter={(value: any) => `${value}%`}
        />
        <Tooltip 
          contentStyle={{
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            border: '1px solid rgba(255, 215, 0, 0.2)',
            borderRadius: '8px',
            color: 'white'
          }}
          formatter={(value: any) => [`${value}%`, 'Returns']}
        />
        <Bar 
          dataKey="returns" 
          fill="#60B5FF"
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
};

export default function AnalyticsClient() {
  const [riskMetrics] = useState({
    portfolioRisk: 'MODERATE',
    concentration: 'LOW',
    volatility: 'MEDIUM',
    diversification: 85
  });

  const performanceData = [
    { month: 'Jan', returns: 12.5 },
    { month: 'Feb', returns: 8.3 },
    { month: 'Mar', returns: -2.1 },
    { month: 'Apr', returns: 15.7 },
    { month: 'May', returns: 23.2 },
    { month: 'Jun', returns: 18.9 }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-gold bg-clip-text text-transparent">
            Portfolio Analytics
          </h1>
          <p className="text-muted-foreground">
            Advanced performance metrics, risk assessment & whale activity
          </p>
        </div>
      </div>

      {/* Risk Metrics */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Portfolio Risk</CardTitle>
              <Shield className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <Badge variant="outline" className="text-green-400 border-green-400">
                {riskMetrics.portfolioRisk}
              </Badge>
              <p className="text-xs text-muted-foreground mt-2">
                Overall risk assessment
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Concentration Risk</CardTitle>
              <AlertTriangle className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <Badge variant="outline" className="text-green-400 border-green-400">
                {riskMetrics.concentration}
              </Badge>
              <p className="text-xs text-muted-foreground mt-2">
                Asset concentration level
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Volatility</CardTitle>
              <TrendingUp className="h-4 w-4 text-yellow-400" />
            </CardHeader>
            <CardContent>
              <Badge variant="outline" className="text-yellow-400 border-yellow-400">
                {riskMetrics.volatility}
              </Badge>
              <p className="text-xs text-muted-foreground mt-2">
                Price volatility exposure
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Diversification</CardTitle>
              <BarChart3 className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {riskMetrics.diversification}%
              </div>
              <p className="text-xs text-muted-foreground">
                Portfolio spread score
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Performance Chart */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.5 }}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              6-Month Performance Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] w-full">
              <BarChartWrapper data={performanceData} />
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Whale Activity */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Whale Activity Monitor
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                <div>
                  <h4 className="font-medium">Large BTC Movement Detected</h4>
                  <p className="text-sm text-muted-foreground">
                    2,500 BTC moved from exchange to unknown wallet
                  </p>
                </div>
                <Badge variant="secondary">2 hours ago</Badge>
              </div>
              
              <div className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                <div>
                  <h4 className="font-medium">Whale Accumulation Alert</h4>
                  <p className="text-sm text-muted-foreground">
                    Top 100 wallets increased ETH holdings by 5%
                  </p>
                </div>
                <Badge variant="secondary">6 hours ago</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}

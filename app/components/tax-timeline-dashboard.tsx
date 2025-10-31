
'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  Calculator, 
  Receipt, 
  Download,
  DollarSign,
  Percent,
  Calendar
} from 'lucide-react';

interface TaxData {
  summary: {
    totalGainLoss: number;
    shortTermGainLoss: number;
    longTermGainLoss: number;
    totalTaxOwed: number;
    effectiveRate: number;
    netProfitAfterTax: number;
    totalTrades: number;
    avgHoldingPeriod: number;
  };
  timeline: Array<{
    date: string;
    asset: string;
    gainLoss: number;
    taxOwed: number;
    netProfit: number;
    category: string;
    holdingPeriod: number;
  }>;
  monthlySummary: Array<{
    month: string;
    totalGainLoss: number;
    totalTaxOwed: number;
    netProfit: number;
    tradeCount: number;
  }>;
}

export function TaxTimelineDashboard() {
  const [taxData, setTaxData] = useState<TaxData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('all');

  useEffect(() => {
    fetchTaxData();
  }, []);

  const fetchTaxData = async () => {
    try {
      const response = await fetch('/api/pnl/tax-analysis');
      const data = await response.json();
      setTaxData(data);
    } catch (error) {
      console.error('Error fetching tax data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateReport = async () => {
    try {
      const response = await fetch('/api/pnl/tax-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ year: 2025 })
      });
      const data = await response.json();
      
      // Create downloadable report
      const reportContent = JSON.stringify(data.report, null, 2);
      const blob = new Blob([reportContent], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `tax-report-2025.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error generating report:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="text-muted-foreground">Calculating your TRUE tax implications...</p>
        </div>
      </div>
    );
  }

  if (!taxData) {
    return (
      <Card className="p-8 text-center">
        <p>Failed to load tax data. Please try again.</p>
        <Button onClick={fetchTaxData} className="mt-4">Retry</Button>
      </Card>
    );
  }

  const { summary, timeline, monthlySummary } = taxData;

  const pieData = [
    { name: 'Short-term Gains', value: Math.max(0, summary.shortTermGainLoss), color: '#ef4444' },
    { name: 'Long-term Gains', value: Math.max(0, summary.longTermGainLoss), color: '#22c55e' },
    { name: 'Tax Owed', value: summary.totalTaxOwed, color: '#f59e0b' }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-cyan-600 bg-clip-text text-transparent">
            TRUE PnL + Tax Timeline
          </h1>
          <p className="text-muted-foreground mt-2">
            Your complete trading performance with accurate tax calculations
          </p>
        </div>
        <Button onClick={generateReport} className="bg-gradient-to-r from-blue-600 to-purple-600">
          <Download className="w-4 h-4 mr-2" />
          Export Tax Report
        </Button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-gradient-to-br from-green-500/10 to-emerald-500/5 border-green-500/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Gain/Loss</p>
                <p className="text-2xl font-bold text-green-600">
                  ${summary.totalGainLoss.toLocaleString()}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-red-500/10 to-rose-500/5 border-red-500/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Tax Owed</p>
                <p className="text-2xl font-bold text-red-600">
                  ${summary.totalTaxOwed.toLocaleString()}
                </p>
              </div>
              <Receipt className="w-8 h-8 text-red-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-blue-500/10 to-cyan-500/5 border-blue-500/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Net After Tax</p>
                <p className="text-2xl font-bold text-blue-600">
                  ${summary.netProfitAfterTax.toLocaleString()}
                </p>
              </div>
              <DollarSign className="w-8 h-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-br from-purple-500/10 to-violet-500/5 border-purple-500/20">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Effective Rate</p>
                <p className="text-2xl font-bold text-purple-600">
                  {(summary.effectiveRate * 100).toFixed(1)}%
                </p>
              </div>
              <Percent className="w-8 h-8 text-purple-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="timeline" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="timeline">Timeline View</TabsTrigger>
          <TabsTrigger value="monthly">Monthly Summary</TabsTrigger>
          <TabsTrigger value="breakdown">Tax Breakdown</TabsTrigger>
          <TabsTrigger value="details">Trade Details</TabsTrigger>
        </TabsList>

        <TabsContent value="timeline" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>TRUE PnL vs Tax Timeline</CardTitle>
              <CardDescription>
                Track your actual profit after accounting for tax implications
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={monthlySummary}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip 
                    formatter={(value: any, name: string) => [
                      `$${value.toLocaleString()}`,
                      name === 'totalGainLoss' ? 'Gross P&L' :
                      name === 'totalTaxOwed' ? 'Tax Owed' : 'Net P&L'
                    ]}
                  />
                  <Line type="monotone" dataKey="totalGainLoss" stroke="#22c55e" strokeWidth={3} name="Gross P&L" />
                  <Line type="monotone" dataKey="totalTaxOwed" stroke="#ef4444" strokeWidth={2} name="Tax Owed" />
                  <Line type="monotone" dataKey="netProfit" stroke="#3b82f6" strokeWidth={3} name="Net P&L" />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="monthly" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Monthly Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={monthlySummary}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value: any) => [`$${value.toLocaleString()}`, '']} />
                  <Bar dataKey="netProfit" fill="#3b82f6" name="Net Profit After Tax" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="breakdown" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Tax Category Breakdown</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={({ name, value }) => `${name}: $${value.toLocaleString()}`}
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: any) => [`$${value.toLocaleString()}`, '']} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Key Metrics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Total Trades</span>
                  <Badge variant="outline">{summary.totalTrades}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Avg Holding Period</span>
                  <Badge variant="outline">{Math.round(summary.avgHoldingPeriod)} days</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Short-term Gains</span>
                  <Badge variant="outline" className="text-red-600">
                    ${summary.shortTermGainLoss.toLocaleString()}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-muted-foreground">Long-term Gains</span>
                  <Badge variant="outline" className="text-green-600">
                    ${summary.longTermGainLoss.toLocaleString()}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="details" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Trade Tax Details</CardTitle>
              <CardDescription>
                Individual trade tax calculations (showing last 20 trades)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {timeline.slice(0, 20).map((trade, index) => (
                  <div key={index} className="flex items-center justify-between p-3 rounded-lg border">
                    <div className="flex items-center space-x-4">
                      <Badge variant={trade.category === 'short-term' ? 'destructive' : 'secondary'}>
                        {trade.asset}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {new Date(trade.date).toLocaleDateString()}
                      </span>
                      <span className="text-sm">
                        {trade.holdingPeriod} days
                      </span>
                    </div>
                    <div className="text-right space-y-1">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-muted-foreground">G/L:</span>
                        <span className={trade.gainLoss >= 0 ? 'text-green-600' : 'text-red-600'}>
                          ${trade.gainLoss.toFixed(2)}
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-muted-foreground">Tax:</span>
                        <span className="text-red-600">
                          ${trade.taxOwed.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

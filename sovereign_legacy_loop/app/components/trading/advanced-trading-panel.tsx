
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Progress } from '@/components/ui/progress';
import { 
  Zap, 
  Target, 
  TrendingUp, 
  Shield, 
  Activity,
  AlertTriangle,
  CheckCircle,
  Clock,
  DollarSign,
  BarChart3,
  Brain,
  Settings,
  Play,
  Pause,
  RefreshCw
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

interface TradingMetrics {
  avgFillTime: number;
  slippagePercent: number;
  successRate: number;
  profitFactor: number;
  sharpeRatio: number;
  maxConsecutiveLosses: number;
  totalExecutions: number;
}

interface TradeExecution {
  id: string;
  symbol: string;
  side: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  status: string;
  executionStrategy: string;
  expectedProfit: number;
  createdAt: string;
}

export default function AdvancedTradingPanel() {
  const [isLoading, setIsLoading] = useState(false);
  const [metrics, setMetrics] = useState<TradingMetrics | null>(null);
  const [recentTrades, setRecentTrades] = useState<TradeExecution[]>([]);
  const [isTrading, setIsTrading] = useState(false);

  // Order form state
  const [orderForm, setOrderForm] = useState({
    symbol: 'BTCUSDT',
    side: 'BUY' as 'BUY' | 'SELL',
    type: 'LIMIT' as 'LIMIT' | 'MARKET',
    quantity: '',
    price: '',
    riskProfile: {
      maxPositionSize: 10000,
      riskScore: 0.3
    }
  });

  useEffect(() => {
    fetchTradingMetrics();
    const interval = setInterval(fetchTradingMetrics, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchTradingMetrics = async () => {
    try {
      const response = await fetch('/api/trading/metrics');
      const result = await response.json();
      
      if (result.success) {
        setMetrics(result.data.metrics);
        setRecentTrades(result.data.recentTrades);
      }
    } catch (error) {
      console.error('Failed to fetch trading metrics:', error);
    }
  };

  const executeTrade = async () => {
    if (!orderForm.quantity || !orderForm.symbol) {
      toast.error('Please fill in all required fields');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('/api/trading/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderForm),
      });

      const result = await response.json();
      
      if (result.success) {
        toast.success('Trade executed successfully!');
        
        // Show AI analysis
        const analysis = result.data.analysis;
        setTimeout(() => {
          toast.info(`AI Analysis: ${analysis.executionStrategy}`, {
            description: analysis.expectedOutcome,
            duration: 8000
          });
        }, 1000);

        // Refresh metrics
        fetchTradingMetrics();
        
        // Reset form
        setOrderForm(prev => ({
          ...prev,
          quantity: '',
          price: ''
        }));
      } else {
        toast.error(`Trade failed: ${result.error}`);
        if (result.data?.warnings) {
          result.data.warnings.forEach((warning: string) => {
            setTimeout(() => toast.warning(warning), 500);
          });
        }
      }
    } catch (error) {
      toast.error('Failed to execute trade');
      console.error('Trade execution error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'LOW': return 'bg-green-500';
      case 'MEDIUM': return 'bg-yellow-500';
      case 'HIGH': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'FILLED': return 'bg-green-500';
      case 'PENDING': return 'bg-yellow-500';
      case 'CANCELLED': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
            Advanced Trading Engine
          </h2>
          <p className="text-muted-foreground mt-1">
            AI-powered trade execution with advanced risk management
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge variant={isTrading ? "default" : "secondary"} className="px-3 py-1">
            <Activity className="w-4 h-4 mr-1" />
            {isTrading ? 'Active' : 'Standby'}
          </Badge>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchTradingMetrics}
            disabled={isLoading}
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trading Panel */}
        <div className="lg:col-span-2">
          <Tabs defaultValue="execute" className="space-y-4">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="execute">
                <Zap className="w-4 h-4 mr-2" />
                Execute
              </TabsTrigger>
              <TabsTrigger value="analytics">
                <BarChart3 className="w-4 h-4 mr-2" />
                Analytics
              </TabsTrigger>
              <TabsTrigger value="history">
                <Clock className="w-4 h-4 mr-2" />
                History
              </TabsTrigger>
            </TabsList>

            <TabsContent value="execute" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Brain className="w-5 h-5 mr-2 text-purple-400" />
                    AI-Powered Order Execution
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="symbol">Symbol</Label>
                      <Select 
                        value={orderForm.symbol} 
                        onValueChange={(value) => setOrderForm(prev => ({ ...prev, symbol: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="BTCUSDT">BTC/USDT</SelectItem>
                          <SelectItem value="ETHUSDT">ETH/USDT</SelectItem>
                          <SelectItem value="ADAUSDT">ADA/USDT</SelectItem>
                          <SelectItem value="SOLUSDT">SOL/USDT</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="side">Side</Label>
                      <Select 
                        value={orderForm.side} 
                        onValueChange={(value: 'BUY' | 'SELL') => setOrderForm(prev => ({ ...prev, side: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="BUY">BUY</SelectItem>
                          <SelectItem value="SELL">SELL</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="type">Order Type</Label>
                      <Select 
                        value={orderForm.type} 
                        onValueChange={(value: 'LIMIT' | 'MARKET') => setOrderForm(prev => ({ ...prev, type: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="LIMIT">Limit</SelectItem>
                          <SelectItem value="MARKET">Market</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="quantity">Quantity</Label>
                      <Input
                        id="quantity"
                        type="number"
                        placeholder="0.001"
                        value={orderForm.quantity}
                        onChange={(e) => setOrderForm(prev => ({ ...prev, quantity: e.target.value }))}
                      />
                    </div>
                  </div>

                  {orderForm.type === 'LIMIT' && (
                    <div>
                      <Label htmlFor="price">Price</Label>
                      <Input
                        id="price"
                        type="number"
                        placeholder="50000.00"
                        value={orderForm.price}
                        onChange={(e) => setOrderForm(prev => ({ ...prev, price: e.target.value }))}
                      />
                    </div>
                  )}

                  <Button 
                    onClick={executeTrade} 
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
                    size="lg"
                  >
                    {isLoading ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Analyzing & Executing...
                      </>
                    ) : (
                      <>
                        <Zap className="w-4 h-4 mr-2" />
                        Execute Smart Trade
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="analytics" className="space-y-4">
              {metrics && (
                <div className="grid grid-cols-2 gap-4">
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Success Rate</span>
                        <span className="text-2xl font-bold text-green-400">
                          {metrics.successRate.toFixed(1)}%
                        </span>
                      </div>
                      <Progress value={metrics.successRate} className="mt-2" />
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Profit Factor</span>
                        <span className="text-2xl font-bold text-blue-400">
                          {metrics.profitFactor.toFixed(2)}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Avg Fill Time</span>
                        <span className="text-2xl font-bold text-purple-400">
                          {metrics.avgFillTime.toFixed(0)}ms
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                  
                  <Card>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Slippage</span>
                        <span className="text-2xl font-bold text-yellow-400">
                          {(metrics.slippagePercent * 100).toFixed(3)}%
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </TabsContent>

            <TabsContent value="history" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Executions</CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[400px]">
                    <div className="space-y-3">
                      {recentTrades.map((trade) => (
                        <div key={trade.id} className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div className={`w-3 h-3 rounded-full ${getStatusColor(trade.status)}`} />
                            <div>
                              <div className="font-medium">{trade.symbol}</div>
                              <div className="text-sm text-muted-foreground">
                                {trade.side} • {trade.executionStrategy}
                              </div>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-medium">${trade.price.toFixed(2)}</div>
                            <div className="text-sm text-green-400">
                              +{trade.expectedProfit.toFixed(2)}%
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ScrollArea>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Metrics Panel */}
        <div className="space-y-4">
          {metrics && (
            <>
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Target className="w-5 h-5 mr-2 text-green-400" />
                    Performance
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">Sharpe Ratio</span>
                      <span className="text-sm font-medium">{metrics.sharpeRatio.toFixed(2)}</span>
                    </div>
                    <Progress value={Math.min(metrics.sharpeRatio * 25, 100)} />
                  </div>
                  
                  <Separator />
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm">Total Executions</span>
                      <span className="font-medium">{metrics.totalExecutions}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Max Consecutive Losses</span>
                      <span className="font-medium text-red-400">{metrics.maxConsecutiveLosses}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Shield className="w-5 h-5 mr-2 text-blue-400" />
                    Risk Management
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-2">
                      <span className="text-sm">Risk Score</span>
                      <span className="text-sm font-medium">
                        {(orderForm.riskProfile.riskScore * 100).toFixed(0)}%
                      </span>
                    </div>
                    <Progress value={orderForm.riskProfile.riskScore * 100} />
                  </div>
                  
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Max Position Size</span>
                      <span className="font-medium">${orderForm.riskProfile.maxPositionSize.toLocaleString()}</span>
                    </div>
                  </div>
                  
                  <div className="p-3 bg-muted rounded-lg">
                    <div className="flex items-start space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-400 mt-0.5" />
                      <div className="text-xs">
                        <div className="font-medium text-green-400">Risk Controls Active</div>
                        <div className="text-muted-foreground mt-1">
                          AI monitors positions and automatically applies risk limits
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

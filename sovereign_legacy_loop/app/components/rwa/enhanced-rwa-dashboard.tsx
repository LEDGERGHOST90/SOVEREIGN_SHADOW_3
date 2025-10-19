
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Crown,
  TrendingUp,
  TrendingDown,
  DollarSign,
  Target,
  Zap,
  Building2,
  Shield,
  BarChart3,
  Trophy,
  ArrowUpRight,
  Coins,
  RefreshCw,
  Plus,
  Settings,
  AlertTriangle,
  CheckCircle,
  Activity,
  Eye,
  Brain
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

interface OracleStrategy {
  name: string;
  description: string;
  rwaAllocation: number;
  cryptoAllocation: number;
  targetAssets: string[];
  riskLevel: 'CONSERVATIVE' | 'BALANCED' | 'AGGRESSIVE';
  expectedYield: number;
  oracleAlignment: number;
}

interface RWAAsset {
  symbol: string;
  name: string;
  type: string;
  apy: number;
  minInvestment: number;
  tvl: number;
  description: string;
}

interface RWAAnalytics {
  portfolioComposition: {
    byAssetType: { [key: string]: number };
    byRiskLevel: any[];
    concentration: number;
  };
  yieldProjections: {
    currentYield: number;
    projectedAnnual: number;
    compoundingEffect: number;
  };
  riskAssessment: {
    overallRisk: string;
    diversificationScore: number;
    correlationAnalysis?: string;
  };
  oracleComparison: {
    alignmentScore: number;
    performanceVsOracle: {
      userYield: number;
      oracleYield: number;
      difference: number;
      relative: number;
    };
    recommendations?: string[];
  };
}

export default function EnhancedRWADashboard() {
  const [isLoading, setIsLoading] = useState(false);
  const [strategy, setStrategy] = useState<OracleStrategy | null>(null);
  const [analytics, setAnalytics] = useState<RWAAnalytics | null>(null);
  const [ondoAssets, setOndoAssets] = useState<RWAAsset[]>([]);
  const [robinhoodAssets, setRobinhoodAssets] = useState<any[]>([]);
  
  // Strategy generation form
  const [strategyForm, setStrategyForm] = useState({
    portfolioValue: '',
    riskTolerance: 'BALANCED'
  });

  // Transaction form
  const [transactionForm, setTransactionForm] = useState({
    assetSymbol: '',
    type: 'BUY' as 'BUY' | 'SELL',
    amount: ''
  });

  useEffect(() => {
    fetchRWAAnalytics();
  }, []);

  const fetchRWAAnalytics = async () => {
    try {
      const response = await fetch('/api/rwa/analytics');
      const result = await response.json();
      
      if (result.success) {
        setAnalytics(result.data.analytics);
        setOndoAssets(result.data.availableAssets.ondo);
        setRobinhoodAssets(result.data.availableAssets.robinhood);
      }
    } catch (error) {
      console.error('Failed to fetch RWA analytics:', error);
    }
  };

  const generateStrategy = async () => {
    if (!strategyForm.portfolioValue) {
      toast.error('Please enter your portfolio value');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('/api/rwa/strategy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          portfolioValue: parseFloat(strategyForm.portfolioValue),
          riskTolerance: strategyForm.riskTolerance
        }),
      });

      const result = await response.json();
      
      if (result.success) {
        setStrategy(result.data.strategy);
        toast.success('Oracle-inspired strategy generated successfully!');
        
        // Show strategy details
        setTimeout(() => {
          toast.info(`Strategy: ${result.data.strategy.name}`, {
            description: result.data.strategy.description,
            duration: 8000
          });
        }, 1000);
      } else {
        toast.error(`Strategy generation failed: ${result.error}`);
      }
    } catch (error) {
      toast.error('Failed to generate strategy');
      console.error('Strategy generation error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const executeTransaction = async () => {
    if (!transactionForm.assetSymbol || !transactionForm.amount) {
      toast.error('Please fill in all transaction details');
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('/api/rwa/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transactionForm),
      });

      const result = await response.json();
      
      if (result.success && result.data.success) {
        toast.success('Transaction executed successfully!');
        
        // Show transaction details
        setTimeout(() => {
          toast.info(`Transaction ID: ${result.data.transactionId}`, {
            description: `Executed ${transactionForm.amount} ${transactionForm.assetSymbol}`,
            duration: 6000
          });
        }, 1000);

        // Refresh analytics
        fetchRWAAnalytics();
        
        // Reset form
        setTransactionForm({
          assetSymbol: '',
          type: 'BUY',
          amount: ''
        });
      } else {
        toast.error('Transaction failed');
      }
    } catch (error) {
      toast.error('Failed to execute transaction');
      console.error('Transaction execution error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'LOW': return 'text-green-400';
      case 'MEDIUM': return 'text-yellow-400';
      case 'HIGH': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getStrategyColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'CONSERVATIVE': return 'from-blue-500 to-cyan-500';
      case 'BALANCED': return 'from-purple-500 to-blue-500';
      case 'AGGRESSIVE': return 'from-red-500 to-orange-500';
      default: return 'from-gray-500 to-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
            Enhanced RWA Engine
          </h2>
          <p className="text-muted-foreground mt-1">
            Oracle-inspired Real-World Asset management with Ondo Finance & Robinhood integration
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Badge variant="secondary" className="px-3 py-1">
            <Crown className="w-4 h-4 mr-1 text-yellow-400" />
            Ellison-Inspired
          </Badge>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={fetchRWAAnalytics}
            disabled={isLoading}
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Strategy Generation */}
        <div className="lg:col-span-3">
          <Tabs defaultValue="strategy" className="space-y-4">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="strategy">
                <Brain className="w-4 h-4 mr-2" />
                Strategy
              </TabsTrigger>
              <TabsTrigger value="assets">
                <Building2 className="w-4 h-4 mr-2" />
                Assets
              </TabsTrigger>
              <TabsTrigger value="analytics">
                <BarChart3 className="w-4 h-4 mr-2" />
                Analytics
              </TabsTrigger>
              <TabsTrigger value="execute">
                <Zap className="w-4 h-4 mr-2" />
                Execute
              </TabsTrigger>
            </TabsList>

            <TabsContent value="strategy" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Target className="w-5 h-5 mr-2 text-purple-400" />
                    Oracle Strategy Generator
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="portfolioValue">Portfolio Value ($)</Label>
                      <Input
                        id="portfolioValue"
                        type="number"
                        placeholder="100000"
                        value={strategyForm.portfolioValue}
                        onChange={(e) => setStrategyForm(prev => ({ ...prev, portfolioValue: e.target.value }))}
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="riskTolerance">Risk Tolerance</Label>
                      <Select 
                        value={strategyForm.riskTolerance} 
                        onValueChange={(value) => setStrategyForm(prev => ({ ...prev, riskTolerance: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="CONSERVATIVE">Conservative</SelectItem>
                          <SelectItem value="BALANCED">Balanced</SelectItem>
                          <SelectItem value="AGGRESSIVE">Aggressive</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <Button 
                    onClick={generateStrategy} 
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600"
                    size="lg"
                  >
                    {isLoading ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Generating Oracle Strategy...
                      </>
                    ) : (
                      <>
                        <Crown className="w-4 h-4 mr-2" />
                        Generate Oracle Strategy
                      </>
                    )}
                  </Button>

                  {strategy && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-6 p-4 border rounded-lg bg-gradient-to-r from-purple-900/20 to-blue-900/20"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-lg font-semibold">{strategy.name}</h3>
                        <Badge className={`bg-gradient-to-r ${getStrategyColor(strategy.riskLevel)}`}>
                          {strategy.riskLevel}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground mb-4">{strategy.description}</p>
                      
                      <div className="grid grid-cols-2 gap-4 mb-4">
                        <div>
                          <div className="text-sm text-muted-foreground">RWA Allocation</div>
                          <div className="text-2xl font-bold text-blue-400">{strategy.rwaAllocation}%</div>
                        </div>
                        <div>
                          <div className="text-sm text-muted-foreground">Expected Yield</div>
                          <div className="text-2xl font-bold text-green-400">{strategy.expectedYield}%</div>
                        </div>
                      </div>
                      
                      <div className="mb-4">
                        <div className="flex justify-between text-sm mb-1">
                          <span>Oracle Alignment</span>
                          <span>{strategy.oracleAlignment}%</span>
                        </div>
                        <Progress value={strategy.oracleAlignment} className="h-2" />
                      </div>
                      
                      <div>
                        <div className="text-sm text-muted-foreground mb-2">Target Assets</div>
                        <div className="flex flex-wrap gap-2">
                          {strategy.targetAssets.map((asset) => (
                            <Badge key={asset} variant="secondary" className="text-xs">
                              {asset}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </motion.div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="assets" className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Building2 className="w-5 h-5 mr-2 text-blue-400" />
                      Ondo Finance Assets
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ScrollArea className="h-[300px]">
                      <div className="space-y-3">
                        {ondoAssets.map((asset) => (
                          <div key={asset.symbol} className="p-3 border rounded-lg">
                            <div className="flex items-center justify-between mb-2">
                              <div className="font-medium">{asset.symbol}</div>
                              <Badge className="bg-blue-500/20 text-blue-400">
                                {asset.apy.toFixed(2)}% APY
                              </Badge>
                            </div>
                            <div className="text-sm text-muted-foreground mb-2">
                              {asset.name}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              Min: ${asset.minInvestment.toLocaleString()} • 
                              TVL: ${(asset.tvl / 1_000_000).toFixed(0)}M
                            </div>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Trophy className="w-5 h-5 mr-2 text-green-400" />
                      Oracle Ecosystem Stocks
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ScrollArea className="h-[300px]">
                      <div className="space-y-3">
                        {robinhoodAssets.map((stock) => (
                          <div key={stock.symbol} className="p-3 border rounded-lg">
                            <div className="flex items-center justify-between mb-2">
                              <div className="font-medium">{stock.symbol}</div>
                              <div className="text-right">
                                <div className="font-medium">${stock.price.toFixed(2)}</div>
                                <div className={`text-xs flex items-center ${stock.change > 0 ? 'text-green-400' : 'text-red-400'}`}>
                                  {stock.change > 0 ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
                                  {stock.changePercent.toFixed(2)}%
                                </div>
                              </div>
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {stock.name}
                            </div>
                            {stock.marketCap && (
                              <div className="text-xs text-muted-foreground mt-1">
                                Market Cap: ${(stock.marketCap / 1_000_000_000).toFixed(0)}B
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="analytics" className="space-y-4">
              {analytics && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Portfolio Composition</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <div className="text-sm text-muted-foreground mb-2">By Asset Type</div>
                        {Object.entries(analytics.portfolioComposition.byAssetType).map(([type, percent]) => (
                          <div key={type} className="mb-2">
                            <div className="flex justify-between text-sm mb-1">
                              <span>{type}</span>
                              <span>{percent.toFixed(1)}%</span>
                            </div>
                            <Progress value={percent} className="h-2" />
                          </div>
                        ))}
                      </div>
                      
                      <Separator />
                      
                      <div>
                        <div className="text-sm text-muted-foreground mb-2">Risk Assessment</div>
                        <div className="flex justify-between items-center">
                          <span>Overall Risk</span>
                          <span className={`font-medium ${getRiskColor(analytics.riskAssessment.overallRisk)}`}>
                            {analytics.riskAssessment.overallRisk}
                          </span>
                        </div>
                        <div className="flex justify-between items-center mt-2">
                          <span>Diversification</span>
                          <span className="font-medium">
                            {analytics.riskAssessment.diversificationScore.toFixed(0)}/100
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <Crown className="w-5 h-5 mr-2 text-yellow-400" />
                        Oracle Comparison
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div>
                        <div className="flex justify-between text-sm mb-1">
                          <span>Alignment Score</span>
                          <span>{analytics.oracleComparison.alignmentScore.toFixed(0)}%</span>
                        </div>
                        <Progress value={analytics.oracleComparison.alignmentScore} className="h-2" />
                      </div>
                      
                      <Separator />
                      
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span className="text-sm">Your Yield</span>
                          <span className="font-medium text-blue-400">
                            {analytics.oracleComparison.performanceVsOracle.userYield.toFixed(2)}%
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">Oracle Benchmark</span>
                          <span className="font-medium text-yellow-400">
                            {analytics.oracleComparison.performanceVsOracle.oracleYield.toFixed(2)}%
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm">Gap</span>
                          <span className={`font-medium ${analytics.oracleComparison.performanceVsOracle.difference > 0 ? 'text-red-400' : 'text-green-400'}`}>
                            {analytics.oracleComparison.performanceVsOracle.difference > 0 ? '+' : ''}{analytics.oracleComparison.performanceVsOracle.difference.toFixed(2)}%
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="md:col-span-2">
                    <CardHeader>
                      <CardTitle>Yield Projections</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid grid-cols-3 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-400">
                            {analytics.yieldProjections.currentYield.toFixed(2)}%
                          </div>
                          <div className="text-sm text-muted-foreground">Current Yield</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-blue-400">
                            {analytics.yieldProjections.projectedAnnual.toFixed(2)}%
                          </div>
                          <div className="text-sm text-muted-foreground">Projected Annual</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold text-purple-400">
                            {(analytics.yieldProjections.compoundingEffect * 100).toFixed(1)}%
                          </div>
                          <div className="text-sm text-muted-foreground">5-Year Compound</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </TabsContent>

            <TabsContent value="execute" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Zap className="w-5 h-5 mr-2 text-green-400" />
                    Execute RWA Transaction
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <Label htmlFor="assetSymbol">Asset</Label>
                      <Select 
                        value={transactionForm.assetSymbol} 
                        onValueChange={(value) => setTransactionForm(prev => ({ ...prev, assetSymbol: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select asset" />
                        </SelectTrigger>
                        <SelectContent>
                          {ondoAssets.map((asset) => (
                            <SelectItem key={asset.symbol} value={asset.symbol}>
                              {asset.symbol} - {asset.apy.toFixed(2)}% APY
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="type">Type</Label>
                      <Select 
                        value={transactionForm.type} 
                        onValueChange={(value: 'BUY' | 'SELL') => setTransactionForm(prev => ({ ...prev, type: value }))}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="BUY">Buy</SelectItem>
                          <SelectItem value="SELL">Sell</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="amount">Amount ($)</Label>
                      <Input
                        id="amount"
                        type="number"
                        placeholder="1000"
                        value={transactionForm.amount}
                        onChange={(e) => setTransactionForm(prev => ({ ...prev, amount: e.target.value }))}
                      />
                    </div>
                  </div>

                  <Button 
                    onClick={executeTransaction} 
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600"
                    size="lg"
                  >
                    {isLoading ? (
                      <>
                        <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                        Executing Transaction...
                      </>
                    ) : (
                      <>
                        <Zap className="w-4 h-4 mr-2" />
                        Execute Transaction
                      </>
                    )}
                  </Button>

                  <div className="p-3 bg-muted rounded-lg text-xs text-muted-foreground">
                    <div className="flex items-start space-x-2">
                      <AlertTriangle className="w-4 h-4 text-yellow-400 mt-0.5" />
                      <div>
                        <div className="font-medium text-yellow-400">Transaction Simulation</div>
                        <div className="mt-1">
                          This demo simulates RWA transactions. In production, this would integrate with 
                          Ondo Finance APIs for tokenized treasury execution.
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>

        {/* Oracle Metrics Sidebar */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Crown className="w-5 h-5 mr-2 text-yellow-400" />
                Oracle Metrics
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="text-xs text-muted-foreground">Larry Ellison Net Worth</div>
                <div className="text-xl font-bold text-yellow-400">$393.5B</div>
                <div className="text-xs text-green-400">+$15.8B (Oracle AI Surge)</div>
              </div>
              
              <Separator />
              
              <div>
                <div className="text-xs text-muted-foreground">Oracle Stock (ORCL)</div>
                <div className="text-xl font-bold">$142.85</div>
                <div className="text-xs text-green-400 flex items-center">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  +1.74% Today
                </div>
              </div>
              
              <Separator />
              
              <div>
                <div className="text-xs text-muted-foreground mb-2">AI Infrastructure Boom</div>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span>ORCL YTD</span>
                    <span className="text-green-400">+47.3%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>NVDA YTD</span>
                    <span className="text-green-400">+195.2%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Cloud Revenue</span>
                    <span className="text-blue-400">+25% Growth</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Shield className="w-5 h-5 mr-2 text-blue-400" />
                Strategy Health
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>RWA Allocation</span>
                  <span>65%</span>
                </div>
                <Progress value={65} className="h-2" />
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Risk Score</span>
                  <span className="text-green-400">Low</span>
                </div>
                <Progress value={25} className="h-2" />
              </div>
              
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Yield Efficiency</span>
                  <span>88%</span>
                </div>
                <Progress value={88} className="h-2" />
              </div>
              
              <div className="p-3 bg-green-500/10 rounded-lg">
                <div className="flex items-start space-x-2">
                  <CheckCircle className="w-4 h-4 text-green-400 mt-0.5" />
                  <div className="text-xs">
                    <div className="font-medium text-green-400">Oracle Aligned</div>
                    <div className="text-muted-foreground mt-1">
                      Your strategy closely follows Oracle's systematic wealth preservation approach
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

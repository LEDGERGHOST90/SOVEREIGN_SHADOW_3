
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Target, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  ArrowRight,
  Zap,
  Shield,
  Eye,
  DollarSign,
  Activity,
  BarChart3,
  Clock,
  Sparkles
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

interface EnhancedSiphonData {
  portfolioData: {
    totalValue: number;
    totalProfit: number;
    unrealizedPnL: number;
    realizedPnL: number;
    positions: any[];
    lastUpdated: string;
  };
  config: {
    realTimeTracking: boolean;
    feeOptimization: boolean;
    autoTrigger: boolean;
    thresholdAmount: number;
    baseSiphonRatio: number;
  };
  features: {
    realTimeTracking: boolean;
    feeOptimization: boolean;
    autoTrigger: boolean;
  };
}

export default function EnhancedSiphonMonitor() {
  const [siphonData, setSiphonData] = useState<EnhancedSiphonData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [lastExecution, setLastExecution] = useState<any>(null);
  const [realTimeStats, setRealTimeStats] = useState({
    profitVelocity: 0,
    riskLevel: 'MEDIUM',
    optimalTiming: '6:00 AM UTC'
  });

  const fetchEnhancedData = async () => {
    try {
      const response = await fetch('/api/siphon/enhanced');
      if (response.ok) {
        const data = await response.json();
        setSiphonData(data);
        
        // Update real-time stats
        if (data.portfolioData) {
          const velocity = data.portfolioData.totalProfit / data.portfolioData.totalValue * 100;
          setRealTimeStats(prev => ({
            ...prev,
            profitVelocity: velocity
          }));
        }
      }
    } catch (error) {
      console.error('Failed to fetch enhanced siphon data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const executeEnhancedSiphon = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/siphon/enhanced', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ manualTrigger: true })
      });

      if (response.ok) {
        const data = await response.json();
        setLastExecution(data.result);
        
        if (data.result.triggered) {
          toast.success(
            `🎯 Enhanced Siphon Executed: $${data.result.siphonedAmount.toFixed(2)} secured`,
            { description: data.result.reasoning.tactical }
          );
        } else {
          toast.info('Siphon conditions not met', {
            description: data.result.reasoning.tactical
          });
        }
        
        fetchEnhancedData();
      }
    } catch (error) {
      toast.error('Enhanced siphon execution failed');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEnhancedData();
    
    // Real-time updates every 30 seconds
    const interval = setInterval(fetchEnhancedData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading && !siphonData) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const profitThresholdProgress = siphonData 
    ? Math.min((siphonData.portfolioData.realizedPnL / siphonData.config.thresholdAmount) * 100, 100)
    : 0;

  const formatCurrency = (amount: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);

  const formatPercent = (value: number) => 
    `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;

  return (
    <div className="space-y-6">
      {/* Enhanced Status Header */}
      <Card className="border-primary/20 bg-gradient-to-r from-primary/5 to-primary/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-primary/20">
              <Sparkles className="h-5 w-5 text-primary" />
            </div>
            <div>
              <div className="text-xl">💎 Enhanced Siphon Engine v2.0</div>
              <div className="text-sm text-muted-foreground font-normal">
                Real-time wealth preservation with AI-driven optimization
              </div>
            </div>
            <div className="ml-auto flex items-center gap-2">
              <Badge variant={siphonData?.features.autoTrigger ? "default" : "secondary"}>
                {siphonData?.features.autoTrigger ? '🔥 Auto-Armed' : '⏸️ Manual'}
              </Badge>
              <Badge variant="outline" className="border-green-500/50 text-green-300">
                <Activity className="h-3 w-3 mr-1" />
                Live
              </Badge>
            </div>
          </CardTitle>
        </CardHeader>
      </Card>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="realtime">Real-Time</TabsTrigger>
          <TabsTrigger value="optimization">Fee Optimization</TabsTrigger>
          <TabsTrigger value="execution">Execution Log</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid md:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <DollarSign className="h-8 w-8 text-green-500" />
                  <div>
                    <div className="text-2xl font-bold">
                      {siphonData ? formatCurrency(siphonData.portfolioData.totalValue) : '$0'}
                    </div>
                    <div className="text-xs text-muted-foreground">Total Portfolio</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <TrendingUp className="h-8 w-8 text-blue-500" />
                  <div>
                    <div className="text-2xl font-bold text-green-400">
                      {siphonData ? formatCurrency(siphonData.portfolioData.realizedPnL) : '$0'}
                    </div>
                    <div className="text-xs text-muted-foreground">Realized P&L</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <BarChart3 className="h-8 w-8 text-purple-500" />
                  <div>
                    <div className="text-2xl font-bold">
                      {siphonData ? formatPercent(realTimeStats.profitVelocity) : '0%'}
                    </div>
                    <div className="text-xs text-muted-foreground">Profit Velocity</div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-3">
                  <Target className="h-8 w-8 text-orange-500" />
                  <div>
                    <div className="text-2xl font-bold">
                      {siphonData ? formatCurrency(siphonData.config.thresholdAmount) : '$0'}
                    </div>
                    <div className="text-xs text-muted-foreground">Trigger Threshold</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Threshold Progress */}
          <Card>
            <CardContent className="p-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold">Siphon Trigger Progress</h4>
                  <Badge variant={profitThresholdProgress >= 100 ? "default" : "secondary"}>
                    {profitThresholdProgress.toFixed(1)}% Ready
                  </Badge>
                </div>
                
                <Progress value={profitThresholdProgress} className="h-3" />
                
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <span>
                    Realized: {siphonData ? formatCurrency(siphonData.portfolioData.realizedPnL) : '$0'}
                  </span>
                  <span>
                    Target: {siphonData ? formatCurrency(siphonData.config.thresholdAmount) : '$0'}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Enhanced Execution Button */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="space-y-1">
                  <h4 className="font-semibold">Enhanced Siphon Execution</h4>
                  <p className="text-sm text-muted-foreground">
                    Execute intelligent siphon with real-time optimization
                  </p>
                </div>
                <Button
                  onClick={executeEnhancedSiphon}
                  disabled={isLoading}
                  size="lg"
                  className="gap-2 px-6"
                >
                  <Zap className="h-5 w-5" />
                  Execute Enhanced Siphon
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Real-Time Tab */}
        <TabsContent value="realtime" className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Live Portfolio Metrics
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center p-3 rounded-lg bg-muted/50">
                    <div className="text-lg font-bold text-green-400">
                      {siphonData ? formatCurrency(siphonData.portfolioData.unrealizedPnL) : '$0'}
                    </div>
                    <div className="text-xs text-muted-foreground">Unrealized P&L</div>
                  </div>
                  <div className="text-center p-3 rounded-lg bg-muted/50">
                    <div className="text-lg font-bold">
                      {siphonData?.portfolioData.positions.length || 0}
                    </div>
                    <div className="text-xs text-muted-foreground">Active Positions</div>
                  </div>
                </div>
                
                {siphonData && (
                  <div className="text-xs text-muted-foreground text-center">
                    Last updated: {new Date(siphonData.portfolioData.lastUpdated).toLocaleTimeString()}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Risk Assessment
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Risk Level</span>
                  <Badge variant={
                    realTimeStats.riskLevel === 'LOW' ? 'default' :
                    realTimeStats.riskLevel === 'MEDIUM' ? 'secondary' : 'destructive'
                  }>
                    {realTimeStats.riskLevel}
                  </Badge>
                </div>
                
                <div className="flex items-center justify-between">
                  <span className="text-sm">Optimal Timing</span>
                  <Badge variant="outline">
                    <Clock className="h-3 w-3 mr-1" />
                    {realTimeStats.optimalTiming}
                  </Badge>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Fee Optimization Tab */}
        <TabsContent value="optimization" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                Fee Optimization Engine
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <BarChart3 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <h4 className="text-lg font-medium mb-2">Advanced Fee Analysis</h4>
                <p>Fee optimization data will appear here with real trading activity</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Execution Log Tab */}
        <TabsContent value="execution" className="space-y-6">
          {lastExecution && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="p-4 rounded-lg border border-primary/20 bg-primary/5"
            >
              <div className="flex items-start gap-3">
                <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                <div className="flex-1">
                  <div className="font-medium">Latest Execution</div>
                  <div className="text-sm text-muted-foreground mb-2">
                    {lastExecution.reasoning.tactical}
                  </div>
                  <div className="text-sm italic text-primary/80">
                    "{lastExecution.reasoning.sage}"
                  </div>
                  
                  {lastExecution.triggered && (
                    <div className="mt-3 grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Secured:</span>
                        <span className="ml-2 font-medium text-green-400">
                          {formatCurrency(lastExecution.siphonedAmount)}
                        </span>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Retained:</span>
                        <span className="ml-2 font-medium">
                          {formatCurrency(lastExecution.retainedAmount)}
                        </span>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )}
          
          <Card>
            <CardHeader>
              <CardTitle>Execution History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <Target className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Enhanced siphon execution history will appear here</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

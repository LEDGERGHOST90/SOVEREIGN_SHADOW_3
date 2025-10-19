
'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Target, 
  TrendingUp, 
  AlertTriangle, 
  CheckCircle, 
  ArrowRight,
  Zap,
  Shield,
  Eye
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';

interface SiphonConfig {
  thresholdAmount: number;
  baseSiphonRatio: number;
  baseRetentionRatio: number;
  volatilityAdjustment: number;
}

interface SiphonLog {
  id: string;
  amount: number;
  type: string;
  status: string;
  createdAt: string;
}

interface SiphonStatus {
  config: SiphonConfig;
  recentSiphons: SiphonLog[];
  totalSiphoned: number;
  status: string;
}

export default function SiphonMonitor() {
  const [siphonStatus, setSiphonStatus] = useState<SiphonStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [testAmount, setTestAmount] = useState(5000);
  const [shadowIntel, setShadowIntel] = useState<any>(null);

  const fetchSiphonStatus = async () => {
    try {
      const response = await fetch('/api/siphon/execute');
      if (response.ok) {
        const data = await response.json();
        setSiphonStatus(data);
      }
    } catch (error) {
      console.error('Failed to fetch siphon status:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchShadowIntel = async () => {
    try {
      const response = await fetch('/api/shadow-ai/intel');
      if (response.ok) {
        const data = await response.json();
        setShadowIntel(data);
      }
    } catch (error) {
      console.error('Failed to fetch shadow intel:', error);
    }
  };

  const executeSiphonTest = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/siphon/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          profitAmount: testAmount,
          assetSymbol: 'BTC',
          source: 'test'
        })
      });

      if (response.ok) {
        const data = await response.json();
        if (data.result.triggered) {
          toast.success(`Siphon executed: $${data.result.siphonedAmount.toFixed(2)} secured`);
        } else {
          toast.info('Siphon threshold not met');
        }
        fetchSiphonStatus();
      }
    } catch (error) {
      toast.error('Siphon execution failed');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchSiphonStatus();
    fetchShadowIntel();
    
    const interval = setInterval(() => {
      fetchShadowIntel();
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  if (isLoading && !siphonStatus) {
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

  const progressPercentage = siphonStatus 
    ? Math.min((testAmount / siphonStatus.config.thresholdAmount) * 100, 100)
    : 0;

  return (
    <div className="space-y-6">
      {/* Hybrid Siphon Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-primary" />
            💎 Hybrid Siphon Engine
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Status Overview */}
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center p-4 rounded-lg bg-muted/50">
              <div className="text-2xl font-bold text-primary">
                ${siphonStatus?.totalSiphoned.toLocaleString() || '0'}
              </div>
              <div className="text-sm text-muted-foreground">Total Secured</div>
            </div>
            <div className="text-center p-4 rounded-lg bg-muted/50">
              <div className="text-2xl font-bold">
                ${siphonStatus?.config.thresholdAmount.toLocaleString() || '3,500'}
              </div>
              <div className="text-sm text-muted-foreground">Trigger Threshold</div>
            </div>
            <div className="text-center p-4 rounded-lg bg-muted/50">
              <div className="text-2xl font-bold">
                {((siphonStatus?.config.baseSiphonRatio || 0.3) * 100).toFixed(0)}%
              </div>
              <div className="text-sm text-muted-foreground">Base Siphon Ratio</div>
            </div>
          </div>

          <Separator />

          {/* Siphon Test */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="font-semibold">Test Siphon Logic</h4>
              <Badge variant={siphonStatus?.status === 'ARMED' ? 'default' : 'secondary'}>
                {siphonStatus?.status === 'ARMED' ? '⚔️ Armed' : '🔄 Standby'}
              </Badge>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span>Test Amount: ${testAmount.toLocaleString()}</span>
                <span>{progressPercentage.toFixed(1)}% of threshold</span>
              </div>
              <Progress value={progressPercentage} className="h-2" />
            </div>

            <div className="flex items-center gap-2">
              <Button
                onClick={() => setTestAmount(Math.max(1000, testAmount - 1000))}
                variant="outline"
                size="sm"
                disabled={isLoading}
              >
                -$1K
              </Button>
              <Button
                onClick={() => setTestAmount(testAmount + 1000)}
                variant="outline"
                size="sm"
                disabled={isLoading}
              >
                +$1K
              </Button>
              <Button
                onClick={executeSiphonTest}
                className="ml-auto gap-2"
                disabled={isLoading}
              >
                <Zap className="h-4 w-4" />
                Execute Test Siphon
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Shadow.AI Intelligence */}
      {shadowIntel && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5" />
              🌑 Shadow.AI Intelligence
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="text-sm font-medium">Market Regime</div>
                <Badge variant={
                  shadowIntel.intelligence.volatilityRegime === 'LOW' ? 'default' :
                  shadowIntel.intelligence.volatilityRegime === 'MEDIUM' ? 'secondary' :
                  shadowIntel.intelligence.volatilityRegime === 'HIGH' ? 'destructive' :
                  'destructive'
                }>
                  {shadowIntel.intelligence.volatilityRegime} Volatility
                </Badge>
              </div>
              
              <div className="space-y-2">
                <div className="text-sm font-medium">Dark Pool Activity</div>
                <Badge variant="outline">
                  {shadowIntel.intelligence.darkPoolActivity.level} - {shadowIntel.intelligence.darkPoolActivity.direction}
                </Badge>
              </div>
            </div>

            <div className="space-y-2">
              <div className="text-sm font-medium">Risk Assessment</div>
              <div className="flex items-center gap-2">
                <Badge variant={
                  shadowIntel.intelligence.riskSignals.level === 'GREEN' ? 'default' :
                  shadowIntel.intelligence.riskSignals.level === 'YELLOW' ? 'secondary' :
                  shadowIntel.intelligence.riskSignals.level === 'ORANGE' ? 'destructive' :
                  'destructive'
                }>
                  <Shield className="h-3 w-3 mr-1" />
                  {shadowIntel.intelligence.riskSignals.level}
                </Badge>
                <span className="text-sm text-muted-foreground">
                  {shadowIntel.intelligence.riskSignals.recommendation}
                </span>
              </div>
            </div>

            {shadowIntel.intelligence.siphonRecommendation.suggested && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-3 rounded-lg bg-orange-500/10 border border-orange-500/20"
              >
                <div className="flex items-center gap-2 text-orange-300">
                  <AlertTriangle className="h-4 w-4" />
                  <span className="font-medium">Siphon Recommended</span>
                  <Badge variant="outline">
                    {shadowIntel.intelligence.siphonRecommendation.urgency}
                  </Badge>
                </div>
                <p className="text-sm mt-1">
                  {shadowIntel.intelligence.siphonRecommendation.reasoning}
                </p>
              </motion.div>
            )}

            <div className="p-3 rounded-lg bg-muted/50 border-l-4 border-primary">
              <div className="text-sm italic text-muted-foreground">
                "{shadowIntel.wisdom}"
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recent Siphon History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Recent Siphon Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-48">
            {siphonStatus?.recentSiphons.length ? (
              <div className="space-y-2">
                {siphonStatus.recentSiphons.map((log) => (
                  <div key={log.id} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <div>
                        <div className="text-sm font-medium">
                          ${log.amount.toFixed(2)} secured
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {new Date(log.createdAt).toLocaleString()}
                        </div>
                      </div>
                    </div>
                    <Badge variant="outline">
                      {log.status}
                    </Badge>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-32 text-muted-foreground">
                <div className="text-center">
                  <Target className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>No siphon activity yet</p>
                </div>
              </div>
            )}
          </ScrollArea>
        </CardContent>
      </Card>
    </div>
  );
}

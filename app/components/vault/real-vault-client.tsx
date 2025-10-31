
'use client';

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { 
  Shield, 
  Vault, 
  ArrowUpRight, 
  ArrowDownLeft, 
  Clock,
  AlertTriangle,
  CheckCircle,
  Wallet,
  Key,
  RefreshCw,
  TrendingUp,
  Database
} from "lucide-react";
import { toast } from "sonner";
import { motion } from "framer-motion";

const PieChartWrapper = ({ data }: { data: any[] }) => {
  if (typeof window === 'undefined') {
    return <div className="flex items-center justify-center h-full text-muted-foreground">Loading chart...</div>;
  }
  
  const { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } = require('recharts');
  
  const COLORS = ['#f7931a', '#627eea', '#f0b90b', '#8b5cf6', '#22c55e', '#ef4444'];
  
  return (
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={5}
          dataKey="percentage"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip 
          formatter={(value: any, name: any) => [`${parseFloat(value).toFixed(2)}%`, 'Allocation']}
          contentStyle={{
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            border: '1px solid rgba(255, 215, 0, 0.2)',
            borderRadius: '8px',
            color: 'white'
          }}
        />
        <Legend 
          verticalAlign="top" 
          height={36}
          wrapperStyle={{ fontSize: 11 }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
};

interface RealVaultData {
  totalValue: number;
  hotWalletValue: number;
  coldVaultValue: number;
  assets: Array<{
    symbol: string;
    amount: number;
    usdValue: number;
    percentage: number;
  }>;
  recentActivity: Array<{
    id: string;
    asset: string;
    amount: number;
    type: string;
    fromWallet: string;
    toWallet: string;
    status: string;
    createdAt: string;
    completedAt?: string;
  }>;
}

interface VaultMetadata {
  totalDeposits: number;
  totalTrades: number;
  lastUpdated: string;
  siphonRatio: number;
  nextGraduation: number;
  dataSource: string;
}

export default function RealVaultClient() {
  const [vaultData, setVaultData] = useState<RealVaultData | null>(null);
  const [metadata, setMetadata] = useState<VaultMetadata | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchRealVaultData = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/vault/real-data');
      const result = await response.json();
      
      if (result.success) {
        setVaultData(result.data);
        setMetadata(result.metadata);
        toast.success("Real vault data loaded from Binance US");
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      console.error('Error fetching real vault data:', error);
      toast.error("Failed to fetch real vault data");
    } finally {
      setLoading(false);
    }
  };

  const handleManualSiphon = async () => {
    setActionLoading(true);
    try {
      const response = await fetch('/api/vault/real-data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'MANUAL_SIPHON',
          asset: 'BTC',
          amount: 0.001
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        toast.success("Manual siphon initiated - Check activity log");
        // Refresh data after 2 seconds
        setTimeout(fetchRealVaultData, 2000);
      } else {
        throw new Error(result.error);
      }
    } catch (error) {
      console.error('Error initiating siphon:', error);
      toast.error("Failed to initiate manual siphon");
    } finally {
      setActionLoading(false);
    }
  };

  useEffect(() => {
    fetchRealVaultData();
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="text-center py-12">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
          <p className="text-muted-foreground">Loading your real vault data from Binance US...</p>
        </div>
      </div>
    );
  }

  if (!vaultData) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="text-center py-12">
            <AlertTriangle className="h-8 w-8 mx-auto mb-4 text-destructive" />
            <p className="text-muted-foreground">Failed to load vault data</p>
            <Button onClick={fetchRealVaultData} className="mt-4">
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const pendingTransfers = vaultData.recentActivity.filter(log => log.status === 'PENDING').length;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-gold bg-clip-text text-transparent">
            Vault Tracker
          </h1>
          <p className="text-muted-foreground flex items-center gap-2">
            <Database className="h-4 w-4" />
            Real data from {metadata?.dataSource} • Updated {metadata ? new Date(metadata.lastUpdated).toLocaleTimeString() : 'now'}
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            onClick={handleManualSiphon}
            disabled={actionLoading}
            variant="outline" 
            size="sm"
            className="gap-2"
          >
            <ArrowUpRight className="h-4 w-4" />
            {actionLoading ? 'Processing...' : 'Manual Siphon'}
          </Button>
          <Button 
            onClick={fetchRealVaultData}
            variant="outline" 
            size="sm"
            disabled={loading}
            className="gap-2"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Real Portfolio Overview */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="vault-card glow-green">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Cold Vault (25%)</CardTitle>
              <Shield className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-400">
                ${vaultData.coldVaultValue.toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground">
                Secured profits
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="trading-card glow-blue">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Hot Wallet (75%)</CardTitle>
              <Wallet className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-400">
                ${vaultData.hotWalletValue.toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground">
                Active trading balance
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="wealth-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending Transfers</CardTitle>
              <Clock className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">
                {pendingTransfers}
              </div>
              <p className="text-xs text-muted-foreground">
                Awaiting confirmation
              </p>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="border-primary/20">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Next Graduation</CardTitle>
              <Key className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-muted-foreground">
                ${metadata?.nextGraduation.toFixed(0)}
              </div>
              <p className="text-xs text-muted-foreground">
                Until next milestone
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Real Asset Allocation */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Real Asset Allocation
              </CardTitle>
              <p className="text-sm text-muted-foreground">
                Based on your Binance US portfolio
              </p>
            </CardHeader>
            <CardContent>
              {vaultData.assets.length > 0 ? (
                <div className="h-[300px] w-full">
                  <PieChartWrapper data={vaultData.assets} />
                </div>
              ) : (
                <div className="h-[300px] flex items-center justify-center text-muted-foreground">
                  No assets found in portfolio
                </div>
              )}
              
              {/* Asset breakdown */}
              <div className="mt-4 space-y-2">
                {vaultData.assets.slice(0, 5).map((asset, index) => (
                  <div key={asset.symbol} className="flex justify-between items-center text-sm">
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ 
                          backgroundColor: ['#f7931a', '#627eea', '#f0b90b', '#8b5cf6', '#22c55e'][index] 
                        }}
                      />
                      <span>{asset.symbol}</span>
                    </div>
                    <div className="text-right">
                      <div>${asset.usdValue.toFixed(2)}</div>
                      <div className="text-xs text-muted-foreground">
                        {asset.percentage.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Portfolio Stats */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Portfolio Statistics
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">Total Portfolio Value</span>
                <Badge variant="default" className="bg-green-600 text-lg px-3 py-1">
                  ${vaultData.totalValue.toLocaleString()}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Total Deposits Tracked</span>
                <Badge variant="outline">
                  ${metadata?.totalDeposits.toFixed(2)}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Total Trades Processed</span>
                <Badge variant="outline">
                  {metadata?.totalTrades}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Active Assets</span>
                <Badge variant="outline">
                  {vaultData.assets.length}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Siphon Ratio</span>
                <Badge variant="default" className="bg-blue-600">
                  {((metadata?.siphonRatio || 0) * 100).toFixed(0)}%
                </Badge>
              </div>
              <Separator />
              <div className="text-xs text-muted-foreground">
                Data source: {metadata?.dataSource}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Real Vault Activity */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ArrowUpRight className="h-5 w-5" />
              Real Vault Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {vaultData.recentActivity.length > 0 ? (
                vaultData.recentActivity.slice(0, 10).map((log) => (
                  <div key={log.id} className="flex items-center justify-between p-4 rounded-lg bg-muted/30">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-full ${
                        log.type === 'SIPHON' ? 'bg-blue-500/20 text-blue-400' :
                        log.type === 'GRADUATION' ? 'bg-green-500/20 text-green-400' :
                        log.type === 'MANUAL_TRANSFER' ? 'bg-primary/20 text-primary' :
                        'bg-red-500/20 text-red-400'
                      }`}>
                        {log.type === 'SIPHON' || log.type === 'Deposit' ? <ArrowUpRight className="h-4 w-4" /> :
                         log.type === 'GRADUATION' ? <Shield className="h-4 w-4" /> :
                         log.type === 'MANUAL_TRANSFER' ? <Wallet className="h-4 w-4" /> :
                         <AlertTriangle className="h-4 w-4" />}
                      </div>
                      <div>
                        <div className="font-medium">
                          {log.type.replace('_', ' ')} - {typeof log.amount === 'number' ? log.amount.toFixed(6) : log.amount} {log.asset}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {log.fromWallet} → {log.toWallet}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant={
                        log.status === 'COMPLETED' ? 'default' : 
                        log.status === 'PENDING' ? 'secondary' : 
                        'destructive'
                      }>
                        {log.status}
                      </Badge>
                      <div className="text-xs text-muted-foreground mt-1">
                        {new Date(log.createdAt).toLocaleString()}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Vault className="h-8 w-8 mx-auto mb-2" />
                  <p>No vault activity found</p>
                  <p className="text-xs">Start trading to see vault transfers</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}

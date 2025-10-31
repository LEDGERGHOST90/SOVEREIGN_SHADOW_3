
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
  RefreshCw
} from "lucide-react";
import { VaultLog } from "@/lib/types";
import { toast } from "sonner";
import { motion } from "framer-motion";

const PieChartWrapper = ({ data, colors }: { data: any[], colors: string[] }) => {
  if (typeof window === 'undefined') {
    return <div>Loading chart...</div>;
  }
  
  const { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } = require('recharts');
  
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
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip 
          formatter={(value: any) => [`${value}%`, 'Allocation']}
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

interface VaultSummary {
  totalColdValue: number;
  totalHotValue: number;
  pendingTransfers: number;
  lastSiphon: string;
  nextGraduation: number;
}

const COLORS = ['#22c55e', '#3b82f6', '#f59e0b', '#ef4444'];

export default function VaultClient() {
  const [vaultSummary, setVaultSummary] = useState<VaultSummary>({
    totalColdValue: 67500,
    totalHotValue: 22500,
    pendingTransfers: 2,
    lastSiphon: '2024-01-15T10:30:00Z',
    nextGraduation: 500
  });
  
  const [vaultLogs, setVaultLogs] = useState<VaultLog[]>([
    {
      id: '1',
      asset: 'BTC',
      amount: 0.5,
      type: 'SIPHON',
      fromWallet: 'hot',
      toWallet: 'cold',
      status: 'COMPLETED',
      createdAt: '2024-01-15T10:30:00Z',
      completedAt: '2024-01-15T10:35:00Z'
    },
    {
      id: '2',
      asset: 'ETH',
      amount: 8.2,
      type: 'GRADUATION',
      fromWallet: 'hot',
      toWallet: 'cold',
      status: 'PENDING',
      createdAt: '2024-01-15T11:00:00Z'
    }
  ]);

  const [loading, setLoading] = useState(false);

  // Mock vault allocation data
  const allocationData = [
    { name: 'Bitcoin (BTC)', value: 45, color: '#f7931a' },
    { name: 'Ethereum (ETH)', value: 30, color: '#627eea' },
    { name: 'Binance Coin (BNB)', value: 15, color: '#f0b90b' },
    { name: 'Others', value: 10, color: '#8b5cf6' }
  ];

  const fetchVaultData = async () => {
    setLoading(true);
    try {
      // In a real app, this would fetch from API
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success("Vault data refreshed");
    } catch (error) {
      toast.error("Failed to fetch vault data");
    } finally {
      setLoading(false);
    }
  };

  const handleManualSiphon = async () => {
    try {
      toast.success("Manual siphon initiated");
      // Add new log entry
      const newLog: VaultLog = {
        id: Date.now().toString(),
        asset: 'BTC',
        amount: 0.3,
        type: 'MANUAL_TRANSFER',
        fromWallet: 'hot',
        toWallet: 'cold',
        status: 'PENDING',
        createdAt: new Date().toISOString()
      };
      setVaultLogs(prev => [newLog, ...prev]);
    } catch (error) {
      toast.error("Failed to initiate siphon");
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-gold bg-clip-text text-transparent">
            Vault Tracker
          </h1>
          <p className="text-muted-foreground">
            Cold storage security & automated profit siphoning
          </p>
        </div>
        <div className="flex gap-2">
          <Button 
            onClick={handleManualSiphon}
            variant="outline" 
            size="sm"
            className="gap-2"
          >
            <ArrowUpRight className="h-4 w-4" />
            Manual Siphon
          </Button>
          <Button 
            onClick={fetchVaultData}
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

      {/* Vault Overview */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card className="vault-card glow-green">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Cold Vault</CardTitle>
              <Shield className="h-4 w-4 text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-400">
                ${vaultSummary.totalColdValue.toLocaleString()}
              </div>
              <p className="text-xs text-muted-foreground">
                Secured in hardware wallets
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
              <CardTitle className="text-sm font-medium">Hot Wallet</CardTitle>
              <Wallet className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-400">
                ${vaultSummary.totalHotValue.toLocaleString()}
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
                {vaultSummary.pendingTransfers}
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
                ${vaultSummary.nextGraduation}
              </div>
              <p className="text-xs text-muted-foreground">
                Until $3,500 threshold
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Vault Allocation */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Vault className="h-5 w-5" />
                Cold Storage Allocation
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[300px] w-full">
                <PieChartWrapper 
                  data={allocationData}
                  colors={allocationData.map(item => item.color)}
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Security Status */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Security Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">Hardware Wallet Connection</span>
                <Badge variant="default" className="bg-green-600">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Connected
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Multi-Signature Wallet</span>
                <Badge variant="default" className="bg-green-600">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Active
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Backup Seed Security</span>
                <Badge variant="default" className="bg-green-600">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Verified
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Auto-Siphon Rules</span>
                <Badge variant="default" className="bg-blue-600">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Enabled
                </Badge>
              </div>
              <Separator />
              <div className="text-xs text-muted-foreground">
                Last security audit: {new Date(vaultSummary.lastSiphon).toLocaleDateString()}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Recent Vault Activity */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ArrowUpRight className="h-5 w-5" />
              Recent Vault Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {vaultLogs.map((log) => (
                <div key={log.id} className="flex items-center justify-between p-4 rounded-lg bg-muted/30">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full ${
                      log.type === 'SIPHON' ? 'bg-blue-500/20 text-blue-400' :
                      log.type === 'GRADUATION' ? 'bg-green-500/20 text-green-400' :
                      log.type === 'MANUAL_TRANSFER' ? 'bg-primary/20 text-primary' :
                      'bg-red-500/20 text-red-400'
                    }`}>
                      {log.type === 'SIPHON' ? <ArrowUpRight className="h-4 w-4" /> :
                       log.type === 'GRADUATION' ? <Shield className="h-4 w-4" /> :
                       log.type === 'MANUAL_TRANSFER' ? <Wallet className="h-4 w-4" /> :
                       <AlertTriangle className="h-4 w-4" />}
                    </div>
                    <div>
                      <div className="font-medium">
                        {log.type.replace('_', ' ')} - {log.amount} {log.asset}
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
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  );
}

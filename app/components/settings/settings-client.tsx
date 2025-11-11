
'use client';

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { 
  Settings, 
  Shield, 
  Key, 
  DollarSign, 
  Bot,
  AlertTriangle,
  Save,
  Eye,
  EyeOff
} from "lucide-react";
import { UserSettings } from "@/lib/types";
import { toast } from "sonner";

export default function SettingsClient() {
  const [settings, setSettings] = useState<Partial<UserSettings>>({
    liveTrading: false,
    dailyLimit: 1000,
    siphonRatio: 0.70,
    graduationThreshold: 3500,
    agentReviewInterval: 24,
    agentStrictMode: false,
    riskLevel: 'MODERATE'
  });
  
  const [apiCredentials, setApiCredentials] = useState({
    binance: { apiKey: '', apiSecret: '', showSecret: false },
    kraken: { apiKey: '', apiSecret: '', showSecret: false },
    okx: { apiKey: '', apiSecret: '', passphrase: '', showSecret: false },
    coinbase: { apiKey: '', apiSecret: '', showSecret: false },
    infura: { apiKey: '', showSecret: false },
    etherscan: { apiKey: '', showSecret: false },
    ledger: { address: '', note: 'Hardware wallet - view only' },
    metamask: { address: '', note: 'Connected via Etherscan API' }
  });
  
  const [loading, setLoading] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  const handleSettingChange = (key: string, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    setHasChanges(true);
  };

  const handleSaveSettings = async () => {
    setLoading(true);
    try {
      // In a real app, this would save to API
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success("Settings saved successfully");
      setHasChanges(false);
    } catch (error) {
      toast.error("Failed to save settings");
    } finally {
      setLoading(false);
    }
  };

  const handleSaveCredentials = async (exchange: string) => {
    const creds = apiCredentials[exchange as keyof typeof apiCredentials];

    // Validation based on exchange type
    if (exchange === 'infura' || exchange === 'etherscan') {
      if (!('apiKey' in creds) || !creds.apiKey) {
        toast.error("Please provide API key");
        return;
      }
    } else if (exchange === 'ledger' || exchange === 'metamask') {
      if (!('address' in creds) || !creds.address) {
        toast.error("Please provide wallet address");
        return;
      }
    } else if (exchange === 'okx') {
      if (!('apiKey' in creds) || !('apiSecret' in creds) || !('passphrase' in creds) || !creds.apiKey || !creds.apiSecret || !creds.passphrase) {
        toast.error("Please provide API key, secret, and passphrase");
        return;
      }
    } else {
      if (!('apiKey' in creds) || !('apiSecret' in creds) || !creds.apiKey || !creds.apiSecret) {
        toast.error("Please provide both API key and secret");
        return;
      }
    }

    setLoading(true);
    try {
      const payload: any = {
        exchange,
        apiKey: ('apiKey' in creds) ? creds.apiKey : undefined,
        apiSecret: ('apiSecret' in creds) ? creds.apiSecret : undefined
      };

      if (exchange === 'okx' && 'passphrase' in creds) {
        payload.passphrase = creds.passphrase;
      }

      const response = await fetch('/api/settings/credentials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Failed to save credentials');
      }

      toast.success(`${exchange.toUpperCase()} credentials verified and saved!`);

      // Clear the form for this exchange
      setApiCredentials(prev => ({
        ...prev,
        [exchange]: exchange === 'okx'
          ? { apiKey: '', apiSecret: '', passphrase: '', showSecret: false }
          : exchange === 'infura' || exchange === 'etherscan'
          ? { apiKey: '', showSecret: false }
          : exchange === 'ledger' || exchange === 'metamask'
          ? { address: '', note: prev[exchange as keyof typeof prev].note }
          : { apiKey: '', apiSecret: '', showSecret: false }
      }));
    } catch (error: any) {
      toast.error(error.message || `Failed to save ${exchange.toUpperCase()} credentials`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-gold bg-clip-text text-transparent">
            System Settings
          </h1>
          <p className="text-muted-foreground">
            Configure trading parameters, security options, and AI agent behavior
          </p>
        </div>
        {hasChanges && (
          <Button onClick={handleSaveSettings} disabled={loading} className="gap-2">
            <Save className="h-4 w-4" />
            {loading ? "Saving..." : "Save Changes"}
          </Button>
        )}
      </div>

      <div className="grid gap-6">
        {/* Trading Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <DollarSign className="h-5 w-5" />
              Trading Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label>Live Trading Mode</Label>
                <p className="text-sm text-muted-foreground">
                  Enable real trading with Binance API (disable for paper trading)
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  checked={settings.liveTrading}
                  onCheckedChange={(checked) => handleSettingChange('liveTrading', checked)}
                />
                <Badge variant={settings.liveTrading ? "destructive" : "default"}>
                  {settings.liveTrading ? "LIVE" : "PAPER"}
                </Badge>
              </div>
            </div>
            
            <Separator />
            
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="dailyLimit">Daily Trading Limit ($)</Label>
                <Input
                  id="dailyLimit"
                  type="number"
                  value={settings.dailyLimit}
                  onChange={(e) => handleSettingChange('dailyLimit', parseFloat(e.target.value))}
                />
                <p className="text-xs text-muted-foreground">
                  Maximum amount for daily trading activities
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="riskLevel">Risk Level</Label>
                <select
                  id="riskLevel"
                  value={settings.riskLevel}
                  onChange={(e) => handleSettingChange('riskLevel', e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="CONSERVATIVE">Conservative</option>
                  <option value="MODERATE">Moderate</option>
                  <option value="AGGRESSIVE">Aggressive</option>
                </select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Vault Configuration */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Vault Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="siphonRatio">Profit Siphon Ratio</Label>
                <Input
                  id="siphonRatio"
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  value={settings.siphonRatio}
                  onChange={(e) => handleSettingChange('siphonRatio', parseFloat(e.target.value))}
                />
                <p className="text-xs text-muted-foreground">
                  Percentage of profits moved to cold vault (0.70 = 70%)
                </p>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="graduationThreshold">Graduation Threshold ($)</Label>
                <Input
                  id="graduationThreshold"
                  type="number"
                  value={settings.graduationThreshold}
                  onChange={(e) => handleSettingChange('graduationThreshold', parseFloat(e.target.value))}
                />
                <p className="text-xs text-muted-foreground">
                  Amount threshold for vault graduation
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Exchange API Credentials */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">Exchange & Service Credentials</h2>
          <p className="text-sm text-muted-foreground flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-orange-400" />
            All credentials are encrypted and stored securely
          </p>

          <div className="grid gap-4 md:grid-cols-2">
            {/* Binance US */}
            <Card className="border-amber-500/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Key className="h-4 w-4 text-amber-400" />
                  Binance US
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-1">
                  <Label className="text-xs">API Key</Label>
                  <Input
                    type="text"
                    value={apiCredentials.binance.apiKey}
                    onChange={(e) => setApiCredentials(prev => ({
                      ...prev,
                      binance: { ...prev.binance, apiKey: e.target.value }
                    }))}
                    placeholder="Enter API key"
                    className="h-9 text-sm"
                  />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">API Secret</Label>
                  <div className="relative">
                    <Input
                      type={apiCredentials.binance.showSecret ? "text" : "password"}
                      value={apiCredentials.binance.apiSecret}
                      onChange={(e) => setApiCredentials(prev => ({
                        ...prev,
                        binance: { ...prev.binance, apiSecret: e.target.value }
                      }))}
                      placeholder="Enter API secret"
                      className="h-9 text-sm pr-9"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-9 px-2"
                      onClick={() => setApiCredentials(prev => ({
                        ...prev,
                        binance: { ...prev.binance, showSecret: !prev.binance.showSecret }
                      }))}
                    >
                      {apiCredentials.binance.showSecret ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                    </Button>
                  </div>
                </div>
                <Button onClick={() => handleSaveCredentials('binance')} disabled={loading} size="sm" className="w-full">
                  {loading ? "Verifying..." : "Save & Test"}
                </Button>
              </CardContent>
            </Card>

            {/* Coinbase */}
            <Card className="border-blue-500/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Key className="h-4 w-4 text-blue-400" />
                  Coinbase Advanced
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-1">
                  <Label className="text-xs">API Key</Label>
                  <Input
                    type="text"
                    value={apiCredentials.coinbase.apiKey}
                    onChange={(e) => setApiCredentials(prev => ({
                      ...prev,
                      coinbase: { ...prev.coinbase, apiKey: e.target.value }
                    }))}
                    placeholder="Enter API key"
                    className="h-9 text-sm"
                  />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">API Secret</Label>
                  <div className="relative">
                    <Input
                      type={apiCredentials.coinbase.showSecret ? "text" : "password"}
                      value={apiCredentials.coinbase.apiSecret}
                      onChange={(e) => setApiCredentials(prev => ({
                        ...prev,
                        coinbase: { ...prev.coinbase, apiSecret: e.target.value }
                      }))}
                      placeholder="Enter API secret"
                      className="h-9 text-sm pr-9"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-9 px-2"
                      onClick={() => setApiCredentials(prev => ({
                        ...prev,
                        coinbase: { ...prev.coinbase, showSecret: !prev.coinbase.showSecret }
                      }))}
                    >
                      {apiCredentials.coinbase.showSecret ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                    </Button>
                  </div>
                </div>
                <Button onClick={() => handleSaveCredentials('coinbase')} disabled={loading} size="sm" className="w-full">
                  {loading ? "Verifying..." : "Save & Test"}
                </Button>
              </CardContent>
            </Card>

            {/* Kraken */}
            <Card className="border-purple-500/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Key className="h-4 w-4 text-purple-400" />
                  Kraken
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-1">
                  <Label className="text-xs">API Key</Label>
                  <Input
                    type="text"
                    value={apiCredentials.kraken.apiKey}
                    onChange={(e) => setApiCredentials(prev => ({
                      ...prev,
                      kraken: { ...prev.kraken, apiKey: e.target.value }
                    }))}
                    placeholder="Enter API key"
                    className="h-9 text-sm"
                  />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">API Secret</Label>
                  <div className="relative">
                    <Input
                      type={apiCredentials.kraken.showSecret ? "text" : "password"}
                      value={apiCredentials.kraken.apiSecret}
                      onChange={(e) => setApiCredentials(prev => ({
                        ...prev,
                        kraken: { ...prev.kraken, apiSecret: e.target.value }
                      }))}
                      placeholder="Enter API secret"
                      className="h-9 text-sm pr-9"
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="absolute right-0 top-0 h-9 px-2"
                      onClick={() => setApiCredentials(prev => ({
                        ...prev,
                        kraken: { ...prev.kraken, showSecret: !prev.kraken.showSecret }
                      }))}
                    >
                      {apiCredentials.kraken.showSecret ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                    </Button>
                  </div>
                </div>
                <Button onClick={() => handleSaveCredentials('kraken')} disabled={loading} size="sm" className="w-full">
                  {loading ? "Verifying..." : "Save & Test"}
                </Button>
              </CardContent>
            </Card>

            {/* OKX */}
            <Card className="border-green-500/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Key className="h-4 w-4 text-green-400" />
                  OKX
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-1">
                  <Label className="text-xs">API Key</Label>
                  <Input
                    type="text"
                    value={apiCredentials.okx.apiKey}
                    onChange={(e) => setApiCredentials(prev => ({
                      ...prev,
                      okx: { ...prev.okx, apiKey: e.target.value }
                    }))}
                    placeholder="Enter API key"
                    className="h-9 text-sm"
                  />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">API Secret</Label>
                  <Input
                    type={apiCredentials.okx.showSecret ? "text" : "password"}
                    value={apiCredentials.okx.apiSecret}
                    onChange={(e) => setApiCredentials(prev => ({
                      ...prev,
                      okx: { ...prev.okx, apiSecret: e.target.value }
                    }))}
                    placeholder="Enter API secret"
                    className="h-9 text-sm"
                  />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Passphrase</Label>
                  <Input
                    type="password"
                    value={apiCredentials.okx.passphrase}
                    onChange={(e) => setApiCredentials(prev => ({
                      ...prev,
                      okx: { ...prev.okx, passphrase: e.target.value }
                    }))}
                    placeholder="Enter passphrase"
                    className="h-9 text-sm"
                  />
                </div>
                <Button onClick={() => handleSaveCredentials('okx')} disabled={loading} size="sm" className="w-full">
                  {loading ? "Verifying..." : "Save & Test"}
                </Button>
              </CardContent>
            </Card>

            {/* Infura */}
            <Card className="border-orange-500/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Key className="h-4 w-4 text-orange-400" />
                  Infura RPC
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-1">
                  <Label className="text-xs">Project ID / API Key</Label>
                  <Input
                    type="text"
                    value={apiCredentials.infura.apiKey}
                    onChange={(e) => setApiCredentials(prev => ({
                      ...prev,
                      infura: { ...prev.infura, apiKey: e.target.value }
                    }))}
                    placeholder="Enter Infura project ID"
                    className="h-9 text-sm"
                  />
                </div>
                <Button onClick={() => handleSaveCredentials('infura')} disabled={loading} size="sm" className="w-full">
                  {loading ? "Saving..." : "Save API Key"}
                </Button>
              </CardContent>
            </Card>

            {/* Etherscan */}
            <Card className="border-cyan-500/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Key className="h-4 w-4 text-cyan-400" />
                  Etherscan API
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-1">
                  <Label className="text-xs">API Key</Label>
                  <Input
                    type="text"
                    value={apiCredentials.etherscan.apiKey}
                    onChange={(e) => setApiCredentials(prev => ({
                      ...prev,
                      etherscan: { ...prev.etherscan, apiKey: e.target.value }
                    }))}
                    placeholder="Enter Etherscan API key"
                    className="h-9 text-sm"
                  />
                </div>
                <Button onClick={() => handleSaveCredentials('etherscan')} disabled={loading} size="sm" className="w-full">
                  {loading ? "Saving..." : "Save API Key"}
                </Button>
              </CardContent>
            </Card>

            {/* Ledger */}
            <Card className="border-amber-500/20 bg-amber-950/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Shield className="h-4 w-4 text-amber-400" />
                  Ledger Wallet
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-1">
                  <Label className="text-xs">Wallet Address (View Only)</Label>
                  <Input
                    type="text"
                    value={apiCredentials.ledger.address}
                    onChange={(e) => setApiCredentials(prev => ({
                      ...prev,
                      ledger: { ...prev.ledger, address: e.target.value }
                    }))}
                    placeholder="0x..."
                    className="h-9 text-sm font-mono"
                  />
                </div>
                <p className="text-xs text-muted-foreground">{apiCredentials.ledger.note}</p>
                <Button onClick={() => handleSaveCredentials('ledger')} disabled={loading} size="sm" className="w-full">
                  {loading ? "Saving..." : "Save Address"}
                </Button>
              </CardContent>
            </Card>

            {/* MetaMask */}
            <Card className="border-orange-500/20 bg-orange-950/5">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-base">
                  <Shield className="h-4 w-4 text-orange-400" />
                  MetaMask Wallet
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="space-y-1">
                  <Label className="text-xs">Wallet Address</Label>
                  <Input
                    type="text"
                    value={apiCredentials.metamask.address}
                    onChange={(e) => setApiCredentials(prev => ({
                      ...prev,
                      metamask: { ...prev.metamask, address: e.target.value }
                    }))}
                    placeholder="0x..."
                    className="h-9 text-sm font-mono"
                  />
                </div>
                <p className="text-xs text-muted-foreground">{apiCredentials.metamask.note}</p>
                <Button onClick={() => handleSaveCredentials('metamask')} disabled={loading} size="sm" className="w-full">
                  {loading ? "Saving..." : "Save Address"}
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Agent Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5" />
              Personal Agent Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label>Strict Mode</Label>
                <p className="text-sm text-muted-foreground">
                  Enable enhanced monitoring and stricter review criteria
                </p>
              </div>
              <Switch
                checked={settings.agentStrictMode}
                onCheckedChange={(checked) => handleSettingChange('agentStrictMode', checked)}
              />
            </div>
            
            <Separator />
            
            <div className="space-y-2">
              <Label htmlFor="reviewInterval">Review Interval (hours)</Label>
              <Input
                id="reviewInterval"
                type="number"
                min="1"
                max="168"
                value={settings.agentReviewInterval}
                onChange={(e) => handleSettingChange('agentReviewInterval', parseInt(e.target.value))}
              />
              <p className="text-xs text-muted-foreground">
                How often the agent performs system reviews and generates insights
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

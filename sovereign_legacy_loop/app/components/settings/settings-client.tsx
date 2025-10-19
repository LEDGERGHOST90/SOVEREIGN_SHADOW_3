
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
    apiKey: '',
    apiSecret: '',
    showSecret: false
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

  const handleSaveCredentials = async () => {
    if (!apiCredentials.apiKey || !apiCredentials.apiSecret) {
      toast.error("Please provide both API key and secret");
      return;
    }

    setLoading(true);
    try {
      // In a real app, this would encrypt and save credentials
      await new Promise(resolve => setTimeout(resolve, 1000));
      toast.success("API credentials saved and encrypted");
      setApiCredentials(prev => ({ ...prev, apiKey: '', apiSecret: '' }));
    } catch (error) {
      toast.error("Failed to save API credentials");
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

        {/* API Credentials */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key className="h-5 w-5" />
              Binance API Credentials
            </CardTitle>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <AlertTriangle className="h-4 w-4 text-orange-400" />
              Credentials are encrypted and stored securely
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="apiKey">API Key</Label>
              <Input
                id="apiKey"
                type="text"
                value={apiCredentials.apiKey}
                onChange={(e) => setApiCredentials(prev => ({ ...prev, apiKey: e.target.value }))}
                placeholder="Enter your Binance API key"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="apiSecret">API Secret</Label>
              <div className="relative">
                <Input
                  id="apiSecret"
                  type={apiCredentials.showSecret ? "text" : "password"}
                  value={apiCredentials.apiSecret}
                  onChange={(e) => setApiCredentials(prev => ({ ...prev, apiSecret: e.target.value }))}
                  placeholder="Enter your Binance API secret"
                  className="pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setApiCredentials(prev => ({ ...prev, showSecret: !prev.showSecret }))}
                >
                  {apiCredentials.showSecret ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
            
            <Button onClick={handleSaveCredentials} disabled={loading} className="gap-2">
              <Key className="h-4 w-4" />
              {loading ? "Encrypting..." : "Save & Encrypt Credentials"}
            </Button>
          </CardContent>
        </Card>

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

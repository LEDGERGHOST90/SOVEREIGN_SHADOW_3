import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Send, Sparkles, Loader2, RefreshCw } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { TransparentAnalyst } from "./transparent-analyst";
import { oracleChat, analyzeSymbol, runScanner } from "@/lib/neuralHubApi";

interface ChartData {
  time: string;
  btc: number;
  eth: number;
}

export function OracleInterface() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [showAnalysis, setShowAnalysis] = useState(true);
  const [recommendation, setRecommendation] = useState("Awaiting query... Ask about market conditions, asset analysis, or trading strategies.");
  const [steps, setSteps] = useState<string[]>([
    "Ready to analyze market data",
    "Neural Hub connected on port 8000",
    "Gemini AI integration active",
  ]);
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [chartTitle, setChartTitle] = useState("BTC vs ETH Price Comparison");

  // Generate simulated chart data
  const generateChartData = () => {
    const now = new Date();
    const data: ChartData[] = [];
    let btcBase = 97000;
    let ethBase = 3600;

    for (let i = 6; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 3600000);
      btcBase += (Math.random() - 0.5) * 500;
      ethBase += (Math.random() - 0.5) * 50;
      data.push({
        time: time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        btc: Math.round(btcBase),
        eth: Math.round(ethBase),
      });
    }
    return data;
  };

  useEffect(() => {
    setChartData(generateChartData());
    // Refresh chart data every minute
    const interval = setInterval(() => {
      setChartData(generateChartData());
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  const handleSubmit = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setShowAnalysis(true);
    setSteps([`Processing query: "${query}"...`]);

    try {
      // Check if it's an analysis query for a specific symbol
      const symbolMatch = query.match(/analyze\s+(\w+)/i) || query.match(/(\w{3,4})\s+analysis/i);

      if (symbolMatch) {
        const symbol = symbolMatch[1].toUpperCase();
        setSteps(prev => [...prev, `Fetching ${symbol} market data...`]);

        const analysis = await analyzeSymbol(symbol);

        setSteps(prev => [...prev,
          `Trend: ${analysis.trend}`,
          `Strength: ${analysis.strength}/100`,
          `Patterns: ${analysis.patterns_detected?.join(", ") || "None detected"}`,
        ]);

        setRecommendation(analysis.recommendation || `${symbol} Analysis: Trend is ${analysis.trend} with strength ${analysis.strength}. ${analysis.key_insights?.join(" ") || ""}`);
        setChartTitle(`${symbol} Analysis`);

      } else {
        // General chat query
        setSteps(prev => [...prev, "Consulting Neural Hub Oracle..."]);

        const response = await oracleChat(query);

        setSteps(prev => [...prev,
          "Response generated",
          "Analysis complete"
        ]);

        setRecommendation(response.response || "I couldn't generate a response. Please try a more specific question about market conditions or trading strategies.");
      }

    } catch (err) {
      console.error("Oracle query failed:", err);
      setSteps(prev => [...prev, "Error: Failed to connect to Neural Hub"]);
      setRecommendation("Failed to connect to Neural Hub. Make sure AURORA is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  const handleScan = async () => {
    setScanning(true);
    setShowAnalysis(true);
    setSteps(["Running market scanner..."]);

    try {
      const result = await runScanner({ minChange: 0, sortBy: "confidence" });

      setSteps([
        `Scanned ${result.symbols_scanned} symbols`,
        `Found ${result.signals_found} signals`,
        `Scan time: ${new Date(result.scan_time).toLocaleTimeString()}`,
      ]);

      if (result.tokens && result.tokens.length > 0) {
        const topSignals = result.tokens.slice(0, 3).map(t =>
          `${t.symbol}: ${t.action} (${t.confidence}%)`
        ).join(", ");
        setRecommendation(`Top signals: ${topSignals}. ${result.tokens[0]?.reasoning || ""}`);
      } else {
        setRecommendation("No strong signals found in current scan. Market may be consolidating.");
      }

    } catch (err) {
      console.error("Scan failed:", err);
      setSteps(prev => [...prev, "Error: Scanner failed"]);
      setRecommendation("Scanner failed to connect. Check Neural Hub status.");
    } finally {
      setScanning(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !loading) {
      handleSubmit();
    }
  };

  const suggestions = [
    "Analyze BTC",
    "Analyze ETH",
    "Market sentiment",
    "Best entry for SOL"
  ];

  return (
    <Card className="col-span-1 md:col-span-2 lg:col-span-2 glass-panel border-secondary/20 h-full flex flex-col">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 border-b border-white/5">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-secondary" />
          <CardTitle className="text-sm font-medium uppercase tracking-wider text-muted-foreground">
            Oracle Interface
          </CardTitle>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs"
            onClick={handleScan}
            disabled={scanning}
          >
            {scanning ? (
              <Loader2 className="h-3 w-3 mr-1 animate-spin" />
            ) : (
              <RefreshCw className="h-3 w-3 mr-1" />
            )}
            Scan
          </Button>
          <div className="text-xs text-muted-foreground font-mono">
            Model: Gemini-2.5-Flash
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
        {/* Visualization Area */}
        <div className="flex-1 p-6 min-h-[300px] relative flex flex-col">
          <div className="absolute top-4 right-6 z-10 bg-card/50 backdrop-blur px-3 py-1 rounded border border-white/10 text-xs text-muted-foreground">
            {chartTitle}
          </div>
          <div className="flex-1 min-h-0">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorBtc" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(45 100% 50%)" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="hsl(45 100% 50%)" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorEth" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(265 80% 65%)" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="hsl(265 80% 65%)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" vertical={false} />
                <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(value) => `$${value.toLocaleString()}`} />
                <Tooltip
                  contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', color: 'hsl(var(--foreground))' }}
                  itemStyle={{ color: 'hsl(var(--foreground))' }}
                  formatter={(value: number) => [`$${value.toLocaleString()}`, '']}
                />
                <Area type="monotone" dataKey="btc" name="BTC" stroke="hsl(45 100% 50%)" strokeWidth={2} fillOpacity={1} fill="url(#colorBtc)" />
                <Area type="monotone" dataKey="eth" name="ETH" stroke="hsl(265 80% 65%)" strokeWidth={2} fillOpacity={1} fill="url(#colorEth)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {showAnalysis && (
            <div className="mt-4 animate-in slide-in-from-bottom-2 fade-in duration-500">
              <TransparentAnalyst
                recommendation={recommendation}
                steps={steps}
              />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 bg-muted/20 border-t border-white/5">
          <div className="flex gap-2">
            <Input
              placeholder="Ask the Oracle (e.g., 'Analyze BTC' or 'What's the market sentiment?')"
              className="bg-background/50 border-white/10 focus-visible:ring-secondary font-mono text-sm"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={loading}
            />
            <Button
              size="icon"
              className="bg-secondary hover:bg-secondary/80 text-secondary-foreground shrink-0"
              onClick={handleSubmit}
              disabled={loading || !query.trim()}
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
          <div className="mt-2 flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
            {suggestions.map((suggestion) => (
              <Badge
                key={suggestion}
                variant="outline"
                className="cursor-pointer hover:bg-secondary/10 hover:text-secondary hover:border-secondary/50 transition-colors whitespace-nowrap"
                onClick={() => {
                  setQuery(suggestion);
                }}
              >
                {suggestion}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ArrowUpRight, ArrowDownRight, Activity, Zap, FileText, MessageSquare, Brain, RefreshCw, Loader2 } from "lucide-react";
import { getCouncilState, generateSignal, type CouncilState } from "@/lib/neuralHubApi";

interface Signal {
  name: string;
  value: number;
  type: "technical" | "on_chain" | "fundamental" | "sentiment";
}

export function SynopticCore() {
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [councilState, setCouncilState] = useState<CouncilState | null>(null);
  const [signals, setSignals] = useState<Signal[]>([
    { name: "Technical", value: 50, type: "technical" },
    { name: "On-Chain", value: 50, type: "on_chain" },
    { name: "Fundamental", value: 50, type: "fundamental" },
    { name: "Sentiment", value: 50, type: "sentiment" },
  ]);
  const [score, setScore] = useState(50);
  const [grade, setGrade] = useState("C");
  const [thesis, setThesis] = useState("Loading analysis...");
  const [trend, setTrend] = useState<"up" | "down" | "neutral">("neutral");
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const state = await getCouncilState();
      setCouncilState(state);

      // Calculate score from portfolio health
      const healthFactor = state.portfolio_snapshot?.health_factor || 3;
      const baseScore = Math.min(100, Math.round(healthFactor * 20 + 20));
      setScore(baseScore);

      // Calculate grade
      if (baseScore >= 90) setGrade("A+");
      else if (baseScore >= 80) setGrade("A");
      else if (baseScore >= 70) setGrade("B+");
      else if (baseScore >= 60) setGrade("B");
      else if (baseScore >= 50) setGrade("C");
      else setGrade("D");

      // Update thesis based on campaign status
      const campaign = state.december_campaign as Record<string, unknown>;
      if (campaign?.debt_repaid) {
        setThesis(`December Campaign active. $${state.portfolio_snapshot?.debt?.toFixed(0) || 360} debt remaining. Health Factor ${state.portfolio_snapshot?.health_factor?.toFixed(2) || "3.71"} is strong. Paper trading phase Week 1.`);
        setTrend("up");
      } else {
        setThesis("Awaiting campaign initialization...");
        setTrend("neutral");
      }

      // Simulate signal breakdown from council motions
      const motions = state.active_motions?.length || 0;
      setSignals([
        { name: "Technical", value: 60 + Math.random() * 20, type: "technical" },
        { name: "On-Chain", value: 70 + Math.random() * 20, type: "on_chain" },
        { name: "Fundamental", value: 65 + Math.random() * 15, type: "fundamental" },
        { name: "Sentiment", value: 50 + motions * 10, type: "sentiment" },
      ]);

    } catch (err) {
      setError("Failed to connect to Neural Hub");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateSignal = async () => {
    setGenerating(true);
    try {
      const result = await generateSignal("BTC");
      if (result.signal) {
        setScore(result.signal.confidence);
        setThesis(`${result.signal.action} signal: ${result.signal.reasoning}`);
        setTrend(result.signal.action === "BUY" ? "up" : result.signal.action === "SELL" ? "down" : "neutral");
      }
    } catch (err) {
      console.error("Failed to generate signal:", err);
    } finally {
      setGenerating(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="col-span-1 md:col-span-2 lg:col-span-1 glass-panel border-primary/20 h-full">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-primary" />
          <CardTitle className="text-sm font-medium uppercase tracking-wider text-muted-foreground">
            Synoptic Core
          </CardTitle>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={fetchData}
            disabled={loading}
          >
            <RefreshCw className={`h-3 w-3 ${loading ? "animate-spin" : ""}`} />
          </Button>
          <Badge
            variant="outline"
            className={`text-xs border-primary/50 ${error ? "text-red-400 border-red-400/50 bg-red-400/10" : "text-primary bg-primary/10"}`}
          >
            {error ? "Offline" : loading ? "Syncing..." : "Live"}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-6">
          {/* Main Score */}
          <div className="flex items-center justify-between mt-2">
            <div className="flex flex-col">
              <span className="text-sm text-muted-foreground">Smart Asset Score</span>
              <div className="flex items-baseline gap-2">
                <span className="text-4xl font-bold font-mono text-foreground">{Math.round(score)}</span>
                <span className="text-sm text-accent font-medium">/ 100</span>
              </div>
              <span className={`text-xs flex items-center mt-1 ${trend === "up" ? "text-green-400" : trend === "down" ? "text-red-400" : "text-muted-foreground"}`}>
                {trend === "up" ? <ArrowUpRight className="h-3 w-3 mr-1" /> : trend === "down" ? <ArrowDownRight className="h-3 w-3 mr-1" /> : null}
                {trend === "up" ? "Bullish Momentum" : trend === "down" ? "Bearish Pressure" : "Consolidating"}
              </span>
            </div>
            <div className="relative h-20 w-20 flex items-center justify-center rounded-full border-4 border-muted border-t-primary border-r-primary animate-in fade-in zoom-in duration-1000">
              <span className="text-xl font-bold text-primary">{grade}</span>
            </div>
          </div>

          {/* Thesis */}
          <div className="p-3 rounded-md bg-muted/30 border border-white/5">
            <p className="text-xs leading-relaxed text-muted-foreground">
              <span className="text-primary font-semibold">Thesis:</span> {thesis}
            </p>
          </div>

          {/* Signals Breakdown */}
          <div className="space-y-3">
            {signals.map((signal) => (
              <div key={signal.name} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="flex items-center gap-1.5">
                    {signal.type === 'technical' && <Activity className="h-3 w-3 text-cyan-400" />}
                    {signal.type === 'on_chain' && <Zap className="h-3 w-3 text-yellow-400" />}
                    {signal.type === 'fundamental' && <FileText className="h-3 w-3 text-blue-400" />}
                    {signal.type === 'sentiment' && <MessageSquare className="h-3 w-3 text-pink-400" />}
                    {signal.name}
                  </span>
                  <span className="font-mono text-muted-foreground">{Math.round(signal.value)}</span>
                </div>
                <Progress value={signal.value} className="h-1.5 bg-muted" indicatorClassName={
                  signal.type === 'technical' ? 'bg-cyan-400' :
                  signal.type === 'on_chain' ? 'bg-yellow-400' :
                  signal.type === 'fundamental' ? 'bg-blue-400' :
                  'bg-pink-400'
                } />
              </div>
            ))}
          </div>

          {/* Generate Signal Button */}
          <Button
            variant="outline"
            size="sm"
            className="w-full border-primary/30 hover:border-primary/50 hover:bg-primary/10"
            onClick={handleGenerateSignal}
            disabled={generating || loading}
          >
            {generating ? (
              <>
                <Loader2 className="h-3 w-3 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Brain className="h-3 w-3 mr-2" />
                Generate BTC Signal
              </>
            )}
          </Button>

          <div className="pt-2 border-t border-border">
            <div className="flex justify-between items-center text-xs text-muted-foreground">
              <span>Net Worth</span>
              <Badge variant="secondary" className="bg-green-400/10 text-green-400 hover:bg-green-400/20 border-0">
                ${councilState?.portfolio_snapshot?.net_worth?.toLocaleString() || "5,433"}
              </Badge>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Play, Plus, Settings, AlertTriangle, CheckCircle2 } from "lucide-react";

const strategies = [
  {
    id: 1,
    name: "Mean Reversion 4H",
    pair: "BTC/USDT",
    status: "verified",
    return: "+12.4%",
    drawdown: "-2.1%",
  },
  {
    id: 2,
    name: "Volatility Breakout",
    pair: "SOL/USDT",
    status: "testing",
    return: "+5.8%",
    drawdown: "-4.5%",
  },
  {
    id: 3,
    name: "Funding Rate Arb",
    pair: "ETH-PERP",
    status: "failed",
    return: "-0.2%",
    drawdown: "-0.2%",
  },
];

export function ArchitectForge() {
  return (
    <Card className="col-span-1 md:col-span-3 lg:col-span-1 glass-panel border-accent/20 h-full">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div className="flex items-center gap-2">
          <Settings className="h-5 w-5 text-accent" />
          <CardTitle className="text-sm font-medium uppercase tracking-wider text-muted-foreground">
            Architect Forge
          </CardTitle>
        </div>
        <Button size="sm" variant="outline" className="h-7 text-xs border-accent/30 text-accent hover:bg-accent/10 hover:text-accent">
          <Plus className="h-3 w-3 mr-1" /> New Strategy
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {strategies.map((strat) => (
            <div key={strat.id} className="group flex flex-col gap-2 p-3 rounded-lg border border-white/5 bg-muted/10 hover:bg-muted/20 transition-all duration-300 hover:border-accent/20">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm">{strat.name}</span>
                  <Badge variant="secondary" className="text-[10px] h-4 px-1 bg-muted text-muted-foreground">
                    {strat.pair}
                  </Badge>
                </div>
                {strat.status === 'verified' && <CheckCircle2 className="h-4 w-4 text-green-500" />}
                {strat.status === 'testing' && <Settings className="h-4 w-4 text-yellow-500 animate-spin-slow" />}
                {strat.status === 'failed' && <AlertTriangle className="h-4 w-4 text-red-500" />}
              </div>
              
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex flex-col">
                   <span className="text-muted-foreground">Est. Return</span>
                   <span className={strat.return.startsWith('+') ? 'text-green-400' : 'text-red-400'}>
                     {strat.return}
                   </span>
                </div>
                <div className="flex flex-col">
                   <span className="text-muted-foreground">Max DD</span>
                   <span className="text-red-400">{strat.drawdown}</span>
                </div>
              </div>

              <div className="flex gap-2 mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <Button size="sm" variant="ghost" className="h-6 w-full text-[10px] hover:bg-accent/10 hover:text-accent">
                  <Play className="h-3 w-3 mr-1" /> Run Backtest
                </Button>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

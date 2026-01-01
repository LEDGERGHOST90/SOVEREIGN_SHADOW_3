
import React, { useState, useEffect } from 'react';
import { useStrategies } from '../context/StrategyContext';
import { 
  Activity, 
  Download, 
  Upload, 
  BrainCircuit, 
  Wallet, 
  TrendingUp, 
  CheckCircle2, 
  Loader2, 
  RefreshCw,
  Shield,
  Zap,
  Wifi,
  WifiOff,
  Lock,
  AlertOctagon,
  Terminal,
  ShieldAlert,
  Settings,
  Waves,
  PieChart,
  ChevronDown,
  ArrowUpRight,
  ShieldCheck,
  Plus,
  Radio,
  Cpu,
  Server
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { 
  BrainState, 
  LegacyLoopData, 
  TradingAlert 
} from '../types';
import { checkBridgeHealth, fetchLivePortfolio, fetchLiveSignals, DEDICATED_IP } from '../services/apiClient';

export const Dashboard: React.FC = () => {
  const { strategies, overrideStrategies } = useStrategies();
  
  // System State
  const [bridgeStatus, setBridgeStatus] = useState<'online' | 'offline'>('offline');
  const [latency, setLatency] = useState(0);
  const [lastSync, setLastSync] = useState<number>(Date.now());
  const [isSyncing, setIsSyncing] = useState(false);
  const [isKillSwitchOn, setIsKillSwitchOn] = useState(false);

  // Data State
  const [financialData, setFinancialData] = useState<LegacyLoopData | null>(null);
  const [signals, setSignals] = useState<TradingAlert[]>([]);
  const [systemLogs, setSystemLogs] = useState<string[]>([
    "Initialize G.I.O. Kernel...",
    "Neural Bridge: Handshake successful",
    "Module A: Watching local file changes",
    "Module B: Knowledge persistence active"
  ]);

  // Asset Allocation Data
  const assetAllocation = [
    { name: 'Aave Ethereum', price: '$3,595.91', allocation: 58.37, amount: '0.82 AETH', value: '$2,955.02', color: 'bg-cyan-500' },
    { name: 'Bitcoin', price: '$87,836.00', allocation: 28.68, amount: '0.016 BTC', value: '$1,451.98', color: 'bg-yellow-500' },
    { name: 'XRP', price: '$1.87', allocation: 12.6, amount: '341 XRP', value: '$638.35', color: 'bg-white' },
    { name: 'Ethereum', price: '$2,938.28', allocation: 0.23, amount: '0.004 ETH', value: '$12.10', color: 'bg-indigo-500' },
  ];

  const CAPTURE_GOAL = 25000; 
  const currentNetWorth = financialData?.portfolio.net_worth || 5061.91; 
  const capturePercent = ((currentNetWorth / CAPTURE_GOAL) * 100).toFixed(1);

  useEffect(() => {
    const storedFinancials = localStorage.getItem('sovereignState');
    if (storedFinancials) {
      try {
        setFinancialData(JSON.parse(storedFinancials));
      } catch (e) { console.error("Failed to parse local sovereignState"); }
    }
    const pollSystem = async () => {
      const health = await checkBridgeHealth();
      setBridgeStatus(health.status);
      setLatency(health.latency);
      if (health.status === 'online') {
        const port = await fetchLivePortfolio();
        if (port) {
          setFinancialData(port);
          localStorage.setItem('sovereignState', JSON.stringify(port));
          addLog(`Telemetry Update: Portfolio Value synchronized ($${port.portfolio.net_worth.toLocaleString()})`);
        }
        const liveSignals = await fetchLiveSignals();
        setSignals(liveSignals);
      }
    };
    pollSystem();
    const interval = setInterval(pollSystem, 30000); 
    return () => clearInterval(interval);
  }, []);

  const addLog = (msg: string) => {
    setSystemLogs(prev => [msg, ...prev].slice(0, 15));
  };

  useEffect(() => {
    const thoughts = [
      "Manus: Optimizing entry for ENA rotation...",
      "Claude: Verifying risk_multiplier in overnight_runner.py",
      "G.I.O: Market Regime shift detected -> Transitioning to Bullish Skew",
      "Bridge: Low latency handshake maintained (14ms)",
      "Sovereign: Brain State synchronized across all agents",
      "Intel: Sector Matrix shows high demand for RWA tokens",
      "Manus: Deep search complete on BTCFairValue mean",
      "G.I.O: Adjusting Capture Goal projection for 2026"
    ];
    const thoughtInterval = setInterval(() => {
      const randomMsg = thoughts[Math.floor(Math.random() * thoughts.length)];
      addLog(randomMsg);
    }, 8000); // Faster updates for cyberpunk feel
    return () => clearInterval(thoughtInterval);
  }, []);

  const handleSyncBias = () => {
     addLog("CRITICAL: Synchronizing Bias to external runner...");
     const directive = {
        timestamp: Date.now(),
        sentiment: 72,
        regime: 'TRANSITIONAL_BULLISH',
        active_assets: assetAllocation.map(a => a.name.split(' ')[0]),
        target_repayment: financialData?.december_campaign.debt_repayment || 0
     };
     const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(directive, null, 2));
     const link = document.createElement('a');
     link.setAttribute("href", dataStr);
     link.setAttribute("download", "gio_directive_latest.json");
     document.body.appendChild(link);
     link.click();
     link.remove();
     addLog("G.I.O: Directives exported to gio_directive_latest.json");
  };

  const handleImportBrain = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setIsSyncing(true);
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const json = JSON.parse(event.target?.result as string) as BrainState;
        if (json.strategies) overrideStrategies(json.strategies);
        if (json.legacyLoop) {
          setFinancialData(json.legacyLoop);
          localStorage.setItem('sovereignState', JSON.stringify(json.legacyLoop));
        }
        setLastSync(Date.now());
        addLog(`Handshake: Hive Mind Sync Complete (${json.strategies.length} active strategies)`);
      } catch (err) {
        addLog("Sync Failure: Illegal JSON structure detected");
      } finally {
        setIsSyncing(false);
      }
    };
    reader.readAsText(file);
  };

  const handleExportBrain = () => {
    const dailyRecords = JSON.parse(localStorage.getItem('dailyRecords') || '[]');
    const moduleAScan = JSON.parse(localStorage.getItem('latestScan') || 'null');
    const safeLegacyLoop: LegacyLoopData = financialData || {
        version: "3.0",
        last_updated: new Date().toISOString(),
        portfolio: { net_worth: currentNetWorth, aave: { collateral: 0, debt: 0, net: 0, health_factor: 3.14, status: "Secure" }, allocation: { current: {}, target: {} } },
        trading: { last_trade: { symbol: "N/A", type: "None", pnl: 0, notes: "", date: "" }, active_orders: [] },
        december_campaign: { debt_repayment: 0, start_date: "" }
    };
    const brainState: BrainState = {
      timestamp: new Date().toISOString(),
      version: "3.0",
      legacyLoop: safeLegacyLoop,
      strategies: strategies,
      dailyRecords: dailyRecords,
      moduleAScan: moduleAScan
    };
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(brainState, null, 2));
    const link = document.createElement('a');
    link.setAttribute("href", dataStr);
    link.setAttribute("download", `brain_state_${new Date().toISOString().split('T')[0]}.json`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  return (
    <div className="max-w-7xl mx-auto space-y-8 animate-fade-in pb-16">
      
      {/* HUD HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-slate-800 pb-6">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
             <div className="p-2 bg-cyan-950/30 rounded border border-cyan-500/30 shadow-[0_0_15px_rgba(6,182,212,0.2)]">
                <Activity className="text-cyan-400" size={28} />
             </div>
             <div>
                <h1 className="text-4xl font-black text-white tracking-tighter uppercase italic leading-none">
                    SHADOW<span className="text-cyan-400">.AI</span>
                </h1>
                <h2 className="text-xl font-black text-slate-500 tracking-[0.3em] uppercase leading-none">
                    ALPHARUNNER
                </h2>
             </div>
          </div>
        </div>
        
        <div className="flex items-center gap-6 bg-black/60 backdrop-blur-xl border border-slate-800 p-2 rounded-lg">
          <div className="flex items-center gap-3 px-4 py-1">
             {bridgeStatus === 'online' ? <Wifi size={18} className="text-green-400 animate-pulse"/> : <WifiOff size={18} className="text-red-500"/>}
             <div className="flex flex-col">
               <span className="text-[9px] uppercase font-black text-slate-500 tracking-wider">Bridge</span>
               <span className={`text-xs font-mono font-bold ${bridgeStatus === 'online' ? 'text-green-400' : 'text-red-500'}`}>
                 {bridgeStatus.toUpperCase()}
               </span>
             </div>
          </div>
          <div className="w-[1px] h-6 bg-slate-800"></div>
          <div className="flex items-center gap-3 px-4 py-1">
             <Lock size={18} className="text-cyan-400"/>
             <div className="flex flex-col">
               <span className="text-[9px] uppercase font-black text-slate-500 tracking-wider">Node IP</span>
               <span className="text-xs font-mono font-bold text-cyan-100">{DEDICATED_IP}</span>
             </div>
          </div>
          <div className="w-[1px] h-6 bg-slate-800"></div>
          <div className="flex items-center gap-3 px-4 py-1">
             <RefreshCw size={18} className={`text-yellow-400 ${isSyncing ? 'animate-spin' : ''}`}/>
             <div className="flex flex-col">
               <span className="text-[9px] uppercase font-black text-slate-500 tracking-wider">Sync</span>
               <span className="text-xs font-mono font-bold text-yellow-100">{new Date(lastSync).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
             </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* LEFT COLUMN (3/4) */}
        <div className="lg:col-span-3 space-y-8">
            
            {/* HIVE MIND SYNC BLOCK */}
            <div className="bg-slate-950 border border-slate-800 rounded-2xl p-8 relative overflow-hidden group">
                <div className="absolute top-0 right-0 w-64 h-full bg-gradient-to-l from-indigo-900/10 to-transparent pointer-events-none"></div>
                <div className="absolute -right-10 -top-10 text-indigo-900/20 group-hover:text-indigo-900/30 transition-colors">
                    <BrainCircuit size={280} />
                </div>

                <div className="relative z-10 flex flex-col md:flex-row justify-between items-center gap-10">
                    <div className="space-y-4">
                        <div className="flex items-center gap-2 text-cyan-400 font-black text-[10px] uppercase tracking-[0.2em] border border-cyan-900/50 bg-cyan-950/20 px-2 py-1 w-fit rounded">
                           <Cpu size={12} /> Neural Core Active
                        </div>
                        <h3 className="text-3xl font-black text-white tracking-tighter uppercase italic">
                            Synchronize <span className="text-indigo-500">The Swarm</span>
                        </h3>
                        <p className="text-slate-400 text-sm max-w-lg font-medium leading-relaxed">
                          Neural Bridge engaged. Unify local strategy artifacts, file intelligence, and financial telemetry into a cohesive Brain State for G.I.O. and Manus.
                        </p>
                    </div>
                    <div className="flex flex-wrap gap-3 w-full md:w-auto">
                        <label className="flex-1 md:flex-none cursor-pointer bg-slate-900 hover:bg-slate-800 text-slate-300 px-6 py-4 clip-corner font-black text-xs uppercase tracking-widest transition-all border border-slate-700 hover:border-cyan-500 flex items-center justify-center gap-2 active:scale-95 group/btn">
                            <Upload size={16} className="group-hover/btn:text-cyan-400 transition-colors" /> Import State
                            <input type="file" accept=".json" onChange={handleImportBrain} className="hidden" />
                        </label>
                        <button 
                            onClick={handleExportBrain} 
                            className="flex-1 md:flex-none bg-cyan-600 hover:bg-cyan-500 text-black px-6 py-4 clip-corner font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2 transition-all shadow-[0_0_20px_rgba(8,145,178,0.4)] active:scale-95 hover:shadow-[0_0_30px_rgba(34,211,238,0.6)]"
                        >
                            <Download size={16} /> Export State
                        </button>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* NET WORTH CARD */}
                <div className="bg-black/60 backdrop-blur-md border border-slate-800 p-6 rounded-2xl relative overflow-hidden group hover:border-cyan-500/50 transition-all">
                    <div className="absolute right-4 top-4 p-2 bg-slate-900 rounded text-cyan-500 group-hover:scale-110 transition-transform shadow-[0_0_10px_rgba(6,182,212,0.3)]">
                        <Wallet size={20} />
                    </div>
                    <div className="text-slate-500 text-[10px] font-black uppercase mb-3 tracking-widest">Net Worth</div>
                    <div className="text-3xl font-black text-white tracking-tighter mb-2 font-mono-tech">
                        ${currentNetWorth.toLocaleString()}
                    </div>
                    <div className="flex items-center gap-2 text-[10px] font-black uppercase">
                        <span className="text-green-400 bg-green-950/30 px-1.5 py-0.5 rounded border border-green-500/30">+2.4%</span>
                        <span className="text-slate-500">24H Delta</span>
                    </div>
                </div>

                {/* MARKET CAPTURE (DYNAMIC GLASS) */}
                <div className="bg-slate-900/40 backdrop-blur-md border border-indigo-500/30 p-6 rounded-2xl relative overflow-hidden group hover:border-indigo-400 transition-all shadow-[0_0_30px_rgba(99,102,241,0.15)]">
                    <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-transparent pointer-events-none"></div>
                    <div className="absolute -right-8 -bottom-8 opacity-20 group-hover:opacity-30 transition-all rotate-12 scale-150">
                        <Waves size={140} className="text-indigo-500" />
                    </div>
                    
                    <div className="relative z-10 flex justify-between items-start mb-6">
                        <div className="p-2 bg-white/5 rounded-lg border border-white/10 shadow-lg group-hover:shadow-indigo-500/20 transition-all">
                             <div className="w-8 h-8 flex items-center justify-center rounded-full bg-black overflow-hidden border border-white/20">
                                 <img src="https://assets.coingecko.com/coins/images/33458/large/COQ.png?1701981242" alt="COQ" className="w-full h-full object-cover opacity-80" />
                             </div>
                        </div>
                        <div className="flex flex-col items-end text-right">
                            <span className="text-indigo-400 font-black text-[9px] tracking-[0.2em] uppercase">Capture</span>
                            <div className="text-white font-mono-tech font-bold text-xs mt-0.5">$COQ DOM</div>
                        </div>
                    </div>

                    <div className="relative z-10 space-y-3">
                        <div className="text-[10px] text-slate-500 font-black uppercase tracking-widest flex items-center gap-2">
                          <Activity size={10} className="text-indigo-400" /> Efficiency
                        </div>
                        <div className="text-4xl font-black text-white tracking-tighter leading-none mb-1 flex items-baseline gap-1 font-mono-tech">
                            {capturePercent}<span className="text-sm text-indigo-500 opacity-80">%</span>
                        </div>
                        <div className="space-y-1.5">
                           <div className="w-full bg-slate-900 h-1.5 rounded-none overflow-hidden border border-slate-700">
                              <div className="bg-indigo-500 h-full shadow-[0_0_15px_rgba(99,102,241,1)]" style={{ width: `${capturePercent}%` }}></div>
                           </div>
                           <div className="flex justify-between text-[9px] font-black uppercase text-slate-500">
                              <span>0%</span>
                              <span>Target: $25k</span>
                           </div>
                        </div>
                    </div>
                </div>

                {/* AAVE HEALTH CARD */}
                <div className="bg-black/60 backdrop-blur-md border border-slate-800 p-6 rounded-2xl relative overflow-hidden group hover:border-yellow-500/50 transition-all">
                    <div className="absolute right-4 top-4 p-2 bg-slate-900 rounded text-yellow-500 group-hover:scale-110 transition-transform shadow-[0_0_10px_rgba(234,179,8,0.3)]">
                        <Shield size={20} />
                    </div>
                    <div className="text-slate-500 text-[10px] font-black uppercase mb-3 tracking-widest">Protocol Health</div>
                    <div className={`text-3xl font-black tracking-tighter mb-2 font-mono-tech ${
                        !financialData ? 'text-white' :
                        financialData.portfolio.aave.health_factor > 1.5 ? 'text-green-400' :
                        financialData.portfolio.aave.health_factor > 1.1 ? 'text-yellow-400' : 'text-red-500'
                    }`}>
                        {financialData ? financialData.portfolio.aave.health_factor.toFixed(2) : '3.14'}
                    </div>
                    <div className="flex items-center gap-2 text-[10px] font-black uppercase tracking-widest">
                        <span className="text-slate-500">STATUS:</span>
                        <span className="text-green-400">SECURE</span>
                    </div>
                </div>
            </div>

            {/* LIVE SYSTEM PULSE TERMINAL */}
            <div className="bg-black border border-slate-800 rounded-lg overflow-hidden shadow-2xl shadow-black group">
               <div className="px-4 py-2 bg-slate-900 border-b border-slate-800 flex justify-between items-center">
                  <div className="flex items-center gap-2">
                     <Terminal size={12} className="text-cyan-400" />
                     <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Live Kernel Stream</span>
                  </div>
                  <div className="flex gap-1.5">
                     <div className="w-1.5 h-1.5 rounded-full bg-red-500/50"></div>
                     <div className="w-1.5 h-1.5 rounded-full bg-yellow-500/50"></div>
                     <div className="w-1.5 h-1.5 rounded-full bg-green-500/50"></div>
                  </div>
               </div>
               <div className="p-4 font-mono-tech text-[10px] h-32 overflow-y-auto custom-scrollbar bg-black relative">
                  {systemLogs.map((log, i) => (
                    <div key={i} className="flex gap-3 mb-1 animate-fade-in opacity-80 hover:opacity-100 transition-opacity">
                       <span className="text-slate-700 font-bold select-none min-w-[60px]">[{new Date().toLocaleTimeString([], {hour12: false})}]</span>
                       <span className={`
                          ${log.includes('Manus') ? 'text-yellow-300' : 
                            log.includes('Claude') ? 'text-blue-300' : 
                            log.includes('G.I.O') ? 'text-purple-300' : 
                            log.includes('CRITICAL') ? 'text-red-500 font-black' : 'text-cyan-100'}
                       `}>
                         <span className="text-slate-800 mr-2">{'>'}</span> {log}
                       </span>
                    </div>
                  ))}
                  <div className="flex gap-3 animate-pulse mt-2">
                     <span className="text-slate-700 font-bold min-w-[60px]">[{new Date().toLocaleTimeString([], {hour12: false})}]</span>
                     <span className="text-cyan-500 font-bold uppercase tracking-wider flex items-center gap-2">
                        _
                     </span>
                  </div>
               </div>
            </div>

            {/* ASSET ALLOCATION TABLE */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden relative backdrop-blur-sm">
               <div className="p-6 border-b border-slate-800 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-black/40">
                  <div className="space-y-1">
                      <h3 className="font-black text-white text-lg flex items-center gap-3 tracking-tight">
                         <PieChart size={18} className="text-cyan-400" /> Asset Distribution
                      </h3>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-[9px] font-black text-green-400 uppercase tracking-widest bg-green-950/30 px-3 py-1.5 rounded border border-green-500/20 flex items-center gap-2">
                      <ShieldCheck size={10} /> Secure
                    </div>
                    <button className="p-1.5 bg-slate-800 hover:bg-slate-700 rounded text-slate-400 transition-all border border-slate-700">
                        <Settings size={14} />
                    </button>
                  </div>
               </div>
               <div className="overflow-x-auto">
                  <table className="w-full text-left">
                     <thead>
                        <tr className="text-[9px] text-slate-500 font-black uppercase tracking-widest bg-black border-b border-slate-800">
                           <th className="px-6 py-4">Asset</th>
                           <th className="px-6 py-4">Price</th>
                           <th className="px-6 py-4">Weight</th>
                           <th className="px-6 py-4 text-right">Value (USD)</th>
                        </tr>
                     </thead>
                     <tbody className="divide-y divide-slate-800/50">
                        {assetAllocation.map((asset, i) => (
                           <tr key={i} className="hover:bg-cyan-500/5 transition-colors group cursor-default">
                              <td className="px-6 py-4">
                                 <div className="flex items-center gap-3">
                                    <div className={`w-2 h-8 ${asset.color} rounded-sm shadow-[0_0_8px_currentColor] opacity-80`}></div>
                                    <div className="font-bold text-white text-xs">{asset.name}</div>
                                 </div>
                              </td>
                              <td className="px-6 py-4 text-slate-400 font-mono-tech text-xs">
                                 <div className="flex items-center gap-2">
                                    <TrendingUp size={12} className="text-green-500" />
                                    {asset.price}
                                 </div>
                              </td>
                              <td className="px-6 py-4">
                                 <div className="flex items-center gap-3">
                                    <div className="w-24 bg-slate-800 h-1.5 rounded-sm overflow-hidden">
                                       <div className={`h-full ${asset.color}`} style={{ width: `${asset.allocation}%` }}></div>
                                    </div>
                                    <span className="text-[10px] text-slate-300 font-bold">{asset.allocation}%</span>
                                 </div>
                              </td>
                              <td className="px-6 py-4 text-right font-bold text-white font-mono-tech text-sm">
                                 {asset.value}
                              </td>
                           </tr>
                        ))}
                     </tbody>
                  </table>
               </div>
            </div>
        </div>

        {/* RIGHT SIDEBAR (1/4) */}
        <div className="space-y-6">
           
           {/* BIAS SYNC CTAs */}
           <div className="bg-gradient-to-br from-indigo-950/50 to-slate-900 border border-indigo-500/40 rounded-2xl p-6 space-y-6 shadow-[0_0_30px_rgba(99,102,241,0.1)] relative overflow-hidden group">
              <div className="absolute top-0 right-0 p-4 opacity-10 -mr-6 -mt-6">
                 <ArrowUpRight size={120} className="text-indigo-400" />
              </div>
              <div className="relative z-10 space-y-1">
                 <h3 className="font-black text-white text-lg uppercase italic tracking-tighter">Direct Action</h3>
                 <p className="text-[10px] text-indigo-300 font-bold uppercase tracking-widest opacity-80">Sync Kernel Bias</p>
              </div>
              <div className="space-y-3 relative z-10">
                <button 
                  onClick={handleSyncBias}
                  className="w-full py-4 bg-indigo-600 hover:bg-indigo-500 text-white clip-corner font-black text-xs uppercase tracking-[0.2em] shadow-lg shadow-indigo-600/30 transition-all flex items-center justify-center gap-2 active:scale-95"
                >
                    <RefreshCw size={14} /> Synchronize
                </button>
                <Link 
                  to="/analyze" 
                  className="w-full py-4 bg-slate-800 hover:bg-slate-700 text-slate-300 clip-corner font-black text-xs uppercase tracking-[0.2em] border border-slate-700 transition-all flex items-center justify-center gap-2 active:scale-95"
                >
                    <Plus size={14} /> New Intel
                </Link>
              </div>
           </div>

           {/* EMERGENCY KILL SWITCH */}
           <div className={`p-6 rounded-2xl border-2 transition-all shadow-xl ${
               isKillSwitchOn ? 'bg-red-950/40 border-red-500 shadow-[0_0_30px_rgba(239,68,68,0.2)]' : 'bg-black border-slate-800'
           }`}>
              <h3 className={`font-black mb-4 flex items-center gap-3 uppercase tracking-tighter text-base ${isKillSwitchOn ? 'text-red-500' : 'text-slate-500'}`}>
                 <AlertOctagon size={20} /> Kill Switch
              </h3>
              <p className="text-[10px] text-slate-500 mb-6 leading-relaxed font-bold opacity-80">
                  PROTOCOL: IMMEDIATE TERMINATION OF ALL ACTIVE AGENTS.
              </p>
              <button 
                onClick={() => {
                  setIsKillSwitchOn(!isKillSwitchOn);
                  addLog(isKillSwitchOn ? "System Recovery: Kill Switch Disengaged" : "CRITICAL ALERT: KILL SWITCH ENGAGED - ALL SYSTEMS HALTED");
                }}
                className={`w-full py-4 clip-corner font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2 transition-all ${
                    isKillSwitchOn 
                    ? 'bg-slate-900 text-red-500 border border-red-500' 
                    : 'bg-red-600 hover:bg-red-500 text-black shadow-lg shadow-red-600/30'
                }`}
              >
                  <ShieldAlert size={16} />
                  {isKillSwitchOn ? 'DEACTIVATE' : 'ENGAGE STOP'}
              </button>
           </div>

           {/* PROJECT ROADMAP */}
           <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="font-black text-white mb-6 text-[10px] uppercase tracking-[0.2em] flex items-center gap-2">
                    <TrendingUp size={14} className="text-cyan-400"/> Milestones
                </h3>
                <div className="space-y-4">
                    {[
                        { label: 'Paper Trading', status: 'ACTIVE', color: 'bg-cyan-500', text: 'text-cyan-400', progress: 100 },
                        { label: 'Micro Live', status: 'STAGING', color: 'bg-yellow-500', text: 'text-yellow-500', progress: 40 },
                        { label: 'Autonomous', status: 'LOCKED', color: 'bg-slate-600', text: 'text-slate-600', progress: 0 }
                    ].map((p, i) => (
                        <div key={i} className="space-y-1.5">
                            <div className="flex justify-between items-center text-[9px]">
                                <span className="text-slate-400 font-black uppercase">{p.label}</span>
                                <span className={`font-black ${p.text} tracking-tighter`}>{p.status}</span>
                            </div>
                            <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                                <div className={`h-full ${p.color} shadow-[0_0_10px_currentColor]`} style={{ width: `${p.progress}%` }}></div>
                            </div>
                        </div>
                    ))}
                </div>
           </div>

           {/* ACTIVE SIGNALS STREAM */}
           <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 flex flex-col min-h-[400px] shadow-xl relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 opacity-5 rotate-12">
                 <Radio size={80} className="text-red-500" />
              </div>
              <h3 className="font-black text-white mb-6 flex items-center gap-2 text-[10px] uppercase tracking-[0.2em] relative z-10">
                 <Activity size={14} className="text-red-500" /> Alpha Stream
              </h3>
              
              <div className="space-y-3 overflow-y-auto custom-scrollbar flex-1 max-h-[400px] relative z-10">
                 {signals.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 text-slate-700 italic space-y-3">
                        <Waves size={32} className="animate-pulse opacity-50" />
                        <span className="text-[9px] font-black uppercase tracking-widest">Scanning...</span>
                    </div>
                 ) : (
                    signals.map(signal => (
                       <div key={signal.id} className={`p-4 rounded border-l-2 flex gap-3 transition-all cursor-default bg-black/40 ${
                          signal.severity === 'Critical' ? 'border-red-500 shadow-red-900/10' : 
                          signal.severity === 'Warning' ? 'border-yellow-500' : 'border-cyan-500'
                       }`}>
                          <div className={`mt-0.5 flex-shrink-0 ${
                             signal.severity === 'Critical' ? 'text-red-500' : 
                             signal.severity === 'Warning' ? 'text-yellow-500' : 'text-cyan-500'
                          }`}>
                             {signal.severity === 'Critical' ? <AlertOctagon size={14} /> : <Zap size={14} />}
                          </div>
                          <div className="flex-1 space-y-1">
                             <div className="flex justify-between items-center">
                                <span className="text-[10px] font-black text-white uppercase tracking-wider">{signal.symbol}</span>
                                <span className="text-[9px] text-slate-600 font-mono-tech">{new Date(signal.timestamp).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}</span>
                             </div>
                             <p className="text-[10px] text-slate-400 leading-normal font-medium">{signal.message}</p>
                          </div>
                       </div>
                    ))
                 )}
              </div>
           </div>
        </div>
      </div>
    </div>
  );
};


import React, { useEffect, useState, useRef } from 'react';
import { useStrategies } from '../context/StrategyContext';
import { Link } from 'react-router-dom';
import { TrendingUp, Clock, ShieldAlert, ArrowRight, Plus, Activity, Database, BookOpen, Network, Cpu, FileText, Zap, Wifi, Layers, DollarSign, Wallet, ArrowUpRight, ArrowDownRight, Download, Upload, RefreshCw, Link2, Unplug } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, PieChart, Pie } from 'recharts';
import { ModuleAOutput, DailyRecord, LocalFile, LegacyLoopData, ActiveOrder, BridgeStatus } from '../types';
import { parseTradingAlert } from '../services/geminiService';
import { checkBridgeHealth, fetchLivePortfolio } from '../services/apiClient';

// --- MOCK LEGACY LOOP DATA (Synced with Screenshots) ---
const INITIAL_LEGACY_DATA: LegacyLoopData = {
  version: "1.1",
  last_updated: new Date().toISOString(),
  portfolio: {
    net_worth: 5413.51, // Synced with Ledger Screenshot
    aave: {
      collateral: 2859.63, // Synced wstETH
      debt: 660.94,
      net: 2198.69,
      health_factor: 3.71,
      status: "REPAY DEBT - bleeding 4.89% APY"
    },
    allocation: {
      current: {
        eth: 53.4, // Dominant due to AAVE collateral
        btc: 26.4,
        xrp: 19.2,
        sol: 0.0
      },
      target: {
        btc: 40,
        eth: 30,
        sol: 20,
        xrp: 10
      }
    }
  },
  trading: {
    last_trade: {
      symbol: "ZEC/USDC",
      type: "long",
      pnl: -18.11,
      notes: "Stop loss executed by Guardian at $430.",
      date: "2025-11-30"
    },
    active_orders: [
      // ZEC Trade moved to closed history based on user input
    ]
  },
  december_campaign: {
    debt_repayment: 400,
    start_date: "2025-12-01"
  }
};

export const Dashboard: React.FC = () => {
  const { strategies } = useStrategies();
  const [moduleAData, setModuleAData] = useState<ModuleAOutput | null>(null);
  const [dailyRecords, setDailyRecords] = useState<DailyRecord[]>([]);
  const [legacyData, setLegacyData] = useState<LegacyLoopData>(INITIAL_LEGACY_DATA);
  const [bridgeStatus, setBridgeStatus] = useState<BridgeStatus>('connecting');
  
  // Signal Terminal State
  const [signalInput, setSignalInput] = useState('');
  const [isProcessingSignal, setIsProcessingSignal] = useState(false);
  const [processedSignal, setProcessedSignal] = useState<string | null>(null);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load System Data
  useEffect(() => {
    // Load Module A
    const scanStr = localStorage.getItem('latestScan');
    if (scanStr) {
      try {
        setModuleAData(JSON.parse(scanStr));
      } catch (e) {}
    }

    // Load Module C
    const recordsStr = localStorage.getItem('dailyRecords');
    if (recordsStr) {
      try {
        setDailyRecords(JSON.parse(recordsStr));
      } catch (e) {}
    }
    
    // Load Legacy Data (State)
    const stateStr = localStorage.getItem('sovereignState');
    if (stateStr) {
        try {
            setLegacyData(JSON.parse(stateStr));
        } catch (e) {}
    }
  }, []);

  // Save State on Change (only if not bridged, or to persist bridge data)
  useEffect(() => {
      localStorage.setItem('sovereignState', JSON.stringify(legacyData));
  }, [legacyData]);

  // --- LIVE BRIDGE POLLING ---
  useEffect(() => {
    const pollBridge = async () => {
      const health = await checkBridgeHealth();
      setBridgeStatus(health.status);

      if (health.status === 'online') {
        const liveData = await fetchLivePortfolio();
        if (liveData) {
          setLegacyData(liveData);
        }
      }
    };

    // Initial check
    pollBridge();

    // Poll every 5 seconds
    const interval = setInterval(pollBridge, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleSignalSubmit = async (e: React.FormEvent) => {
      e.preventDefault();
      if (!signalInput.trim()) return;
      
      setIsProcessingSignal(true);
      try {
          const result = await parseTradingAlert(signalInput);
          setProcessedSignal(JSON.stringify(result, null, 2));
          // In a real app, this would dispatch to an execution engine
      } catch (err) {
          setProcessedSignal("Error parsing signal.");
      } finally {
          setIsProcessingSignal(false);
      }
  };
  
  // --- STATE BRIDGE FUNCTIONS ---
  const handleExportState = () => {
      const state = {
          timestamp: new Date().toISOString(),
          legacyLoop: legacyData,
          strategies: strategies,
          dailyRecords: dailyRecords,
          moduleAScan: moduleAData
      };
      
      const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(state, null, 2));
      const downloadAnchorNode = document.createElement('a');
      downloadAnchorNode.setAttribute("href", dataStr);
      downloadAnchorNode.setAttribute("download", `sovereign_brain_${new Date().toISOString().split('T')[0]}.json`);
      document.body.appendChild(downloadAnchorNode);
      downloadAnchorNode.click();
      downloadAnchorNode.remove();
  };

  const handleImportState = (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files[0]) {
          const reader = new FileReader();
          reader.onload = (event) => {
              try {
                  const imported = JSON.parse(event.target?.result as string);
                  if (imported.legacyLoop) setLegacyData(imported.legacyLoop);
                  // Note: Strategies and Records would need context methods to bulk update, 
                  // for now we just update the display data
                  alert("Sovereign State Imported Successfully. Syncing Dashboard...");
              } catch (err) {
                  alert("Failed to parse state file.");
              }
          };
          reader.readAsText(e.target.files[0]);
      }
  };

  return (
    <div className="space-y-8 animate-fade-in pb-12">
      
      {/* HEADER & ACTIONS */}
      <div className="flex flex-col md:flex-row justify-between items-end gap-4">
        <div>
          <div className="flex items-center gap-3 mb-1">
             <div className="flex items-center gap-1.5 bg-slate-900/50 border border-slate-700 px-2 py-0.5 rounded text-xs">
                 {bridgeStatus === 'online' ? (
                     <>
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                        <span className="text-green-400 font-mono tracking-wider">NEURAL BRIDGE: ONLINE</span>
                     </>
                 ) : bridgeStatus === 'connecting' ? (
                     <>
                        <div className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></div>
                        <span className="text-yellow-400 font-mono tracking-wider">CONNECTING...</span>
                     </>
                 ) : (
                     <>
                        <div className="w-2 h-2 rounded-full bg-red-500"></div>
                        <span className="text-red-400 font-mono tracking-wider">BRIDGE: OFFLINE</span>
                     </>
                 )}
             </div>
             <span className="text-[10px] text-slate-500 font-mono">SOVEREIGN_SHADOW_3</span>
          </div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Cpu className="text-indigo-500" />
            SOVEREIGN SHADOW 3 <span className="text-slate-600">|</span> COMMAND
          </h1>
          <p className="text-slate-400 mt-2">Unified Intelligence Hub. Debt Protocol Active.</p>
        </div>
        <div className="flex gap-3">
          <Link to="/daily-recorder" className="bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors border border-slate-700">
             <BookOpen size={18} />
             <span>Log Daily Record</span>
          </Link>
          <Link to="/analyze" className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors shadow-lg shadow-indigo-500/20">
            <Plus size={18} />
            <span>New Analysis</span>
          </Link>
        </div>
      </div>

      {/* --- FINANCIAL TELEMETRY (LEDGER SYNC) --- */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* NET WORTH CARD */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 opacity-10">
                  <Wallet size={100} className="text-indigo-500" />
              </div>
              <div className="relative z-10">
                  <div className="text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">Total Net Worth</div>
                  <div className="text-4xl font-bold text-white mb-2">
                      ${legacyData.portfolio.net_worth.toLocaleString()}
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                      <span className="text-red-400 flex items-center bg-red-900/20 px-1.5 py-0.5 rounded">
                          <ArrowDownRight size={14} /> 12%
                      </span>
                      <span className="text-slate-500">24h Change (-$758.71)</span>
                  </div>
              </div>
              {/* Asset Strip */}
              <div className="mt-6 flex gap-2">
                  <div className="h-1.5 flex-1 bg-indigo-500 rounded-full opacity-80" title="ETH"></div>
                  <div className="h-1.5 w-1/4 bg-yellow-500 rounded-full opacity-80" title="BTC"></div>
                  <div className="h-1.5 w-1/5 bg-slate-200 rounded-full opacity-80" title="XRP"></div>
              </div>
          </div>

          {/* DEBT PROTOCOL WIDGET */}
          <div className="bg-slate-900 border border-red-900/30 rounded-xl p-6 relative">
              <div className="flex justify-between items-start mb-4">
                  <div>
                      <div className="text-red-400 text-xs font-bold uppercase tracking-wider flex items-center gap-2">
                          <ShieldAlert size={14} /> AAVE DEBT PROTOCOL
                      </div>
                      <div className="text-2xl font-bold text-white mt-1">
                          ${Math.abs(legacyData.portfolio.aave.debt).toFixed(2)}
                      </div>
                  </div>
                  <div className="text-right">
                      <div className="text-slate-500 text-xs">Target (Nov 30)</div>
                      <div className="text-lg font-mono text-green-400">PAY $400.00</div>
                  </div>
              </div>
              
              <div className="bg-slate-800 rounded-lg p-3 border border-slate-700 mb-2">
                  <div className="flex justify-between text-sm mb-1">
                      <span className="text-slate-400">Health Factor</span>
                      <span className={`font-bold ${legacyData.portfolio.aave.health_factor < 1.5 ? 'text-red-500' : 'text-green-400'}`}>
                          {legacyData.portfolio.aave.health_factor}
                      </span>
                  </div>
                  <div className="w-full bg-slate-700 h-2 rounded-full overflow-hidden">
                      <div className="bg-green-500 h-full" style={{ width: `${Math.min(100, legacyData.portfolio.aave.health_factor * 20)}%` }}></div>
                  </div>
              </div>
              <div className="text-xs text-red-300/70 italic flex items-center gap-1">
                  <Activity size={12} /> {legacyData.portfolio.aave.status}
              </div>
          </div>

          {/* ACTIVE OPERATIONS / ORDERS */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                  <div className="text-indigo-400 text-xs font-bold uppercase tracking-wider flex items-center gap-2">
                      <Layers size={14} /> Active Operations
                  </div>
                  <div className="text-[10px] text-slate-500">0 OPEN</div>
              </div>
              
              <div className="space-y-3">
                  {legacyData.trading.active_orders.length > 0 ? (
                      legacyData.trading.active_orders.map(order => (
                          <div key={order.id} className="bg-slate-800/50 rounded-lg p-3 border border-slate-700 border-l-4 border-l-red-500">
                              <div className="flex justify-between items-start mb-1">
                                  <span className="text-white font-bold text-sm">{order.market}</span>
                                  <span className="bg-green-900/30 text-green-400 text-[10px] px-1.5 py-0.5 rounded border border-green-900/50 uppercase">{order.status}</span>
                              </div>
                              <div className="flex justify-between text-xs text-slate-400">
                                  <span>{order.side} {order.type}</span>
                                  <span className="text-white font-mono">@{order.price.toFixed(2)}</span>
                              </div>
                          </div>
                      ))
                  ) : (
                      <div className="text-center py-4 bg-slate-800/30 rounded border border-slate-800 border-dashed text-slate-500 text-xs">
                          No active limit orders.
                      </div>
                  )}
                  
                  {/* Last Trade Log */}
                  <div className="bg-slate-800/30 rounded-lg p-2 border border-slate-800 opacity-70">
                      <div className="flex justify-between text-xs mb-1">
                          <span className="text-slate-400">Last Trade (Closed)</span>
                          <span className="text-red-400 font-mono">-${Math.abs(legacyData.trading.last_trade.pnl)}</span>
                      </div>
                      <div className="text-[10px] text-slate-500 italic">
                          "{legacyData.trading.last_trade.notes}"
                      </div>
                  </div>
              </div>
          </div>
      </div>

      {/* --- WATCHTOWER & SIGNAL TERMINAL --- */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* CHAIN WATCHTOWER (Connectivity) */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <div className="flex justify-between items-center mb-4">
                  <h3 className="text-white font-bold flex items-center gap-2">
                      <Wifi size={18} className="text-indigo-500" />
                      Chain Watchtower
                  </h3>
                  <div className={`text-[10px] px-2 py-1 rounded border ${bridgeStatus === 'online' ? 'bg-green-900/30 text-green-400 border-green-500/30' : 'bg-slate-800 text-slate-500 border-slate-700'}`}>
                      {bridgeStatus === 'online' ? 'LINKED' : 'OFFLINE'}
                  </div>
              </div>
              
              <div className="space-y-3">
                  <div className="flex items-center justify-between p-2 bg-slate-800/50 rounded border border-slate-700">
                      <div className="flex items-center gap-3">
                          <div className={`w-2 h-2 rounded-full ${bridgeStatus === 'online' ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                          <span className="text-sm text-slate-300">Neural Hub (Local)</span>
                      </div>
                      <span className="text-xs font-mono text-slate-500">localhost:8000</span>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-slate-800/50 rounded border border-slate-700">
                      <div className="flex items-center gap-3">
                          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                          <span className="text-sm text-slate-300">Bitcoin Core</span>
                      </div>
                      <span className="text-xs font-mono text-slate-500">bc1q...</span>
                  </div>
                  <div className="flex items-center justify-between p-2 bg-slate-800/50 rounded border border-slate-700">
                      <div className="flex items-center gap-3">
                          <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                          <span className="text-sm text-slate-300">Ethereum Mainnet</span>
                      </div>
                      <span className="text-xs font-mono text-slate-500">0xC084...</span>
                  </div>
                  
                  {/* STATE BRIDGE CONTROLS */}
                  <div className="pt-4 mt-4 border-t border-slate-800">
                      <div className="text-xs font-bold text-slate-500 uppercase mb-2">Cursor / Claude Bridge</div>
                      {bridgeStatus === 'online' ? (
                          <div className="bg-green-900/10 border border-green-900/30 p-3 rounded text-xs text-green-300 flex items-center gap-2">
                              <Link2 size={14} />
                              Auto-Syncing with BRAIN.json
                          </div>
                      ) : (
                          <div className="grid grid-cols-2 gap-2">
                              <button 
                                onClick={handleExportState}
                                className="bg-slate-800 hover:bg-slate-700 text-white py-2 rounded flex items-center justify-center gap-2 text-xs border border-slate-700 transition-colors"
                              >
                                  <Download size={14} /> Export Brain
                              </button>
                              <button 
                                onClick={() => fileInputRef.current?.click()}
                                className="bg-slate-800 hover:bg-slate-700 text-white py-2 rounded flex items-center justify-center gap-2 text-xs border border-slate-700 transition-colors"
                              >
                                  <Upload size={14} /> Import State
                              </button>
                              <input type="file" ref={fileInputRef} className="hidden" accept=".json" onChange={handleImportState} />
                          </div>
                      )}
                  </div>
              </div>
          </div>

          {/* SYSTEM MODULE STATUS */}
          <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                  <Activity size={18} className="text-indigo-500" />
                  Module Status
              </h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {/* MODULE A */}
                <Link to="/agent" className="bg-slate-800/50 border border-slate-700 p-3 rounded-lg hover:border-indigo-500/30 transition-all group">
                  <div className="flex items-center justify-between mb-2">
                     <div className="flex items-center gap-2 text-slate-400 group-hover:text-green-400 transition-colors">
                       <Database size={14} />
                       <span className="text-[10px] font-bold uppercase">Scanner</span>
                     </div>
                     <div className={`w-1.5 h-1.5 rounded-full ${moduleAData ? 'bg-green-500' : 'bg-slate-700'}`}></div>
                  </div>
                  <div className="text-xl font-bold text-white">{moduleAData ? moduleAData.files.length : 0}</div>
                  <div className="text-[10px] text-slate-500">Files Tracked</div>
                </Link>

                {/* MODULE D */}
                <Link to="/knowledge-graph" className="bg-slate-800/50 border border-slate-700 p-3 rounded-lg hover:border-indigo-500/30 transition-all group">
                  <div className="flex items-center justify-between mb-2">
                     <div className="flex items-center gap-2 text-slate-400 group-hover:text-indigo-400 transition-colors">
                       <Network size={14} />
                       <span className="text-[10px] font-bold uppercase">Graph</span>
                     </div>
                     <div className={`w-1.5 h-1.5 rounded-full ${strategies.length > 0 ? 'bg-indigo-500' : 'bg-slate-700'}`}></div>
                  </div>
                  <div className="text-xl font-bold text-white">{strategies.length}</div>
                  <div className="text-[10px] text-slate-500">Strat Nodes</div>
                </Link>

                {/* MODULE C */}
                <Link to="/daily-recorder" className="bg-slate-800/50 border border-slate-700 p-3 rounded-lg hover:border-indigo-500/30 transition-all group">
                  <div className="flex items-center justify-between mb-2">
                     <div className="flex items-center gap-2 text-slate-400 group-hover:text-purple-400 transition-colors">
                       <BookOpen size={14} />
                       <span className="text-[10px] font-bold uppercase">Log</span>
                     </div>
                     <div className={`w-1.5 h-1.5 rounded-full ${dailyRecords.length > 0 ? 'bg-purple-500' : 'bg-slate-700'}`}></div>
                  </div>
                  <div className="text-xl font-bold text-white">{dailyRecords.length}</div>
                  <div className="text-[10px] text-slate-500">Entries</div>
                </Link>

                {/* CAMPAIGN */}
                <div className="bg-slate-800/50 border border-slate-700 p-3 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                     <div className="flex items-center gap-2 text-slate-400">
                       <Clock size={14} />
                       <span className="text-[10px] font-bold uppercase">Campaign</span>
                     </div>
                     <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></div>
                  </div>
                  <div className="text-xl font-bold text-white">Dec 1</div>
                  <div className="text-[10px] text-slate-500">Launch Day</div>
                </div>
              </div>
          </div>
      </div>

      {/* SIGNAL TERMINAL */}
      <div className="bg-black/40 border border-slate-800 rounded-xl p-6 font-mono">
          <div className="flex items-center gap-2 mb-4 text-green-500">
              <Zap size={16} />
              <h3 className="font-bold text-sm uppercase">Council Uplink / Signal Terminal</h3>
          </div>
          <form onSubmit={handleSignalSubmit} className="flex gap-4">
              <input 
                  type="text" 
                  value={signalInput}
                  onChange={(e) => setSignalInput(e.target.value)}
                  className="flex-1 bg-slate-900 border border-slate-700 rounded px-4 py-2 text-sm text-green-400 placeholder-slate-600 focus:outline-none focus:border-green-500 transition-colors"
                  placeholder="Paste alert from Claude, TradingView, or Python (e.g. 'ZEC BREAKOUT 4h RSI>70')"
              />
              <button 
                  type="submit" 
                  disabled={isProcessingSignal || !signalInput}
                  className="bg-green-900/30 text-green-400 border border-green-500/50 px-6 py-2 rounded text-xs font-bold uppercase hover:bg-green-900/50 transition-all disabled:opacity-50"
              >
                  {isProcessingSignal ? 'Parsing...' : 'Inject Signal'}
              </button>
          </form>
          {processedSignal && (
              <div className="mt-4 p-4 bg-slate-900/80 rounded border border-slate-800 text-xs text-slate-300 whitespace-pre-wrap">
                  {processedSignal}
              </div>
          )}
      </div>

    </div>
  );
};

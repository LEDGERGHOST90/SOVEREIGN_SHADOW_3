
import React, { useState } from 'react';
import { 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  ShieldAlert, 
  Zap, 
  BarChart3, 
  Layers, 
  Target, 
  PieChart, 
  AlertTriangle,
  CheckCircle2,
  ChevronRight,
  Eye,
  ArrowUpRight,
  Fish,
  Globe,
  Radio,
  FileText,
  Percent,
  Flame,
  Scale,
  Waves,
  Cpu,
  Crosshair
} from 'lucide-react';

export const AlphaDigest: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'overview' | 'predictions' | 'risk'>('overview');

  const criticalNumbers = [
    { label: 'BTC from ATH', value: '-30%', signal: 'Correction', sub: '$126K → $87K', color: 'text-red-400' },
    { label: 'MVRV-Z Ratio', value: '2.31', signal: 'Intermediate', sub: 'Peak = 4.0+', color: 'text-yellow-400' },
    { label: 'Fear & Greed', value: '20/100', signal: 'Extreme Fear', sub: '14 Day Streak', color: 'text-orange-500' },
    { label: 'Q4 2025 Perf', value: '-22.5%', signal: 'Bearish', sub: 'Worst since 2018', color: 'text-red-500' },
    { label: 'ETF Cumulative', value: '$56.88B', signal: 'Structural', sub: 'Net Support', color: 'text-indigo-400' },
    { label: 'Hash Rate', value: '-4%', signal: 'BULLISH', sub: 'Contrarian', color: 'text-green-400' }
  ];

  const sectorOpportunities = [
    { name: 'RWA Tokenization', rating: 'VERY HIGH', catalyst: '$36B+ market, 10-20x growth projected', bg: 'bg-green-900/20', border: 'border-green-500/30', icon: <Layers className="text-green-400" /> },
    { name: 'Stablecoins', rating: 'VERY HIGH', catalyst: 'GENIUS Act, $1.5B VC, "internet\'s dollar"', bg: 'bg-green-900/20', border: 'border-green-500/30', icon: <Waves className="text-green-400" /> },
    { name: 'AI x Crypto', rating: 'HIGH', catalyst: '40% of crypto VC to AI projects', bg: 'bg-blue-900/20', border: 'border-blue-500/30', icon: <Zap className="text-blue-400" /> },
    { name: 'BTCFi', rating: 'HIGH', catalyst: 'ETH stake ETFs drive BTC yield demand', bg: 'bg-blue-900/20', border: 'border-blue-500/30', icon: <TrendingUp className="text-blue-400" /> },
    { name: 'DeFi Revival', rating: 'MEDIUM-HIGH', catalyst: 'Rate cuts, yield seeking, $117B TVL', bg: 'bg-yellow-900/10', border: 'border-yellow-500/20', icon: <Activity className="text-yellow-400" /> },
    { name: 'Privacy/ZK', rating: 'MEDIUM-HIGH', catalyst: 'Institutional requirement, Zcash +860% Q4', bg: 'bg-yellow-900/10', border: 'border-yellow-500/20', icon: <ShieldAlert className="text-yellow-400" /> }
  ];

  const whaleAccumulation = [
    { token: 'AVNT (Avantis)', sector: 'DEX (Base)', cap: '$89M', accumulation: '+11M tokens' },
    { token: 'PROVE (Succinct)', sector: 'ZK Privacy', cap: '$75.6M', accumulation: '+5.34%' },
    { token: 'PLUME (Plume)', sector: 'RWA L2', cap: '$60M', accumulation: '+7B tokens' }
  ];

  const hayesRotation = [
    { token: 'ENA', thesis: 'Yield product growth, stablecoin momentum', scale: '95%' },
    { token: 'PENDLE', thesis: 'Yield trading focus, DeFi rotation play', scale: '88%' },
    { token: 'LDO', thesis: 'Staking infrastructure, ETH rotation', scale: '72%' },
    { token: 'ETHFI', thesis: 'Liquid restaking ecosystem lead', scale: '65%' }
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-20 animate-fade-in font-sans">
      {/* HUD HEADER */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-end gap-6 bg-slate-900/60 p-8 rounded-3xl border border-slate-800 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-600/5 blur-[120px] rounded-full -mr-20 -mt-20"></div>
        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-4">
            <span className="px-3 py-1 bg-indigo-500/10 text-indigo-400 text-[10px] font-black border border-indigo-500/30 rounded-full uppercase tracking-[0.2em]">Alpha Digest Dec 2025</span>
            <div className="flex items-center gap-1.5 px-3 py-1 bg-red-500/10 text-red-400 text-[10px] font-black border border-red-500/30 rounded-full uppercase">
              <Flame size={12} /> Live Intelligence
            </div>
          </div>
          <h1 className="text-5xl font-black text-white tracking-tighter leading-none">
            MARKET <span className="text-indigo-500">INTELLIGENCE</span>
          </h1>
          <div className="flex flex-wrap gap-6 mt-6">
            <div className="flex flex-col">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Market Regime</span>
              <span className="text-white font-bold flex items-center gap-2">
                Transitional <span className="text-[10px] bg-yellow-500/20 text-yellow-500 px-1.5 rounded">BULLISH SKEW</span>
              </span>
            </div>
            <div className="w-[1px] h-8 bg-slate-800 hidden md:block"></div>
            <div className="flex flex-col">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">CoinGlass Peak Status</span>
              <span className="text-green-400 font-bold">0/30 TRIGGERS</span>
            </div>
            <div className="w-[1px] h-8 bg-slate-800 hidden md:block"></div>
            <div className="flex flex-col">
              <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">BTC Bear Floor</span>
              <span className="text-white font-mono font-bold">$56,000</span>
            </div>
          </div>
        </div>

        <div className="relative z-10 w-full lg:w-auto">
          <div className="bg-slate-950/70 p-6 rounded-2xl border border-slate-800 flex items-center gap-8 shadow-inner shadow-black/40">
            <div className="flex flex-col items-center">
              <div className="text-[10px] text-slate-500 font-black uppercase mb-2">Cycle Progress</div>
              <div className="relative w-16 h-16">
                <svg className="w-full h-full" viewBox="0 0 36 36">
                  <path className="text-slate-800 stroke-current" strokeWidth="3" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                  <path className="text-indigo-500 stroke-current" strokeWidth="3" strokeDasharray="43.46, 100" strokeLinecap="round" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center text-[10px] font-black text-white">43%</div>
              </div>
            </div>
            <div className="flex flex-col justify-center">
               <div className="text-xs font-bold text-slate-400">BTC Fair Value</div>
               <div className="text-xl font-black text-white">$81,300</div>
               <div className="text-[10px] text-indigo-400 font-bold uppercase mt-1 flex items-center gap-1">
                 <CheckCircle2 size={10} /> Status: Accumulation
               </div>
            </div>
          </div>
        </div>
      </div>

      {/* METRICS GRID */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {criticalNumbers.map((m, i) => (
          <div key={i} className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl hover:border-indigo-500/50 transition-all group cursor-default shadow-lg">
            <div className="text-[10px] text-slate-500 font-black uppercase tracking-widest mb-3 group-hover:text-indigo-400 transition-colors">{m.label}</div>
            <div className="text-3xl font-black text-white tracking-tighter mb-1">{m.value}</div>
            <div className={`text-[10px] font-bold uppercase mb-1 ${m.color}`}>{m.signal}</div>
            <div className="text-[10px] text-slate-600 font-mono italic">{m.sub}</div>
          </div>
        ))}
      </div>

      {/* NAVIGATION TABS */}
      <div className="flex border-b border-slate-800 gap-8">
         <button onClick={() => setActiveTab('overview')} className={`pb-4 text-sm font-black uppercase tracking-widest transition-all relative ${activeTab === 'overview' ? 'text-white' : 'text-slate-500 hover:text-slate-300'}`}>
            Intelligence Feed {activeTab === 'overview' && <div className="absolute bottom-0 left-0 right-0 h-1 bg-indigo-500 rounded-full"></div>}
         </button>
         <button onClick={() => setActiveTab('predictions')} className={`pb-4 text-sm font-black uppercase tracking-widest transition-all relative ${activeTab === 'predictions' ? 'text-white' : 'text-slate-500 hover:text-slate-300'}`}>
            2026 Consensus {activeTab === 'predictions' && <div className="absolute bottom-0 left-0 right-0 h-1 bg-indigo-500 rounded-full"></div>}
         </button>
         <button onClick={() => setActiveTab('risk')} className={`pb-4 text-sm font-black uppercase tracking-widest transition-all relative ${activeTab === 'risk' ? 'text-white' : 'text-slate-500 hover:text-slate-300'}`}>
            Risk Matrix {activeTab === 'risk' && <div className="absolute bottom-0 left-0 right-0 h-1 bg-indigo-500 rounded-full"></div>}
         </button>
      </div>

      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-fade-in">
          {/* MAIN COLUMN */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* ACTIONABLE ALERTS - TOP PRIORITY */}
            <div className="bg-indigo-600/10 border border-indigo-500/30 p-6 rounded-3xl relative overflow-hidden">
               <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
                  <Zap size={140} />
               </div>
               <h3 className="text-white font-black text-lg mb-4 flex items-center gap-2">
                  <Zap size={20} className="text-yellow-400" /> Actionable Directives
               </h3>
               <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800">
                    <div className="flex items-center gap-2 text-green-400 font-black text-[10px] uppercase mb-2">
                      <TrendingUp size={14} /> Buy Signal Alpha
                    </div>
                    <ul className="space-y-2 text-xs text-slate-300">
                      <li className="flex items-start gap-2">• <b>Hash Rate Decline:</b> historically +72% 180-day returns.</li>
                      <li className="flex items-start gap-2">• <b>Extreme Fear:</b> 14+ day duration = accumulation zone.</li>
                      <li className="flex items-start gap-2">• <b>Zero Peak:</b> 0/30 peak indicators triggered.</li>
                    </ul>
                  </div>
                  <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800">
                    <div className="flex items-center gap-2 text-yellow-400 font-black text-[10px] uppercase mb-2">
                      <Eye size={14} /> Watch Protocol
                    </div>
                    <ul className="space-y-2 text-xs text-slate-300">
                      <li className="flex items-start gap-2">• <b>LTH Distribution:</b> Monitor for 95.82% completion.</li>
                      <li className="flex items-start gap-2">• <b>DeFi Rotation:</b> Accumulate ENA, PENDLE, LDO.</li>
                      <li className="flex items-start gap-2">• <b>RWA Surge:</b> Monitor PLUME whale accumulation.</li>
                    </ul>
                  </div>
               </div>
            </div>

            {/* SECTOR MATRIX */}
            <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
              <div className="p-6 bg-slate-800/50 border-b border-slate-800 flex justify-between items-center">
                 <h3 className="text-white font-black text-sm uppercase tracking-widest flex items-center gap-2">
                    <Target size={18} className="text-indigo-500" /> 2026 Opportunity Matrix
                 </h3>
                 <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest">Sentiment Bias</span>
              </div>
              <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                 {sectorOpportunities.map((s, i) => (
                   <div key={i} className={`${s.bg} ${s.border} border p-5 rounded-2xl flex items-start gap-4 hover:brightness-110 transition-all cursor-default`}>
                      <div className="p-2.5 bg-slate-950/50 rounded-xl shadow-inner">
                        {s.icon}
                      </div>
                      <div className="flex-1">
                        <div className="flex justify-between items-center mb-1">
                          <h4 className="text-sm font-bold text-white">{s.name}</h4>
                          <span className={`text-[9px] font-black px-1.5 py-0.5 rounded border ${s.border} bg-slate-950/50`}>{s.rating}</span>
                        </div>
                        <p className="text-[11px] text-slate-400 leading-tight">{s.catalyst}</p>
                      </div>
                   </div>
                 ))}
              </div>
            </div>

            {/* ARTHUR HAYES ROTATION Tracker */}
            <div className="bg-gradient-to-br from-indigo-600/10 via-slate-900 to-purple-600/10 border border-indigo-500/30 rounded-3xl p-8 relative overflow-hidden group">
               <Fish size={120} className="absolute right-[-20px] bottom-[-20px] text-white/5 group-hover:rotate-12 transition-transform duration-1000" />
               <div className="flex items-start justify-between mb-8">
                  <div>
                    <h3 className="text-2xl font-black text-white tracking-tighter mb-1 italic">Arthur Hayes DeFi Rotation</h3>
                    <p className="text-xs text-indigo-300/80 uppercase font-bold tracking-widest">Reallocation: $5.53M ETH → DeFi Yield</p>
                  </div>
                  <div className="p-3 bg-indigo-500 text-white rounded-full shadow-lg shadow-indigo-500/20">
                    <TrendingUp size={24} />
                  </div>
               </div>
               <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {hayesRotation.map((h, i) => (
                    <div key={i} className="bg-slate-950/80 p-5 rounded-2xl border border-white/5 hover:border-white/20 transition-all relative">
                      <div className="flex justify-between items-start mb-2">
                        <div className="text-lg font-black text-white tracking-tight">{h.token}</div>
                        <div className="text-[10px] font-bold text-green-400">{h.scale} Confidence</div>
                      </div>
                      <p className="text-[11px] text-slate-500 uppercase font-bold leading-tight mb-4">{h.thesis}</p>
                      <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-indigo-500 h-full" style={{ width: h.scale }}></div>
                      </div>
                    </div>
                  ))}
               </div>
            </div>
          </div>

          {/* SIDEBAR */}
          <div className="space-y-6">
            
            {/* WHALE ACCUMULATION ALERTS */}
            <div className="bg-slate-900 border border-slate-800 rounded-3xl overflow-hidden shadow-2xl">
              <div className="p-5 bg-slate-800/50 border-b border-slate-800">
                <h3 className="text-white font-black text-xs uppercase tracking-widest flex items-center gap-2">
                  <Fish size={14} className="text-indigo-400" /> Whale Alerts (Dec 2025)
                </h3>
              </div>
              <div className="p-5 space-y-4">
                 {whaleAccumulation.map((w, i) => (
                   <div key={i} className="flex justify-between items-center p-3 bg-slate-800/30 rounded-xl border border-slate-700 hover:border-indigo-500/30 transition-all">
                      <div>
                        <div className="text-xs font-black text-white">{w.token}</div>
                        <div className="text-[9px] text-slate-500 uppercase">{w.sector}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs font-bold text-green-400">{w.accumulation}</div>
                        <div className="text-[9px] text-slate-600 font-mono">CAP: {w.cap}</div>
                      </div>
                   </div>
                 ))}
                 <div className="pt-2 text-center">
                    <div className="text-[9px] text-slate-500 italic mb-2">Corporate Accumulation Surge</div>
                    <div className="flex items-center justify-center gap-1.5">
                       <span className="text-xs font-black text-white">MicroStrategy:</span>
                       <span className="text-xs font-black text-green-400">29.4k BTC</span>
                    </div>
                 </div>
              </div>
            </div>

            {/* ON-CHAIN MAGNET LEVELS */}
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-xl">
               <h3 className="text-white font-black text-xs uppercase tracking-widest mb-6 flex items-center gap-2">
                 <Crosshair size={14} className="text-red-400" /> On-Chain Magnet Levels
               </h3>
               <div className="space-y-5">
                  {[
                    { label: 'Bear Market Floor', val: '$56,000', sub: 'Realized Price', color: 'bg-red-500' },
                    { label: 'Fair Value Mean', val: '$81,300', sub: 'Glassnode Protocol', color: 'bg-indigo-500' },
                    { label: 'Golden Ratio Target', val: '$135,522', sub: '64% Progress', color: 'bg-yellow-500' },
                    { label: 'Terminal Price', val: '$187,702', sub: 'Max Extension', color: 'bg-green-500' }
                  ].map((l, i) => (
                    <div key={i} className="relative pl-4 border-l-2 border-slate-800 group hover:border-slate-500 transition-all">
                       <div className="absolute left-[-2px] top-0 bottom-0 w-0.5 group-hover:h-full transition-all" />
                       <div className="text-[9px] text-slate-500 font-bold uppercase tracking-tighter">{l.label}</div>
                       <div className="text-sm font-black text-white font-mono">{l.val}</div>
                       <div className="text-[9px] text-slate-600 italic">{l.sub}</div>
                    </div>
                  ))}
               </div>
            </div>

            {/* ETF FLOW MONITOR */}
            <div className="bg-indigo-600/90 rounded-3xl p-6 text-white shadow-2xl shadow-indigo-600/20 relative overflow-hidden group">
               <Waves className="absolute right-[-10px] bottom-[-10px] text-white/10 group-hover:scale-110 transition-transform" size={100} />
               <div className="flex items-start justify-between mb-4 relative z-10">
                  <Waves size={24} />
                  <span className="text-[10px] font-black bg-white/20 px-2 py-0.5 rounded backdrop-blur-sm">IBIT: $62.2B</span>
               </div>
               <h4 className="text-lg font-black tracking-tight mb-2 relative z-10">ETF Flow Pulse</h4>
               <p className="text-[11px] text-indigo-100 leading-relaxed mb-4 relative z-10">
                  $56.88B cumulative net. Dec outflows (-$825M) are tax-loss harvest indicators, not structural breakdowns.
               </p>
               <div className="flex items-center gap-2 text-[10px] font-black uppercase relative z-10">
                  <span className="text-green-300">Bullish Structural</span>
                  <div className="w-1 h-1 rounded-full bg-white/40"></div>
                  <span className="text-white/60">Dec Neutral</span>
               </div>
            </div>

            {/* SYSTEMIC INJECTION CALLOUT */}
            <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 text-center group cursor-pointer hover:border-indigo-500/50 transition-all">
               <Cpu size={32} className="mx-auto text-indigo-500 mb-3 group-hover:scale-110 transition-transform" />
               <h4 className="text-white font-black text-sm uppercase mb-1">Inject to G.I.O.</h4>
               <p className="text-[10px] text-slate-500 leading-relaxed">
                  Auto-calibrate <code>risk_multiplier</code> variables based on Alpha Sentiment.
               </p>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'predictions' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 animate-fade-in">
           {/* BITWISE */}
           <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 space-y-6 hover:border-blue-500/30 transition-all">
              <div className="flex items-center gap-3">
                 <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center font-black text-white shadow-lg shadow-blue-600/20">B</div>
                 <h3 className="text-xl font-black text-white tracking-tighter uppercase">Bitwise (2026)</h3>
              </div>
              <ul className="space-y-4">
                 {[
                   'BTC breaks 4-year cycle, new ATH in 2026',
                   'BTC less volatile than Nvidia stocks',
                   'ETFs buy >100% of new BTC/ETH/SOL supply',
                   'Crypto equities outperform tech peers',
                   'Polymarket hits new ATH open interest',
                   'Half of Ivy League endowments invest in crypto'
                 ].map((p, i) => (
                    <li key={i} className="text-xs text-slate-400 flex items-start gap-3">
                       <span className="text-indigo-500 font-black">0{i+1}</span>
                       <span>{p}</span>
                    </li>
                 ))}
              </ul>
           </div>

           {/* TIGER RESEARCH */}
           <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 space-y-6 hover:border-orange-500/30 transition-all">
              <div className="flex items-center gap-3">
                 <div className="w-10 h-10 bg-orange-600 rounded-xl flex items-center justify-center font-black text-white shadow-lg shadow-orange-600/20">T</div>
                 <h3 className="text-xl font-black text-white tracking-tighter uppercase">Tiger Research</h3>
              </div>
              <ul className="space-y-4">
                 {[
                   'Institutional capital stays in BTC/ETH',
                   'Revenue > Narrative (post-TGE realism)',
                   'Buybacks/burns replace utility tokenomics',
                   'M&A acceleration across crypto protocols',
                   'Robotics data economy emerges on-chain',
                   'Fintech apps overtake centralized exchanges'
                 ].map((p, i) => (
                    <li key={i} className="text-xs text-slate-400 flex items-start gap-3">
                       <span className="text-orange-500 font-black">0{i+1}</span>
                       <span>{p}</span>
                    </li>
                 ))}
              </ul>
           </div>

           {/* GRAYSCALE */}
           <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 space-y-6 hover:border-slate-500/30 transition-all">
              <div className="flex items-center gap-3">
                 <div className="w-10 h-10 bg-slate-100 rounded-xl flex items-center justify-center font-black text-slate-900 text-lg">G</div>
                 <h3 className="text-xl font-black text-white tracking-tighter uppercase">Grayscale Themes</h3>
              </div>
              <ul className="space-y-4">
                 {[
                   'Dollar debasement risk (BTC, ETH, ZEC)',
                   'Asset tokenization inflection point',
                   'Privacy tech becomes institutional infra',
                   'AI decentralization via blockchain logic',
                   'Staking by default in institutional funds',
                   'Next-gen infra focuses on sustainable revenue'
                 ].map((p, i) => (
                    <li key={i} className="text-xs text-slate-400 flex items-start gap-3">
                       <span className="text-slate-300 font-black">0{i+1}</span>
                       <span>{p}</span>
                    </li>
                 ))}
              </ul>
           </div>
        </div>
      )}

      {activeTab === 'risk' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 animate-fade-in">
           {/* MARKET STRUCTURE RISKS */}
           <div className="bg-red-950/10 border border-red-500/20 rounded-3xl p-8 space-y-8">
              <h3 className="text-2xl font-black text-red-400 tracking-tighter uppercase flex items-center gap-3">
                 <ShieldAlert size={24} /> Market Structure Risks
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                 {[
                   { label: 'October Crash Precedent', val: '$19B Liquidation', desc: 'Market still sensitive to leverage wipes' },
                   { label: 'Liquidity Depth', val: '90% Collapse Risk', desc: 'Top-of-book depth can vanish during stress' },
                   { label: 'Leverage Limits', val: '20-50x Available', desc: 'Retail still heavily over-indexed' },
                   { label: 'Venue Concentration', val: 'Single Venue Risk', desc: 'Vulnerability in unified margin accounts' }
                 ].map((r, i) => (
                    <div key={i} className="bg-slate-950/80 p-5 rounded-2xl border border-red-900/20">
                       <div className="text-[10px] text-red-400 font-black uppercase mb-1">{r.label}</div>
                       <div className="text-white font-bold text-sm mb-2">{r.val}</div>
                       <div className="text-[10px] text-slate-500 leading-tight">{r.desc}</div>
                    </div>
                 ))}
              </div>
           </div>

           {/* MACRO/SPECIFIC RISKS */}
           <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 space-y-8">
              <h3 className="text-2xl font-black text-white tracking-tighter uppercase flex items-center gap-3">
                 <Globe size={24} className="text-indigo-500" /> Macro/Specific Risks
              </h3>
              <div className="space-y-6">
                 <div className="p-6 bg-slate-950/80 rounded-2xl border border-slate-800 flex justify-between items-center group hover:border-slate-600 transition-all">
                    <div>
                       <div className="text-xs font-bold text-white mb-1">Recession Probability</div>
                       <div className="text-[10px] text-slate-500 font-bold uppercase">Consensus: 35%</div>
                    </div>
                    <div className="text-3xl font-black text-red-400">35%</div>
                 </div>
                 <div className="space-y-4">
                    <div className="flex items-start gap-4 p-5 bg-indigo-500/5 rounded-2xl border border-indigo-500/10 hover:bg-indigo-500/10 transition-all">
                       <AlertTriangle size={18} className="text-yellow-500 flex-shrink-0 mt-0.5" />
                       <div>
                          <div className="text-xs font-bold text-white mb-1">USDe De-peg Risk</div>
                          <p className="text-[10px] text-slate-400 leading-relaxed">
                             Ethena USDe traded at $0.65 on Binance recently. Avoid USDe as primary system collateral until stability returns.
                          </p>
                       </div>
                    </div>
                    <div className="flex items-start gap-4 p-5 bg-red-500/5 rounded-2xl border border-red-500/10">
                       <Percent size={18} className="text-red-400 flex-shrink-0 mt-0.5" />
                       <div>
                          <div className="text-xs font-bold text-white mb-1">Fed Hawkish Pivot</div>
                          <p className="text-[10px] text-slate-400 leading-relaxed">
                             Strong USD headwinds and hawkish pivot probability remains the primary macro "Black Swan" for risk-on assets.
                          </p>
                       </div>
                    </div>
                 </div>
              </div>
           </div>
        </div>
      )}

      {/* FOOTER CALL TO ACTION */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-8 flex flex-col md:flex-row justify-between items-center gap-6 shadow-2xl relative overflow-hidden">
         <div className="absolute inset-0 bg-gradient-to-r from-indigo-600/5 to-transparent pointer-events-none" />
         <div className="flex items-center gap-5 relative z-10">
            <div className="w-14 h-14 bg-indigo-600 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-indigo-600/30">
               <Cpu size={32} />
            </div>
            <div>
               <h4 className="text-white font-black text-xl tracking-tight">Systemic Bias Sync</h4>
               <p className="text-xs text-slate-500 font-medium">Auto-calibrate <code>overnight_runner.py</code> thresholds based on Alpha Sentiment.</p>
            </div>
         </div>
         <div className="flex items-center gap-4 relative z-10 w-full md:w-auto">
            <button className="flex-1 md:flex-none px-8 py-3 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-black text-[10px] uppercase tracking-widest border border-slate-700 transition-all">
               View Raw Report
            </button>
            <button className="flex-1 md:flex-none px-8 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-black text-[10px] uppercase tracking-widest shadow-xl shadow-indigo-600/20 transition-all active:scale-95 flex items-center justify-center gap-2">
               Synchronize Bias <ArrowUpRight size={14} />
            </button>
         </div>
      </div>

    </div>
  );
};

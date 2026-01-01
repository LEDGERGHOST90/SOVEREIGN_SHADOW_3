
import React, { useState } from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { useStrategies } from '../context/StrategyContext';
import { ChatBot } from './ChatBot';
import { refineStrategy, generateFullStrategyPackage } from '../services/geminiService';
import { ArrowLeft, ExternalLink, AlertTriangle, CheckCircle2, Ban, BarChart3, Edit3, Save, X, Sparkles, Loader2, Target, ShieldCheck, Crosshair, Brain, Layers, BrainCircuit, Code, FileJson, FileCode, Check, Award, FileText, Copy, Terminal } from 'lucide-react';
import { Link } from 'react-router-dom';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Mock function to generate "backtest" data based on sentiment
const generateMockBacktestData = (sentiment: number) => {
  const data = [];
  let equity = 10000;
  const volatility = 0.02; // 2% daily volatility
  const trend = (sentiment - 50) / 1000; // Bias based on sentiment

  for (let i = 0; i < 30; i++) {
    const change = (Math.random() - 0.5) * volatility + trend;
    equity = equity * (1 + change);
    data.push({
      day: `Day ${i + 1}`,
      equity: Math.round(equity)
    });
  }
  return data;
};

export const StrategyDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { strategies, updateStrategy } = useStrategies();
  const [isRefining, setIsRefining] = useState(false);
  const [refinePrompt, setRefinePrompt] = useState('');
  const [isSubmittingRefinement, setIsSubmittingRefinement] = useState(false);
  
  // Forge State
  const [activeTab, setActiveTab] = useState<'details' | 'forge'>('details');
  const [artifactTab, setArtifactTab] = useState<'python' | 'pine' | 'config' | 'narrative'>('python');
  const [isForging, setIsForging] = useState(false);
  const [copiedArtifact, setCopiedArtifact] = useState<string | null>(null);

  const strategy = strategies.find(s => s.id === id);

  if (!strategy) {
    return <Navigate to="/" replace />;
  }

  const { analysis } = strategy;
  const mockData = generateMockBacktestData(analysis.overallSentiment);
  const isProfitable = mockData[mockData.length - 1].equity > 10000;
  const isCertified = strategy.pipelineStatus === 'certified';

  const handleRefine = async () => {
    if (!refinePrompt.trim()) return;
    setIsSubmittingRefinement(true);
    try {
      const newAnalysis = await refineStrategy(strategy.analysis, refinePrompt, strategy.model);
      updateStrategy(strategy.id, { analysis: newAnalysis });
      setIsRefining(false);
      setRefinePrompt('');
    } catch (error: any) {
      alert(`Failed to refine: ${error.message}`);
    } finally {
      setIsSubmittingRefinement(false);
    }
  };

  const handleCertify = () => {
      updateStrategy(strategy.id, { pipelineStatus: 'certified' });
  };

  // If artifacts failed to generate automatically, allow manual trigger
  const handleManualForge = async () => {
      setIsForging(true);
      try {
          const artifacts = await generateFullStrategyPackage(analysis, strategy.model);
          updateStrategy(strategy.id, { artifacts });
      } catch (e: any) {
          alert("Forge failed: " + e.message);
      } finally {
          setIsForging(false);
      }
  };

  const getCategoryColor = (cat: string) => {
    switch(cat) {
      case 'Sniper': return 'bg-red-900/20 text-red-400 border-red-500/30';
      case 'Vault': return 'bg-green-900/20 text-green-400 border-green-500/30';
      case 'Ladder': return 'bg-blue-900/20 text-blue-400 border-blue-500/30';
      case 'MENACE': return 'bg-purple-900/20 text-purple-400 border-purple-500/30';
      default: return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  const getCategoryIcon = (cat: string) => {
    switch(cat) {
      case 'Sniper': return <Crosshair size={14} />;
      case 'Vault': return <ShieldCheck size={14} />;
      case 'Ladder': return <Layers size={14} />;
      case 'MENACE': return <Brain size={14} />;
      default: return <Target size={14} />;
    }
  };

  const copyToClipboard = (text: string, type: string) => {
      navigator.clipboard.writeText(text);
      setCopiedArtifact(type);
      setTimeout(() => setCopiedArtifact(null), 2000);
  };

  const getActiveArtifactContent = () => {
      if (!strategy.artifacts) return '';
      switch(artifactTab) {
          case 'python': return strategy.artifacts.pythonCode;
          case 'pine': return strategy.artifacts.pineScript;
          case 'config': return strategy.artifacts.configJson;
          case 'narrative': return strategy.artifacts.narrative;
          default: return '';
      }
  };

  return (
    <div className="max-w-7xl mx-auto pb-12 animate-fade-in">
      {/* HEADER */}
      <div className="mb-8 border-b border-slate-800/60 pb-6">
        <Link to="/" className="inline-flex items-center text-xs font-bold uppercase tracking-widest text-slate-500 hover:text-cyan-400 mb-4 transition-colors">
          <ArrowLeft size={14} className="mr-2" /> Return to Terminal
        </Link>
        
        <div className="flex flex-col md:flex-row justify-between items-start gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
                 <h1 className="text-3xl md:text-4xl font-black text-white tracking-tighter uppercase italic">{analysis.name}</h1>
                 {/* PIPELINE STATUS */}
                 {isCertified ? (
                     <div className="flex items-center gap-1.5 px-3 py-1 bg-green-900/20 text-green-400 border border-green-500/50 rounded text-[10px] font-black uppercase tracking-widest shadow-[0_0_15px_rgba(34,197,94,0.2)]">
                         <Award size={12} /> Certified
                     </div>
                 ) : (
                     <div className="flex items-center gap-1.5 px-3 py-1 bg-slate-900 text-slate-500 border border-slate-800 rounded text-[10px] font-black uppercase tracking-widest">
                         <Loader2 size={12} className="animate-spin" /> Draft Status
                     </div>
                 )}
            </div>
            
            <div className="flex flex-wrap items-center gap-3 text-sm">
               {/* SOVEREIGN CATEGORY */}
               <div className={`flex items-center gap-2 px-3 py-1 rounded border text-[10px] font-bold uppercase tracking-wide ${getCategoryColor(analysis.sovereignCategory)}`}>
                  {getCategoryIcon(analysis.sovereignCategory)}
                  <span>{analysis.sovereignCategory} Protocol</span>
               </div>
               
               {/* ASSET TIER */}
               {analysis.assetTier && (
                 <div className="bg-black text-slate-400 px-3 py-1 rounded border border-slate-800 text-[10px] font-mono">
                    {analysis.assetTier.replace('_', ' ')}
                 </div>
               )}

               <span className="text-slate-700">|</span>
               <span className="text-slate-500 font-mono text-xs">{new Date(strategy.createdAt).toLocaleDateString()}</span>
            </div>
          </div>

          <div className="flex gap-2">
              {!isCertified && (
                <button 
                    onClick={handleCertify}
                    className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-black px-4 py-2 clip-corner transition-colors font-black text-xs uppercase tracking-widest"
                >
                    <CheckCircle2 size={14} /> Certify
                </button>
              )}
              <button 
                onClick={() => setIsRefining(true)}
                className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-500 text-black px-4 py-2 clip-corner transition-colors font-black text-xs uppercase tracking-widest shadow-[0_0_15px_rgba(8,145,178,0.3)]"
              >
                <Sparkles size={14} /> Refine Logic
              </button>
          </div>
        </div>
      </div>

      {/* TABS */}
      <div className="flex items-center gap-1 bg-black p-1 rounded-lg w-fit border border-slate-800 mb-8">
          <button 
             onClick={() => setActiveTab('details')}
             className={`px-5 py-2 rounded text-xs font-bold uppercase tracking-wider transition-all flex items-center gap-2 ${activeTab === 'details' ? 'bg-slate-900 text-white shadow border border-slate-700' : 'text-slate-500 hover:text-white'}`}
          >
             <Target size={14} /> Strategy Blueprint
          </button>
          <button 
             onClick={() => setActiveTab('forge')}
             className={`px-5 py-2 rounded text-xs font-bold uppercase tracking-wider transition-all flex items-center gap-2 ${activeTab === 'forge' ? 'bg-indigo-900/20 text-indigo-400 border border-indigo-500/30 shadow' : 'text-slate-500 hover:text-white'}`}
          >
             <Code size={14} /> Code Forge
          </button>
      </div>

      {/* REFINEMENT MODAL */}
      {isRefining && (
        <div className="fixed inset-0 z-50 bg-black/90 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-black border border-slate-700 rounded-xl w-full max-w-lg p-6 shadow-2xl relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-cyan-500 to-purple-500"></div>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-black text-white flex items-center gap-2 uppercase italic tracking-tighter">
                <Edit3 size={20} className="text-cyan-400" /> Refine Logic
              </h3>
              <button onClick={() => setIsRefining(false)} className="text-slate-500 hover:text-white">
                <X size={24} />
              </button>
            </div>
            <textarea 
              className="w-full bg-slate-900 border border-slate-800 rounded-lg p-4 text-white h-32 focus:border-cyan-500 outline-none mb-6 font-mono text-xs leading-relaxed"
              placeholder="e.g., 'Make the stop loss tighter' or 'Add volume confirmation'"
              value={refinePrompt}
              onChange={(e) => setRefinePrompt(e.target.value)}
            />
            <div className="flex justify-end gap-3">
              <button onClick={() => setIsRefining(false)} className="px-4 py-2 text-slate-500 hover:text-white text-xs font-bold uppercase">Cancel</button>
              <button 
                onClick={handleRefine} 
                disabled={isSubmittingRefinement || !refinePrompt.trim()}
                className="bg-cyan-600 hover:bg-cyan-500 text-black px-6 py-2 clip-corner flex items-center gap-2 disabled:opacity-50 font-black text-xs uppercase tracking-widest"
              >
                {isSubmittingRefinement ? <Loader2 className="animate-spin" size={14} /> : <Save size={14} />}
                Apply Updates
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CONTENT: DETAILS TAB */}
      {activeTab === 'details' && (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-fade-in">
        
        {/* LEFT COLUMN: DETAILS */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* OVERVIEW CARD */}
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6 relative overflow-hidden">
             <div className="absolute top-0 right-0 p-4 opacity-5">
                <Target size={120} />
             </div>
             <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest mb-4">Executive Summary</h3>
             <p className="text-slate-200 leading-relaxed font-medium text-lg mb-6 relative z-10">
               {analysis.description}
             </p>

             <div className="grid grid-cols-2 md:grid-cols-4 gap-4 relative z-10">
                <div className="p-3 bg-black border border-slate-800 rounded">
                  <div className="text-[9px] text-slate-500 uppercase font-black mb-1">Risk Level</div>
                  <div className={`font-mono text-sm font-bold ${
                    analysis.riskLevel === 'Low' ? 'text-green-400' : 
                    analysis.riskLevel === 'Medium' ? 'text-yellow-400' : 'text-red-400'
                  }`}>{analysis.riskLevel.toUpperCase()}</div>
                </div>
                <div className="p-3 bg-black border border-slate-800 rounded">
                  <div className="text-[9px] text-slate-500 uppercase font-black mb-1">Timeframe</div>
                  <div className="font-mono text-sm font-bold text-cyan-300">{analysis.timeframe}</div>
                </div>
                <div className="p-3 bg-black border border-slate-800 rounded">
                  <div className="text-[9px] text-slate-500 uppercase font-black mb-1">Asset Class</div>
                  <div className="font-mono text-sm font-bold text-white truncate">{analysis.assets.join(', ')}</div>
                </div>
                <div className="p-3 bg-black border border-slate-800 rounded">
                  <div className="text-[9px] text-slate-500 uppercase font-black mb-1">Sentiment</div>
                  <div className="font-mono text-sm font-bold text-purple-400">{analysis.overallSentiment}/100</div>
                </div>
             </div>
          </div>

          {/* LOGIC BLOCKS */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* ENTRY LOGIC */}
            <div className="bg-black border border-green-900/40 rounded-xl p-6 relative group hover:border-green-500/40 transition-all">
               <h3 className="text-sm font-black text-green-400 mb-4 flex items-center gap-2 uppercase tracking-wider">
                 <CheckCircle2 size={16} /> Entry Protocol
               </h3>
               <ul className="space-y-3">
                 {analysis.buyConditions.map((condition, i) => (
                   <li key={i} className="flex items-start gap-3 text-slate-300 text-xs font-medium leading-relaxed">
                     <span className="font-mono text-green-500/50 mt-0.5">0{i+1}</span>
                     <span>{condition}</span>
                   </li>
                 ))}
               </ul>
            </div>

            {/* EXIT LOGIC */}
            <div className="bg-black border border-red-900/40 rounded-xl p-6 relative group hover:border-red-500/40 transition-all">
               <h3 className="text-sm font-black text-red-400 mb-4 flex items-center gap-2 uppercase tracking-wider">
                 <Ban size={16} /> Exit Protocol
               </h3>
               <ul className="space-y-3 mb-6">
                 {analysis.sellConditions.map((condition, i) => (
                   <li key={i} className="flex items-start gap-3 text-slate-300 text-xs font-medium leading-relaxed">
                     <span className="font-mono text-red-500/50 mt-0.5">0{i+1}</span>
                     <span>{condition}</span>
                   </li>
                 ))}
               </ul>
               
               <div className="space-y-2 pt-4 border-t border-slate-800/50">
                 <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-500 font-bold uppercase">Stop Loss</span>
                    <span className="text-red-300 font-mono">{analysis.stopLoss}</span>
                 </div>
                 <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-500 font-bold uppercase">Take Profit</span>
                    <span className="text-green-300 font-mono">{analysis.takeProfit}</span>
                 </div>
               </div>
            </div>
          </div>

          {/* FAILURE MODES & SCENARIOS */}
          {(analysis.failureModes || analysis.exampleScenario) && (
             <div className="bg-slate-900/30 border border-slate-800 rounded-xl p-6">
                <h3 className="text-xs font-black text-white mb-4 flex items-center gap-2 uppercase tracking-widest">
                   <BrainCircuit size={16} className="text-purple-400" /> Deep Analysis
                </h3>
                
                {analysis.exampleScenario && (
                    <div className="mb-6 bg-purple-900/10 border-l-2 border-purple-500/50 p-4">
                        <h4 className="text-[10px] font-black text-purple-300 mb-2 uppercase tracking-wider">Scenario Simulation</h4>
                        <p className="text-slate-300 text-xs leading-relaxed italic font-mono">
                            "{analysis.exampleScenario}"
                        </p>
                    </div>
                )}

                {analysis.failureModes && analysis.failureModes.length > 0 && (
                    <div>
                        <h4 className="text-[10px] font-black text-red-400 mb-3 flex items-center gap-2 uppercase tracking-wider">
                            <AlertTriangle size={12} /> Failure Modes
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {analysis.failureModes.map((mode, i) => (
                                <div key={i} className="bg-red-950/10 border border-red-900/20 p-2 rounded text-[10px] text-red-200/70 font-mono">
                                    <span className="text-red-500 mr-2">!</span> {mode}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
             </div>
          )}
          
        </div>

        {/* RIGHT COLUMN: CHAT & PERFORMANCE */}
        <div className="space-y-6">
           
           {/* PERFORMANCE CHART */}
           <div className="bg-black border border-slate-800 rounded-xl p-6 shadow-xl">
              <h3 className="text-xs font-black text-white mb-4 flex items-center gap-2 uppercase tracking-widest">
                <BarChart3 size={16} className="text-cyan-400" /> Backtest Projection
              </h3>
              <div className="h-48 w-full bg-slate-900/30 rounded border border-slate-800/50 mb-3">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={mockData}>
                    <defs>
                      <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={isProfitable ? '#4ade80' : '#f87171'} stopOpacity={0.2}/>
                        <stop offset="95%" stopColor={isProfitable ? '#4ade80' : '#f87171'} stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                    <XAxis dataKey="day" hide />
                    <YAxis hide domain={['auto', 'auto']} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#000', borderColor: '#334155', color: '#f1f5f9', fontSize: '12px', fontFamily: 'monospace' }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="equity" 
                      stroke={isProfitable ? '#4ade80' : '#f87171'} 
                      strokeWidth={2}
                      fillOpacity={1} 
                      fill="url(#colorEquity)" 
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
              <div className="flex justify-between items-center text-xs font-mono">
                <span className="text-slate-500">30 DAY DELTA</span>
                <span className={`font-bold ${isProfitable ? 'text-green-400' : 'text-red-400'}`}>
                  {isProfitable ? '+12.4%' : '-4.2%'}
                </span>
              </div>
           </div>

           {/* CHATBOT */}
           <ChatBot contextData={JSON.stringify(analysis, null, 2)} />
        </div>
      </div>
      )}

      {/* CONTENT: THE FORGE TAB */}
      {activeTab === 'forge' && (
          <div className="bg-black border border-slate-800 rounded-xl overflow-hidden min-h-[600px] flex flex-col shadow-2xl relative">
              <div className="absolute top-0 right-0 w-full h-1 bg-gradient-to-r from-indigo-600 to-purple-600 z-20"></div>
              {strategy.artifacts ? (
                  <>
                    {/* ARTIFACT NAVIGATION */}
                    <div className="flex border-b border-slate-800 bg-slate-950">
                        <button 
                            onClick={() => setArtifactTab('python')}
                            className={`px-6 py-4 text-xs font-black uppercase tracking-widest border-b-2 transition-colors flex items-center gap-2 ${artifactTab === 'python' ? 'border-indigo-500 text-white bg-slate-900' : 'border-transparent text-slate-500 hover:text-white'}`}
                        >
                            <Terminal size={14} /> Python (CCXT)
                        </button>
                        <button 
                            onClick={() => setArtifactTab('pine')}
                            className={`px-6 py-4 text-xs font-black uppercase tracking-widest border-b-2 transition-colors flex items-center gap-2 ${artifactTab === 'pine' ? 'border-indigo-500 text-white bg-slate-900' : 'border-transparent text-slate-500 hover:text-white'}`}
                        >
                            <BarChart3 size={14} /> Pine Script
                        </button>
                        <button 
                            onClick={() => setArtifactTab('config')}
                            className={`px-6 py-4 text-xs font-black uppercase tracking-widest border-b-2 transition-colors flex items-center gap-2 ${artifactTab === 'config' ? 'border-indigo-500 text-white bg-slate-900' : 'border-transparent text-slate-500 hover:text-white'}`}
                        >
                            <FileJson size={14} /> Config.json
                        </button>
                        <button 
                            onClick={() => setArtifactTab('narrative')}
                            className={`px-6 py-4 text-xs font-black uppercase tracking-widest border-b-2 transition-colors flex items-center gap-2 ${artifactTab === 'narrative' ? 'border-indigo-500 text-white bg-slate-900' : 'border-transparent text-slate-500 hover:text-white'}`}
                        >
                            <FileText size={14} /> Narrative
                        </button>
                    </div>

                    {/* CODE VIEWER */}
                    <div className="flex-1 p-0 relative group bg-[#0d0d0d]">
                        <button 
                            onClick={() => copyToClipboard(getActiveArtifactContent(), artifactTab)}
                            className="absolute top-4 right-4 px-3 py-1.5 bg-indigo-900/50 hover:bg-indigo-600 text-indigo-200 hover:text-white rounded border border-indigo-500/30 backdrop-blur opacity-0 group-hover:opacity-100 transition-all flex items-center gap-2 z-10 text-[10px] font-bold uppercase tracking-widest"
                        >
                            {copiedArtifact === artifactTab ? <Check size={12} /> : <Copy size={12} />}
                            {copiedArtifact === artifactTab ? 'COPIED' : 'COPY'}
                        </button>
                        
                        <div className="h-[600px] overflow-auto custom-scrollbar p-6">
                            {artifactTab === 'narrative' ? (
                                <div className="prose prose-invert prose-slate max-w-none">
                                    <pre className="whitespace-pre-wrap font-sans text-sm text-slate-300 leading-relaxed bg-transparent border-none p-0">
                                        {strategy.artifacts.narrative}
                                    </pre>
                                </div>
                            ) : (
                                <pre className="font-mono-tech text-[11px] leading-relaxed text-blue-300 selection:bg-indigo-500/30 selection:text-white">
                                    <code>{getActiveArtifactContent()}</code>
                                </pre>
                            )}
                        </div>
                    </div>
                  </>
              ) : (
                  <div className="flex-1 flex flex-col items-center justify-center p-12 text-center bg-black/50">
                      <div className="w-20 h-20 bg-slate-900 rounded-full flex items-center justify-center mb-6 border border-slate-800 shadow-[0_0_30px_rgba(0,0,0,0.5)]">
                          <Code size={40} className="text-slate-600" />
                      </div>
                      <h3 className="text-xl font-black text-white mb-2 uppercase tracking-tight">Artifacts Not Forged</h3>
                      <p className="text-slate-500 max-w-md mb-8 text-xs font-mono">
                          The Sovereign Artifacts (Python bot, Pine Script, Config) have not been generated for this strategy yet.
                      </p>
                      <button 
                          onClick={handleManualForge}
                          disabled={isForging}
                          className="bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-3 clip-corner font-black text-xs uppercase tracking-widest flex items-center gap-2 shadow-[0_0_20px_rgba(79,70,229,0.4)] transition-all disabled:opacity-50"
                      >
                          {isForging ? <Loader2 className="animate-spin" /> : <Sparkles size={16} />}
                          {isForging ? 'Forging...' : 'Initialize Code Forge'}
                      </button>
                  </div>
              )}
          </div>
      )}

    </div>
  );
};

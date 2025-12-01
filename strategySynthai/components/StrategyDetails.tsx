
import React, { useState } from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { useStrategies } from '../context/StrategyContext';
import { ChatBot } from './ChatBot';
import { refineStrategy, generateFullStrategyPackage } from '../services/geminiService';
import { ArrowLeft, ExternalLink, AlertTriangle, CheckCircle2, Ban, BarChart3, Edit3, Save, X, Sparkles, Loader2, Target, ShieldCheck, Crosshair, Brain, Layers, BrainCircuit, Code, FileJson, FileCode, Check, Award, FileText, Copy } from 'lucide-react';
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
      case 'Sniper': return 'bg-red-900/30 text-red-400 border-red-500/30';
      case 'Vault': return 'bg-green-900/30 text-green-400 border-green-500/30';
      case 'Ladder': return 'bg-blue-900/30 text-blue-400 border-blue-500/30';
      case 'MENACE': return 'bg-purple-900/30 text-purple-400 border-purple-500/30';
      default: return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  const getCategoryIcon = (cat: string) => {
    switch(cat) {
      case 'Sniper': return <Crosshair size={16} />;
      case 'Vault': return <ShieldCheck size={16} />;
      case 'Ladder': return <Layers size={16} />;
      case 'MENACE': return <Brain size={16} />;
      default: return <Target size={16} />;
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
      <div className="mb-6">
        <Link to="/" className="inline-flex items-center text-slate-400 hover:text-white mb-4 transition-colors">
          <ArrowLeft size={18} className="mr-2" /> Back to Dashboard
        </Link>
        
        <div className="flex flex-col md:flex-row justify-between items-start gap-4">
          <div>
            <div className="flex items-center gap-3 mb-2">
                 <h1 className="text-3xl md:text-4xl font-bold text-white">{analysis.name}</h1>
                 {/* PIPELINE STATUS */}
                 {isCertified ? (
                     <div className="flex items-center gap-1.5 px-3 py-1 bg-green-900/30 text-green-400 border border-green-500/50 rounded-full text-xs font-bold uppercase tracking-wider shadow-lg shadow-green-900/20">
                         <Award size={14} /> Sovereign Certified
                     </div>
                 ) : (
                     <div className="flex items-center gap-1.5 px-3 py-1 bg-slate-800 text-slate-400 border border-slate-700 rounded-full text-xs font-bold uppercase tracking-wider">
                         <Loader2 size={12} className="animate-spin" /> Draft (Uncertified)
                     </div>
                 )}
            </div>
            
            <div className="flex flex-wrap items-center gap-3 text-sm">
               {/* SOVEREIGN CATEGORY */}
               <div className={`flex items-center gap-2 px-3 py-1 rounded-full border font-bold uppercase tracking-wide ${getCategoryColor(analysis.sovereignCategory)}`}>
                  {getCategoryIcon(analysis.sovereignCategory)}
                  <span>{analysis.sovereignCategory} Protocol</span>
               </div>
               
               {/* ASSET TIER */}
               {analysis.assetTier && (
                 <div className="bg-slate-800 text-slate-300 px-3 py-1 rounded-full border border-slate-700">
                    {analysis.assetTier.replace('_', ' ')}
                 </div>
               )}

               <span className="text-slate-500">•</span>
               <span className="text-slate-400">{new Date(strategy.createdAt).toLocaleDateString()}</span>
            </div>
          </div>

          <div className="flex gap-2">
              {!isCertified && (
                <button 
                    onClick={handleCertify}
                    className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition-colors font-medium shadow-lg shadow-green-500/20"
                >
                    <CheckCircle2 size={18} /> Certify Strategy
                </button>
              )}
              <button 
                onClick={() => setIsRefining(true)}
                className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors font-medium shadow-lg shadow-indigo-500/20"
              >
                <Sparkles size={18} /> Refine
              </button>
          </div>
        </div>
      </div>

      {/* TABS */}
      <div className="flex items-center gap-1 bg-slate-900/50 p-1 rounded-lg w-fit border border-slate-800 mb-8">
          <button 
             onClick={() => setActiveTab('details')}
             className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'details' ? 'bg-slate-800 text-white shadow' : 'text-slate-400 hover:text-white'}`}
          >
             <Target size={16} /> Strategy Details
          </button>
          <button 
             onClick={() => setActiveTab('forge')}
             className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'forge' ? 'bg-indigo-900/30 text-indigo-300 border border-indigo-500/30 shadow' : 'text-slate-400 hover:text-white'}`}
          >
             <Code size={16} /> The Code Forge
          </button>
      </div>

      {/* REFINEMENT MODAL */}
      {isRefining && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-700 rounded-xl w-full max-w-lg p-6 shadow-2xl">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Edit3 size={20} className="text-indigo-400" /> Refine Strategy
              </h3>
              <button onClick={() => setIsRefining(false)} className="text-slate-500 hover:text-white">
                <X size={24} />
              </button>
            </div>
            <textarea 
              className="w-full bg-slate-800 border border-slate-700 rounded-lg p-3 text-white h-32 focus:ring-2 focus:ring-indigo-500 outline-none mb-4"
              placeholder="e.g., 'Make the stop loss tighter' or 'Add volume confirmation'"
              value={refinePrompt}
              onChange={(e) => setRefinePrompt(e.target.value)}
            />
            <div className="flex justify-end gap-3">
              <button onClick={() => setIsRefining(false)} className="px-4 py-2 text-slate-300 hover:text-white">Cancel</button>
              <button 
                onClick={handleRefine} 
                disabled={isSubmittingRefinement || !refinePrompt.trim()}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 disabled:opacity-50"
              >
                {isSubmittingRefinement ? <Loader2 className="animate-spin" size={18} /> : <Save size={18} />}
                Apply
              </button>
            </div>
          </div>
        </div>
      )}

      {/* CONTENT: DETAILS TAB */}
      {activeTab === 'details' && (
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* LEFT COLUMN: DETAILS */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* OVERVIEW CARD */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
             <h3 className="text-lg font-semibold text-white mb-4">Executive Summary</h3>
             <p className="text-slate-300 leading-relaxed text-lg mb-6">
               {analysis.description}
             </p>

             <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-800">
                  <div className="text-xs text-slate-500 uppercase font-bold mb-1">Risk Level</div>
                  <div className={`font-bold ${
                    analysis.riskLevel === 'Low' ? 'text-green-400' : 
                    analysis.riskLevel === 'Medium' ? 'text-yellow-400' : 'text-red-400'
                  }`}>{analysis.riskLevel}</div>
                </div>
                <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-800">
                  <div className="text-xs text-slate-500 uppercase font-bold mb-1">Timeframe</div>
                  <div className="font-bold text-indigo-300">{analysis.timeframe}</div>
                </div>
                <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-800">
                  <div className="text-xs text-slate-500 uppercase font-bold mb-1">Assets</div>
                  <div className="font-bold text-white truncate">{analysis.assets.join(', ')}</div>
                </div>
                <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-800">
                  <div className="text-xs text-slate-500 uppercase font-bold mb-1">Sentiment</div>
                  <div className="font-bold text-purple-400">{analysis.overallSentiment}/100</div>
                </div>
             </div>
          </div>

          {/* LOGIC BLOCKS */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* ENTRY LOGIC */}
            <div className="bg-slate-900 border border-green-900/30 rounded-xl p-6">
               <h3 className="text-lg font-semibold text-green-400 mb-4 flex items-center gap-2">
                 <CheckCircle2 size={20} /> Entry Protocol
               </h3>
               <ul className="space-y-3">
                 {analysis.buyConditions.map((condition, i) => (
                   <li key={i} className="flex items-start gap-3 text-slate-300 text-sm">
                     <div className="w-1.5 h-1.5 rounded-full bg-green-500 mt-2 flex-shrink-0"></div>
                     <span>{condition}</span>
                   </li>
                 ))}
               </ul>
            </div>

            {/* EXIT LOGIC */}
            <div className="bg-slate-900 border border-red-900/30 rounded-xl p-6">
               <h3 className="text-lg font-semibold text-red-400 mb-4 flex items-center gap-2">
                 <Ban size={20} /> Exit Protocol
               </h3>
               <ul className="space-y-3 mb-6">
                 {analysis.sellConditions.map((condition, i) => (
                   <li key={i} className="flex items-start gap-3 text-slate-300 text-sm">
                     <div className="w-1.5 h-1.5 rounded-full bg-red-500 mt-2 flex-shrink-0"></div>
                     <span>{condition}</span>
                   </li>
                 ))}
               </ul>
               
               <div className="space-y-3 pt-4 border-t border-slate-800">
                 <div className="flex justify-between items-center text-sm">
                    <span className="text-slate-500">Stop Loss:</span>
                    <span className="text-white font-mono bg-slate-800 px-2 py-1 rounded border border-slate-700">{analysis.stopLoss}</span>
                 </div>
                 <div className="flex justify-between items-center text-sm">
                    <span className="text-slate-500">Take Profit:</span>
                    <span className="text-white font-mono bg-slate-800 px-2 py-1 rounded border border-slate-700">{analysis.takeProfit}</span>
                 </div>
               </div>
            </div>
          </div>

          {/* FAILURE MODES & SCENARIOS */}
          {(analysis.failureModes || analysis.exampleScenario) && (
             <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                   <BrainCircuit size={20} className="text-indigo-400" /> Deep Analysis
                </h3>
                
                {analysis.exampleScenario && (
                    <div className="mb-6 bg-indigo-900/10 border border-indigo-900/30 p-4 rounded-lg">
                        <h4 className="text-sm font-bold text-indigo-300 mb-2">Example Scenario</h4>
                        <p className="text-slate-300 text-sm leading-relaxed italic">
                            "{analysis.exampleScenario}"
                        </p>
                    </div>
                )}

                {analysis.failureModes && analysis.failureModes.length > 0 && (
                    <div>
                        <h4 className="text-sm font-bold text-red-300 mb-2 flex items-center gap-2">
                            <AlertTriangle size={14} /> Known Failure Modes
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {analysis.failureModes.map((mode, i) => (
                                <div key={i} className="bg-red-950/20 border border-red-900/20 p-2 rounded text-xs text-red-200/80 flex items-start gap-2">
                                    <span className="mt-1">•</span> {mode}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
             </div>
          )}

          {/* INDICATORS */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
             <h3 className="text-lg font-semibold text-white mb-4">Technical Indicators</h3>
             <div className="flex flex-wrap gap-2">
               {analysis.indicators.map((ind, i) => (
                 <span key={i} className="bg-slate-800 text-slate-300 px-3 py-1.5 rounded-md text-sm border border-slate-700">
                   {ind}
                 </span>
               ))}
             </div>
          </div>
          
        </div>

        {/* RIGHT COLUMN: CHAT & PERFORMANCE */}
        <div className="space-y-6">
           
           {/* PERFORMANCE CHART */}
           <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <BarChart3 size={20} className="text-indigo-400" /> Projected Performance
              </h3>
              <div className="h-48 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={mockData}>
                    <defs>
                      <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={isProfitable ? '#4ade80' : '#f87171'} stopOpacity={0.3}/>
                        <stop offset="95%" stopColor={isProfitable ? '#4ade80' : '#f87171'} stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis dataKey="day" hide />
                    <YAxis hide domain={['auto', 'auto']} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f1f5f9' }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="equity" 
                      stroke={isProfitable ? '#4ade80' : '#f87171'} 
                      fillOpacity={1} 
                      fill="url(#colorEquity)" 
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
              <div className="mt-4 flex justify-between items-center text-sm">
                <span className="text-slate-500">30 Day Projection</span>
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
          <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden min-h-[600px] flex flex-col shadow-2xl">
              {strategy.artifacts ? (
                  <>
                    {/* ARTIFACT NAVIGATION */}
                    <div className="flex border-b border-slate-800 bg-slate-900/50">
                        <button 
                            onClick={() => setArtifactTab('python')}
                            className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${artifactTab === 'python' ? 'border-indigo-500 text-white bg-slate-800' : 'border-transparent text-slate-400 hover:text-white'}`}
                        >
                            <FileCode size={16} /> Python (CCXT)
                        </button>
                        <button 
                            onClick={() => setArtifactTab('pine')}
                            className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${artifactTab === 'pine' ? 'border-indigo-500 text-white bg-slate-800' : 'border-transparent text-slate-400 hover:text-white'}`}
                        >
                            <BarChart3 size={16} /> Pine Script
                        </button>
                        <button 
                            onClick={() => setArtifactTab('config')}
                            className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${artifactTab === 'config' ? 'border-indigo-500 text-white bg-slate-800' : 'border-transparent text-slate-400 hover:text-white'}`}
                        >
                            <FileJson size={16} /> JSON Config
                        </button>
                        <button 
                            onClick={() => setArtifactTab('narrative')}
                            className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${artifactTab === 'narrative' ? 'border-indigo-500 text-white bg-slate-800' : 'border-transparent text-slate-400 hover:text-white'}`}
                        >
                            <FileText size={16} /> Narrative
                        </button>
                    </div>

                    {/* CODE VIEWER */}
                    <div className="flex-1 p-0 relative group bg-[#0d1117]">
                        <button 
                            onClick={() => copyToClipboard(getActiveArtifactContent(), artifactTab)}
                            className="absolute top-4 right-4 p-2 bg-slate-800/80 hover:bg-slate-700 text-slate-300 rounded-md border border-slate-700 backdrop-blur opacity-0 group-hover:opacity-100 transition-all flex items-center gap-2 z-10"
                        >
                            {copiedArtifact === artifactTab ? <CheckCircle2 size={16} className="text-green-400"/> : <Copy size={16} />}
                            <span className="text-xs">{copiedArtifact === artifactTab ? 'Copied!' : 'Copy Code'}</span>
                        </button>
                        
                        <div className="h-[600px] overflow-auto custom-scrollbar p-6">
                            {artifactTab === 'narrative' ? (
                                <div className="prose prose-invert prose-slate max-w-none">
                                    <pre className="whitespace-pre-wrap font-sans text-sm text-slate-300 leading-relaxed bg-transparent border-none p-0">
                                        {strategy.artifacts.narrative}
                                    </pre>
                                </div>
                            ) : (
                                <pre className="font-mono text-sm leading-relaxed">
                                    <code className="language-python text-blue-300">
                                        {getActiveArtifactContent()}
                                    </code>
                                </pre>
                            )}
                        </div>
                    </div>
                  </>
              ) : (
                  <div className="flex-1 flex flex-col items-center justify-center p-12 text-center">
                      <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mb-6">
                          <Code size={32} className="text-slate-500" />
                      </div>
                      <h3 className="text-xl font-bold text-white mb-2">Artifacts Not Forged</h3>
                      <p className="text-slate-400 max-w-md mb-8">
                          The Sovereign Artifacts (Python bot, Pine Script, Config) have not been generated for this strategy yet.
                      </p>
                      <button 
                          onClick={handleManualForge}
                          disabled={isForging}
                          className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-3 rounded-lg font-bold flex items-center gap-2 shadow-lg shadow-indigo-500/20 transition-all disabled:opacity-50"
                      >
                          {isForging ? <Loader2 className="animate-spin" /> : <Sparkles size={18} />}
                          {isForging ? 'Forging Artifacts...' : 'Forge Strategy Artifacts Now'}
                      </button>
                  </div>
              )}
          </div>
      )}

    </div>
  );
};

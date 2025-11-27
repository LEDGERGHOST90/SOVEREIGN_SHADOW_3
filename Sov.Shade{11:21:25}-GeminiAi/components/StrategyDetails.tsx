import React, { useState } from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { useStrategies } from '../context/StrategyContext';
import { ChatBot } from './ChatBot';
import { refineStrategy } from '../services/geminiService';
import { ArrowLeft, ExternalLink, AlertTriangle, CheckCircle2, Ban, BarChart3, Edit3, Save, X, Sparkles, Loader2 } from 'lucide-react';
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

  const strategy = strategies.find(s => s.id === id);

  if (!strategy) {
    return <Navigate to="/" replace />;
  }

  const { analysis } = strategy;
  const mockData = generateMockBacktestData(analysis.overallSentiment);
  const isProfitable = mockData[mockData.length - 1].equity > 10000;

  const handleRefine = async () => {
    if (!refinePrompt.trim()) return;
    setIsSubmittingRefinement(true);
    try {
      const updatedAnalysis = await refineStrategy(analysis, refinePrompt, strategy.model);
      updateStrategy(strategy.id, { analysis: updatedAnalysis });
      setIsRefining(false);
      setRefinePrompt('');
    } catch (error) {
      console.error("Refinement failed", error);
      alert("Failed to refine strategy. Please try again.");
    } finally {
      setIsSubmittingRefinement(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col gap-4">
        <Link to="/" className="text-slate-400 hover:text-white flex items-center gap-2 mb-1 text-sm w-fit">
          <ArrowLeft size={16} /> Back to Dashboard
        </Link>
        
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2 flex items-center gap-3">
              {analysis.name}
              <span className="px-2 py-0.5 text-xs font-normal bg-indigo-900/50 text-indigo-300 border border-indigo-700/50 rounded-full">
                {strategy.model === 'gemini-3-pro-preview' ? 'Pro Analysis' : 'Flash Analysis'}
              </span>
            </h1>
            <div className="flex flex-wrap gap-3">
              {analysis.assets.map(asset => (
                <span key={asset} className="px-2 py-1 bg-slate-800 text-slate-300 text-xs rounded border border-slate-700 font-mono">
                  {asset}
                </span>
              ))}
              <span className="px-2 py-1 bg-slate-800 text-slate-300 text-xs rounded border border-slate-700 font-mono">
                {analysis.timeframe}
              </span>
            </div>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={() => setIsRefining(!isRefining)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg border transition-all ${
                isRefining 
                  ? 'bg-indigo-600 text-white border-indigo-500' 
                  : 'bg-slate-800 text-slate-300 border-slate-700 hover:border-indigo-500 hover:text-white'
              }`}
            >
              <Edit3 size={16} />
              {isRefining ? 'Cancel Edit' : 'Refine Strategy'}
            </button>
            
            {strategy.videoUrl && (
              <a 
                href={strategy.videoUrl} 
                target="_blank" 
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-red-600/20 text-red-400 hover:bg-red-600/30 border border-red-600/30 rounded-lg transition-colors"
              >
                <ExternalLink size={16} />
                Video
              </a>
            )}
            <div className={`
              px-4 py-2 rounded-lg border font-bold flex items-center
              ${analysis.riskLevel === 'Low' ? 'bg-green-900/20 border-green-900 text-green-400' : 
                analysis.riskLevel === 'Medium' ? 'bg-yellow-900/20 border-yellow-900 text-yellow-400' : 
                'bg-red-900/20 border-red-900 text-red-400'}
            `}>
              {analysis.riskLevel} Risk
            </div>
          </div>
        </div>
      </div>

      {/* Refinement Panel */}
      {isRefining && (
        <div className="bg-slate-800 border border-indigo-500/30 rounded-xl p-6 animate-fade-in shadow-lg shadow-indigo-900/20">
          <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
            <Sparkles className="text-indigo-400" size={18} />
            Refine Strategy Logic
          </h3>
          <p className="text-slate-400 text-sm mb-4">
            Tell the AI how to modify this strategy. For example: "Make the stop loss tighter", "Add a volume confirmation rule", or "Change this to a Python scalping bot description".
          </p>
          <div className="flex gap-2">
            <input
              type="text"
              value={refinePrompt}
              onChange={(e) => setRefinePrompt(e.target.value)}
              placeholder="E.g., Add RSI divergence as an entry condition..."
              className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              onKeyDown={(e) => e.key === 'Enter' && handleRefine()}
            />
            <button
              onClick={handleRefine}
              disabled={isSubmittingRefinement || !refinePrompt.trim()}
              className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {isSubmittingRefinement ? <Loader2 className="animate-spin" size={18} /> : <Save size={18} />}
              Update
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Strategy Details */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Description */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <BarChart3 className="text-indigo-400" size={20} />
              Strategy Overview
            </h3>
            <p className="text-slate-300 leading-relaxed">
              {analysis.description}
            </p>
          </div>

          {/* Conditions Grid */}
          <div className="grid md:grid-cols-2 gap-6">
            {/* Buy Conditions */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-green-400 mb-4 flex items-center gap-2">
                <CheckCircle2 size={20} />
                Entry Conditions (Long)
              </h3>
              <ul className="space-y-3">
                {analysis.buyConditions.map((condition, idx) => (
                  <li key={idx} className="flex items-start gap-3 text-slate-300 text-sm">
                    <span className="min-w-[6px] h-[6px] rounded-full bg-green-500 mt-2" />
                    {condition}
                  </li>
                ))}
              </ul>
            </div>

            {/* Sell Conditions */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-red-400 mb-4 flex items-center gap-2">
                <Ban size={20} />
                Exit / Short Conditions
              </h3>
              <ul className="space-y-3">
                {analysis.sellConditions.map((condition, idx) => (
                  <li key={idx} className="flex items-start gap-3 text-slate-300 text-sm">
                    <span className="min-w-[6px] h-[6px] rounded-full bg-red-500 mt-2" />
                    {condition}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Risk Management */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
             <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <AlertTriangle className="text-yellow-400" size={20} />
              Risk Management
            </h3>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="p-4 bg-slate-800/50 rounded-lg">
                <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">Stop Loss</div>
                <div className="font-medium text-white">{analysis.stopLoss}</div>
              </div>
              <div className="p-4 bg-slate-800/50 rounded-lg">
                <div className="text-xs text-slate-400 uppercase tracking-wider mb-1">Take Profit</div>
                <div className="font-medium text-white">{analysis.takeProfit}</div>
              </div>
            </div>
          </div>

          {/* Indicators */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
             <h3 className="text-lg font-semibold text-white mb-4">Required Indicators</h3>
             <div className="flex flex-wrap gap-2">
               {analysis.indicators.map((ind, i) => (
                 <span key={i} className="px-3 py-1.5 bg-slate-800 text-indigo-300 rounded-md text-sm border border-slate-700">
                   {ind}
                 </span>
               ))}
             </div>
          </div>

          {/* Mock Performance Chart */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-1">Projected Performance (AI Simulation)</h3>
            <p className="text-sm text-slate-500 mb-6">Based on sentiment score of {analysis.overallSentiment}/100. *Not financial advice.</p>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={mockData}>
                  <defs>
                    <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={isProfitable ? "#4ade80" : "#f87171"} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={isProfitable ? "#4ade80" : "#f87171"} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis dataKey="day" hide />
                  <YAxis domain={['auto', 'auto']} stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f1f5f9' }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="equity" 
                    stroke={isProfitable ? "#4ade80" : "#f87171"} 
                    fillOpacity={1} 
                    fill="url(#colorEquity)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Right Column: Chat */}
        <div className="lg:col-span-1">
          <div className="sticky top-8 space-y-6">
             <ChatBot contextData={JSON.stringify(analysis, null, 2)} />
             
             <div className="p-5 rounded-xl bg-indigo-900/10 border border-indigo-500/20 text-sm text-indigo-200">
               <div className="flex gap-2 mb-2 font-semibold text-indigo-100">
                 <Sparkles size={16} />
                 <span>Pro Tip</span>
               </div>
               <p className="opacity-80 mb-3">
                 Since you used {strategy.model === 'gemini-3-pro-preview' ? 'Gemini Pro' : 'Gemini Flash'}, the context window is large enough to handle complex coding requests.
               </p>
               <p className="opacity-80">
                 Try asking: "Write a complete Python script using the `ccxt` library to trade this strategy on Binance."
               </p>
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};

import React, { useState } from 'react';
import { Plus, Trash2, Code, Play, Save, Settings, Layers, Zap, AlertTriangle, ArrowRight } from 'lucide-react';
import { generateStrategyCode } from '../services/geminiService';
import { GeneratedCode } from '../types';

interface Condition {
  id: string;
  type: 'indicator' | 'price' | 'time' | 'pattern';
  left: string;
  operator: '>' | '<' | '>=' | '<=' | '==' | 'crosses_above' | 'crosses_below';
  right: string;
}

export const StrategyBuilder: React.FC = () => {
  const [name, setName] = useState('New Sovereign Strategy');
  const [entries, setEntries] = useState<Condition[]>([]);
  const [exits, setExits] = useState<Condition[]>([]);
  const [stopLoss, setStopLoss] = useState(2.0);
  const [takeProfit, setTakeProfit] = useState(4.0);
  const [timeframe, setTimeframe] = useState('15m');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedCode, setGeneratedCode] = useState<GeneratedCode | null>(null);
  const [activeTab, setActiveTab] = useState<'builder' | 'python' | 'pine'>('builder');

  const addEntry = () => {
    setEntries([...entries, { id: crypto.randomUUID(), type: 'indicator', left: 'RSI(14)', operator: '<', right: '30' }]);
  };

  const addExit = () => {
    setExits([...exits, { id: crypto.randomUUID(), type: 'indicator', left: 'RSI(14)', operator: '>', right: '70' }]);
  };

  const removeEntry = (id: string) => setEntries(entries.filter(e => e.id !== id));
  const removeExit = (id: string) => setExits(exits.filter(e => e.id !== id));

  const updateEntry = (id: string, field: keyof Condition, value: string) => {
    setEntries(entries.map(e => e.id === id ? { ...e, [field]: value } : e));
  };
  
  const updateExit = (id: string, field: keyof Condition, value: string) => {
    setExits(exits.map(e => e.id === id ? { ...e, [field]: value } : e));
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    const strategySpec = {
      name,
      timeframe,
      buyConditions: entries.map(e => `${e.left} ${e.operator} ${e.right}`),
      sellConditions: exits.map(e => `${e.left} ${e.operator} ${e.right}`),
      stopLoss: `${stopLoss}%`,
      takeProfit: `${takeProfit}%`,
      sovereignCategory: stopLoss < 1.5 ? 'Sniper' : 'Vault'
    };

    try {
      const code = await generateStrategyCode(strategySpec);
      setGeneratedCode(code);
      setActiveTab('python');
    } catch (e) {
      alert("Failed to generate code.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto pb-12 animate-fade-in">
       <div className="mb-8 flex flex-col md:flex-row justify-between items-start gap-4">
         <div>
            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
              <Code className="text-indigo-500" />
              Module E <span className="text-slate-500 text-lg font-normal">| The Forge</span>
            </h1>
            <p className="text-slate-400 mt-2">Interactive Strategy Builder & Code Generator.</p>
         </div>
         <div className="flex gap-3">
            <div className="bg-slate-900 border border-slate-700 rounded-lg p-1 flex items-center gap-2 px-3">
              <Settings size={14} className="text-slate-500" />
              <select 
                value={timeframe} 
                onChange={(e) => setTimeframe(e.target.value)}
                className="bg-transparent text-white text-sm focus:outline-none"
              >
                <option value="1m">1m</option>
                <option value="5m">5m</option>
                <option value="15m">15m</option>
                <option value="1h">1h</option>
                <option value="4h">4h</option>
                <option value="1d">1d</option>
              </select>
            </div>
            <button 
              onClick={handleGenerate}
              disabled={isGenerating}
              className="px-6 py-2 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white rounded-lg font-bold flex items-center gap-2 shadow-lg shadow-indigo-500/20"
            >
              {isGenerating ? <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div> : <Zap size={18} />}
              Generate Code
            </button>
         </div>
       </div>

       <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* LEFT: VISUAL BUILDER */}
          <div className="lg:col-span-2 space-y-6">
             <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                <input 
                  type="text" 
                  value={name} 
                  onChange={(e) => setName(e.target.value)}
                  className="bg-transparent text-2xl font-bold text-white w-full border-none focus:ring-0 placeholder-slate-600 mb-6"
                  placeholder="Strategy Name..."
                />

                {/* LOGIC FLOW */}
                <div className="space-y-4">
                   
                   {/* ENTRY BLOCK */}
                   <div className="bg-slate-800/50 rounded-xl border border-green-500/20 p-4">
                      <div className="flex justify-between items-center mb-3">
                        <h3 className="text-green-400 font-bold flex items-center gap-2"><ArrowRight size={18} /> Entry Conditions</h3>
                        <button onClick={addEntry} className="text-xs bg-slate-800 hover:bg-slate-700 text-white px-2 py-1 rounded border border-slate-700 flex items-center gap-1"><Plus size={12} /> Add</button>
                      </div>
                      <div className="space-y-2">
                        {entries.length === 0 && <div className="text-slate-500 text-sm italic text-center py-2">No conditions added.</div>}
                        {entries.map(e => (
                           <div key={e.id} className="flex items-center gap-2 bg-slate-900 p-2 rounded border border-slate-800">
                              <input 
                                className="bg-transparent text-white text-sm w-full focus:outline-none" 
                                value={e.left} 
                                onChange={evt => updateEntry(e.id, 'left', evt.target.value)}
                                placeholder="Indicator (e.g., RSI)"
                              />
                              <select 
                                className="bg-slate-800 text-slate-300 text-xs rounded p-1"
                                value={e.operator}
                                onChange={evt => updateEntry(e.id, 'operator', evt.target.value as any)}
                              >
                                <option value=">">&gt;</option>
                                <option value="<">&lt;</option>
                                <option value="==">==</option>
                                <option value="crosses_above">Crosses Above</option>
                                <option value="crosses_below">Crosses Below</option>
                              </select>
                              <input 
                                className="bg-transparent text-white text-sm w-full focus:outline-none text-right" 
                                value={e.right} 
                                onChange={evt => updateEntry(e.id, 'right', evt.target.value)}
                                placeholder="Value (e.g., 30)"
                              />
                              <button onClick={() => removeEntry(e.id)} className="text-slate-500 hover:text-red-400"><Trash2 size={14} /></button>
                           </div>
                        ))}
                      </div>
                   </div>

                   {/* EXIT BLOCK */}
                   <div className="bg-slate-800/50 rounded-xl border border-red-500/20 p-4">
                      <div className="flex justify-between items-center mb-3">
                        <h3 className="text-red-400 font-bold flex items-center gap-2"><AlertTriangle size={18} /> Exit Conditions</h3>
                        <button onClick={addExit} className="text-xs bg-slate-800 hover:bg-slate-700 text-white px-2 py-1 rounded border border-slate-700 flex items-center gap-1"><Plus size={12} /> Add</button>
                      </div>
                      <div className="space-y-2">
                        {exits.length === 0 && <div className="text-slate-500 text-sm italic text-center py-2">No conditions added.</div>}
                        {exits.map(e => (
                           <div key={e.id} className="flex items-center gap-2 bg-slate-900 p-2 rounded border border-slate-800">
                              <input 
                                className="bg-transparent text-white text-sm w-full focus:outline-none" 
                                value={e.left} 
                                onChange={evt => updateExit(e.id, 'left', evt.target.value)}
                              />
                              <select 
                                className="bg-slate-800 text-slate-300 text-xs rounded p-1"
                                value={e.operator}
                                onChange={evt => updateExit(e.id, 'operator', evt.target.value as any)}
                              >
                                <option value=">">&gt;</option>
                                <option value="<">&lt;</option>
                                <option value="==">==</option>
                                <option value="crosses_above">Crosses Above</option>
                                <option value="crosses_below">Crosses Below</option>
                              </select>
                              <input 
                                className="bg-transparent text-white text-sm w-full focus:outline-none text-right" 
                                value={e.right} 
                                onChange={evt => updateExit(e.id, 'right', evt.target.value)}
                              />
                              <button onClick={() => removeExit(e.id)} className="text-slate-500 hover:text-red-400"><Trash2 size={14} /></button>
                           </div>
                        ))}
                      </div>
                   </div>
                   
                </div>
             </div>

             {/* RISK MANAGEMENT */}
             <div className="grid grid-cols-2 gap-6">
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                    <h4 className="text-slate-400 text-xs font-bold uppercase mb-4">Stop Loss (%)</h4>
                    <div className="flex items-center gap-4">
                        <input 
                           type="range" min="0.1" max="10" step="0.1"
                           value={stopLoss} onChange={e => setStopLoss(parseFloat(e.target.value))}
                           className="w-full accent-red-500"
                        />
                        <span className="text-white font-mono font-bold w-12">{stopLoss}%</span>
                    </div>
                </div>
                <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                    <h4 className="text-slate-400 text-xs font-bold uppercase mb-4">Take Profit (%)</h4>
                    <div className="flex items-center gap-4">
                        <input 
                           type="range" min="0.5" max="50" step="0.5"
                           value={takeProfit} onChange={e => setTakeProfit(parseFloat(e.target.value))}
                           className="w-full accent-green-500"
                        />
                        <span className="text-white font-mono font-bold w-12">{takeProfit}%</span>
                    </div>
                </div>
             </div>
          </div>

          {/* RIGHT: CODE PREVIEW */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl flex flex-col h-[600px] overflow-hidden shadow-2xl">
             <div className="flex items-center border-b border-slate-800 bg-slate-950">
                <button 
                  onClick={() => setActiveTab('builder')}
                  className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'builder' ? 'border-indigo-500 text-white bg-slate-900' : 'border-transparent text-slate-500 hover:text-white'}`}
                >
                  Logic View
                </button>
                <button 
                  onClick={() => setActiveTab('python')}
                  disabled={!generatedCode}
                  className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'python' ? 'border-indigo-500 text-white bg-slate-900' : 'border-transparent text-slate-500 hover:text-white disabled:opacity-30'}`}
                >
                  Python (CCXT)
                </button>
                <button 
                  onClick={() => setActiveTab('pine')}
                  disabled={!generatedCode}
                  className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'pine' ? 'border-indigo-500 text-white bg-slate-900' : 'border-transparent text-slate-500 hover:text-white disabled:opacity-30'}`}
                >
                  Pine Script
                </button>
             </div>

             <div className="flex-1 overflow-auto bg-slate-950 p-0 relative">
                 {activeTab === 'builder' && (
                     <div className="p-8 flex flex-col items-center justify-center h-full text-center text-slate-500">
                         {generatedCode ? (
                             <>
                               <Code size={48} className="text-green-500 mb-4" />
                               <h3 className="text-white font-bold mb-2">Code Generated!</h3>
                               <p className="text-sm">Switch tabs to view Python or Pine Script.</p>
                             </>
                         ) : (
                             <>
                               <Layers size={48} className="opacity-20 mb-4" />
                               <p className="max-w-xs">Configure your logic on the left and click "Generate Code" to build the bot.</p>
                             </>
                         )}
                     </div>
                 )}

                 {(activeTab === 'python' || activeTab === 'pine') && generatedCode && (
                     <pre className="p-4 text-xs font-mono text-indigo-300 leading-relaxed custom-scrollbar">
                         {activeTab === 'python' ? generatedCode.python : generatedCode.pineScript}
                     </pre>
                 )}
                 
                 {generatedCode && activeTab !== 'builder' && (
                    <button 
                        onClick={() => navigator.clipboard.writeText(activeTab === 'python' ? generatedCode.python : generatedCode.pineScript)}
                        className="absolute top-4 right-4 p-2 bg-slate-800 hover:bg-slate-700 text-white rounded border border-slate-600 shadow-lg"
                        title="Copy Code"
                    >
                        <Save size={16} />
                    </button>
                 )}
             </div>
          </div>
       </div>
    </div>
  );
};

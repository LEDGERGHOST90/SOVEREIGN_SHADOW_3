
import React, { useState } from 'react';
import { FlaskConical, Upload, FileText, Database, Activity, Play, CheckCircle2, AlertTriangle, Plus, Trash2, FileJson, Table, BarChart2, Loader2, Zap } from 'lucide-react';
import { runDSStarAnalysis } from '../services/geminiService';
import { DataSet, DSAnalysis } from '../types';

export const DataScienceLab: React.FC = () => {
  const [datasets, setDatasets] = useState<DataSet[]>([]);
  const [analysis, setAnalysis] = useState<DSAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // File Handlers
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>, type: DataSet['type']) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const reader = new FileReader();
      reader.onload = (event) => {
        const newDataset: DataSet = {
          id: crypto.randomUUID(),
          name: file.name,
          type,
          content: event.target?.result as string,
          size: file.size
        };
        setDatasets(prev => [...prev, newDataset]);
      };
      reader.readAsText(file);
    }
  };

  const removeDataset = (id: string) => {
    setDatasets(prev => prev.filter(d => d.id !== id));
  };

  // Execution
  const handleRunFusion = async () => {
    const technical = datasets.find(d => d.type === 'technical')?.content || "No technical data provided.";
    const fundamental = datasets.find(d => d.type === 'fundamental')?.content || "No fundamental data provided.";
    const sentiment = datasets.find(d => d.type === 'sentiment')?.content || "No sentiment data provided.";

    setIsAnalyzing(true);
    setError(null);

    try {
      const result = await runDSStarAnalysis(technical, fundamental, sentiment);
      setAnalysis(result);
    } catch (e: any) {
      setError(e.message || "DS-Star Analysis Failed");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getSmartScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400 bg-green-900/20 border-green-500/50';
    if (score >= 50) return 'text-yellow-400 bg-yellow-900/20 border-yellow-500/50';
    return 'text-red-400 bg-red-900/20 border-red-500/50';
  };

  return (
    <div className="max-w-6xl mx-auto animate-fade-in pb-12">
      
      {/* HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-end gap-6 border-b border-slate-800/60 pb-6 mb-8">
        <div>
          <h1 className="text-3xl font-black text-white tracking-tighter uppercase italic flex items-center gap-3">
             <FlaskConical className="text-indigo-500" size={32} /> 
             DS-STAR <span className="text-slate-500 not-italic text-2xl">| Data Science Lab</span>
          </h1>
          <p className="text-slate-400 font-mono-tech text-xs mt-2 max-w-2xl border-l-2 border-indigo-500/30 pl-3">
             Heterogeneous Data Fusion Engine. Smart Asset Scoring.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* LEFT: DATA INGESTION */}
        <div className="space-y-6">
          <div className="bg-black border border-slate-800 rounded-xl p-6 shadow-2xl">
            <h3 className="text-white font-black text-xs uppercase tracking-widest mb-6 flex items-center gap-2">
              <Database size={14} className="text-indigo-400" /> Ingest Data
            </h3>
            
            <div className="space-y-4">
              {/* Technical Input */}
              <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-800 hover:border-indigo-500/30 transition-all group">
                <div className="flex justify-between items-start mb-2">
                  <div className="text-xs font-bold text-white flex items-center gap-2 uppercase">
                    <Activity size={12} className="text-blue-400" /> Technical
                  </div>
                  <label className="cursor-pointer bg-slate-800 hover:bg-slate-700 text-white p-1.5 rounded transition-colors border border-slate-700">
                    <Plus size={12} />
                    <input type="file" className="hidden" onChange={(e) => handleFileUpload(e, 'technical')} />
                  </label>
                </div>
                <div className="text-[10px] text-slate-500 mb-3 font-mono">CSV, JSON (Price, Volume, RSI)</div>
                {datasets.filter(d => d.type === 'technical').map(d => (
                  <div key={d.id} className="flex items-center justify-between text-[10px] bg-black p-2 rounded border border-slate-800 text-slate-300 font-mono">
                    <span className="truncate max-w-[150px]">{d.name}</span>
                    <button onClick={() => removeDataset(d.id)} className="text-slate-500 hover:text-red-400"><Trash2 size={12} /></button>
                  </div>
                ))}
              </div>

              {/* Fundamental Input */}
              <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-800 hover:border-indigo-500/30 transition-all group">
                <div className="flex justify-between items-start mb-2">
                  <div className="text-xs font-bold text-white flex items-center gap-2 uppercase">
                    <FileJson size={12} className="text-yellow-400" /> Fundamental
                  </div>
                  <label className="cursor-pointer bg-slate-800 hover:bg-slate-700 text-white p-1.5 rounded transition-colors border border-slate-700">
                    <Plus size={12} />
                    <input type="file" className="hidden" onChange={(e) => handleFileUpload(e, 'fundamental')} />
                  </label>
                </div>
                <div className="text-[10px] text-slate-500 mb-3 font-mono">JSON (On-Chain, TVL, Unlocks)</div>
                {datasets.filter(d => d.type === 'fundamental').map(d => (
                  <div key={d.id} className="flex items-center justify-between text-[10px] bg-black p-2 rounded border border-slate-800 text-slate-300 font-mono">
                    <span className="truncate max-w-[150px]">{d.name}</span>
                    <button onClick={() => removeDataset(d.id)} className="text-slate-500 hover:text-red-400"><Trash2 size={12} /></button>
                  </div>
                ))}
              </div>

              {/* Sentiment Input */}
              <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-800 hover:border-indigo-500/30 transition-all group">
                <div className="flex justify-between items-start mb-2">
                  <div className="text-xs font-bold text-white flex items-center gap-2 uppercase">
                    <FileText size={12} className="text-pink-400" /> Sentiment
                  </div>
                  <label className="cursor-pointer bg-slate-800 hover:bg-slate-700 text-white p-1.5 rounded transition-colors border border-slate-700">
                    <Plus size={12} />
                    <input type="file" className="hidden" onChange={(e) => handleFileUpload(e, 'sentiment')} />
                  </label>
                </div>
                <div className="text-[10px] text-slate-500 mb-3 font-mono">MD, TXT (Docs, News, Social)</div>
                {datasets.filter(d => d.type === 'sentiment').map(d => (
                  <div key={d.id} className="flex items-center justify-between text-[10px] bg-black p-2 rounded border border-slate-800 text-slate-300 font-mono">
                    <span className="truncate max-w-[150px]">{d.name}</span>
                    <button onClick={() => removeDataset(d.id)} className="text-slate-500 hover:text-red-400"><Trash2 size={12} /></button>
                  </div>
                ))}
              </div>
            </div>

            <button 
              onClick={handleRunFusion}
              disabled={isAnalyzing || datasets.length === 0}
              className="w-full mt-6 py-4 bg-indigo-600 hover:bg-indigo-500 text-white rounded font-black text-xs uppercase tracking-widest flex items-center justify-center gap-2 shadow-[0_0_20px_rgba(79,70,229,0.3)] disabled:opacity-50 disabled:cursor-not-allowed transition-all clip-corner"
            >
              {isAnalyzing ? <Loader2 className="animate-spin" size={16} /> : <Zap size={16} fill="currentColor" />}
              {isAnalyzing ? 'Fusing Data...' : 'Run Fusion Engine'}
            </button>
            
            {error && <div className="mt-4 text-[10px] font-mono text-red-400 text-center">{error}</div>}
          </div>
        </div>

        {/* RIGHT: ANALYSIS OUTPUT */}
        <div className="lg:col-span-2">
          {analysis ? (
            <div className="bg-black border border-slate-800 rounded-xl p-8 shadow-2xl animate-fade-in relative overflow-hidden">
              <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none">
                 <Zap size={200} />
              </div>

              <div className="flex justify-between items-start mb-8 relative z-10">
                <div>
                  <h2 className="text-4xl font-black text-white mb-1 uppercase italic tracking-tighter">{analysis.asset}</h2>
                  <div className="text-xs font-mono text-slate-500">HETEROGENEOUS FUSION REPORT</div>
                </div>
                <div className={`px-4 py-3 rounded-lg border ${getSmartScoreColor(analysis.smartScore)} text-center`}>
                  <div className="text-[9px] font-black uppercase tracking-widest opacity-80 mb-1">Smart Score</div>
                  <div className="text-4xl font-black">{analysis.smartScore}</div>
                </div>
              </div>

              {/* Signals Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8 relative z-10">
                <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800">
                  <div className="text-[10px] text-blue-400 font-black uppercase tracking-wider mb-2">Technical</div>
                  <div className="text-xs text-white font-medium">{analysis.technicalSignal}</div>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800">
                  <div className="text-[10px] text-yellow-400 font-black uppercase tracking-wider mb-2">Fundamental</div>
                  <div className="text-xs text-white font-medium">{analysis.fundamentalSignal}</div>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-lg border border-slate-800">
                  <div className="text-[10px] text-pink-400 font-black uppercase tracking-wider mb-2">Sentiment</div>
                  <div className="text-xs text-white font-medium">{analysis.sentimentSignal}</div>
                </div>
              </div>

              {/* Unified Verdict */}
              <div className="bg-indigo-950/20 border border-indigo-500/20 rounded-xl p-6 mb-6 relative z-10">
                <h3 className="text-sm font-black text-indigo-400 mb-3 flex items-center gap-2 uppercase tracking-wider">
                  <CheckCircle2 size={16} /> Unified Verdict
                </h3>
                <p className="text-slate-300 leading-relaxed text-sm font-medium">
                  {analysis.unifiedVerdict}
                </p>
                <div className="mt-4 pt-4 border-t border-indigo-500/20 flex items-center gap-3">
                  <div className="text-xs font-bold text-white uppercase">Recommended Action:</div>
                  <div className="text-indigo-200 font-mono text-xs px-2 py-1 bg-indigo-900/40 rounded border border-indigo-500/30">{analysis.suggestedAction}</div>
                </div>
              </div>

              {/* Risks */}
              <div className="relative z-10">
                <h3 className="text-xs font-black text-red-400 mb-3 flex items-center gap-2 uppercase tracking-wider">
                  <AlertTriangle size={14} /> Key Risk Factors
                </h3>
                <div className="space-y-2">
                  {analysis.keyRisks.map((risk, i) => (
                    <div key={i} className="flex items-start gap-3 bg-red-950/10 p-3 rounded border border-red-900/20">
                      <div className="w-1 h-1 rounded-full bg-red-500 mt-1.5"></div>
                      <span className="text-xs text-slate-400">{risk}</span>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center bg-black/40 border border-slate-800 rounded-xl border-dashed p-12 text-slate-600">
              <BarChart2 size={64} className="mb-6 opacity-20" />
              <h3 className="text-xl font-black mb-2 uppercase tracking-tight text-white">Lab Ready</h3>
              <p className="max-w-md text-center text-xs font-mono">
                  Upload datasets on the left to initialize the DS-STAR Fusion Engine.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

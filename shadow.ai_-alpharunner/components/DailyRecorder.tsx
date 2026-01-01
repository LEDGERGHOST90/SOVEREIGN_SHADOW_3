
import React, { useState, useEffect } from 'react';
import { DailyRecord, ModuleAOutput, Strategy, LegacyLoopData } from '../types';
import { generateSovereignDailyReport } from '../services/geminiService';
import { useStrategies } from '../context/StrategyContext';
import { BookOpen, Loader2, Calendar, Save, Plus, RefreshCw, FileText } from 'lucide-react';

export const DailyRecorder: React.FC = () => {
  const { strategies } = useStrategies();
  const [records, setRecords] = useState<DailyRecord[]>([]);
  const [selectedRecord, setSelectedRecord] = useState<DailyRecord | null>(null);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load from LocalStorage
  useEffect(() => {
    const stored = localStorage.getItem('dailyRecords');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        setRecords(parsed);
        if (parsed.length > 0) setSelectedRecord(parsed[0]);
      } catch (e) {
        console.error("Failed to load records");
      }
    }
  }, []);

  // Save to LocalStorage
  useEffect(() => {
    localStorage.setItem('dailyRecords', JSON.stringify(records));
  }, [records]);

  const handleGenerateReport = async () => {
    setGenerating(true);
    setError(null);

    // Try to get Module A scan from local storage to use as context
    let moduleAOutput: ModuleAOutput | null = null;
    const scanStr = localStorage.getItem('latestScan');
    if (scanStr) {
        try {
            moduleAOutput = JSON.parse(scanStr);
        } catch (e) {
            console.warn("Could not load Module A scan for report context");
        }
    }

    // Try to get Legacy Data (Financials) from local storage
    let legacyData: LegacyLoopData | undefined;
    const stateStr = localStorage.getItem('sovereignState');
    if (stateStr) {
        try {
            legacyData = JSON.parse(stateStr);
        } catch (e) {
            console.warn("Could not load Sovereign State for report context");
        }
    }

    if (!moduleAOutput && !legacyData) {
        setError("Insufficient data. Please run a Local Agent scan OR connect Financial Data (Dashboard) to generate a report.");
        setGenerating(false);
        return;
    }

    try {
      // Use latest 10 strategies
      const recentStrategies = strategies.slice(0, 10);
      const reportText = await generateSovereignDailyReport(moduleAOutput, recentStrategies, legacyData);

      const newRecord: DailyRecord = {
        id: crypto.randomUUID(),
        date: new Date().toISOString().split('T')[0],
        reportMarkdown: reportText,
        timestamp: Date.now()
      };

      setRecords(prev => [newRecord, ...prev]);
      setSelectedRecord(newRecord);
    } catch (err: any) {
      setError(err.message || "Failed to generate daily report");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto animate-fade-in pb-12">
      
      {/* HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-end gap-6 border-b border-slate-800/60 pb-6 mb-8">
        <div>
          <h1 className="text-3xl font-black text-white tracking-tighter uppercase italic flex items-center gap-3">
             <BookOpen className="text-indigo-500" size={32} /> 
             Module C <span className="text-slate-500 not-italic text-2xl">| Daily Log</span>
          </h1>
          <p className="text-slate-400 font-mono-tech text-xs mt-2 max-w-2xl border-l-2 border-indigo-500/30 pl-3">
             System State Persistence. Autonomous Journaling.
          </p>
        </div>
        
        <button 
          onClick={handleGenerateReport}
          disabled={generating}
          className="px-6 py-3 bg-indigo-600 hover:bg-indigo-500 text-white clip-corner font-black text-xs uppercase tracking-widest flex items-center gap-2 shadow-[0_0_20px_rgba(79,70,229,0.3)] transition-all disabled:opacity-50"
        >
          {generating ? <Loader2 className="animate-spin" size={16} /> : <Plus size={16} />}
          {generating ? 'Generating...' : "Log Today's Record"}
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-950/20 border border-red-500/30 rounded-lg text-red-400 font-mono text-xs mb-6">
            ERROR: {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* SIDEBAR LIST */}
        <div className="bg-black border border-slate-800 rounded-xl p-4 h-[600px] overflow-y-auto">
            <h3 className="text-slate-500 text-[10px] font-black uppercase tracking-widest mb-4 flex items-center gap-2">
                <Calendar size={12} /> Archive
            </h3>
            <div className="space-y-2">
                {records.length === 0 && <div className="text-slate-600 text-xs text-center py-8 font-mono">NO RECORDS FOUND</div>}
                {records.map(rec => (
                    <button
                        key={rec.id}
                        onClick={() => setSelectedRecord(rec)}
                        className={`w-full text-left p-3 rounded-lg border transition-all ${
                            selectedRecord?.id === rec.id 
                            ? 'bg-indigo-900/20 border-indigo-500/50 text-white shadow-lg' 
                            : 'bg-slate-900/30 border-transparent text-slate-500 hover:bg-slate-900 hover:text-slate-300'
                        }`}
                    >
                        <div className="font-bold text-xs mb-1">{rec.date}</div>
                        <div className="text-[10px] font-mono opacity-60">
                            {new Date(rec.timestamp).toLocaleTimeString()}
                        </div>
                    </button>
                ))}
            </div>
        </div>

        {/* MAIN CONTENT RENDERER */}
        <div className="lg:col-span-3 bg-black border border-slate-800 rounded-xl p-8 min-h-[600px] relative overflow-hidden shadow-2xl">
            <div className="absolute inset-0 bg-scanline opacity-5 pointer-events-none"></div>
            {selectedRecord ? (
                <div className="relative z-10 h-full overflow-y-auto custom-scrollbar pr-2">
                     <div className="flex items-center gap-3 mb-8 border-b border-slate-800 pb-4">
                        <FileText className="text-indigo-500" size={24} />
                        <div>
                             <h2 className="text-xl font-black text-white uppercase tracking-tight">System Log: {selectedRecord.date}</h2>
                             <span className="text-[10px] font-mono text-slate-500">TIMESTAMP: {new Date(selectedRecord.timestamp).toISOString()}</span>
                        </div>
                     </div>
                    <article className="prose prose-invert prose-slate max-w-none prose-sm">
                        {selectedRecord.reportMarkdown.split('\n').map((line, i) => {
                            // Simple manual markdown rendering for demo
                            if (line.startsWith('# ')) return <h1 key={i} className="text-2xl font-black text-white mb-6 uppercase tracking-tight">{line.replace('# ', '')}</h1>
                            if (line.startsWith('### ')) return <h3 key={i} className="text-sm font-black text-indigo-400 mt-6 mb-2 uppercase tracking-wider flex items-center gap-2 before:content-['//'] before:text-slate-600 before:mr-2">{line.replace('### ', '')}</h3>
                            if (line.startsWith('- ')) return <li key={i} className="ml-4 text-slate-300 text-xs font-mono leading-relaxed mb-1 list-disc marker:text-indigo-500">{line.replace('- ', '')}</li>
                            return <p key={i} className="text-slate-300 text-sm leading-relaxed mb-3">{line}</p>
                        })}
                    </article>
                </div>
            ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-600">
                    <BookOpen size={64} className="mb-4 opacity-20" />
                    <p className="font-mono text-xs">SELECT RECORD TO DECRYPT</p>
                </div>
            )}
        </div>
      </div>
    </div>
  );
};

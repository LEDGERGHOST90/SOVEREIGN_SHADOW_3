
import React, { useState, useEffect } from 'react';
import { DailyRecord, ModuleAOutput, Strategy } from '../types';
import { generateSovereignDailyReport } from '../services/geminiService';
import { useStrategies } from '../context/StrategyContext';
import { BookOpen, Loader2, Calendar, Save, Plus, RefreshCw } from 'lucide-react';

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

    if (!moduleAOutput) {
        setError("No Local Agent scan data found. Please run a scan in the Local Agent first to give the AI context.");
        setGenerating(false);
        return;
    }

    try {
      // Use latest 10 strategies
      const recentStrategies = strategies.slice(0, 10);
      const reportText = await generateSovereignDailyReport(moduleAOutput, recentStrategies);

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
    <div className="max-w-6xl mx-auto animate-fade-in">
      <div className="flex justify-between items-start mb-8">
        <div>
           <h1 className="text-3xl font-bold text-white flex items-center gap-3">
             <BookOpen className="text-indigo-500" />
             Module C <span className="text-slate-500 text-lg font-normal">| Daily Recorder</span>
           </h1>
           <p className="text-slate-400 mt-2">SovereignShadow's automated daily journal and system log.</p>
        </div>
        <button 
          onClick={handleGenerateReport}
          disabled={generating}
          className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold flex items-center gap-2 shadow-lg shadow-indigo-500/20 transition-all disabled:opacity-50"
        >
          {generating ? <Loader2 className="animate-spin" size={18} /> : <Plus size={18} />}
          Generate Today's Record
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-900/20 border border-red-900/50 rounded-lg text-red-300 mb-6">
            {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* SIDEBAR LIST */}
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 h-[600px] overflow-y-auto">
            <h3 className="text-slate-500 text-xs font-bold uppercase mb-4 flex items-center gap-2">
                <Calendar size={14} /> History
            </h3>
            <div className="space-y-2">
                {records.length === 0 && <div className="text-slate-600 text-sm text-center py-4">No records yet.</div>}
                {records.map(rec => (
                    <button
                        key={rec.id}
                        onClick={() => setSelectedRecord(rec)}
                        className={`w-full text-left p-3 rounded-lg border transition-all ${
                            selectedRecord?.id === rec.id 
                            ? 'bg-indigo-900/20 border-indigo-500/50 text-white' 
                            : 'bg-slate-800/50 border-transparent text-slate-400 hover:bg-slate-800'
                        }`}
                    >
                        <div className="font-bold text-sm">{rec.date}</div>
                        <div className="text-xs opacity-70 truncate">
                            {new Date(rec.timestamp).toLocaleTimeString()}
                        </div>
                    </button>
                ))}
            </div>
        </div>

        {/* MAIN CONTENT RENDERER */}
        <div className="lg:col-span-3 bg-slate-900 border border-slate-800 rounded-xl p-8 min-h-[600px]">
            {selectedRecord ? (
                <article className="prose prose-invert prose-slate max-w-none">
                    {selectedRecord.reportMarkdown.split('\n').map((line, i) => {
                        // Simple manual markdown rendering for demo
                        if (line.startsWith('# ')) return <h1 key={i} className="text-3xl font-bold text-white mb-6 border-b border-slate-800 pb-4">{line.replace('# ', '')}</h1>
                        if (line.startsWith('### ')) return <h3 key={i} className="text-xl font-bold text-indigo-400 mt-8 mb-3">{line.replace('### ', '')}</h3>
                        if (line.startsWith('- ')) return <li key={i} className="ml-4 text-slate-300">{line.replace('- ', '')}</li>
                        return <p key={i} className="text-slate-300 leading-relaxed mb-2">{line}</p>
                    })}
                </article>
            ) : (
                <div className="h-full flex flex-col items-center justify-center text-slate-600">
                    <BookOpen size={48} className="mb-4 opacity-20" />
                    <p>Select a record to view or generate a new one.</p>
                </div>
            )}
        </div>
      </div>
    </div>
  );
};

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStrategies } from '../context/StrategyContext';
import { analyzeTranscript, generateFullStrategyPackage, transcribeAudio, synthesizeMultiAnalysis } from '../services/geminiService';
import { Loader2, Youtube, FileText, PlayCircle, Sparkles, Zap, BrainCircuit, ExternalLink, Copy, Music, UploadCloud, Plus, Trash2, Layers, CheckCircle2, Command, AlertCircle } from 'lucide-react';
import { Strategy } from '../types';

const SAMPLE_TRANSCRIPT = `
Here is a simple scalp trading strategy for Bitcoin on the 5-minute timeframe.
First, we use the Exponential Moving Average (EMA) 200 to determine the trend. If price is above EMA 200, we only look for longs.
Second, we add the RSI indicator. We wait for the RSI to dip below 30 (oversold) while price is above the 200 EMA.
Entry Trigger: Once RSI crosses back above 30, we enter a long position.
Stop Loss: Place the stop loss slightly below the recent swing low.
Take Profit: We aim for a 1.5 Risk to Reward ratio.
This strategy works best during the New York and London overlap sessions.
Avoid trading this during high impact news events like FOMC or CPI.
The win rate historically is around 60% if you follow the rules strictly.
`;

export const Analyzer: React.FC = () => {
  const navigate = useNavigate();
  const { addStrategy, updateStrategy } = useStrategies();
  
  // Batch Mode State
  const [developerName, setDeveloperName] = useState('');
  const [sources, setSources] = useState<any[]>([
      { id: '1', url: '', content: '', status: 'idle' }
  ]);
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isForging, setIsForging] = useState(false);
  const [progressStep, setProgressStep] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<'gemini-2.5-flash' | 'gemini-3-pro-preview'>('gemini-3-pro-preview');
  
  // Audio State
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isTranscribing, setIsTranscribing] = useState(false);

  // --- SOURCE MANAGEMENT ---
  const addSource = () => {
      setSources(prev => [...prev, { id: crypto.randomUUID(), url: '', content: '', status: 'idle' }]);
  };

  const removeSource = (id: string) => {
      if (sources.length > 1) {
          setSources(prev => prev.filter(s => s.id !== id));
      }
  };

  const updateSource = (id: string, field: 'url' | 'content', value: string) => {
      setSources(prev => prev.map(s => s.id === id ? { ...s, [field]: value } : s));
  };

  const loadSample = (id: string) => {
      updateSource(id, 'url', 'https://www.youtube.com/watch?v=sample123');
      updateSource(id, 'content', SAMPLE_TRANSCRIPT.trim());
  };

  // --- AUDIO HANDLERS ---
  const handleAudioDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        validateAndSetAudio(e.dataTransfer.files[0]);
    }
  };

  const handleAudioSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
        validateAndSetAudio(e.target.files[0]);
    }
  };

  const validateAndSetAudio = (file: File) => {
    const validTypes = ['audio/mpeg', 'audio/wav', 'audio/x-m4a', 'audio/mp4'];
    const ext = file.name.split('.').pop()?.toLowerCase();
    const validExts = ['mp3', 'wav', 'm4a', 'mp4'];
    
    if (validTypes.includes(file.type) || (ext && validExts.includes(ext))) {
        setAudioFile(file);
        setError(null);
    } else {
        setError("Invalid file type. Please upload .mp3, .wav, or .m4a");
    }
  };

  const handleTranscribe = async () => {
    if (!audioFile) return;
    setIsTranscribing(true);
    setError(null);
    try {
        const text = await transcribeAudio(audioFile, 'gemini-2.5-flash');
        const newSourceId = crypto.randomUUID();
        setSources(prev => [...prev, { id: newSourceId, url: 'Audio Upload', content: text, status: 'idle' }]);
        setAudioFile(null); 
    } catch (err: any) {
        setError(err.message || "Transcription failed");
    } finally {
        setIsTranscribing(false);
    }
  };

  // --- ANALYSIS LOGIC ---
  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    const validSources = sources.filter(s => s.content.trim().length > 0);
    if (validSources.length === 0) {
        setError("Please provide at least one transcript.");
        return;
    }

    setIsAnalyzing(true);
    setError(null);
    setProgressStep('Initializing G.I.O Kernel...');

    try {
      let analysis;
      let transcriptSnippet = "";

      if (validSources.length === 1) {
          setProgressStep('Analyzing single strategy source...');
          analysis = await analyzeTranscript(validSources[0].content, selectedModel);
          transcriptSnippet = validSources[0].content;
      } else {
          setProgressStep(`Synthesizing master strategy from ${validSources.length} sources...`);
          const devName = developerName || "Unknown Developer";
          analysis = await synthesizeMultiAnalysis(devName, validSources.map(s => ({ url: s.url, content: s.content })), selectedModel);
          transcriptSnippet = `Merged Analysis of ${validSources.length} videos from ${devName}.`;
      }
      
      setProgressStep('Strategy Extracted. Preparing artifacts...');
      
      const newStrategy: Strategy = {
        id: crypto.randomUUID(),
        title: analysis.name,
        videoUrl: validSources[0].url || 'Multi-Source',
        transcriptSnippet: transcriptSnippet,
        analysis,
        createdAt: Date.now(),
        model: selectedModel,
        pipelineStatus: 'draft' 
      };

      addStrategy(newStrategy);
      setIsAnalyzing(false);

      setIsForging(true);
      setProgressStep('AURORA: Forging Python & PineScript...');
      try {
        const artifacts = await generateFullStrategyPackage(analysis, 'gemini-3-pro-preview');
        updateStrategy(newStrategy.id, { artifacts });
      } catch (forgeError) {
        console.error("Auto-Forge failed:", forgeError);
      }
      
      setIsForging(false);
      navigate(`/strategy/${newStrategy.id}`);
      
    } catch (err: any) {
      setError(err.message || "Failed to analyze content. Please check your API key and quota.");
      setIsAnalyzing(false);
      setIsForging(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto animate-fade-in pb-16">
      
      {/* HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-end gap-6 border-b border-slate-800/60 pb-6 mb-8">
        <div>
          <h1 className="text-3xl font-black text-white tracking-tighter uppercase italic flex items-center gap-3">
             <Layers className="text-cyan-400" size={32} /> 
             Strategy <span className="text-slate-500 not-italic text-2xl">| Synthesis Engine</span>
          </h1>
          <p className="text-slate-400 font-mono-tech text-xs mt-2 max-w-2xl border-l-2 border-cyan-500/30 pl-3">
            Ingest unstructured intelligence. Forge executable Alpha.
          </p>
        </div>
      </div>

      <form onSubmit={handleAnalyze} className="space-y-6">
        
        {/* TOP ROW: CONFIG */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* MODEL SELECTOR */}
            <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                    type="button"
                    onClick={() => setSelectedModel('gemini-2.5-flash')}
                    className={`relative p-4 rounded-xl border-2 transition-all text-left overflow-hidden group ${
                    selectedModel === 'gemini-2.5-flash'
                        ? 'bg-slate-900 border-cyan-500 shadow-[0_0_20px_rgba(6,182,212,0.15)]'
                        : 'bg-black border-slate-800 text-slate-500 hover:border-slate-600'
                    }`}
                >
                    <div className="flex items-center gap-3 mb-2">
                         <div className={`p-2 rounded-lg ${selectedModel === 'gemini-2.5-flash' ? 'bg-cyan-500 text-black' : 'bg-slate-800 text-slate-400'}`}>
                             <Zap size={20} />
                         </div>
                         <div className="font-black text-sm uppercase tracking-wider">Flash Runner</div>
                    </div>
                    <div className="text-[10px] font-mono-tech opacity-80">
                        Low Latency / Single Source Analysis
                    </div>
                </button>

                <button
                    type="button"
                    onClick={() => setSelectedModel('gemini-3-pro-preview')}
                    className={`relative p-4 rounded-xl border-2 transition-all text-left overflow-hidden group ${
                    selectedModel === 'gemini-3-pro-preview'
                        ? 'bg-slate-900 border-purple-500 shadow-[0_0_20px_rgba(168,85,247,0.15)]'
                        : 'bg-black border-slate-800 text-slate-500 hover:border-slate-600'
                    }`}
                >
                    <div className="flex items-center gap-3 mb-2">
                         <div className={`p-2 rounded-lg ${selectedModel === 'gemini-3-pro-preview' ? 'bg-purple-500 text-white' : 'bg-slate-800 text-slate-400'}`}>
                             <BrainCircuit size={20} />
                         </div>
                         <div className="font-black text-sm uppercase tracking-wider">Pro Logic</div>
                    </div>
                    <div className="text-[10px] font-mono-tech opacity-80">
                         Deep Reasoning / Multi-Source Synthesis
                    </div>
                </button>
            </div>

            {/* IDENTITY INPUT */}
            <div className="bg-black border border-slate-800 rounded-xl p-4">
                <label className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-2 block">
                  Data Origin / Developer Identity
                </label>
                <div className="relative">
                    <Command className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" size={14} />
                    <input
                        type="text"
                        className="w-full bg-slate-900 border border-slate-700 rounded-lg pl-9 pr-4 py-2.5 text-xs font-mono text-cyan-300 focus:outline-none focus:border-cyan-500 transition-all placeholder-slate-700"
                        placeholder="e.g. 'The Trading Nerd'"
                        value={developerName}
                        onChange={(e) => setDeveloperName(e.target.value)}
                    />
                </div>
            </div>
        </div>

        {/* AUDIO INGESTION */}
        <div 
            className={`border-2 border-dashed rounded-xl p-6 transition-all text-center relative overflow-hidden group ${
                audioFile ? 'border-cyan-500 bg-cyan-950/10' : 'border-slate-800 bg-slate-900/50 hover:border-slate-600'
            }`}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleAudioDrop}
        >
            <div className="absolute inset-0 bg-scanline opacity-10 pointer-events-none"></div>
            {!audioFile ? (
                <div className="flex flex-col items-center justify-center gap-3 relative z-10">
                    <div className="p-3 bg-slate-900 border border-slate-700 rounded-full text-slate-400 group-hover:text-cyan-400 group-hover:border-cyan-500 transition-all">
                        <Music size={20} />
                    </div>
                    <div>
                        <div className="text-sm font-bold text-slate-300">
                            Audio Intelligence Ingest
                        </div>
                        <div className="text-[10px] text-slate-500 font-mono mt-1">
                            DRAG & DROP .MP3 / .M4A
                        </div>
                    </div>
                    <label className="mt-2 text-[10px] text-cyan-500 font-bold uppercase tracking-widest cursor-pointer hover:underline">
                        [ Browse Local Drive ]
                        <input type="file" className="hidden" accept=".mp3,audio/*" onChange={handleAudioSelect} />
                    </label>
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center gap-4 relative z-10">
                    <div className="flex items-center gap-3 text-cyan-300 font-mono text-sm bg-slate-900 px-4 py-2 rounded border border-cyan-900">
                        <FileText size={16} />
                        {audioFile.name}
                    </div>
                    <div className="flex gap-2">
                        <button 
                            type="button"
                            onClick={handleTranscribe}
                            disabled={isTranscribing}
                            className="px-6 py-2 bg-cyan-600 hover:bg-cyan-500 text-black font-black text-xs uppercase tracking-widest clip-corner flex items-center gap-2 disabled:opacity-50"
                        >
                            {isTranscribing ? <Loader2 className="animate-spin" size={14} /> : <UploadCloud size={14} />}
                            {isTranscribing ? 'Processing Waveforms...' : 'Transcribe'}
                        </button>
                        <button type="button" onClick={() => setAudioFile(null)} className="text-xs text-slate-500 hover:text-red-400 underline font-mono">Cancel</button>
                    </div>
                </div>
            )}
        </div>

        {/* SOURCES TERMINAL */}
        <div className="space-y-4">
            <div className="flex items-center justify-between px-2">
                <h3 className="text-white font-bold text-sm uppercase tracking-widest flex items-center gap-2">
                    <Youtube className="text-red-500" size={16} /> Signal Sources
                </h3>
                <button type="button" onClick={addSource} className="text-[10px] font-black uppercase tracking-widest bg-slate-800 hover:bg-slate-700 text-white px-3 py-1.5 rounded flex items-center gap-1 transition-colors border border-slate-700">
                    <Plus size={12} /> Add Stream
                </button>
            </div>

            {sources.map((source, index) => (
                <div key={source.id} className="bg-black border border-slate-800 p-4 rounded-xl relative group hover:border-slate-600 transition-colors">
                    <div className="absolute top-4 right-4 flex gap-2">
                         <button 
                            type="button"
                            onClick={() => loadSample(source.id)}
                            className="text-[9px] font-mono text-cyan-500 hover:text-cyan-300 flex items-center gap-1 bg-cyan-950/30 px-2 py-1 rounded border border-cyan-900/50"
                        >
                            <PlayCircle size={10} /> LOAD_SAMPLE_DATA
                        </button>
                        {sources.length > 1 && (
                            <button type="button" onClick={() => removeSource(source.id)} className="text-slate-600 hover:text-red-500 p-1 transition-colors">
                                <Trash2 size={14} />
                            </button>
                        )}
                    </div>

                    <div className="grid gap-3">
                        <div className="flex items-center gap-3">
                            <span className="bg-slate-800 text-slate-500 px-2 py-1 rounded text-[10px] font-mono font-bold">SRC_{index + 1}</span>
                            <input
                                type="url"
                                className="flex-1 bg-slate-900 border border-slate-800 rounded px-3 py-1.5 text-xs text-white placeholder-slate-700 focus:outline-none focus:border-cyan-500/50 font-mono transition-all"
                                placeholder="https://youtube.com/..."
                                value={source.url}
                                onChange={(e) => updateSource(source.id, 'url', e.target.value)}
                            />
                        </div>
                        <textarea
                            className="w-full h-32 bg-slate-900 border border-slate-800 rounded-lg px-4 py-3 text-slate-300 placeholder-slate-700 focus:outline-none focus:border-cyan-500/50 transition-all font-mono text-[11px] leading-relaxed custom-scrollbar"
                            placeholder="Paste raw transcript or notes here..."
                            value={source.content}
                            onChange={(e) => updateSource(source.id, 'content', e.target.value)}
                            required
                        />
                    </div>
                </div>
            ))}
        </div>

        {error && (
          <div className="p-4 bg-red-950/20 border border-red-500/30 rounded-lg text-red-400 text-xs font-mono flex items-center gap-3 animate-pulse">
            <AlertCircle size={16} />
            <span>ERROR: {error}</span>
          </div>
        )}

        <button
          type="submit"
          disabled={isAnalyzing || isForging}
          className={`
            w-full py-5 clip-corner font-black text-sm uppercase tracking-[0.2em] transition-all flex items-center justify-center gap-3
            ${isAnalyzing || isForging
              ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
              : sources.length > 1
                ? 'bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-black shadow-[0_0_30px_rgba(6,182,212,0.3)]'
                : 'bg-cyan-600 hover:bg-cyan-500 text-black shadow-[0_0_20px_rgba(6,182,212,0.3)]'
            }
          `}
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="animate-spin" size={18} />
              <div className="flex flex-col items-start leading-none">
                  <span>PROCESSING STREAM...</span>
                  <span className="text-[9px] font-mono normal-case opacity-70 mt-1">{progressStep}</span>
              </div>
            </>
          ) : isForging ? (
             <>
              <Loader2 className="animate-spin" size={18} />
              <div className="flex flex-col items-start leading-none">
                  <span>FORGING ARTIFACTS...</span>
                  <span className="text-[9px] font-mono normal-case opacity-70 mt-1">{progressStep}</span>
              </div>
            </>
          ) : (
            <>
              {sources.length > 1 ? <Layers size={18} /> : <Sparkles size={18} />}
              {sources.length > 1 ? 'SYNTHESIZE MASTER STRATEGY' : 'ANALYZE & FORGE CODE'}
            </>
          )}
        </button>
      </form>
    </div>
  );
};
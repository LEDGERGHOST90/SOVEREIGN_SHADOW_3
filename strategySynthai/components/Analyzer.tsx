
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStrategies } from '../context/StrategyContext';
import { analyzeTranscript, generateFullStrategyPackage, transcribeAudio } from '../services/geminiService';
import { Loader2, Youtube, FileText, PlayCircle, Sparkles, Zap, BrainCircuit, ExternalLink, Copy, Music, UploadCloud } from 'lucide-react';
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
  
  const [videoUrl, setVideoUrl] = useState('');
  const [transcript, setTranscript] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isForging, setIsForging] = useState(false); // New state for forging artifacts
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<'gemini-2.5-flash' | 'gemini-3-pro-preview'>('gemini-2.5-flash');
  
  // Audio State
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [isTranscribing, setIsTranscribing] = useState(false);

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
    // Check extension as fallback
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
        const text = await transcribeAudio(audioFile, selectedModel);
        setTranscript(text);
        setAudioFile(null); // Clear file after success
    } catch (err: any) {
        setError(err.message || "Transcription failed");
    } finally {
        setIsTranscribing(false);
    }
  };

  // --- ANALYSIS HANDLER (UPDATED FOR AUTO-FORGE) ---
  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!transcript.trim()) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      // 1. EXTRACT STRATEGY (GIO)
      const analysis = await analyzeTranscript(transcript, selectedModel);
      
      const newStrategy: Strategy = {
        id: crypto.randomUUID(),
        title: analysis.name,
        videoUrl,
        transcriptSnippet: transcript,
        analysis,
        createdAt: Date.now(),
        model: selectedModel,
        pipelineStatus: 'draft' // Start as draft
      };

      addStrategy(newStrategy);
      setIsAnalyzing(false);

      // 2. AUTO-FORGE ARTIFACTS (AURORA)
      setIsForging(true);
      try {
        const artifacts = await generateFullStrategyPackage(analysis, 'gemini-3-pro-preview');
        // Update the strategy in context with artifacts
        updateStrategy(newStrategy.id, { artifacts });
      } catch (forgeError) {
        console.error("Auto-Forge failed (continuing without artifacts):", forgeError);
        // We continue even if forge fails, user can retry manually in details
      }
      
      setIsForging(false);
      navigate(`/strategy/${newStrategy.id}`);
      
    } catch (err: any) {
      setError(err.message || "Failed to analyze content. Please check your API key and quota.");
      setIsAnalyzing(false);
    }
  };

  const loadSample = () => {
    setVideoUrl('https://www.youtube.com/watch?v=sample123');
    setTranscript(SAMPLE_TRANSCRIPT.trim());
  };

  const openNoteGPT = () => {
    window.open('https://notegpt.io/youtube-transcript-generator', '_blank');
  };

  return (
    <div className="max-w-4xl mx-auto animate-fade-in pb-12">
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-white mb-3">AI Strategy Scout</h1>
        <p className="text-slate-400 max-w-2xl mx-auto text-lg">
          Synthesize YouTube strategies into actionable code.
        </p>
      </div>

      <form onSubmit={handleAnalyze} className="space-y-6 bg-slate-900 p-6 md:p-8 rounded-2xl border border-slate-800 shadow-xl">
        
        {/* Model Selection */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-1 bg-slate-800/50 rounded-xl">
          <button
            type="button"
            onClick={() => setSelectedModel('gemini-2.5-flash')}
            className={`flex items-center gap-3 p-4 rounded-lg border transition-all text-left ${
              selectedModel === 'gemini-2.5-flash'
                ? 'bg-indigo-600/20 border-indigo-500 text-white'
                : 'bg-transparent border-transparent text-slate-400 hover:bg-slate-800'
            }`}
          >
            <div className={`p-2 rounded-full ${selectedModel === 'gemini-2.5-flash' ? 'bg-indigo-500 text-white' : 'bg-slate-700'}`}>
              <Zap size={20} />
            </div>
            <div>
              <div className="font-semibold">Flash (Fast)</div>
              <div className="text-xs opacity-80">Best for single videos & quick summaries</div>
            </div>
          </button>

          <button
            type="button"
            onClick={() => setSelectedModel('gemini-3-pro-preview')}
            className={`flex items-center gap-3 p-4 rounded-lg border transition-all text-left ${
              selectedModel === 'gemini-3-pro-preview'
                ? 'bg-purple-600/20 border-purple-500 text-white'
                : 'bg-transparent border-transparent text-slate-400 hover:bg-slate-800'
            }`}
          >
            <div className={`p-2 rounded-full ${selectedModel === 'gemini-3-pro-preview' ? 'bg-purple-500 text-white' : 'bg-slate-700'}`}>
              <BrainCircuit size={20} />
            </div>
            <div>
              <div className="font-semibold">Pro (Deep Logic)</div>
              <div className="text-xs opacity-80">Best for complex reasoning & multiple sources</div>
            </div>
          </button>
        </div>

        {/* AUDIO DROPZONE */}
        <div 
            className={`border-2 border-dashed rounded-xl p-6 transition-all text-center ${
                audioFile ? 'border-indigo-500 bg-indigo-900/10' : 'border-slate-700 bg-slate-800/30 hover:border-slate-500'
            }`}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleAudioDrop}
        >
            {!audioFile ? (
                <div className="flex flex-col items-center justify-center gap-2">
                    <div className="p-3 bg-slate-800 rounded-full text-slate-400">
                        <Music size={24} />
                    </div>
                    <div className="text-sm font-medium text-slate-300">
                        Drop Audio File (.mp3, .m4a) to Transcribe
                    </div>
                    <label className="text-xs text-indigo-400 cursor-pointer hover:underline">
                        or click to browse
                        <input type="file" className="hidden" accept=".mp3,audio/*" onChange={handleAudioSelect} />
                    </label>
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center gap-3">
                    <div className="flex items-center gap-2 text-indigo-300 font-medium">
                        <FileText size={18} />
                        {audioFile.name}
                    </div>
                    <button 
                        type="button"
                        onClick={handleTranscribe}
                        disabled={isTranscribing}
                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm flex items-center gap-2 disabled:opacity-50"
                    >
                        {isTranscribing ? <Loader2 className="animate-spin" size={14} /> : <UploadCloud size={14} />}
                        {isTranscribing ? 'Transcribing...' : 'Start Transcription'}
                    </button>
                    <button type="button" onClick={() => setAudioFile(null)} className="text-xs text-slate-500 hover:text-slate-400">Cancel</button>
                </div>
            )}
        </div>

        {/* Input Fields */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Video URL <span className="text-slate-500 font-normal">(Optional, for reference)</span>
            </label>
            <input
              type="url"
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              placeholder="https://youtube.com/..."
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-slate-300">
                Transcript Content
              </label>
              <button 
                type="button"
                onClick={loadSample}
                className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 bg-indigo-900/30 px-2 py-1 rounded"
              >
                <PlayCircle size={12} /> Load Sample
              </button>
            </div>
            <textarea
              className="w-full h-64 bg-slate-800 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all font-mono text-sm leading-relaxed"
              placeholder="Paste transcript from NoteGPT here..."
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              required
            />
            <div className="flex justify-between items-center mt-2 text-xs text-slate-500">
              <span className="flex items-center gap-1 text-green-500/80">
                <Sparkles size={12} /> Auto-cleaning enabled
              </span>
              <span>{transcript.length} chars</span>
            </div>
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-900/20 border border-red-900/50 rounded-lg text-red-400 text-sm flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-red-500 flex-shrink-0"></div>
            <span>{error}</span>
          </div>
        )}

        <button
          type="submit"
          disabled={isAnalyzing || isForging || !transcript}
          className={`
            w-full flex items-center justify-center gap-3 py-4 rounded-xl font-bold text-lg text-white transition-all shadow-lg
            ${isAnalyzing || isForging || !transcript
              ? 'bg-slate-700 cursor-not-allowed opacity-50'
              : selectedModel === 'gemini-3-pro-preview' 
                ? 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 shadow-purple-500/20'
                : 'bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 shadow-indigo-500/20'
            }
          `}
        >
          {isAnalyzing ? (
            <>
              <Loader2 className="animate-spin" size={24} />
              GIO: Analyzing Strategy...
            </>
          ) : isForging ? (
             <>
              <Loader2 className="animate-spin text-purple-400" size={24} />
              AURORA: Forging Sovereign Artifacts...
            </>
          ) : (
            <>
              <Sparkles size={20} />
              Extract Strategy & Forge Artifacts
            </>
          )}
        </button>
      </form>
    </div>
  );
};

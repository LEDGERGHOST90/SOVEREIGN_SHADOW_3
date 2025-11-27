
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useStrategies } from '../context/StrategyContext';
import { analyzeTranscript } from '../services/geminiService';
import { Loader2, Youtube, FileText, PlayCircle, Sparkles, Zap, BrainCircuit, ExternalLink, Copy } from 'lucide-react';

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
  const { addStrategy } = useStrategies();
  
  const [videoUrl, setVideoUrl] = useState('');
  const [transcript, setTranscript] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<'gemini-2.5-flash' | 'gemini-3-pro-preview'>('gemini-2.5-flash');

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!transcript.trim()) return;

    setIsAnalyzing(true);
    setError(null);

    try {
      const analysis = await analyzeTranscript(transcript, selectedModel);
      
      const newStrategy = {
        id: crypto.randomUUID(),
        title: analysis.name,
        videoUrl,
        transcriptSnippet: transcript,
        analysis,
        createdAt: Date.now(),
        model: selectedModel,
      };

      addStrategy(newStrategy);
      navigate(`/strategy/${newStrategy.id}`);
    } catch (err) {
      setError("Failed to analyze content. Please check your API key and try again.");
    } finally {
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
    <div className="max-w-4xl mx-auto animate-fade-in">
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

        {/* Import Workflow Helper */}
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl border border-slate-700/50 overflow-hidden">
          <div className="p-4 border-b border-slate-700/50 bg-slate-800/30 flex items-center gap-2">
            <Youtube className="text-red-500" size={18} />
            <h3 className="font-semibold text-white text-sm">Strategy Extraction Pipeline</h3>
          </div>
          
          <div className="p-4 grid md:grid-cols-2 gap-4 text-sm">
             <div className="space-y-2">
                <div className="text-slate-400 font-medium flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-slate-700 text-white flex items-center justify-center text-xs">1</span>
                  Get Transcript
                </div>
                <p className="text-slate-500 text-xs">
                  Use NoteGPT to extract text from any YouTube video URL.
                </p>
                <button 
                  type="button" 
                  onClick={openNoteGPT}
                  className="flex items-center gap-2 text-indigo-400 hover:text-indigo-300 hover:underline text-xs font-medium"
                >
                  <ExternalLink size={12} /> Open NoteGPT Generator
                </button>
             </div>
             
             <div className="space-y-2">
                <div className="text-slate-400 font-medium flex items-center gap-2">
                  <span className="w-5 h-5 rounded-full bg-slate-700 text-white flex items-center justify-center text-xs">2</span>
                  Paste & Analyze
                </div>
                <p className="text-slate-500 text-xs">
                  Paste the raw text below. Our AI will auto-clean timestamps (e.g., [12:00]) and extract the alpha.
                </p>
             </div>
          </div>
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
            <div className="w-2 h-2 rounded-full bg-red-500"></div>
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={isAnalyzing || !transcript}
          className={`
            w-full flex items-center justify-center gap-3 py-4 rounded-xl font-bold text-lg text-white transition-all shadow-lg
            ${isAnalyzing || !transcript
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
              Analyzing with {selectedModel === 'gemini-3-pro-preview' ? 'Gemini Pro' : 'Gemini Flash'}...
            </>
          ) : (
            <>
              <Sparkles size={20} />
              Extract Strategy & Add to Knowledge Graph
            </>
          )}
        </button>
      </form>
    </div>
  );
};


import React, { useState } from 'react';
import { Shield, Crosshair, Layers, Brain, Copy, CheckCircle2, User, Terminal, Hexagon } from 'lucide-react';

interface Protocol {
  id: string;
  name: string;
  identity: string;
  line: string;
  keywords: string[];
  angle: string;
  color: string;
  borderColor: string;
  glowColor: string;
  icon: React.ReactNode;
}

export const SovereignProtocols: React.FC = () => {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const protocols: Protocol[] = [
    {
      id: 'vault',
      name: 'THE VAULT',
      identity: 'Guardian of Capital',
      line: "Architect of robust portfolios. My focus is compounding wealth through stringent risk management. Capital preservation is the only metric that matters.",
      keywords: ['Preservation', 'Stability', 'Defensive'],
      angle: 'Long-term wealth management.',
      color: 'text-green-400',
      borderColor: 'border-green-500',
      glowColor: 'shadow-green-500/20',
      icon: <Shield size={32} />
    },
    {
      id: 'sniper',
      name: 'THE SNIPER',
      identity: 'Precision Executioner',
      line: "I wait patiently for optimal entry points, executing with surgical precision. One shot, one kill. Quality over quantity, always.",
      keywords: ['Precision', 'Patience', 'Surgical'],
      angle: 'High-conviction swing trading.',
      color: 'text-red-500',
      borderColor: 'border-red-500',
      glowColor: 'shadow-red-500/20',
      icon: <Crosshair size={32} />
    },
    {
      id: 'ladder',
      name: 'THE LADDER',
      identity: 'Systematic Scaler',
      line: "I de-risk by scaling positions incrementally. I adapt to market flow with a structured approach to distribution. Building positions, brick by brick.",
      keywords: ['Systematic', 'Scaling', 'Adaptive'],
      angle: 'DCA / Grid Trading systems.',
      color: 'text-blue-400',
      borderColor: 'border-blue-500',
      glowColor: 'shadow-blue-500/20',
      icon: <Layers size={32} />
    },
    {
      id: 'menace',
      name: 'THE MENACE',
      identity: 'Algorithmic Disruptor',
      line: "Proprietary algorithms drive my edge. I leverage recursive intelligence to exploit inefficiencies at machine speed. Evolve or die.",
      keywords: ['Algorithmic', 'HFT', 'Autonomous'],
      angle: 'Quantitative / AI strategies.',
      color: 'text-purple-400',
      borderColor: 'border-purple-500',
      glowColor: 'shadow-purple-500/20',
      icon: <Brain size={32} />
    }
  ];

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="max-w-7xl mx-auto animate-fade-in pb-12">
      
      {/* HEADER */}
      <div className="flex flex-col md:flex-row justify-between items-end gap-6 border-b border-slate-800/60 pb-6 mb-8">
        <div>
          <h1 className="text-3xl font-black text-white tracking-tighter uppercase italic flex items-center gap-3">
             <Hexagon className="text-indigo-500" size={32} /> 
             Sovereign <span className="text-slate-500 not-italic text-2xl">| Protocols</span>
          </h1>
          <p className="text-slate-400 font-mono-tech text-xs mt-2 max-w-2xl border-l-2 border-indigo-500/30 pl-3">
            Archetypal Identities. Select your trading stance.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {protocols.map((p) => (
          <div key={p.id} className={`bg-black border-2 ${p.borderColor} rounded-2xl p-6 shadow-2xl ${p.glowColor} relative overflow-hidden group hover:-translate-y-2 transition-transform duration-300`}>
            
            {/* Background Texture */}
            <div className={`absolute top-0 right-0 p-8 opacity-10 ${p.color} -mr-8 -mt-8 rotate-12 transition-transform group-hover:rotate-0 group-hover:scale-110`}>
                {p.icon}
            </div>

            {/* Header */}
            <div className="relative z-10 mb-6 text-center">
              <div className={`w-16 h-16 mx-auto mb-4 bg-slate-900 rounded-full flex items-center justify-center border-2 ${p.borderColor} shadow-[0_0_15px_currentColor] ${p.color}`}>
                {p.icon}
              </div>
              <h3 className={`font-black text-2xl uppercase tracking-tighter ${p.color}`}>{p.name}</h3>
              <div className="text-[10px] text-slate-400 font-mono uppercase tracking-widest">{p.identity}</div>
            </div>

            {/* Profile Line */}
            <div className="relative z-10 bg-slate-900/80 rounded border border-slate-800 p-4 mb-4 min-h-[100px] flex items-center">
              <p className="text-slate-300 text-xs leading-relaxed font-medium italic text-center">
                "{p.line}"
              </p>
            </div>

            {/* Footer / Keywords */}
            <div className="relative z-10 space-y-3">
               <div className="flex flex-wrap justify-center gap-2">
                 {p.keywords.map((kw, i) => (
                   <span key={i} className="px-2 py-1 bg-black text-slate-400 text-[9px] font-bold uppercase tracking-wide border border-slate-800 rounded">
                     {kw}
                   </span>
                 ))}
               </div>
               
               <button 
                 onClick={() => handleCopy(p.line, p.id)}
                 className={`w-full py-3 clip-corner font-black text-[10px] uppercase tracking-widest flex items-center justify-center gap-2 transition-all ${copiedId === p.id ? 'bg-green-600 text-black' : 'bg-slate-800 text-white hover:bg-slate-700'}`}
               >
                 {copiedId === p.id ? <CheckCircle2 size={12} /> : <Copy size={12} />}
                 {copiedId === p.id ? 'COPIED IDENTITY' : 'COPY PROTOCOL'}
               </button>
            </div>

          </div>
        ))}
      </div>
    </div>
  );
};

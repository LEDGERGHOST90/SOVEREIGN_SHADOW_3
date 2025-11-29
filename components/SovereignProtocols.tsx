
import React, { useState } from 'react';
import { Shield, Crosshair, Layers, Brain, Copy, CheckCircle2, User, Terminal } from 'lucide-react';

interface Protocol {
  id: string;
  name: string;
  identity: string;
  line: string;
  keywords: string[];
  angle: string;
  color: string;
  borderColor: string;
  icon: React.ReactNode;
}

export const SovereignProtocols: React.FC = () => {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const protocols: Protocol[] = [
    {
      id: 'vault',
      name: 'THE VAULT OPERATOR',
      identity: 'The Guardian of Capital',
      line: "Architect of robust portfolios. My focus is compounding wealth through stringent risk management and strategic asset allocation. I prioritize capital preservation above all, seeking consistent, calculated growth in all market cycles.",
      keywords: ['Preservation', 'Stability', 'Long-Term', 'Allocation', 'Risk-Adjusted', 'Defensive'],
      angle: 'Ideal for long-term investors, wealth managers, or those emphasizing capital safety.',
      color: 'text-green-400',
      borderColor: 'border-green-500/30',
      icon: <Shield size={24} />
    },
    {
      id: 'sniper',
      name: 'THE SNIPER SPECIALIST',
      identity: 'The Precision Executioner',
      line: "Dedicated to high-probability setups. I wait patiently for optimal entry points, executing with surgical precision and strict stop-loss protocols. Quality over quantity, always.",
      keywords: ['Precision', 'Patience', 'Opportunistic', 'High-Conviction', 'Surgical'],
      angle: 'Suited for swing traders, day traders focused on specific patterns, or strict technical analysis.',
      color: 'text-red-400',
      borderColor: 'border-red-500/30',
      icon: <Crosshair size={24} />
    },
    {
      id: 'ladder',
      name: 'THE LADDER BUILDER',
      identity: 'The Systematic Scaler',
      line: "Master of systematic entries and exits. I de-risk by scaling positions incrementally, adapting to market flow with a structured approach to dollar-cost averaging and distribution. Building positions, brick by brick.",
      keywords: ['Systematic', 'Scaling', 'Incremental', 'DCA/DSA', 'Adaptive', 'Phased'],
      angle: 'Perfect for managing larger capital, averaging into positions, or grid/range trading.',
      color: 'text-blue-400',
      borderColor: 'border-blue-500/30',
      icon: <Layers size={24} />
    },
    {
      id: 'menace',
      name: 'THE MENACE INNOVATOR',
      identity: 'The Algorithmic Disruptor',
      line: "Proprietary algorithms drive my edge. I leverage advanced computational power and recursive intelligence to identify and exploit market inefficiencies, constantly adapting and innovating at machine speed. My strategies evolve as fast as the market does.",
      keywords: ['Algorithmic', 'Disruptive', 'AI-Driven', 'Quantitative', 'HFT', 'Autonomous'],
      angle: 'For quant traders, algo developers, or those pushing boundaries with AI/ML.',
      color: 'text-purple-400',
      borderColor: 'border-purple-500/30',
      icon: <Brain size={24} />
    }
  ];

  const handleCopy = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="max-w-6xl mx-auto animate-fade-in pb-12">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white flex items-center gap-3">
          <User className="text-indigo-500" />
          Sovereign Protocols <span className="text-slate-500 text-lg font-normal">| Trader Profiles</span>
        </h1>
        <p className="text-slate-400 mt-2 max-w-2xl">
          Archetypal identities for the SovereignShadow ecosystem. Copy and remix these personas to define your trading stance.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {protocols.map((p) => (
          <div key={p.id} className={`bg-slate-900 border ${p.borderColor} rounded-xl p-6 shadow-lg transition-all hover:scale-[1.01]`}>
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={`p-3 rounded-lg bg-slate-800 ${p.color}`}>
                  {p.icon}
                </div>
                <div>
                  <h3 className={`font-bold text-lg ${p.color}`}>{p.name}</h3>
                  <div className="text-slate-400 text-sm italic">{p.identity}</div>
                </div>
              </div>
            </div>

            {/* Profile Line */}
            <div className="bg-black/30 rounded-lg p-4 border border-slate-800 mb-4 relative group">
              <p className="text-slate-200 text-sm leading-relaxed font-medium">
                "{p.line}"
              </p>
              <button
                onClick={() => handleCopy(p.line, p.id)}
                className="absolute top-2 right-2 p-2 bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white rounded-md transition-colors opacity-0 group-hover:opacity-100"
                title="Copy Profile Line"
              >
                {copiedId === p.id ? <CheckCircle2 size={16} className="text-green-400" /> : <Copy size={16} />}
              </button>
            </div>

            {/* Keywords */}
            <div className="mb-4">
              <div className="text-xs font-bold text-slate-500 uppercase mb-2">Key Attributes</div>
              <div className="flex flex-wrap gap-2">
                {p.keywords.map((kw, i) => (
                  <span key={i} className="px-2 py-1 bg-slate-800 text-slate-300 text-xs rounded border border-slate-700">
                    {kw}
                  </span>
                ))}
              </div>
            </div>

            {/* Remix Angle */}
            <div className="bg-slate-800/50 rounded p-3 flex items-start gap-2 border border-slate-800">
              <Terminal size={14} className="text-slate-500 mt-1 flex-shrink-0" />
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase">Remix Angle: </span>
                <span className="text-xs text-slate-500">{p.angle}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

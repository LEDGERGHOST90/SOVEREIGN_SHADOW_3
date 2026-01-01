
import React, { useState } from 'react';
import { 
  Users, 
  ShieldCheck, 
  GitBranch, 
  Zap, 
  AlertOctagon, 
  Terminal, 
  MessageSquare, 
  Settings,
  ShieldAlert,
  HardDrive,
  UserCheck,
  Copy,
  Check,
  ExternalLink,
  Cpu,
  Globe,
  Bell,
  Code,
  Network
} from 'lucide-react';

export const CollaborationFramework: React.FC = () => {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const copyToClipboard = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const aiCouncil = [
    { 
      name: 'Claude Code', 
      role: 'Execution & Deployment', 
      tasks: 'Run trading systems, Execute overnight runner, Push to GitHub/Replit.', 
      icon: <Terminal className="text-blue-400" size={20} />,
      commands: 'python3 bin/overnight_runner.py --duration 8'
    },
    { 
      name: 'Cursor', 
      role: 'Code Editing & Refactoring', 
      tasks: 'Edit Python files, Debug issues, Add new features, Code review.', 
      icon: <Settings className="text-indigo-400" size={20} />,
      commands: 'Read AI_COLLABORATION.md first'
    },
    { 
      name: 'Manus', 
      role: 'Research & Strategy', 
      tasks: 'Market analysis, Strategy optimization, Deep research (web access).', 
      icon: <Zap className="text-yellow-400" size={20} />,
      commands: 'Research Swarm Active'
    },
    { 
      name: 'Gemini (GIO)', 
      role: 'Pattern Recognition', 
      tasks: 'Market regime detection, Sentiment analysis, Data correlation.', 
      icon: <Cpu className="text-purple-400" size={20} />,
      commands: 'Pattern Correlation Engine'
    }
  ];

  const accessPoints = [
    { name: 'Claude Code (Terminal)', location: '/Volumes/LegacySafe/SS_III', type: 'bash' },
    { name: 'Claude Desktop (MCP)', location: 'shadow-sdk & ds-star', type: 'config' },
    { name: 'Cursor / VS Code', location: '/Volumes/LegacySafe/SS_III', type: 'ide' }
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-end gap-6 border-b border-slate-800/60 pb-6 mb-8">
        <div>
          <div className="bg-indigo-950/30 text-indigo-400 px-3 py-1 rounded border border-indigo-500/30 w-fit mb-3 text-[10px] font-black uppercase tracking-widest flex items-center gap-2">
            <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse"></div>
            Protocol SS_III Active
          </div>
          <h1 className="text-3xl font-black text-white tracking-tighter uppercase italic flex items-center gap-3">
             <Users className="text-indigo-500" size={32} /> 
             The <span className="text-slate-500 not-italic text-2xl">| Council</span>
          </h1>
          <p className="text-slate-400 font-mono-tech text-xs mt-2 max-w-2xl border-l-2 border-indigo-500/30 pl-3">
            Unified AI Swarm Coordination Framework. Established Dec 18, 2025.
          </p>
        </div>
        <div className="flex gap-2">
            <a href="https://github.com/LEDGERGHOST90/SOVEREIGN_SHADOW_3" target="_blank" className="flex items-center gap-2 bg-slate-900 hover:bg-slate-800 text-white px-4 py-2 clip-corner font-black text-xs uppercase tracking-widest border border-slate-700 transition-all">
                <Globe size={14} /> GitHub Repo
            </a>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* LEFT: THE RULES & COUNCIL */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* THE COUNCIL GRID */}
          <section>
            <div className="flex items-center gap-2 mb-4 text-xs font-black text-indigo-400 uppercase tracking-widest">
                <Cpu size={14} /> Active Agents
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {aiCouncil.map((ai, idx) => (
                <div key={idx} className="bg-black border border-slate-800 p-6 rounded-xl hover:border-indigo-500/40 transition-all group shadow-lg relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
                      {ai.icon}
                  </div>
                  <div className="flex justify-between items-start mb-4 relative z-10">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-slate-900 rounded-lg group-hover:scale-110 transition-transform shadow-inner shadow-black border border-slate-800">
                            {ai.icon}
                        </div>
                        <div>
                            <h3 className="font-black text-white text-lg uppercase tracking-tight">{ai.name}</h3>
                            <div className="text-[10px] text-indigo-400 font-mono uppercase tracking-tighter">{ai.role}</div>
                        </div>
                    </div>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed min-h-[40px] mb-4 border-l-2 border-slate-800 pl-3">
                    {ai.tasks}
                  </p>
                  <div className="bg-slate-900/50 rounded p-2 font-mono text-[10px] text-slate-500 flex justify-between items-center group/code border border-slate-800">
                    <span className="truncate text-green-400/80">$ {ai.commands}</span>
                    <button onClick={() => copyToClipboard(ai.commands, ai.name)} className="opacity-0 group-hover/code:opacity-100 transition-opacity text-slate-400 hover:text-white">
                        {copiedId === ai.name ? <Check size={12} className="text-green-500"/> : <Copy size={12}/>}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* THE RULES */}
          <section className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
            <div className="p-3 bg-black border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className="text-green-400" size={16} />
                <h2 className="font-black text-white uppercase tracking-widest text-xs">Directives</h2>
              </div>
              <span className="text-[9px] text-red-500 font-mono font-bold animate-pulse">NON-NEGOTIABLE</span>
            </div>
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-4">
                <div className="flex gap-4 p-4 bg-indigo-950/20 rounded-xl border border-indigo-500/20">
                  <UserCheck className="text-indigo-400 flex-shrink-0" size={20} />
                  <div>
                    <h3 className="text-white font-bold text-xs uppercase mb-1">Human Approval</h3>
                    <p className="text-slate-400 text-[11px] leading-relaxed">
                      NO changes are committed without @LedgerGhost90's consent. Propose via PR or explicit confirmation.
                    </p>
                  </div>
                </div>
                <div className="flex gap-4 p-4 bg-blue-950/20 rounded-xl border border-blue-500/20">
                  <HardDrive className="text-blue-400 flex-shrink-0" size={20} />
                  <div>
                    <h3 className="text-white font-bold text-xs uppercase mb-1">Single Source of Truth</h3>
                    <p className="text-slate-400 text-[11px] leading-relaxed">
                      Always rely on GitHub <code>main</code> and <code>BRAIN.json</code>. Always <code>git pull</code> before starting work.
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-black rounded-xl p-5 border border-slate-800 flex flex-col justify-center">
                <h3 className="text-purple-400 font-bold text-[10px] uppercase mb-3 flex items-center gap-2 tracking-widest">
                    <GitBranch size={12} /> Workflow Protocol
                </h3>
                <div className="space-y-3 relative">
                    <div className="absolute left-3 top-0 bottom-0 w-[1px] bg-slate-800"></div>
                    {[
                        { step: '01', text: 'AI Proposes Change' },
                        { step: '02', text: 'Create Branch' },
                        { step: '03', text: 'Push Pull Request' },
                        { step: '04', text: 'Human Review' },
                        { step: '05', text: 'System Merge' }
                    ].map((s, i) => (
                        <div key={i} className="flex items-center gap-4 relative z-10">
                            <div className="w-6 h-6 rounded bg-slate-900 border border-slate-700 flex items-center justify-center text-[9px] text-indigo-400 font-black font-mono">
                                {s.step}
                            </div>
                            <span className="text-[10px] text-slate-300 font-bold uppercase">{s.text}</span>
                        </div>
                    ))}
                </div>
              </div>
            </div>
          </section>

          {/* ACCESS POINTS */}
          <section className="bg-black border border-slate-800 rounded-xl p-6 relative overflow-hidden">
              <div className="absolute inset-0 bg-scanline opacity-5 pointer-events-none"></div>
              <h3 className="text-white font-bold mb-6 flex items-center gap-2 text-xs uppercase tracking-widest relative z-10">
                  <Terminal size={14} className="text-blue-400" /> AI Access Points
              </h3>
              <div className="space-y-4 relative z-10">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      {accessPoints.map((ap, i) => (
                          <div key={i} className="bg-slate-900 border border-slate-800 p-3 rounded-lg hover:border-slate-600 transition-colors">
                              <div className="text-[9px] text-slate-500 font-black uppercase mb-1">{ap.name}</div>
                              <div className="text-[10px] text-cyan-300 font-mono truncate">{ap.location}</div>
                          </div>
                      ))}
                  </div>
                  <div className="bg-slate-900 p-4 rounded-lg border border-slate-800 font-mono text-[10px] text-indigo-300 relative group">
                    <button onClick={() => copyToClipboard(`PYTHONPATH=/Volumes/LegacySafe/SS_III python3 -c "
from core.integrations.live_data_pipeline import LiveDataPipeline
print(LiveDataPipeline().scan_all())
"`, 'scan')} className="absolute top-2 right-2 p-1.5 bg-slate-800 rounded hover:bg-slate-700 opacity-0 group-hover:opacity-100 transition-all border border-slate-700 text-slate-400 hover:text-white">
                         {copiedId === 'scan' ? <Check size={12} className="text-green-500" /> : <Copy size={12} />}
                    </button>
                    <div className="text-slate-500 mb-2 font-bold uppercase tracking-widest flex items-center gap-2">
                        <Code size={12} /> Run Market Scan (Python)
                    </div>
                    <code className="text-green-400 opacity-80">PYTHONPATH=/Volumes/LegacySafe/SS_III python3 -c "..."</code>
                  </div>
              </div>
          </section>
        </div>

        {/* RIGHT: EMERGENCY, ROADMAP & COMMS */}
        <div className="space-y-6">
          
          {/* EMERGENCY PROTOCOLS */}
          <div className="bg-red-950/20 border border-red-500/30 rounded-xl p-6 shadow-[0_0_30px_rgba(239,68,68,0.1)]">
            <h3 className="text-red-500 font-black mb-4 flex items-center gap-2 uppercase tracking-widest text-sm">
              <AlertOctagon size={16} /> Kill Switch
            </h3>
            <div className="space-y-4">
              <div className="bg-black p-4 rounded-xl border border-red-900/30">
                <h4 className="text-[10px] font-bold text-red-200 mb-3 flex items-center gap-2 uppercase">
                    <ShieldAlert size={12} /> Immediate Termination
                </h4>
                <p className="text-[10px] text-red-300/70 mb-4 leading-relaxed font-mono">
                  Modify <code>BRAIN.json</code> set <code>kill_switch: true</code> or execute:
                </p>
                <div className="flex flex-col gap-2">
                    <button onClick={() => copyToClipboard('pkill -f overnight_runner', 'pkill')} className="p-2 bg-red-900/20 hover:bg-red-900/40 border border-red-500/20 rounded font-mono text-[10px] text-red-400 flex justify-between items-center group/btn transition-colors">
                        <span>pkill -f overnight_runner</span>
                        {copiedId === 'pkill' ? <Check size={12}/> : <Copy size={12} className="opacity-0 group-hover/btn:opacity-100"/>}
                    </button>
                    <button onClick={() => copyToClipboard('python3 bin/emergency_stop.py', 'stop')} className="p-2 bg-red-900/20 hover:bg-red-900/40 border border-red-500/20 rounded font-mono text-[10px] text-red-400 flex justify-between items-center group/btn transition-colors">
                        <span>python3 bin/emergency_stop.py</span>
                        {copiedId === 'stop' ? <Check size={12}/> : <Copy size={12} className="opacity-0 group-hover/btn:opacity-100"/>}
                    </button>
                </div>
              </div>
            </div>
          </div>

          {/* ROADMAP TRACKER */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h3 className="text-white font-black mb-6 flex items-center gap-2 text-xs uppercase tracking-widest">
              <Zap size={14} className="text-yellow-400" /> Execution Roadmap
            </h3>
            <div className="space-y-6">
              {[
                { 
                    phase: '01', 
                    title: 'Paper Trading', 
                    desc: 'Runner monitors markets. Signals generated, no execution.', 
                    status: 'ACTIVE', 
                    active: true 
                },
                { 
                    phase: '02', 
                    title: 'Micro Live', 
                    desc: '$25 positions max. All trades logged & manual approval.', 
                    status: 'STANDBY', 
                    active: false 
                },
                { 
                    phase: '03', 
                    title: 'Full Autonomous', 
                    desc: '$50 max limit. Automated execution within rules.', 
                    status: 'LOCKED', 
                    active: false 
                }
              ].map((p, i) => (
                <div key={i} className={`relative pl-4 border-l-2 transition-all ${p.active ? 'border-indigo-500' : 'border-slate-800 opacity-50'}`}>
                  <div className="flex justify-between items-center mb-1">
                    <span className={`text-[10px] font-black ${p.active ? 'text-indigo-400' : 'text-slate-600'}`}>PHASE {p.phase}</span>
                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border ${p.active ? 'bg-indigo-900/20 border-indigo-500/30 text-indigo-400' : 'bg-slate-800 border-slate-700 text-slate-500'}`}>
                        {p.status}
                    </span>
                  </div>
                  <h4 className={`text-xs font-bold uppercase ${p.active ? 'text-white' : 'text-slate-500'}`}>{p.title}</h4>
                  <p className="text-[10px] text-slate-500 mt-1 leading-relaxed">{p.desc}</p>
                </div>
              ))}
            </div>
          </div>

          {/* WEBHOOKS & COMMS */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="text-white font-black mb-4 flex items-center gap-2 text-xs uppercase tracking-widest">
                  <Bell size={14} className="text-indigo-400" /> Comms Channels
              </h3>
              <div className="space-y-3">
                  <div className="p-3 bg-black rounded border border-slate-800 group relative hover:border-indigo-500/30 transition-colors">
                    <div className="text-[9px] text-slate-500 font-black mb-1">REPLIT API</div>
                    <div className="text-[10px] text-indigo-300 font-mono truncate opacity-60">togxk2caarue.picard.replit.dev/api/...</div>
                    <button onClick={() => copyToClipboard('https://1cba4940-c378-451a-a9f4-741e180329ee-00-togxk2caarue.picard.replit.dev/api/manus-webhook', 'replit')} className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        {copiedId === 'replit' ? <Check size={12} className="text-green-500"/> : <Copy size={12} className="text-slate-500 hover:text-white"/>}
                    </button>
                  </div>
                  <div className="p-3 bg-black rounded border border-slate-800 group relative hover:border-indigo-500/30 transition-colors">
                    <div className="text-[9px] text-slate-500 font-black mb-1">NTFY.SH CHANNEL</div>
                    <div className="text-[10px] text-indigo-300 font-mono opacity-60">sovereignshadow_dc4d2fa1</div>
                    <button onClick={() => copyToClipboard('sovereignshadow_dc4d2fa1', 'ntfy')} className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                        {copiedId === 'ntfy' ? <Check size={12} className="text-green-500"/> : <Copy size={12} className="text-slate-500 hover:text-white"/>}
                    </button>
                  </div>
                  <div className="pt-2">
                    <button onClick={() => copyToClipboard('curl -d "AI Task Complete" ntfy.sh/sovereignshadow_dc4d2fa1', 'curl')} className="w-full py-3 bg-indigo-600 hover:bg-indigo-500 text-white clip-corner rounded-sm text-[10px] font-black uppercase tracking-widest flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-600/20">
                        <Terminal size={12} /> Test Alert System
                    </button>
                  </div>
              </div>
          </div>

        </div>
      </div>
    </div>
  );
};

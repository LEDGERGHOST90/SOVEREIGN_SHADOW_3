
import React, { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, BrainCircuit, Cpu, Zap, FolderOpen, Network, BookOpen, Code, Terminal, Plus, X, Check, ArrowUpRight, Wallet } from 'lucide-react';
import { useStrategies } from '../context/StrategyContext';
import { ModuleAOutput } from '../types';

export const NeuralHub: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { strategies } = useStrategies();
  const [moduleAData, setModuleAData] = useState<ModuleAOutput | null>(null);

  useEffect(() => {
    const scanStr = localStorage.getItem('latestScan');
    if (scanStr) {
      try {
        setModuleAData(JSON.parse(scanStr));
      } catch (e) {}
    }
  }, []);

  // --- BRAIN VISUALIZATION ---
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = canvas.parentElement?.clientWidth || 600;
    canvas.height = 300;

    const particles: { x: number, y: number, vx: number, vy: number, life: number }[] = [];
    
    // Seed particles
    for(let i=0; i<50; i++) {
        particles.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            vx: (Math.random() - 0.5) * 2,
            vy: (Math.random() - 0.5) * 2,
            life: Math.random()
        });
    }

    const animate = () => {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw connections
        ctx.strokeStyle = 'rgba(99, 102, 241, 0.15)'; // Indigo
        ctx.lineWidth = 1;
        
        for(let i=0; i<particles.length; i++) {
            const p = particles[i];
            p.x += p.vx;
            p.y += p.vy;

            // Bounce
            if(p.x < 0 || p.x > canvas.width) p.vx *= -1;
            if(p.y < 0 || p.y > canvas.height) p.vy *= -1;

            // Draw particle
            ctx.fillStyle = `rgba(168, 85, 247, ${p.life})`; // Purple
            ctx.beginPath();
            ctx.arc(p.x, p.y, 2, 0, Math.PI * 2);
            ctx.fill();

            // Connect
            for(let j=i+1; j<particles.length; j++) {
                const p2 = particles[j];
                const dx = p.x - p2.x;
                const dy = p.y - p2.y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                
                if(dist < 100) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }
        }
        
        requestAnimationFrame(animate);
    };
    
    const animId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animId);
  }, []);

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12 animate-fade-in">
       
       {/* TOP HEADER */}
       <div className="flex justify-between items-end">
          <div>
              <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                 <BrainCircuit className="text-purple-500" />
                 Neural Hub <span className="text-slate-500 text-lg font-normal">| Command Center</span>
              </h1>
              <p className="text-slate-400 mt-2">Real-time ecosystem monitoring and execution interface.</p>
          </div>
          <div className="flex items-center gap-2 text-xs font-mono bg-slate-900 border border-slate-800 px-3 py-1.5 rounded-full text-green-400">
             <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
             SYSTEM ONLINE
          </div>
       </div>

       {/* MAIN GRID */}
       <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
           
           {/* LEFT COL: BRAIN & SIGNALS */}
           <div className="lg:col-span-2 space-y-6">
               
               {/* NEURAL VIZ */}
               <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden relative shadow-2xl shadow-black/50 h-[320px]">
                   <div className="absolute top-4 left-4 z-10 flex gap-2">
                       <span className="px-2 py-1 bg-black/50 rounded text-[10px] text-purple-300 border border-purple-500/30 backdrop-blur">
                          GEMINI CORE ACTIVE
                       </span>
                   </div>
                   <canvas ref={canvasRef} className="w-full h-full opacity-60" />
                   
                   <div className="absolute bottom-0 left-0 w-full p-6 bg-gradient-to-t from-slate-900 to-transparent">
                       <div className="flex justify-between items-end">
                           <div>
                               <h3 className="text-white font-bold text-lg">Market Pattern Scanner</h3>
                               <p className="text-slate-400 text-sm">Monitoring {strategies.length} active strategy vectors.</p>
                           </div>
                           <Link to="/analyze" className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-bold flex items-center gap-2">
                               <Plus size={16} /> New Vector
                           </Link>
                       </div>
                   </div>
               </div>

               {/* SIGNAL QUEUE */}
               <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
                   <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                       <Activity className="text-blue-400" size={18} /> Signal Queue
                   </h3>
                   <div className="space-y-3">
                       {/* Mock Signals */}
                       {[1, 2].map((_, i) => (
                           <div key={i} className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 flex items-center justify-between group hover:border-slate-600 transition-all">
                               <div className="flex items-center gap-4">
                                   <div className={`p-3 rounded-lg ${i===0 ? 'bg-green-900/20 text-green-400' : 'bg-red-900/20 text-red-400'}`}>
                                       {i===0 ? <ArrowUpRight size={20} /> : <ArrowUpRight size={20} className="rotate-90" />}
                                   </div>
                                   <div>
                                       <div className="font-bold text-white flex items-center gap-2">
                                           {i===0 ? 'BTC/USD' : 'SOL/USD'} 
                                           <span className="text-xs bg-slate-700 px-1.5 rounded text-slate-300">Swing</span>
                                       </div>
                                       <div className="text-xs text-slate-400 mt-1">
                                           RSI divergence detected on 4h timeframe.
                                       </div>
                                   </div>
                               </div>
                               <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                   <button className="p-2 bg-slate-800 hover:bg-red-900/30 text-slate-400 hover:text-red-400 rounded-lg border border-slate-700">
                                       <X size={18} />
                                   </button>
                                   <button className="p-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg shadow-lg shadow-indigo-500/20">
                                       <Check size={18} />
                                   </button>
                               </div>
                           </div>
                       ))}
                   </div>
               </div>

           </div>

           {/* RIGHT COL: PORTFOLIO & DOCK */}
           <div className="space-y-6">
               
               {/* PORTFOLIO CARD */}
               <div className="bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700 rounded-2xl p-6 relative overflow-hidden">
                   <div className="absolute top-0 right-0 p-4 opacity-10">
                       <Wallet size={100} className="text-white" />
                   </div>
                   <h3 className="text-slate-400 text-sm font-bold uppercase mb-1">Net Liquidity</h3>
                   <div className="text-3xl font-mono font-bold text-white mb-4">$12,450.00</div>
                   <div className="flex gap-2 mb-6">
                       <span className="bg-green-900/30 text-green-400 px-2 py-1 rounded text-xs font-bold border border-green-900/50">+2.4% Today</span>
                   </div>
                   <div className="space-y-3">
                       <div className="flex justify-between text-sm">
                           <span className="text-slate-400">Cash</span>
                           <span className="text-white font-mono">$4,200</span>
                       </div>
                       <div className="w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                           <div className="bg-indigo-500 h-full w-[65%]"></div>
                       </div>
                       <div className="flex justify-between text-sm">
                           <span className="text-slate-400">Deployed</span>
                           <span className="text-white font-mono">$8,250</span>
                       </div>
                   </div>
               </div>

               {/* MODULE DOCK */}
               <div className="grid grid-cols-2 gap-3">
                   <Link to="/agent" className="bg-slate-900 border border-slate-800 p-4 rounded-xl hover:bg-slate-800 transition-colors group">
                       <FolderOpen className="text-indigo-400 mb-2 group-hover:scale-110 transition-transform" />
                       <div className="text-xs font-bold text-slate-500 uppercase">Module A</div>
                       <div className="font-bold text-white text-sm">Local Agent</div>
                   </Link>
                   <Link to="/knowledge-graph" className="bg-slate-900 border border-slate-800 p-4 rounded-xl hover:bg-slate-800 transition-colors group">
                       <Network className="text-blue-400 mb-2 group-hover:scale-110 transition-transform" />
                       <div className="text-xs font-bold text-slate-500 uppercase">Module D</div>
                       <div className="font-bold text-white text-sm">Graph</div>
                   </Link>
                   <Link to="/daily-recorder" className="bg-slate-900 border border-slate-800 p-4 rounded-xl hover:bg-slate-800 transition-colors group">
                       <BookOpen className="text-purple-400 mb-2 group-hover:scale-110 transition-transform" />
                       <div className="text-xs font-bold text-slate-500 uppercase">Module C</div>
                       <div className="font-bold text-white text-sm">Recorder</div>
                   </Link>
                   <Link to="/builder" className="bg-slate-900 border border-slate-800 p-4 rounded-xl hover:bg-slate-800 transition-colors group">
                       <Code className="text-green-400 mb-2 group-hover:scale-110 transition-transform" />
                       <div className="text-xs font-bold text-slate-500 uppercase">Module E</div>
                       <div className="font-bold text-white text-sm">Builder</div>
                   </Link>
               </div>
               
               {/* QUICK EXECUTION */}
               <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                   <h3 className="text-white font-bold mb-4 flex items-center gap-2">
                       <Terminal size={16} className="text-slate-400" /> Execution
                   </h3>
                   <div className="space-y-3">
                       <input type="text" placeholder="Symbol (e.g. BTC)" className="w-full bg-slate-800 border-none rounded p-2 text-sm text-white" />
                       <div className="flex gap-2">
                           <button className="flex-1 bg-green-600 hover:bg-green-500 text-white py-2 rounded font-bold text-sm">BUY</button>
                           <button className="flex-1 bg-red-600 hover:bg-red-500 text-white py-2 rounded font-bold text-sm">SELL</button>
                       </div>
                   </div>
               </div>

           </div>
       </div>
    </div>
  );
};


import React, { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Search, BrainCircuit, Menu, X, FolderOpen, BookOpen, Network, Shield, FlaskConical, Users, Radio, Activity, Terminal, Zap } from 'lucide-react';
import { StarfieldBackground } from './StarfieldBackground';

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const location = useLocation();

  useEffect(() => {
    setIsSidebarOpen(false);
  }, [location.pathname]);

  const isActive = (path: string) => 
    location.pathname === path 
      ? 'bg-cyan-950/30 text-cyan-400 border-r-2 border-cyan-400' 
      : 'text-slate-500 hover:text-white hover:bg-white/5';

  return (
    <div className="flex h-screen bg-black overflow-hidden relative">
      <StarfieldBackground />
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-slate-900/20 via-black to-black pointer-events-none z-0"></div>
      
      {/* Mobile Backdrop Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/80 backdrop-blur-sm z-40 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Mobile Toggle */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button 
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="p-2 bg-black border border-slate-800 text-cyan-400 shadow-[0_0_15px_rgba(0,240,255,0.3)]"
        >
          {isSidebarOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-72 bg-black/90 backdrop-blur-xl border-r border-slate-800/50 transform transition-transform duration-300 ease-in-out flex flex-col
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:w-64 lg:h-screen lg:z-auto
      `}>
        {/* Sidebar Header */}
        <div className="flex items-center justify-center h-24 flex-shrink-0 border-b border-slate-800/50 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/5 to-transparent opacity-50"></div>
          <div className="flex flex-col items-center relative z-10">
             <div className="flex items-center gap-2 mb-1">
                <Zap className="text-yellow-400" size={20} fill="currentColor" />
                <h1 className="text-xl font-black tracking-tighter text-white italic">SHADOW<span className="text-cyan-400">.AI</span></h1>
             </div>
             <div className="flex items-center gap-2">
                <div className="h-[1px] w-4 bg-slate-700"></div>
                <span className="text-[10px] font-mono-tech text-slate-500 tracking-[0.2em] uppercase">ALPHARUNNER</span>
                <div className="h-[1px] w-4 bg-slate-700"></div>
             </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto p-4 space-y-1 custom-scrollbar">
          <div className="text-[10px] font-black text-slate-600 uppercase px-4 mb-3 mt-4 tracking-widest flex items-center gap-2">
             <Terminal size={10} /> Command Deck
          </div>
          
          <Link to="/" className={`flex items-center gap-3 px-4 py-3 text-sm font-bold tracking-wide transition-all ${isActive('/')}`}>
            <LayoutDashboard size={16} />
            <span>DASHBOARD</span>
          </Link>
          <Link to="/analyze" className={`flex items-center gap-3 px-4 py-3 text-sm font-bold tracking-wide transition-all ${isActive('/analyze')}`}>
            <Search size={16} />
            <span>STRATEGY FORGE</span>
          </Link>
          <Link to="/agent" className={`flex items-center gap-3 px-4 py-3 text-sm font-bold tracking-wide transition-all ${isActive('/agent')}`}>
            <FolderOpen size={16} />
            <span>LOCAL RUNNER</span>
          </Link>
          
          <div className="h-[1px] bg-slate-800/50 mx-4 my-4"></div>

          <div className="text-[10px] font-black text-slate-600 uppercase px-4 mb-3 mt-2 tracking-widest flex items-center gap-2">
             <BrainCircuit size={10} /> Neural Swarm
          </div>
          <Link to="/alpha-hub" className={`flex items-center gap-3 px-4 py-3 text-sm font-bold tracking-wide transition-all ${isActive('/alpha-hub')}`}>
            <Radio size={16} />
            <span>ALPHA HUB</span>
          </Link>
          <Link to="/lab" className={`flex items-center gap-3 px-4 py-3 text-sm font-bold tracking-wide transition-all ${isActive('/lab')}`}>
            <FlaskConical size={16} />
            <span>DS LAB</span>
          </Link>
          <Link to="/daily-recorder" className={`flex items-center gap-3 px-4 py-3 text-sm font-bold tracking-wide transition-all ${isActive('/daily-recorder')}`}>
            <BookOpen size={16} />
            <span>DAILY LOG</span>
          </Link>
          <Link to="/knowledge-graph" className={`flex items-center gap-3 px-4 py-3 text-sm font-bold tracking-wide transition-all ${isActive('/knowledge-graph')}`}>
            <Network size={16} />
            <span>NEURAL GRAPH</span>
          </Link>
          <Link to="/collaboration" className={`flex items-center gap-3 px-4 py-3 text-sm font-bold tracking-wide transition-all ${isActive('/collaboration')}`}>
            <Users size={16} />
            <span>COUNCIL</span>
          </Link>
          <Link to="/protocols" className={`flex items-center gap-3 px-4 py-3 text-sm font-bold tracking-wide transition-all ${isActive('/protocols')}`}>
            <Shield size={16} />
            <span>PROTOCOLS</span>
          </Link>
        </nav>
        
        {/* Footer */}
        <div className="p-4 border-t border-slate-800/50 bg-black/50">
           <div className="bg-slate-900/50 border border-slate-800 p-3 relative overflow-hidden group">
              <div className="absolute inset-0 bg-cyan-500/10 translate-y-full group-hover:translate-y-0 transition-transform duration-500"></div>
              <div className="flex justify-between items-center relative z-10">
                 <div className="flex flex-col">
                    <span className="text-[9px] text-slate-500 font-black uppercase tracking-wider">System Status</span>
                    <span className="text-green-400 font-mono-tech text-xs font-bold flex items-center gap-1">
                       <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span> ONLINE
                    </span>
                 </div>
                 <Activity size={16} className="text-slate-600 group-hover:text-cyan-400 transition-colors" />
              </div>
           </div>
           <div className="mt-3 text-[9px] text-center text-slate-700 font-mono-tech">
              G.I.O. KERNEL v3.1
           </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-hidden relative w-full h-full z-10">
        <div className="h-full overflow-y-auto custom-scrollbar p-4 lg:p-8 pt-20 lg:pt-8 scroll-smooth">
           {children}
        </div>
      </main>
    </div>
  );
};

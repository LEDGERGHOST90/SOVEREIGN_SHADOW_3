
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Search, BrainCircuit, Menu, X, FolderOpen, BookOpen, Network, Shield } from 'lucide-react';

export const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isSidebarOpen, setIsSidebarOpen] = React.useState(false);
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path ? 'bg-indigo-600 text-white' : 'text-slate-400 hover:bg-slate-800 hover:text-white';

  return (
    <div className="flex h-screen bg-slate-950 overflow-hidden">
      {/* Sidebar Mobile Toggle */}
      <div className="lg:hidden fixed top-4 left-4 z-50">
        <button 
          onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          className="p-2 rounded-md bg-slate-800 text-white"
        >
          {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Sidebar */}
      <aside className={`
        fixed inset-y-0 left-0 z-40 w-64 bg-slate-900 border-r border-slate-800 transform transition-transform duration-300 ease-in-out
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        lg:translate-x-0 lg:static lg:inset-0
      `}>
        <div className="flex items-center justify-center h-16 border-b border-slate-800">
          <div className="flex items-center gap-2 font-bold text-xl text-indigo-400">
            <BrainCircuit />
            <span>StrategyScout</span>
          </div>
        </div>
        <nav className="p-4 space-y-2">
          <Link to="/" className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive('/')}`}>
            <LayoutDashboard size={20} />
            <span>Dashboard</span>
          </Link>
          <Link to="/analyze" className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive('/analyze')}`}>
            <Search size={20} />
            <span>New Analysis</span>
          </Link>
          <Link to="/agent" className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive('/agent')}`}>
            <FolderOpen size={20} />
            <span>Local Agent</span>
          </Link>
          <Link to="/daily-recorder" className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive('/daily-recorder')}`}>
            <BookOpen size={20} />
            <span>Daily Recorder</span>
          </Link>
          <Link to="/knowledge-graph" className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive('/knowledge-graph')}`}>
            <Network size={20} />
            <span>Knowledge Graph</span>
          </Link>
          <Link to="/protocols" className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive('/protocols')}`}>
            <Shield size={20} />
            <span>Protocols</span>
          </Link>
        </nav>
        
        <div className="absolute bottom-0 left-0 w-full p-4 border-t border-slate-800 bg-slate-900">
          <div className="flex items-center justify-between text-xs">
            <span className="text-slate-500">SovereignShadow</span>
            <span className="px-1.5 py-0.5 bg-green-900/30 text-green-400 rounded border border-green-900/50 font-mono">v1.0</span>
          </div>
          <div className="text-[10px] text-slate-600 text-center mt-2">
            Powered by Gemini 3 Pro
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto relative w-full">
        <div className="container mx-auto p-6 lg:p-8 max-w-7xl">
           {children}
        </div>
      </main>
    </div>
  );
};


import React, { useEffect, useState } from 'react';
import { useStrategies } from '../context/StrategyContext';
import { Link } from 'react-router-dom';
import { TrendingUp, Clock, ShieldAlert, ArrowRight, Plus, Activity, Database, BookOpen, Network, Cpu, FileText, Zap } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { ModuleAOutput, DailyRecord, LocalFile } from '../types';

export const Dashboard: React.FC = () => {
  const { strategies } = useStrategies();
  const [moduleAData, setModuleAData] = useState<ModuleAOutput | null>(null);
  const [dailyRecords, setDailyRecords] = useState<DailyRecord[]>([]);
  const [assets, setAssets] = useState<string[]>([]);

  // Load System Data
  useEffect(() => {
    // Load Module A
    const scanStr = localStorage.getItem('latestScan');
    if (scanStr) {
      try {
        setModuleAData(JSON.parse(scanStr));
      } catch (e) {}
    }

    // Load Module C
    const recordsStr = localStorage.getItem('dailyRecords');
    if (recordsStr) {
      try {
        setDailyRecords(JSON.parse(recordsStr));
      } catch (e) {}
    }
  }, []);

  // Extract Unique Assets
  useEffect(() => {
    const uniqueAssets = new Set<string>();
    strategies.forEach(s => {
      s.analysis.assets.forEach(a => uniqueAssets.add(a));
    });
    setAssets(Array.from(uniqueAssets).slice(0, 6)); // Top 6 assets
  }, [strategies]);

  // Mock data for the aggregate chart
  const chartData = strategies.map(s => ({
    name: s.analysis.name.substring(0, 15) + '...',
    score: s.analysis.overallSentiment,
    risk: s.analysis.riskLevel
  }));

  const getRiskColor = (risk: string) => {
    switch(risk) {
      case 'Low': return '#4ade80';
      case 'Medium': return '#facc15';
      case 'High': return '#f87171';
      case 'Degen': return '#a855f7';
      default: return '#94a3b8';
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      
      {/* HEADER & ACTIONS */}
      <div className="flex flex-col md:flex-row justify-between items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Cpu className="text-indigo-500" />
            Sovereign Command
          </h1>
          <p className="text-slate-400 mt-2">Unified Intelligence Hub for StrategyScout & Local Agent.</p>
        </div>
        <div className="flex gap-3">
          <Link to="/daily-recorder" className="bg-slate-800 hover:bg-slate-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors border border-slate-700">
             <BookOpen size={18} />
             <span>Log Daily Record</span>
          </Link>
          <Link to="/analyze" className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors shadow-lg shadow-indigo-500/20">
            <Plus size={18} />
            <span>New Analysis</span>
          </Link>
        </div>
      </div>

      {/* SYSTEM STATUS GRID */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* MODULE A STATUS */}
        <Link to="/agent" className="bg-slate-900 border border-slate-800 p-4 rounded-xl hover:border-indigo-500/30 transition-all group">
          <div className="flex items-center justify-between mb-2">
             <div className="flex items-center gap-2 text-slate-400 group-hover:text-green-400 transition-colors">
               <Database size={16} />
               <span className="text-xs font-bold uppercase">Module A</span>
             </div>
             <div className={`w-2 h-2 rounded-full ${moduleAData ? 'bg-green-500 animate-pulse' : 'bg-slate-700'}`}></div>
          </div>
          <div className="text-2xl font-bold text-white">{moduleAData ? moduleAData.files.length : 0}</div>
          <div className="text-xs text-slate-500">Files Scanned</div>
        </Link>

        {/* MODULE D STATUS */}
        <Link to="/knowledge-graph" className="bg-slate-900 border border-slate-800 p-4 rounded-xl hover:border-indigo-500/30 transition-all group">
          <div className="flex items-center justify-between mb-2">
             <div className="flex items-center gap-2 text-slate-400 group-hover:text-indigo-400 transition-colors">
               <Network size={16} />
               <span className="text-xs font-bold uppercase">Module D</span>
             </div>
             <div className={`w-2 h-2 rounded-full ${strategies.length > 0 ? 'bg-indigo-500 animate-pulse' : 'bg-slate-700'}`}></div>
          </div>
          <div className="text-2xl font-bold text-white">{strategies.length + (moduleAData?.files.length || 0)}</div>
          <div className="text-xs text-slate-500">Knowledge Nodes</div>
        </Link>

        {/* MODULE C STATUS */}
        <Link to="/daily-recorder" className="bg-slate-900 border border-slate-800 p-4 rounded-xl hover:border-indigo-500/30 transition-all group">
          <div className="flex items-center justify-between mb-2">
             <div className="flex items-center gap-2 text-slate-400 group-hover:text-purple-400 transition-colors">
               <BookOpen size={16} />
               <span className="text-xs font-bold uppercase">Module C</span>
             </div>
             <div className={`w-2 h-2 rounded-full ${dailyRecords.length > 0 ? 'bg-purple-500' : 'bg-slate-700'}`}></div>
          </div>
          <div className="text-2xl font-bold text-white">{dailyRecords.length}</div>
          <div className="text-xs text-slate-500">Daily Records</div>
        </Link>

        {/* STRATEGY STATUS */}
        <Link to="/" className="bg-slate-900 border border
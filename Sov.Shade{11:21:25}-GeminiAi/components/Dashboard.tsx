import React from 'react';
import { useStrategies } from '../context/StrategyContext';
import { Link } from 'react-router-dom';
import { TrendingUp, Clock, ShieldAlert, ArrowRight, Plus } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export const Dashboard: React.FC = () => {
  const { strategies } = useStrategies();

  // Mock data for the aggregate chart based on strategy sentiments
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
    <div className="space-y-8">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-white">Strategy Dashboard</h1>
          <p className="text-slate-400 mt-2">Overview of your AI-analyzed trading strategies.</p>
        </div>
        <Link to="/analyze" className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 transition-colors">
          <Plus size={18} />
          <span>New Analysis</span>
        </Link>
      </div>

      {strategies.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-800 mb-6 text-slate-400">
            <TrendingUp size={32} />
          </div>
          <h3 className="text-xl font-semibold text-white mb-2">No strategies yet</h3>
          <p className="text-slate-400 max-w-md mx-auto mb-6">
            Start by analyzing a YouTube transcript or trading notes to extract actionable strategies using Gemini.
          </p>
          <Link to="/analyze" className="text-indigo-400 hover:text-indigo-300 font-medium">
            Create your first analysis &rarr;
          </Link>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-6">Sentiment Overview</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <XAxis dataKey="name" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                    <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                    <Tooltip 
                      cursor={{fill: 'transparent'}}
                      contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f1f5f9' }}
                    />
                    <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={getRiskColor(entry.risk)} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Quick Stats</h3>
              <div className="space-y-4">
                <div className="p-4 bg-slate-800/50 rounded-lg">
                  <div className="text-sm text-slate-400">Total Strategies</div>
                  <div className="text-2xl font-bold text-white">{strategies.length}</div>
                </div>
                <div className="p-4 bg-slate-800/50 rounded-lg">
                  <div className="text-sm text-slate-400">High Risk / Degen</div>
                  <div className="text-2xl font-bold text-red-400">
                    {strategies.filter(s => ['High', 'Degen'].includes(s.analysis.riskLevel)).length}
                  </div>
                </div>
                <div className="p-4 bg-slate-800/50 rounded-lg">
                  <div className="text-sm text-slate-400">Avg Sentiment</div>
                  <div className="text-2xl font-bold text-indigo-400">
                    {Math.round(strategies.reduce((acc, s) => acc + s.analysis.overallSentiment, 0) / strategies.length)}%
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {strategies.map(strategy => (
              <Link 
                key={strategy.id} 
                to={`/strategy/${strategy.id}`}
                className="group bg-slate-900 border border-slate-800 hover:border-indigo-500/50 rounded-xl p-6 transition-all duration-200 hover:shadow-lg hover:shadow-indigo-500/10"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className={`px-2 py-1 rounded text-xs font-bold uppercase tracking-wide ${
                    strategy.analysis.riskLevel === 'Low' ? 'bg-green-900/30 text-green-400' :
                    strategy.analysis.riskLevel === 'Medium' ? 'bg-yellow-900/30 text-yellow-400' :
                    'bg-red-900/30 text-red-400'
                  }`}>
                    {strategy.analysis.riskLevel} Risk
                  </div>
                  <span className="text-slate-500 text-xs">
                    {new Date(strategy.createdAt).toLocaleDateString()}
                  </span>
                </div>
                
                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-indigo-400 transition-colors truncate">
                  {strategy.analysis.name}
                </h3>
                <p className="text-slate-400 text-sm line-clamp-3 mb-6 h-16">
                  {strategy.analysis.description}
                </p>
                
                <div className="flex items-center gap-4 text-sm text-slate-500 mb-6">
                  <div className="flex items-center gap-1">
                    <Clock size={14} />
                    <span>{strategy.analysis.timeframe}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <TrendingUp size={14} />
                    <span>{strategy.analysis.assets.slice(0, 2).join(', ')}</span>
                  </div>
                </div>

                <div className="flex items-center text-indigo-400 text-sm font-medium">
                  View Analysis <ArrowRight size={16} className="ml-2 group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
            ))}
          </div>
        </>
      )}
    </div>
  );
};
'use client';

import React from 'react';
import { useStrategyStore } from '@/lib/stores/strategy-store';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  TrendingUp,
  Clock,
  ShieldAlert,
  ArrowRight,
  Trash2,
  CheckCircle,
  XCircle,
  Brain
} from 'lucide-react';

export function StrategyDashboard() {
  const { strategies, deleteStrategy } = useStrategyStore();

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'Low':
        return 'bg-green-900/30 text-green-400 border-green-500/20';
      case 'Medium':
        return 'bg-yellow-900/30 text-yellow-400 border-yellow-500/20';
      case 'High':
        return 'bg-red-900/30 text-red-400 border-red-500/20';
      case 'Degen':
        return 'bg-purple-900/30 text-purple-400 border-purple-500/20';
      default:
        return 'bg-slate-900/30 text-slate-400 border-slate-500/20';
    }
  };

  if (strategies.length === 0) {
    return (
      <Card className="bg-slate-900/50 border-white/10 p-12 text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-slate-800 mb-6 text-slate-400">
          <TrendingUp size={32} />
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">
          No strategies analyzed yet
        </h3>
        <p className="text-slate-400 max-w-md mx-auto">
          Start by analyzing a YouTube transcript or trading notes to extract
          actionable strategies using Gemini AI.
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-slate-900/50 border-white/10 p-6">
          <div className="text-sm text-slate-400">Total Strategies</div>
          <div className="text-3xl font-bold text-white mt-2">
            {strategies.length}
          </div>
        </Card>

        <Card className="bg-slate-900/50 border-white/10 p-6">
          <div className="text-sm text-slate-400">Validated</div>
          <div className="text-3xl font-bold text-green-400 mt-2">
            {strategies.filter((s) => s.validated).length}
          </div>
        </Card>

        <Card className="bg-slate-900/50 border-white/10 p-6">
          <div className="text-sm text-slate-400">High Risk</div>
          <div className="text-3xl font-bold text-red-400 mt-2">
            {
              strategies.filter((s) =>
                ['High', 'Degen'].includes(s.analysis.riskLevel)
              ).length
            }
          </div>
        </Card>

        <Card className="bg-slate-900/50 border-white/10 p-6">
          <div className="text-sm text-slate-400">Avg Sentiment</div>
          <div className="text-3xl font-bold text-indigo-400 mt-2">
            {Math.round(
              strategies.reduce((acc, s) => acc + s.analysis.overallSentiment, 0) /
                strategies.length
            )}
            %
          </div>
        </Card>
      </div>

      {/* Strategy Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {strategies.map((strategy) => (
          <Card
            key={strategy.id}
            className="bg-slate-900/50 border-white/10 hover:border-indigo-500/50 transition-all duration-200 hover:shadow-lg hover:shadow-indigo-500/10 p-6"
          >
            <div className="flex justify-between items-start mb-4">
              <Badge
                className={`${getRiskColor(
                  strategy.analysis.riskLevel
                )} border font-bold`}
              >
                {strategy.analysis.riskLevel} Risk
              </Badge>
              <div className="flex gap-2">
                {strategy.validated && (
                  <CheckCircle className="w-5 h-5 text-green-400" />
                )}
                {strategy.shadeScore && (
                  <Badge variant="outline" className="text-xs">
                    SHADE: {strategy.shadeScore}/100
                  </Badge>
                )}
                {strategy.rlScore && (
                  <Badge variant="outline" className="text-xs">
                    <Brain className="w-3 h-3 mr-1" />
                    RL: {strategy.rlScore}%
                  </Badge>
                )}
              </div>
            </div>

            <h3 className="text-xl font-bold text-white mb-2 truncate">
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

            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                className="flex-1 bg-white/5 border-white/10 text-white hover:bg-white/10"
              >
                View Details <ArrowRight size={16} className="ml-2" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => deleteStrategy(strategy.id)}
                className="text-red-400 hover:text-red-300 hover:bg-red-900/20"
              >
                <Trash2 size={16} />
              </Button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

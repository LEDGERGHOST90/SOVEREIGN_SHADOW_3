
import React, { useState, useEffect, useRef } from 'react';
import {
  Brain as BrainIcon,
  Zap,
  Activity,
  MessageSquare,
  Send,
  Loader2,
  RefreshCw,
  ChevronRight,
  AlertTriangle,
  Lightbulb,
  Target,
  Clock,
  Cpu,
  Database,
  Layers,
  TrendingUp,
  CheckCircle2,
  XCircle,
  Eye,
  Sparkles
} from 'lucide-react';
import { useStrategies } from '../context/StrategyContext';
import {
  BrainSession,
  BrainThought,
  BrainDirective,
  BrainInsight,
  ModuleStatus
} from '../types';
import {
  initializeBrain,
  saveBrainSession,
  processThought,
  generateSystemAnalysis,
  executeDirective,
  completeDirective,
  clearBrainSession,
  getBrainStats
} from '../services/brainService';

const MODULE_COLORS: Record<string, string> = {
  'A': 'text-blue-400 bg-blue-900/30 border-blue-700',
  'B': 'text-purple-400 bg-purple-900/30 border-purple-700',
  'C': 'text-green-400 bg-green-900/30 border-green-700',
  'D': 'text-orange-400 bg-orange-900/30 border-orange-700',
  'E': 'text-red-400 bg-red-900/30 border-red-700',
  'StrategyScout': 'text-indigo-400 bg-indigo-900/30 border-indigo-700'
};

const THOUGHT_ICONS: Record<string, React.ReactNode> = {
  'observation': <Eye size={14} />,
  'decision': <Target size={14} />,
  'action': <Zap size={14} />,
  'reflection': <Sparkles size={14} />,
  'insight': <Lightbulb size={14} />
};

const STATE_COLORS: Record<string, string> = {
  'idle': 'bg-slate-600',
  'thinking': 'bg-yellow-500 animate-pulse',
  'processing': 'bg-blue-500 animate-pulse',
  'executing': 'bg-green-500 animate-pulse',
  'reflecting': 'bg-purple-500 animate-pulse'
};

export const Brain: React.FC = () => {
  const { strategies } = useStrategies();
  const [session, setSession] = useState<BrainSession>(initializeBrain);
  const [input, setInput] = useState('');
  const [response, setResponse] = useState<string>('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState<'console' | 'modules' | 'memory' | 'insights'>('console');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const stats = getBrainStats(session);

  useEffect(() => {
    saveBrainSession(session);
  }, [session]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [session.memory.shortTerm]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isProcessing) return;

    setIsProcessing(true);
    try {
      const result = await processThought(session, input, { strategies });
      setSession(result.session);
      setResponse(result.response);
      setInput('');
    } catch (error) {
      console.error('Brain processing error:', error);
      setResponse('Error processing thought. Check API configuration.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSystemAnalysis = async () => {
    setIsProcessing(true);
    try {
      const result = await generateSystemAnalysis(session, { strategies });
      setSession(result.session);
      setResponse(result.analysis.overallAssessment);
    } catch (error) {
      console.error('Analysis error:', error);
      setResponse('Error performing system analysis.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleExecuteDirective = async (directiveId: string) => {
    const updated = await executeDirective(session, directiveId);
    setSession(updated);

    // Simulate completion after a delay
    setTimeout(() => {
      const completed = completeDirective(updated, directiveId, 'Directive executed successfully');
      setSession(completed);
    }, 2000);
  };

  const handleReset = () => {
    if (confirm('Clear all brain memory and start fresh?')) {
      setSession(clearBrainSession());
      setResponse('');
    }
  };

  const formatUptime = (ms: number) => {
    const hours = Math.floor(ms / 3600000);
    const minutes = Math.floor((ms % 3600000) / 60000);
    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="relative">
            <div className={`w-16 h-16 rounded-2xl ${STATE_COLORS[session.state]} flex items-center justify-center`}>
              <BrainIcon className="text-white" size={32} />
            </div>
            <div className={`absolute -bottom-1 -right-1 w-5 h-5 rounded-full ${STATE_COLORS[session.state]} border-2 border-slate-900`} />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-white">The Brain</h1>
            <p className="text-slate-400 text-sm">Central Intelligence Coordinator</p>
            <div className="flex items-center gap-2 mt-1">
              <span className={`px-2 py-0.5 rounded text-xs font-mono ${STATE_COLORS[session.state]} text-white`}>
                {session.state.toUpperCase()}
              </span>
              <span className="text-xs text-slate-500">
                Session: {session.id.substring(0, 12)}...
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleSystemAnalysis}
            disabled={isProcessing}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors disabled:opacity-50"
          >
            {isProcessing ? <Loader2 className="animate-spin" size={18} /> : <Activity size={18} />}
            System Analysis
          </button>
          <button
            onClick={handleReset}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
            title="Reset Brain"
          >
            <RefreshCw size={20} />
          </button>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <Clock size={12} />
            Uptime
          </div>
          <div className="text-lg font-bold text-white">{formatUptime(stats.uptime)}</div>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <Cpu size={12} />
            Thoughts
          </div>
          <div className="text-lg font-bold text-white">{stats.totalThoughts}</div>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <Target size={12} />
            Decisions
          </div>
          <div className="text-lg font-bold text-white">{stats.decisionsToday}</div>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <Layers size={12} />
            Directives
          </div>
          <div className="text-lg font-bold text-yellow-400">{stats.pendingDirectives}</div>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <Database size={12} />
            Memory
          </div>
          <div className="text-lg font-bold text-white">
            {stats.memoryUsage.shortTerm}/{stats.memoryUsage.longTerm}
          </div>
        </div>
        <div className="bg-slate-800/50 rounded-lg p-3 border border-slate-700">
          <div className="flex items-center gap-2 text-slate-400 text-xs mb-1">
            <TrendingUp size={12} />
            Health
          </div>
          <div className={`text-lg font-bold ${stats.avgModuleHealth >= 80 ? 'text-green-400' : stats.avgModuleHealth >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>
            {stats.avgModuleHealth}%
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-slate-700">
        {(['console', 'modules', 'memory', 'insights'] as const).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 -mb-px ${
              activeTab === tab
                ? 'text-indigo-400 border-indigo-400'
                : 'text-slate-400 border-transparent hover:text-white'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="min-h-[500px]">
        {activeTab === 'console' && (
          <div className="space-y-4">
            {/* Response Display */}
            {response && (
              <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
                <div className="flex items-center gap-2 text-indigo-400 text-sm mb-2">
                  <MessageSquare size={14} />
                  Brain Response
                </div>
                <div className="text-slate-300 whitespace-pre-wrap text-sm leading-relaxed">
                  {response}
                </div>
              </div>
            )}

            {/* Thought Stream */}
            <div className="bg-slate-900/50 rounded-lg border border-slate-700 max-h-64 overflow-y-auto">
              <div className="p-3 border-b border-slate-700">
                <span className="text-xs text-slate-400 font-medium">Thought Stream</span>
              </div>
              <div className="p-2 space-y-1">
                {session.memory.shortTerm.slice(0, 15).map(thought => (
                  <div
                    key={thought.id}
                    className="flex items-start gap-2 p-2 rounded bg-slate-800/30 text-xs"
                  >
                    <span className="text-slate-500 mt-0.5">{THOUGHT_ICONS[thought.type]}</span>
                    <div className="flex-1">
                      <span className="text-slate-300">{thought.content}</span>
                      {thought.sourceModule && (
                        <span className={`ml-2 px-1.5 py-0.5 rounded text-[10px] ${MODULE_COLORS[thought.sourceModule]}`}>
                          {thought.sourceModule}
                        </span>
                      )}
                    </div>
                    <span className="text-slate-600 text-[10px]">
                      {new Date(thought.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
                {session.memory.shortTerm.length === 0 && (
                  <div className="text-center text-slate-500 py-4 text-xs">
                    No thoughts yet. Start a conversation with The Brain.
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </div>

            {/* Input Form */}
            <form onSubmit={handleSubmit} className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Communicate with The Brain..."
                className="flex-1 px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                disabled={isProcessing}
              />
              <button
                type="submit"
                disabled={isProcessing || !input.trim()}
                className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-colors disabled:opacity-50 flex items-center gap-2"
              >
                {isProcessing ? <Loader2 className="animate-spin" size={18} /> : <Send size={18} />}
              </button>
            </form>
          </div>
        )}

        {activeTab === 'modules' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {session.moduleStatuses.map(mod => (
              <div
                key={mod.module}
                className={`p-4 rounded-lg border ${MODULE_COLORS[mod.module]} bg-opacity-20`}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-bold">{mod.module}</span>
                    <span className="text-sm opacity-80">{mod.name}</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    mod.status === 'active' ? 'bg-green-500/20 text-green-400' :
                    mod.status === 'processing' ? 'bg-yellow-500/20 text-yellow-400' :
                    mod.status === 'error' ? 'bg-red-500/20 text-red-400' :
                    'bg-slate-500/20 text-slate-400'
                  }`}>
                    {mod.status}
                  </span>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="opacity-60">Health</span>
                    <span>{mod.health}%</span>
                  </div>
                  <div className="w-full h-1.5 bg-black/20 rounded-full overflow-hidden">
                    <div
                      className={`h-full transition-all ${mod.health >= 80 ? 'bg-green-500' : mod.health >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
                      style={{ width: `${mod.health}%` }}
                    />
                  </div>
                  {mod.currentTask && (
                    <div className="text-xs opacity-60 truncate">
                      Task: {mod.currentTask}
                    </div>
                  )}
                  {mod.lastActivity && (
                    <div className="text-[10px] opacity-40">
                      Last: {new Date(mod.lastActivity).toLocaleTimeString()}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'memory' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Short-term Memory */}
            <div className="bg-slate-800/30 rounded-lg border border-slate-700">
              <div className="p-3 border-b border-slate-700 flex items-center justify-between">
                <span className="text-sm font-medium text-white">Short-term Memory</span>
                <span className="text-xs text-slate-500">{session.memory.shortTerm.length}/50</span>
              </div>
              <div className="p-3 space-y-2 max-h-80 overflow-y-auto">
                {session.memory.shortTerm.map(thought => (
                  <div key={thought.id} className="p-2 bg-slate-900/50 rounded text-xs">
                    <div className="flex items-center gap-2 mb-1">
                      {THOUGHT_ICONS[thought.type]}
                      <span className="text-slate-400 capitalize">{thought.type}</span>
                      <span className="text-slate-600 ml-auto">{thought.confidence}%</span>
                    </div>
                    <p className="text-slate-300">{thought.content}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Long-term Memory */}
            <div className="bg-slate-800/30 rounded-lg border border-slate-700">
              <div className="p-3 border-b border-slate-700 flex items-center justify-between">
                <span className="text-sm font-medium text-white">Long-term Memory</span>
                <span className="text-xs text-slate-500">{session.memory.longTerm.length}/200</span>
              </div>
              <div className="p-3 space-y-2 max-h-80 overflow-y-auto">
                {session.memory.longTerm.length === 0 ? (
                  <div className="text-center text-slate-500 py-8 text-xs">
                    High-confidence insights will be archived here.
                  </div>
                ) : (
                  session.memory.longTerm.map(thought => (
                    <div key={thought.id} className="p-2 bg-indigo-900/20 border border-indigo-800/30 rounded text-xs">
                      <div className="flex items-center gap-2 mb-1">
                        {THOUGHT_ICONS[thought.type]}
                        <span className="text-indigo-400 capitalize">{thought.type}</span>
                        <span className="text-indigo-300 ml-auto">{thought.confidence}%</span>
                      </div>
                      <p className="text-slate-300">{thought.content}</p>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="space-y-4">
            {/* Active Directives */}
            <div className="bg-slate-800/30 rounded-lg border border-slate-700">
              <div className="p-3 border-b border-slate-700">
                <span className="text-sm font-medium text-white">Active Directives</span>
              </div>
              <div className="p-3 space-y-2">
                {session.activeDirectives.filter(d => d.status !== 'completed').length === 0 ? (
                  <div className="text-center text-slate-500 py-4 text-xs">
                    No active directives. Run System Analysis to generate.
                  </div>
                ) : (
                  session.activeDirectives.filter(d => d.status !== 'completed').map(directive => (
                    <div
                      key={directive.id}
                      className={`p-3 rounded border ${
                        directive.priority === 'critical' ? 'border-red-700 bg-red-900/20' :
                        directive.priority === 'high' ? 'border-orange-700 bg-orange-900/20' :
                        directive.priority === 'medium' ? 'border-yellow-700 bg-yellow-900/20' :
                        'border-slate-700 bg-slate-800/30'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                            directive.priority === 'critical' ? 'bg-red-500/20 text-red-400' :
                            directive.priority === 'high' ? 'bg-orange-500/20 text-orange-400' :
                            directive.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-slate-500/20 text-slate-400'
                          }`}>
                            {directive.priority.toUpperCase()}
                          </span>
                          <span className={`px-2 py-0.5 rounded text-xs ${MODULE_COLORS[directive.targetModule] || 'text-slate-400'}`}>
                            → {directive.targetModule}
                          </span>
                        </div>
                        {directive.status === 'pending' && (
                          <button
                            onClick={() => handleExecuteDirective(directive.id)}
                            className="px-3 py-1 bg-indigo-600 hover:bg-indigo-700 text-white text-xs rounded transition-colors"
                          >
                            Execute
                          </button>
                        )}
                        {directive.status === 'executing' && (
                          <Loader2 className="animate-spin text-indigo-400" size={16} />
                        )}
                      </div>
                      <p className="text-sm text-slate-300">{directive.instruction}</p>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Insights */}
            <div className="bg-slate-800/30 rounded-lg border border-slate-700">
              <div className="p-3 border-b border-slate-700">
                <span className="text-sm font-medium text-white">System Insights</span>
              </div>
              <div className="p-3 space-y-2">
                {session.insights.length === 0 ? (
                  <div className="text-center text-slate-500 py-4 text-xs">
                    No insights generated yet.
                  </div>
                ) : (
                  session.insights.map(insight => (
                    <div
                      key={insight.id}
                      className={`p-3 rounded border ${
                        insight.severity === 'critical' ? 'border-red-700 bg-red-900/20' :
                        insight.severity === 'warning' ? 'border-yellow-700 bg-yellow-900/20' :
                        'border-slate-700 bg-slate-800/30'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        {insight.severity === 'critical' && <AlertTriangle size={14} className="text-red-400" />}
                        {insight.severity === 'warning' && <AlertTriangle size={14} className="text-yellow-400" />}
                        {insight.severity === 'info' && <Lightbulb size={14} className="text-blue-400" />}
                        <span className="font-medium text-white text-sm">{insight.title}</span>
                        <span className="px-2 py-0.5 rounded text-[10px] bg-slate-700 text-slate-300 capitalize">
                          {insight.category}
                        </span>
                      </div>
                      <p className="text-xs text-slate-400 mb-2">{insight.description}</p>
                      {insight.suggestedAction && (
                        <div className="flex items-center gap-2 text-xs text-indigo-400">
                          <ChevronRight size={12} />
                          {insight.suggestedAction}
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

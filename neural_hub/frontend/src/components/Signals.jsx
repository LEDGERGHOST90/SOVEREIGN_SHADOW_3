import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Zap,
  Check,
  X,
  TrendingUp,
  TrendingDown,
  Clock,
  AlertTriangle,
  ChevronDown,
  ChevronUp,
  Brain,
  Target,
  Shield
} from 'lucide-react'

const fetchSignals = async () => {
  const res = await fetch('/api/signals')
  if (!res.ok) throw new Error('Failed to fetch signals')
  return res.json()
}

function Signals() {
  const queryClient = useQueryClient()
  const [expandedSignal, setExpandedSignal] = useState(null)
  const [filter, setFilter] = useState('all')

  const { data: signals, isLoading } = useQuery({
    queryKey: ['signals'],
    queryFn: fetchSignals,
  })

  const executeSignal = useMutation({
    mutationFn: async ({ signalId, action }) => {
      const res = await fetch(`/api/signals/${signalId}/${action}`, {
        method: 'POST'
      })
      if (!res.ok) throw new Error('Failed to execute signal')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['signals'])
      queryClient.invalidateQueries(['portfolio'])
    }
  })

  const getConfidenceColor = (confidence) => {
    if (confidence >= 80) return 'text-neural-accent'
    if (confidence >= 60) return 'text-neural-warning'
    return 'text-neural-danger'
  }

  const getSignalIcon = (action) => {
    return action === 'BUY' ? TrendingUp : TrendingDown
  }

  const pendingSignals = signals?.pending || []
  const executedSignals = signals?.executed || []
  const rejectedSignals = signals?.rejected || []

  const displaySignals = filter === 'all'
    ? [...pendingSignals, ...executedSignals, ...rejectedSignals]
    : filter === 'pending' ? pendingSignals
    : filter === 'executed' ? executedSignals
    : rejectedSignals

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Zap className="w-6 h-6 text-neural-warning" />
            Trading Signals
          </h1>
          <p className="text-gray-400">AI-generated trading opportunities</p>
        </div>

        {/* Filters */}
        <div className="flex gap-2">
          {['all', 'pending', 'executed', 'rejected'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                filter === f
                  ? 'bg-neural-accent text-black'
                  : 'bg-neural-card text-gray-400 hover:text-white'
              }`}
            >
              {f.charAt(0).toUpperCase() + f.slice(1)}
              {f === 'pending' && pendingSignals.length > 0 && (
                <span className="ml-2 bg-neural-warning text-black px-1.5 py-0.5 rounded-full text-xs">
                  {pendingSignals.length}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Signal Queue */}
      {pendingSignals.length > 0 && filter !== 'executed' && filter !== 'rejected' && (
        <div className="neural-card border-neural-warning/30">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-neural-warning" />
            Awaiting Decision ({pendingSignals.length})
          </h3>

          <div className="space-y-4">
            <AnimatePresence>
              {pendingSignals.map((signal, i) => {
                const SignalIcon = getSignalIcon(signal.action)
                const isExpanded = expandedSignal === signal.id

                return (
                  <motion.div
                    key={signal.id || i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 20 }}
                    transition={{ delay: i * 0.05 }}
                    className="bg-neural-darker rounded-lg border border-neural-warning/20 overflow-hidden"
                  >
                    {/* Signal Header */}
                    <div
                      className="p-4 cursor-pointer hover:bg-neural-card/50 transition-colors"
                      onClick={() => setExpandedSignal(isExpanded ? null : signal.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                            signal.action === 'BUY'
                              ? 'bg-neural-accent/20'
                              : 'bg-neural-danger/20'
                          }`}>
                            <SignalIcon className={`w-6 h-6 ${
                              signal.action === 'BUY' ? 'text-neural-accent' : 'text-neural-danger'
                            }`} />
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-bold text-xl">{signal.symbol}</span>
                              <span className={`text-xs px-2 py-1 rounded font-medium ${
                                signal.action === 'BUY'
                                  ? 'bg-neural-accent/20 text-neural-accent'
                                  : 'bg-neural-danger/20 text-neural-danger'
                              }`}>
                                {signal.action}
                              </span>
                            </div>
                            <p className="text-sm text-gray-400">{signal.reason}</p>
                          </div>
                        </div>

                        <div className="flex items-center gap-6">
                          {/* Confidence */}
                          <div className="text-center">
                            <p className="text-xs text-gray-500 mb-1">Confidence</p>
                            <p className={`text-xl font-bold mono ${getConfidenceColor(signal.confidence)}`}>
                              {signal.confidence}%
                            </p>
                          </div>

                          {/* Entry Price */}
                          <div className="text-center">
                            <p className="text-xs text-gray-500 mb-1">Entry</p>
                            <p className="text-lg font-bold mono">${signal.entry_price?.toFixed(4)}</p>
                          </div>

                          {/* Expand Arrow */}
                          {isExpanded ? (
                            <ChevronUp className="w-5 h-5 text-gray-400" />
                          ) : (
                            <ChevronDown className="w-5 h-5 text-gray-400" />
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Expanded Details */}
                    <AnimatePresence>
                      {isExpanded && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="border-t border-neural-border"
                        >
                          <div className="p-4 grid grid-cols-4 gap-4">
                            <div className="neural-card !p-3">
                              <p className="text-xs text-gray-500 mb-1">Stop Loss</p>
                              <p className="text-lg font-bold mono text-neural-danger">
                                ${signal.stop_loss?.toFixed(4)}
                              </p>
                              <p className="text-xs text-gray-500">-15%</p>
                            </div>
                            <div className="neural-card !p-3">
                              <p className="text-xs text-gray-500 mb-1">Take Profit 1</p>
                              <p className="text-lg font-bold mono text-neural-accent">
                                ${signal.take_profit_1?.toFixed(4)}
                              </p>
                              <p className="text-xs text-gray-500">+30%</p>
                            </div>
                            <div className="neural-card !p-3">
                              <p className="text-xs text-gray-500 mb-1">Take Profit 2</p>
                              <p className="text-lg font-bold mono text-neural-accent">
                                ${signal.take_profit_2?.toFixed(4)}
                              </p>
                              <p className="text-xs text-gray-500">+75%</p>
                            </div>
                            <div className="neural-card !p-3">
                              <p className="text-xs text-gray-500 mb-1">Position Size</p>
                              <p className="text-lg font-bold mono">
                                ${signal.position_size?.toFixed(2)}
                              </p>
                              <p className="text-xs text-gray-500">2% risk</p>
                            </div>
                          </div>

                          {/* AI Analysis */}
                          {signal.analysis && (
                            <div className="px-4 pb-4">
                              <div className="neural-card !bg-neural-card/50">
                                <div className="flex items-center gap-2 mb-2">
                                  <Brain className="w-4 h-4 text-neural-accent" />
                                  <span className="text-sm font-medium">Neural Analysis</span>
                                </div>
                                <p className="text-sm text-gray-400">{signal.analysis}</p>
                              </div>
                            </div>
                          )}

                          {/* Action Buttons */}
                          <div className="p-4 pt-0 flex gap-3">
                            <button
                              onClick={() => executeSignal.mutate({ signalId: signal.id, action: 'execute' })}
                              disabled={executeSignal.isLoading}
                              className="flex-1 btn-primary flex items-center justify-center gap-2"
                            >
                              <Check className="w-5 h-5" />
                              Execute Trade
                            </button>
                            <button
                              onClick={() => executeSignal.mutate({ signalId: signal.id, action: 'reject' })}
                              disabled={executeSignal.isLoading}
                              className="flex-1 btn-danger flex items-center justify-center gap-2"
                            >
                              <X className="w-5 h-5" />
                              Reject
                            </button>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                )
              })}
            </AnimatePresence>
          </div>
        </div>
      )}

      {/* Signal History */}
      <div className="neural-card">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5 text-gray-400" />
          Signal History
        </h3>

        {displaySignals.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-gray-500 text-sm border-b border-neural-border">
                  <th className="pb-3 font-medium">Symbol</th>
                  <th className="pb-3 font-medium">Action</th>
                  <th className="pb-3 font-medium">Entry</th>
                  <th className="pb-3 font-medium">Confidence</th>
                  <th className="pb-3 font-medium">Status</th>
                  <th className="pb-3 font-medium">Result</th>
                </tr>
              </thead>
              <tbody>
                {displaySignals.map((signal, i) => (
                  <tr key={i} className="border-b border-neural-border/50 last:border-0">
                    <td className="py-3 font-medium">{signal.symbol}</td>
                    <td className="py-3">
                      <span className={`text-xs px-2 py-1 rounded ${
                        signal.action === 'BUY'
                          ? 'bg-neural-accent/20 text-neural-accent'
                          : 'bg-neural-danger/20 text-neural-danger'
                      }`}>
                        {signal.action}
                      </span>
                    </td>
                    <td className="py-3 mono">${signal.entry_price?.toFixed(4)}</td>
                    <td className={`py-3 mono ${getConfidenceColor(signal.confidence)}`}>
                      {signal.confidence}%
                    </td>
                    <td className="py-3">
                      <span className={`text-xs px-2 py-1 rounded ${
                        signal.status === 'executed'
                          ? 'bg-neural-accent/20 text-neural-accent'
                          : signal.status === 'pending'
                          ? 'bg-neural-warning/20 text-neural-warning'
                          : 'bg-gray-500/20 text-gray-400'
                      }`}>
                        {signal.status}
                      </span>
                    </td>
                    <td className="py-3">
                      {signal.result ? (
                        <span className={signal.result > 0 ? 'text-neural-accent' : 'text-neural-danger'}>
                          {signal.result > 0 ? '+' : ''}{signal.result.toFixed(2)}%
                        </span>
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <Zap className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>No signals in history</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Signals

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  Briefcase,
  TrendingUp,
  TrendingDown,
  Clock,
  Target,
  Shield,
  AlertCircle,
  DollarSign,
  Percent,
  X
} from 'lucide-react'

const fetchPositions = async () => {
  const res = await fetch('/api/positions')
  if (!res.ok) throw new Error('Failed to fetch positions')
  return res.json()
}

function Positions() {
  const queryClient = useQueryClient()

  const { data: positions, isLoading } = useQuery({
    queryKey: ['positions'],
    queryFn: fetchPositions,
  })

  const closePosition = useMutation({
    mutationFn: async (positionId) => {
      const res = await fetch(`/api/positions/${positionId}/close`, {
        method: 'POST'
      })
      if (!res.ok) throw new Error('Failed to close position')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['positions'])
      queryClient.invalidateQueries(['portfolio'])
    }
  })

  const openPositions = positions?.open || []
  const closedPositions = positions?.closed || []

  const totalPnL = openPositions.reduce((sum, pos) => sum + (pos.unrealized_pnl || 0), 0)
  const totalValue = openPositions.reduce((sum, pos) => sum + (pos.current_value || 0), 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Briefcase className="w-6 h-6 text-neural-accent2" />
            Positions
          </h1>
          <p className="text-gray-400">Manage your open trades</p>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="neural-card"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Open Positions</span>
            <Briefcase className="w-4 h-4 text-neural-accent2" />
          </div>
          <p className="text-2xl font-bold mono">{openPositions.length}</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="neural-card"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Total Value</span>
            <DollarSign className="w-4 h-4 text-neural-accent" />
          </div>
          <p className="text-2xl font-bold mono">${totalValue.toFixed(2)}</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="neural-card"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Unrealized P&L</span>
            {totalPnL >= 0 ? (
              <TrendingUp className="w-4 h-4 text-neural-accent" />
            ) : (
              <TrendingDown className="w-4 h-4 text-neural-danger" />
            )}
          </div>
          <p className={`text-2xl font-bold mono ${totalPnL >= 0 ? 'text-neural-accent' : 'text-neural-danger'}`}>
            {totalPnL >= 0 ? '+' : ''}${totalPnL.toFixed(2)}
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="neural-card"
        >
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400 text-sm">Risk Level</span>
            <Shield className="w-4 h-4 text-neural-warning" />
          </div>
          <p className="text-2xl font-bold">Low</p>
        </motion.div>
      </div>

      {/* Open Positions */}
      <div className="neural-card">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5 text-neural-accent" />
          Open Positions
        </h3>

        {openPositions.length > 0 ? (
          <div className="space-y-4">
            {openPositions.map((position, i) => {
              const pnlPercent = ((position.current_price - position.entry_price) / position.entry_price) * 100
              const isProfit = pnlPercent >= 0

              return (
                <motion.div
                  key={position.id || i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="bg-neural-darker rounded-lg p-4 border border-neural-border"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                        isProfit ? 'bg-neural-accent/20' : 'bg-neural-danger/20'
                      }`}>
                        {isProfit ? (
                          <TrendingUp className="w-6 h-6 text-neural-accent" />
                        ) : (
                          <TrendingDown className="w-6 h-6 text-neural-danger" />
                        )}
                      </div>
                      <div>
                        <p className="text-xl font-bold">{position.symbol}</p>
                        <p className="text-sm text-gray-400">{position.side} • {position.strategy || 'SWING'}</p>
                      </div>
                    </div>

                    <div className="flex items-center gap-6">
                      {/* P&L */}
                      <div className="text-right">
                        <p className="text-xs text-gray-500 mb-1">P&L</p>
                        <p className={`text-xl font-bold mono ${isProfit ? 'text-neural-accent' : 'text-neural-danger'}`}>
                          {isProfit ? '+' : ''}{pnlPercent.toFixed(2)}%
                        </p>
                        <p className={`text-sm mono ${isProfit ? 'text-neural-accent' : 'text-neural-danger'}`}>
                          {isProfit ? '+' : ''}${(position.unrealized_pnl || 0).toFixed(2)}
                        </p>
                      </div>

                      {/* Close Button */}
                      <button
                        onClick={() => closePosition.mutate(position.id)}
                        disabled={closePosition.isLoading}
                        className="btn-danger !py-2 !px-4 flex items-center gap-2"
                      >
                        <X className="w-4 h-4" />
                        Close
                      </button>
                    </div>
                  </div>

                  {/* Position Details */}
                  <div className="grid grid-cols-5 gap-4">
                    <div className="bg-neural-card/50 rounded-lg p-3">
                      <p className="text-xs text-gray-500 mb-1">Entry Price</p>
                      <p className="font-bold mono">${position.entry_price?.toFixed(4)}</p>
                    </div>
                    <div className="bg-neural-card/50 rounded-lg p-3">
                      <p className="text-xs text-gray-500 mb-1">Current Price</p>
                      <p className="font-bold mono">${position.current_price?.toFixed(4)}</p>
                    </div>
                    <div className="bg-neural-card/50 rounded-lg p-3">
                      <p className="text-xs text-gray-500 mb-1">Stop Loss</p>
                      <p className="font-bold mono text-neural-danger">${position.stop_loss?.toFixed(4)}</p>
                    </div>
                    <div className="bg-neural-card/50 rounded-lg p-3">
                      <p className="text-xs text-gray-500 mb-1">Take Profit</p>
                      <p className="font-bold mono text-neural-accent">${position.take_profit?.toFixed(4)}</p>
                    </div>
                    <div className="bg-neural-card/50 rounded-lg p-3">
                      <p className="text-xs text-gray-500 mb-1">Size</p>
                      <p className="font-bold mono">${position.size?.toFixed(2)}</p>
                    </div>
                  </div>

                  {/* Progress to TP/SL */}
                  <div className="mt-4">
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>SL: ${position.stop_loss?.toFixed(2)}</span>
                      <span>Entry: ${position.entry_price?.toFixed(2)}</span>
                      <span>TP: ${position.take_profit?.toFixed(2)}</span>
                    </div>
                    <div className="relative h-2 bg-neural-card rounded-full overflow-hidden">
                      {/* Entry marker */}
                      <div className="absolute top-0 bottom-0 w-0.5 bg-white z-10" style={{ left: '50%' }} />
                      {/* Current price indicator */}
                      <motion.div
                        initial={{ width: '50%' }}
                        animate={{
                          width: `${Math.max(0, Math.min(100, 50 + pnlPercent * 2))}%`
                        }}
                        className={`h-full rounded-full ${isProfit ? 'bg-neural-accent' : 'bg-neural-danger'}`}
                      />
                    </div>
                  </div>

                  {/* Time in Trade */}
                  <div className="mt-3 flex items-center justify-between text-sm text-gray-400">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      <span>Opened {position.opened_at || '2h ago'}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Target className="w-4 h-4" />
                      <span>Strategy: {position.strategy || 'Swing Trade'}</span>
                    </div>
                  </div>
                </motion.div>
              )
            })}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <Briefcase className="w-12 h-12 mx-auto mb-3 opacity-30" />
            <p>No open positions</p>
            <p className="text-sm mt-1">Execute a signal to open a position</p>
          </div>
        )}
      </div>

      {/* Closed Positions */}
      <div className="neural-card">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5 text-gray-400" />
          Trade History
        </h3>

        {closedPositions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-gray-500 text-sm border-b border-neural-border">
                  <th className="pb-3 font-medium">Symbol</th>
                  <th className="pb-3 font-medium">Side</th>
                  <th className="pb-3 font-medium">Entry</th>
                  <th className="pb-3 font-medium">Exit</th>
                  <th className="pb-3 font-medium">P&L</th>
                  <th className="pb-3 font-medium">Duration</th>
                  <th className="pb-3 font-medium">Closed</th>
                </tr>
              </thead>
              <tbody>
                {closedPositions.map((pos, i) => {
                  const isProfit = (pos.realized_pnl || 0) >= 0
                  return (
                    <tr key={i} className="border-b border-neural-border/50 last:border-0">
                      <td className="py-3 font-medium">{pos.symbol}</td>
                      <td className="py-3">
                        <span className={`text-xs px-2 py-1 rounded ${
                          pos.side === 'LONG'
                            ? 'bg-neural-accent/20 text-neural-accent'
                            : 'bg-neural-danger/20 text-neural-danger'
                        }`}>
                          {pos.side}
                        </span>
                      </td>
                      <td className="py-3 mono">${pos.entry_price?.toFixed(4)}</td>
                      <td className="py-3 mono">${pos.exit_price?.toFixed(4)}</td>
                      <td className={`py-3 mono font-medium ${isProfit ? 'text-neural-accent' : 'text-neural-danger'}`}>
                        {isProfit ? '+' : ''}${(pos.realized_pnl || 0).toFixed(2)}
                      </td>
                      <td className="py-3 text-gray-400">{pos.duration || '2d 4h'}</td>
                      <td className="py-3 text-gray-400">{pos.closed_at || 'Yesterday'}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>No closed positions yet</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Positions

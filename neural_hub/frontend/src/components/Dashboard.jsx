import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  PieChart,
  Activity,
  Zap,
  Target,
  Shield
} from 'lucide-react'

const fetchPortfolio = async () => {
  const res = await fetch('/api/portfolio')
  if (!res.ok) throw new Error('Failed to fetch portfolio')
  return res.json()
}

const fetchSignals = async () => {
  const res = await fetch('/api/signals')
  if (!res.ok) throw new Error('Failed to fetch signals')
  return res.json()
}

function Dashboard() {
  const { data: portfolio, isLoading: portfolioLoading } = useQuery({
    queryKey: ['portfolio'],
    queryFn: fetchPortfolio,
  })

  const { data: signals } = useQuery({
    queryKey: ['signals'],
    queryFn: fetchSignals,
  })

  const stats = [
    {
      label: 'Portfolio Value',
      value: portfolio?.total_value || 500,
      prefix: '$',
      icon: DollarSign,
      color: 'neural-accent',
      change: '+2.4%'
    },
    {
      label: 'Available Cash',
      value: portfolio?.available_cash || 500,
      prefix: '$',
      icon: PieChart,
      color: 'neural-accent2',
      change: null
    },
    {
      label: 'Active Signals',
      value: signals?.pending?.length || 0,
      prefix: '',
      icon: Zap,
      color: 'neural-warning',
      change: null
    },
    {
      label: 'Win Rate',
      value: portfolio?.stats?.win_rate || 100,
      prefix: '',
      suffix: '%',
      icon: Target,
      color: 'neural-accent',
      change: null
    },
  ]

  const targetAllocation = [
    { symbol: 'BTC', target: 40, current: 35, color: '#F7931A' },
    { symbol: 'ETH', target: 30, current: 28, color: '#627EEA' },
    { symbol: 'SOL', target: 20, current: 22, color: '#00FFA3' },
    { symbol: 'XRP', target: 10, current: 15, color: '#23292F' },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-gray-400">Neural Trading Command Center</p>
        </div>
        <div className="flex items-center gap-2 neural-card !py-2 !px-4">
          <Shield className="w-4 h-4 text-neural-accent" />
          <span className="text-sm">Paper Trading Mode</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-4">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="neural-card"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-gray-400 text-sm">{stat.label}</span>
              <stat.icon className={`w-5 h-5 text-${stat.color}`} />
            </div>
            <div className="flex items-end gap-2">
              <span className="text-3xl font-bold mono">
                {stat.prefix}{typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}{stat.suffix || ''}
              </span>
              {stat.change && (
                <span className="text-neural-accent text-sm mb-1 flex items-center">
                  <TrendingUp className="w-3 h-3 mr-1" />
                  {stat.change}
                </span>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Portfolio Allocation */}
        <div className="neural-card col-span-2">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <PieChart className="w-5 h-5 text-neural-accent" />
            Portfolio Allocation vs Target
          </h3>

          <div className="space-y-4">
            {targetAllocation.map((asset) => (
              <div key={asset.symbol} className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="font-medium">{asset.symbol}</span>
                  <span className="text-gray-400">
                    {asset.current}% / {asset.target}% target
                  </span>
                </div>
                <div className="relative h-3 bg-neural-darker rounded-full overflow-hidden">
                  {/* Target marker */}
                  <div
                    className="absolute top-0 bottom-0 w-0.5 bg-white/50 z-10"
                    style={{ left: `${asset.target}%` }}
                  />
                  {/* Current allocation */}
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${asset.current}%` }}
                    transition={{ duration: 1, delay: 0.2 }}
                    className="h-full rounded-full"
                    style={{ backgroundColor: asset.color }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="neural-card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-neural-accent2" />
            Recent Activity
          </h3>

          <div className="space-y-3">
            {portfolio?.positions?.length > 0 ? (
              portfolio.positions.slice(0, 5).map((pos, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b border-neural-border last:border-0">
                  <div>
                    <p className="font-medium">{pos.symbol}</p>
                    <p className="text-xs text-gray-500">{pos.type || 'SWING'}</p>
                  </div>
                  <div className={`text-sm ${pos.pnl >= 0 ? 'text-neural-accent' : 'text-neural-danger'}`}>
                    {pos.pnl >= 0 ? '+' : ''}{pos.pnl?.toFixed(2) || '0.00'}%
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <Activity className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>No recent activity</p>
                <p className="text-xs mt-1">Signals will appear here</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Active Signals Preview */}
      <div className="neural-card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <Zap className="w-5 h-5 text-neural-warning" />
            Pending Signals
          </h3>
          <a href="/signals" className="text-neural-accent text-sm hover:underline">
            View All →
          </a>
        </div>

        {signals?.pending?.length > 0 ? (
          <div className="grid grid-cols-3 gap-4">
            {signals.pending.slice(0, 3).map((signal, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.1 }}
                className="bg-neural-darker rounded-lg p-4 border border-neural-warning/30"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-lg">{signal.symbol}</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    signal.action === 'BUY'
                      ? 'bg-neural-accent/20 text-neural-accent'
                      : 'bg-neural-danger/20 text-neural-danger'
                  }`}>
                    {signal.action}
                  </span>
                </div>
                <div className="text-sm text-gray-400 mb-2">{signal.reason}</div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-500">Confidence</span>
                  <span className="text-neural-accent mono">{signal.confidence}%</span>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <Zap className="w-10 h-10 mx-auto mb-3 opacity-30" />
            <p>No pending signals</p>
            <p className="text-xs mt-1">The neural network is scanning for opportunities...</p>
          </div>
        )}
      </div>

      {/* Trading Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="neural-card text-center">
          <p className="text-gray-400 text-sm mb-1">Total Trades</p>
          <p className="text-2xl font-bold mono">{portfolio?.stats?.total_trades || 1}</p>
        </div>
        <div className="neural-card text-center">
          <p className="text-gray-400 text-sm mb-1">Winning Trades</p>
          <p className="text-2xl font-bold mono text-neural-accent">{portfolio?.stats?.winning_trades || 1}</p>
        </div>
        <div className="neural-card text-center">
          <p className="text-gray-400 text-sm mb-1">Total Profit</p>
          <p className="text-2xl font-bold mono text-neural-accent">+${portfolio?.stats?.total_profit?.toFixed(2) || '64.74'}</p>
        </div>
        <div className="neural-card text-center">
          <p className="text-gray-400 text-sm mb-1">Avg Hold Time</p>
          <p className="text-2xl font-bold mono">{portfolio?.stats?.avg_hold_time || '2.5'}d</p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

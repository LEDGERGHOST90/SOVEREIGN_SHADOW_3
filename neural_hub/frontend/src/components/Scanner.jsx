import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  Search,
  TrendingUp,
  TrendingDown,
  Activity,
  Zap,
  RefreshCw,
  Filter,
  ChevronDown,
  Volume2,
  BarChart3,
  Target,
  Clock
} from 'lucide-react'

const fetchScannerData = async (filters) => {
  const params = new URLSearchParams(filters)
  const res = await fetch(`/api/scanner?${params}`)
  if (!res.ok) throw new Error('Failed to fetch scanner data')
  return res.json()
}

function Scanner() {
  const [filters, setFilters] = useState({
    minVolume: 100000,
    minChange: 5,
    sortBy: 'volume_24h'
  })
  const [showFilters, setShowFilters] = useState(false)

  const { data: scannerData, isLoading, refetch, isFetching } = useQuery({
    queryKey: ['scanner', filters],
    queryFn: () => fetchScannerData(filters),
    refetchInterval: 30000
  })

  const tokens = scannerData?.tokens || [
    // Demo data
    { symbol: 'BTC', name: 'Bitcoin', price: 97500, change_24h: 2.4, volume_24h: 45000000000, rsi: 58, signal: 'neutral' },
    { symbol: 'ETH', name: 'Ethereum', price: 3650, change_24h: 3.1, volume_24h: 22000000000, rsi: 62, signal: 'bullish' },
    { symbol: 'SOL', name: 'Solana', price: 245, change_24h: 5.2, volume_24h: 8500000000, rsi: 71, signal: 'overbought' },
    { symbol: 'XRP', name: 'Ripple', price: 1.45, change_24h: -1.2, volume_24h: 5200000000, rsi: 45, signal: 'neutral' },
    { symbol: 'APT', name: 'Aptos', price: 12.50, change_24h: 8.7, volume_24h: 890000000, rsi: 28, signal: 'oversold' },
    { symbol: 'SUI', name: 'Sui', price: 3.85, change_24h: 12.3, volume_24h: 1200000000, rsi: 75, signal: 'overbought' },
    { symbol: 'RENDER', name: 'Render', price: 8.20, change_24h: 6.1, volume_24h: 450000000, rsi: 55, signal: 'bullish' },
    { symbol: 'AVAX', name: 'Avalanche', price: 42.50, change_24h: 4.5, volume_24h: 1800000000, rsi: 52, signal: 'neutral' },
  ]

  const getSignalBadge = (signal) => {
    const badges = {
      oversold: { color: 'bg-neural-accent/20 text-neural-accent', icon: TrendingUp, label: 'OVERSOLD' },
      bullish: { color: 'bg-neural-accent/20 text-neural-accent', icon: TrendingUp, label: 'BULLISH' },
      neutral: { color: 'bg-gray-500/20 text-gray-400', icon: Activity, label: 'NEUTRAL' },
      overbought: { color: 'bg-neural-warning/20 text-neural-warning', icon: TrendingDown, label: 'OVERBOUGHT' },
      bearish: { color: 'bg-neural-danger/20 text-neural-danger', icon: TrendingDown, label: 'BEARISH' },
    }
    return badges[signal] || badges.neutral
  }

  const getRSIColor = (rsi) => {
    if (rsi <= 30) return 'text-neural-accent'
    if (rsi >= 70) return 'text-neural-warning'
    return 'text-gray-400'
  }

  const formatVolume = (vol) => {
    if (vol >= 1e9) return `$${(vol / 1e9).toFixed(1)}B`
    if (vol >= 1e6) return `$${(vol / 1e6).toFixed(1)}M`
    return `$${(vol / 1e3).toFixed(1)}K`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Search className="w-6 h-6 text-neural-accent" />
            Market Scanner
          </h1>
          <p className="text-gray-400">Real-time opportunity detection</p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`neural-card !py-2 !px-4 flex items-center gap-2 transition-colors ${
              showFilters ? 'border-neural-accent/50' : ''
            }`}
          >
            <Filter className="w-4 h-4" />
            Filters
            <ChevronDown className={`w-4 h-4 transition-transform ${showFilters ? 'rotate-180' : ''}`} />
          </button>

          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="btn-primary !py-2 !px-4 flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          className="neural-card"
        >
          <div className="grid grid-cols-4 gap-4">
            <div>
              <label className="text-sm text-gray-400 mb-2 block">Min Volume (24h)</label>
              <select
                value={filters.minVolume}
                onChange={(e) => setFilters({ ...filters, minVolume: Number(e.target.value) })}
                className="w-full bg-neural-darker border border-neural-border rounded-lg px-3 py-2 text-sm"
              >
                <option value={0}>Any</option>
                <option value={100000}>$100K+</option>
                <option value={1000000}>$1M+</option>
                <option value={10000000}>$10M+</option>
                <option value={100000000}>$100M+</option>
              </select>
            </div>

            <div>
              <label className="text-sm text-gray-400 mb-2 block">Min Change (24h)</label>
              <select
                value={filters.minChange}
                onChange={(e) => setFilters({ ...filters, minChange: Number(e.target.value) })}
                className="w-full bg-neural-darker border border-neural-border rounded-lg px-3 py-2 text-sm"
              >
                <option value={0}>Any</option>
                <option value={2}>2%+</option>
                <option value={5}>5%+</option>
                <option value={10}>10%+</option>
                <option value={20}>20%+</option>
              </select>
            </div>

            <div>
              <label className="text-sm text-gray-400 mb-2 block">Signal Type</label>
              <select
                value={filters.signal || 'all'}
                onChange={(e) => setFilters({ ...filters, signal: e.target.value })}
                className="w-full bg-neural-darker border border-neural-border rounded-lg px-3 py-2 text-sm"
              >
                <option value="all">All Signals</option>
                <option value="oversold">Oversold (RSI {'<'} 30)</option>
                <option value="bullish">Bullish</option>
                <option value="overbought">Overbought (RSI {'>'} 70)</option>
              </select>
            </div>

            <div>
              <label className="text-sm text-gray-400 mb-2 block">Sort By</label>
              <select
                value={filters.sortBy}
                onChange={(e) => setFilters({ ...filters, sortBy: e.target.value })}
                className="w-full bg-neural-darker border border-neural-border rounded-lg px-3 py-2 text-sm"
              >
                <option value="volume_24h">Volume</option>
                <option value="change_24h">24h Change</option>
                <option value="rsi">RSI</option>
              </select>
            </div>
          </div>
        </motion.div>
      )}

      {/* Quick Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="neural-card flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-neural-accent/20 flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-neural-accent" />
          </div>
          <div>
            <p className="text-2xl font-bold mono">{tokens.filter(t => t.signal === 'oversold').length}</p>
            <p className="text-xs text-gray-500">Oversold</p>
          </div>
        </div>

        <div className="neural-card flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-neural-warning/20 flex items-center justify-center">
            <TrendingDown className="w-5 h-5 text-neural-warning" />
          </div>
          <div>
            <p className="text-2xl font-bold mono">{tokens.filter(t => t.signal === 'overbought').length}</p>
            <p className="text-xs text-gray-500">Overbought</p>
          </div>
        </div>

        <div className="neural-card flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-neural-accent2/20 flex items-center justify-center">
            <Volume2 className="w-5 h-5 text-neural-accent2" />
          </div>
          <div>
            <p className="text-2xl font-bold mono">{tokens.filter(t => t.change_24h > 5).length}</p>
            <p className="text-xs text-gray-500">Volume Spike</p>
          </div>
        </div>

        <div className="neural-card flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-neural-accent/20 flex items-center justify-center">
            <Zap className="w-5 h-5 text-neural-accent" />
          </div>
          <div>
            <p className="text-2xl font-bold mono">{tokens.filter(t => ['oversold', 'bullish'].includes(t.signal)).length}</p>
            <p className="text-xs text-gray-500">Buy Signals</p>
          </div>
        </div>
      </div>

      {/* Scanner Table */}
      <div className="neural-card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-neural-accent" />
            Market Overview
          </h3>
          <div className="flex items-center gap-2 text-sm text-gray-400">
            <Clock className="w-4 h-4" />
            Updated every 30s
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-gray-500 text-sm border-b border-neural-border">
                <th className="pb-3 font-medium">Asset</th>
                <th className="pb-3 font-medium">Price</th>
                <th className="pb-3 font-medium">24h Change</th>
                <th className="pb-3 font-medium">Volume</th>
                <th className="pb-3 font-medium">RSI</th>
                <th className="pb-3 font-medium">Signal</th>
                <th className="pb-3 font-medium">Action</th>
              </tr>
            </thead>
            <tbody>
              {tokens.map((token, i) => {
                const signalBadge = getSignalBadge(token.signal)
                const SignalIcon = signalBadge.icon

                return (
                  <motion.tr
                    key={token.symbol}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="border-b border-neural-border/50 last:border-0 hover:bg-neural-card/30 transition-colors"
                  >
                    <td className="py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-neural-card flex items-center justify-center font-bold text-sm">
                          {token.symbol.slice(0, 2)}
                        </div>
                        <div>
                          <p className="font-medium">{token.symbol}</p>
                          <p className="text-xs text-gray-500">{token.name}</p>
                        </div>
                      </div>
                    </td>
                    <td className="py-4">
                      <span className="mono font-medium">
                        ${token.price >= 1 ? token.price.toLocaleString() : token.price.toFixed(4)}
                      </span>
                    </td>
                    <td className="py-4">
                      <span className={`mono font-medium flex items-center gap-1 ${
                        token.change_24h >= 0 ? 'text-neural-accent' : 'text-neural-danger'
                      }`}>
                        {token.change_24h >= 0 ? (
                          <TrendingUp className="w-4 h-4" />
                        ) : (
                          <TrendingDown className="w-4 h-4" />
                        )}
                        {token.change_24h >= 0 ? '+' : ''}{token.change_24h.toFixed(2)}%
                      </span>
                    </td>
                    <td className="py-4">
                      <span className="mono text-gray-400">{formatVolume(token.volume_24h)}</span>
                    </td>
                    <td className="py-4">
                      <span className={`mono font-medium ${getRSIColor(token.rsi)}`}>
                        {token.rsi}
                      </span>
                    </td>
                    <td className="py-4">
                      <span className={`text-xs px-2 py-1 rounded flex items-center gap-1 w-fit ${signalBadge.color}`}>
                        <SignalIcon className="w-3 h-3" />
                        {signalBadge.label}
                      </span>
                    </td>
                    <td className="py-4">
                      <button className="text-sm text-neural-accent hover:underline flex items-center gap-1">
                        <Target className="w-4 h-4" />
                        Analyze
                      </button>
                    </td>
                  </motion.tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Opportunities */}
      <div className="grid grid-cols-2 gap-4">
        <div className="neural-card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-neural-accent">
            <TrendingUp className="w-5 h-5" />
            Top Buy Opportunities
          </h3>
          <div className="space-y-3">
            {tokens
              .filter(t => ['oversold', 'bullish'].includes(t.signal))
              .slice(0, 3)
              .map((token, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-neural-darker rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-neural-accent/20 flex items-center justify-center text-neural-accent font-bold text-sm">
                      {token.symbol.slice(0, 2)}
                    </div>
                    <div>
                      <p className="font-medium">{token.symbol}</p>
                      <p className="text-xs text-gray-500">RSI: {token.rsi}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="mono">${token.price >= 1 ? token.price.toLocaleString() : token.price.toFixed(4)}</p>
                    <p className="text-xs text-neural-accent">+{token.change_24h.toFixed(2)}%</p>
                  </div>
                </div>
              ))}
          </div>
        </div>

        <div className="neural-card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-neural-warning">
            <TrendingDown className="w-5 h-5" />
            Overbought (Watch for Exit)
          </h3>
          <div className="space-y-3">
            {tokens
              .filter(t => t.signal === 'overbought')
              .slice(0, 3)
              .map((token, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-neural-darker rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-neural-warning/20 flex items-center justify-center text-neural-warning font-bold text-sm">
                      {token.symbol.slice(0, 2)}
                    </div>
                    <div>
                      <p className="font-medium">{token.symbol}</p>
                      <p className="text-xs text-gray-500">RSI: {token.rsi}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="mono">${token.price >= 1 ? token.price.toLocaleString() : token.price.toFixed(4)}</p>
                    <p className="text-xs text-neural-warning">+{token.change_24h.toFixed(2)}%</p>
                  </div>
                </div>
              ))}
            {tokens.filter(t => t.signal === 'overbought').length === 0 && (
              <p className="text-center text-gray-500 py-4">No overbought assets</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Scanner

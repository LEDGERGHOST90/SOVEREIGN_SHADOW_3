/**
 * PortfolioPanel Component
 * ========================
 * Lightweight panel that displays live portfolio data using usePortfolioSync hook
 */

import React from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, AlertCircle, TrendingUp, TrendingDown } from 'lucide-react';
import { usePortfolioSync } from '../hooks/usePortfolioSync';

export function PortfolioPanel({ className = '' }) {
  const { items, totalValue, loading, error, reload, lastUpdate, isEmpty, hasError } = usePortfolioSync();

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatTime = (date) => {
    if (!date) return 'Never';
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(date);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className={`bg-black/40 backdrop-blur-md border border-white/10 rounded-2xl p-6 ${className}`}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-white">Live Portfolio</h3>
          <p className="text-sm text-gray-400">
            Last updated: {formatTime(lastUpdate)}
          </p>
        </div>
        
        <button
          onClick={reload}
          disabled={loading}
          className="p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors disabled:opacity-50"
        >
          <RefreshCw 
            className={`h-5 w-5 text-white ${loading ? 'animate-spin' : ''}`} 
          />
        </button>
      </div>

      {/* Total Value */}
      <div className="mb-6">
        <div className="text-3xl font-black text-white mb-2">
          {formatCurrency(totalValue)}
        </div>
        <div className="flex items-center gap-2 text-sm">
          <TrendingUp className="h-4 w-4 text-emerald-400" />
          <span className="text-emerald-400">Portfolio Value</span>
        </div>
      </div>

      {/* Error State */}
      {hasError && (
        <div className="mb-4 p-3 rounded-lg bg-red-500/20 border border-red-500/30">
          <div className="flex items-center gap-2 text-red-300">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm">{error}</span>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && isEmpty && (
        <div className="text-center py-8">
          <RefreshCw className="h-8 w-8 text-white/60 animate-spin mx-auto mb-2" />
          <p className="text-white/60">Loading portfolio...</p>
        </div>
      )}

      {/* Assets List */}
      {!isEmpty && (
        <div className="space-y-3">
          <h4 className="text-sm font-semibold text-gray-300 mb-3">
            Assets ({items.length})
          </h4>
          
          <div className="max-h-64 overflow-y-auto space-y-2">
            {items.map((asset) => (
              <motion.div
                key={asset.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <div 
                    className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white"
                    style={{ backgroundColor: asset.accent }}
                  >
                    {asset.symbol.slice(0, 2)}
                  </div>
                  
                  <div>
                    <div className="text-sm font-semibold text-white">
                      {asset.symbol}
                    </div>
                    <div className="text-xs text-gray-400">
                      {asset.balance.toFixed(4)} {asset.symbol}
                    </div>
                  </div>
                </div>
                
                <div className="text-right">
                  <div className="text-sm font-semibold text-white">
                    {formatCurrency(asset.value)}
                  </div>
                  <div className="text-xs text-gray-400">
                    ${asset.price.toFixed(asset.price < 1 ? 6 : 2)}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {isEmpty && !loading && (
        <div className="text-center py-8">
          <div className="text-white/60 mb-2">No assets found</div>
          <button
            onClick={reload}
            className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
          >
            Try refreshing
          </button>
        </div>
      )}
    </motion.div>
  );
}

export default PortfolioPanel;


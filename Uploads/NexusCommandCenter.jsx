import React from "react";

/**
 * NEXUS Command Center - Simplified Version
 * 
 * LedgerGhost90's Trading Dashboard
 */

export default function NexusCommandCenter({ onSignOut, user }) {
  return (
    <div className="min-h-screen bg-black text-white">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-white/10">
        <div>
          <h1 className="text-2xl font-bold text-emerald-400">NEXUS PROTOCOL</h1>
          <p className="text-sm text-white/70">Command Center</p>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="font-semibold">LedgerGhost90</div>
            <div className="text-xs text-emerald-400">Markets bleeding • Hedge protocols armed</div>
          </div>
          <button
            onClick={onSignOut}
            className="px-4 py-2 bg-red-600/20 border border-red-500/30 rounded-lg text-red-400 hover:bg-red-600/30 transition-colors"
          >
            Sign Out
          </button>
        </div>
      </div>

      {/* Main Dashboard */}
      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          {/* Portfolio Summary */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">Portfolio Summary</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-white/70">Total Value</span>
                <span className="font-bold text-emerald-400">$1,260</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/70">24h Change</span>
                <span className="font-bold text-red-400">-2.4%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/70">Active Positions</span>
                <span className="font-bold">8</span>
              </div>
            </div>
          </div>

          {/* Emergency Actions */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">Emergency Actions</h3>
            <div className="space-y-3">
              <button className="w-full py-3 bg-red-600/20 border border-red-500/30 rounded-lg text-red-400 hover:bg-red-600/30 transition-colors font-semibold">
                🛡️ Deploy Emergency Hedge
              </button>
              <button className="w-full py-3 bg-blue-600/20 border border-blue-500/30 rounded-lg text-blue-400 hover:bg-blue-600/30 transition-colors font-semibold">
                ⚖️ Rebalance Portfolio
              </button>
              <button className="w-full py-3 bg-yellow-600/20 border border-yellow-500/30 rounded-lg text-yellow-400 hover:bg-yellow-600/30 transition-colors font-semibold">
                📊 Sync Portfolio
              </button>
            </div>
          </div>

          {/* Market Status */}
          <div className="bg-white/5 border border-white/10 rounded-xl p-6">
            <h3 className="text-lg font-semibold mb-4">Market Status</h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span>BTC</span>
                <span className="text-red-400">-1.2%</span>
              </div>
              <div className="flex justify-between items-center">
                <span>ETH</span>
                <span className="text-red-400">-3.1%</span>
              </div>
              <div className="flex justify-between items-center">
                <span>SOL</span>
                <span className="text-green-400">+2.4%</span>
              </div>
              <div className="flex justify-between items-center">
                <span>RENDER</span>
                <span className="text-green-400">+5.7%</span>
              </div>
            </div>
          </div>

        </div>

        {/* Status Message */}
        <div className="mt-8 p-4 bg-emerald-600/10 border border-emerald-500/20 rounded-xl">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 bg-emerald-400 rounded-full animate-pulse"></div>
            <span className="text-emerald-400 font-semibold">NEXUS Protocol Active</span>
            <span className="text-white/70">• Live portfolio monitoring enabled</span>
          </div>
        </div>
      </div>
    </div>
  );
}


import { useState, useEffect } from 'react'
import { Routes, Route, NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard,
  Zap,
  Briefcase,
  Brain,
  Settings,
  Activity,
  TrendingUp,
  Wallet
} from 'lucide-react'

import Dashboard from './components/Dashboard'
import Signals from './components/Signals'
import Positions from './components/Positions'
import NeuralChat from './components/NeuralChat'
import Scanner from './components/Scanner'

function App() {
  const [isOnline, setIsOnline] = useState(false)

  useEffect(() => {
    // Check if backend is online
    fetch('/api/')
      .then(res => res.json())
      .then(data => setIsOnline(data.status === 'online'))
      .catch(() => setIsOnline(false))

    const interval = setInterval(() => {
      fetch('/api/')
        .then(res => res.json())
        .then(data => setIsOnline(data.status === 'online'))
        .catch(() => setIsOnline(false))
    }, 30000)

    return () => clearInterval(interval)
  }, [])

  const navItems = [
    { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/signals', icon: Zap, label: 'Signals' },
    { path: '/positions', icon: Briefcase, label: 'Positions' },
    { path: '/scanner', icon: TrendingUp, label: 'Scanner' },
    { path: '/neural', icon: Brain, label: 'Neural AI' },
  ]

  return (
    <div className="min-h-screen neural-grid">
      {/* Header */}
      <header className="border-b border-neural-border bg-neural-darker/80 backdrop-blur-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="w-10 h-10 rounded-full bg-gradient-to-r from-neural-accent to-neural-accent2 flex items-center justify-center"
            >
              <Brain className="w-6 h-6 text-black" />
            </motion.div>
            <div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-neural-accent to-neural-accent2 bg-clip-text text-transparent">
                AURORA
              </h1>
              <p className="text-xs text-gray-500">Command Center • Claude AI</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-neural-accent live-indicator' : 'bg-neural-danger'}`} />
              <span className="text-sm text-gray-400 mono">
                {isOnline ? 'ONLINE' : 'OFFLINE'}
              </span>
            </div>
            <div className="neural-card !p-2 flex items-center gap-2">
              <Wallet className="w-4 h-4 text-neural-accent" />
              <span className="mono text-sm">$500.00</span>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <nav className="w-64 min-h-[calc(100vh-64px)] border-r border-neural-border bg-neural-darker/50 p-4">
          <div className="space-y-2">
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    isActive
                      ? 'bg-neural-accent/10 text-neural-accent border border-neural-accent/30'
                      : 'text-gray-400 hover:bg-neural-card hover:text-white'
                  }`
                }
              >
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
              </NavLink>
            ))}
          </div>

          {/* Quick Stats */}
          <div className="mt-8 space-y-4">
            <h3 className="text-xs text-gray-500 uppercase tracking-wider px-4">Quick Stats</h3>

            <div className="neural-card">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Today's P&L</span>
                <Activity className="w-4 h-4 text-neural-accent" />
              </div>
              <p className="text-2xl font-bold text-neural-accent mono">+$0.00</p>
            </div>

            <div className="neural-card">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Open Positions</span>
                <Briefcase className="w-4 h-4 text-neural-accent2" />
              </div>
              <p className="text-2xl font-bold text-white mono">1</p>
            </div>

            <div className="neural-card">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-400 text-sm">Active Signals</span>
                <Zap className="w-4 h-4 text-neural-warning" />
              </div>
              <p className="text-2xl font-bold text-white mono">0</p>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/signals" element={<Signals />} />
            <Route path="/positions" element={<Positions />} />
            <Route path="/scanner" element={<Scanner />} />
            <Route path="/neural" element={<NeuralChat />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App

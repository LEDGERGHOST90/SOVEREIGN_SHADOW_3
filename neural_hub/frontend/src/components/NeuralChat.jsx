import { useState, useRef, useEffect } from 'react'
import { useMutation } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Brain,
  Send,
  Loader2,
  User,
  Sparkles,
  TrendingUp,
  AlertCircle,
  Zap,
  Target,
  BarChart3
} from 'lucide-react'

function NeuralChat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: "I'm your Neural Trading AI powered by Gemini. I can analyze markets, generate signals, and help you make informed trading decisions. What would you like to know?",
      timestamp: new Date().toISOString()
    }
  ])
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = useMutation({
    mutationFn: async (message) => {
      const res = await fetch('/api/neural/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message })
      })
      if (!res.ok) throw new Error('Failed to send message')
      return res.json()
    },
    onSuccess: (data) => {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        analysis: data.analysis
      }])
    }
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || sendMessage.isLoading) return

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    sendMessage.mutate(input)
    setInput('')
  }

  const quickActions = [
    { icon: TrendingUp, label: 'Analyze BTC', prompt: 'Analyze BTC market conditions and suggest entry points' },
    { icon: Target, label: 'Find Signals', prompt: 'Scan the market for swing trade opportunities' },
    { icon: BarChart3, label: 'Portfolio Review', prompt: 'Review my portfolio allocation and suggest rebalancing' },
    { icon: Zap, label: 'Hot Picks', prompt: 'What are the top 3 trading opportunities right now?' },
  ]

  return (
    <div className="h-[calc(100vh-140px)] flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <Brain className="w-6 h-6 text-neural-accent" />
            Neural AI
          </h1>
          <p className="text-gray-400">Powered by Gemini 2.0 Flash</p>
        </div>
        <div className="flex items-center gap-2 neural-card !py-2 !px-4">
          <div className="w-2 h-2 rounded-full bg-neural-accent live-indicator" />
          <span className="text-sm">AI Online</span>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        {quickActions.map((action, i) => (
          <motion.button
            key={i}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => {
              setInput(action.prompt)
            }}
            className="neural-card !p-3 flex items-center gap-2 hover:border-neural-accent/50 transition-colors"
          >
            <action.icon className="w-4 h-4 text-neural-accent" />
            <span className="text-sm">{action.label}</span>
          </motion.button>
        ))}
      </div>

      {/* Chat Messages */}
      <div className="flex-1 neural-card overflow-y-auto mb-4">
        <div className="space-y-4 p-2">
          <AnimatePresence>
            {messages.map((message, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : ''}`}
              >
                {message.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-neural-accent to-neural-accent2 flex items-center justify-center flex-shrink-0">
                    <Brain className="w-5 h-5 text-black" />
                  </div>
                )}

                <div className={`max-w-[70%] ${message.role === 'user' ? 'order-first' : ''}`}>
                  <div className={`rounded-lg p-4 ${
                    message.role === 'user'
                      ? 'bg-neural-accent/20 border border-neural-accent/30'
                      : 'bg-neural-darker border border-neural-border'
                  }`}>
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>

                    {/* Analysis Box */}
                    {message.analysis && (
                      <div className="mt-3 p-3 rounded-lg bg-neural-card/50 border border-neural-accent/20">
                        <div className="flex items-center gap-2 mb-2">
                          <Sparkles className="w-4 h-4 text-neural-accent" />
                          <span className="text-xs font-medium text-neural-accent">AI Analysis</span>
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-xs">
                          {message.analysis.sentiment && (
                            <div>
                              <span className="text-gray-500">Sentiment:</span>
                              <span className={`ml-2 ${
                                message.analysis.sentiment === 'bullish' ? 'text-neural-accent' :
                                message.analysis.sentiment === 'bearish' ? 'text-neural-danger' :
                                'text-gray-400'
                              }`}>
                                {message.analysis.sentiment}
                              </span>
                            </div>
                          )}
                          {message.analysis.confidence && (
                            <div>
                              <span className="text-gray-500">Confidence:</span>
                              <span className="ml-2 text-neural-accent">{message.analysis.confidence}%</span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-1 px-1">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                </div>

                {message.role === 'user' && (
                  <div className="w-8 h-8 rounded-lg bg-neural-card border border-neural-border flex items-center justify-center flex-shrink-0">
                    <User className="w-5 h-5 text-gray-400" />
                  </div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Loading State */}
          {sendMessage.isLoading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-3"
            >
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-neural-accent to-neural-accent2 flex items-center justify-center">
                <Brain className="w-5 h-5 text-black" />
              </div>
              <div className="bg-neural-darker border border-neural-border rounded-lg p-4">
                <div className="flex items-center gap-2">
                  <Loader2 className="w-4 h-4 animate-spin text-neural-accent" />
                  <span className="text-sm text-gray-400">Neural network analyzing...</span>
                </div>
              </div>
            </motion.div>
          )}

          {/* Error State */}
          {sendMessage.isError && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-3"
            >
              <div className="w-8 h-8 rounded-lg bg-neural-danger/20 flex items-center justify-center">
                <AlertCircle className="w-5 h-5 text-neural-danger" />
              </div>
              <div className="bg-neural-danger/10 border border-neural-danger/30 rounded-lg p-4">
                <p className="text-sm text-neural-danger">Failed to get response. Please try again.</p>
              </div>
            </motion.div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="neural-card !p-2 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the Neural AI anything about trading..."
          className="flex-1 bg-neural-darker border border-neural-border rounded-lg px-4 py-3 text-sm focus:outline-none focus:border-neural-accent/50 transition-colors"
          disabled={sendMessage.isLoading}
        />
        <button
          type="submit"
          disabled={!input.trim() || sendMessage.isLoading}
          className="btn-primary !px-6 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {sendMessage.isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </button>
      </form>
    </div>
  )
}

export default NeuralChat

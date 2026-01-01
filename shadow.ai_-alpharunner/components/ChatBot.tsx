
import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Bot, User, BrainCircuit, Zap, AlertCircle } from 'lucide-react';
import { chatWithGemini } from '../services/geminiService';
import { ChatMessage } from '../types';

interface ChatBotProps {
  contextData: string;
}

export const ChatBot: React.FC<ChatBotProps> = ({ contextData }) => {
  const [input, setInput] = useState('');
  const [useThinking, setUseThinking] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'model',
      text: 'Hi! I\'ve analyzed this strategy. Ask me anything about the entry conditions, risks, or how to code it.',
      timestamp: Date.now()
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      text: input,
      timestamp: Date.now()
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setIsLoading(true);

    try {
      const history = messages.map(m => ({ role: m.role, text: m.text }));
      const responseText = await chatWithGemini(history, userMsg.text, contextData, useThinking);
      
      const botMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'model',
        text: responseText,
        timestamp: Date.now()
      };
      
      setMessages(prev => [...prev, botMsg]);
    } catch (error: any) {
      console.error(error);
      const errorMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'model',
        text: `Sorry, I encountered an error: ${error.message || 'Connecting to Gemini failed.'}`,
        timestamp: Date.now()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[600px] bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
      <div className="p-4 border-b border-slate-800 bg-slate-900/50 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="text-indigo-400" size={20} />
          <h3 className="font-semibold text-white">Strategy Assistant</h3>
        </div>
        
        {/* Thinking Mode Toggle */}
        <button 
          onClick={() => setUseThinking(!useThinking)}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-widest transition-all border ${
            useThinking 
            ? 'bg-purple-900/30 border-purple-500/50 text-purple-400 shadow-[0_0_10px_rgba(168,85,247,0.2)]' 
            : 'bg-slate-800 border-slate-700 text-slate-500 hover:text-slate-300'
          }`}
        >
          <BrainCircuit size={14} className={useThinking ? 'animate-pulse' : ''} />
          {useThinking ? 'Deep Thinking ON' : 'Deep Thinking OFF'}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            <div className={`
              w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0
              ${msg.role === 'user' ? 'bg-indigo-600 shadow-lg shadow-indigo-600/20' : 'bg-slate-800 border border-slate-700 shadow-lg'}
            `}>
              {msg.role === 'user' ? <User size={14} /> : <Bot size={14} className="text-indigo-400" />}
            </div>
            <div className={`
              max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-relaxed
              ${msg.role === 'user' 
                ? 'bg-indigo-600 text-white shadow-xl' 
                : 'bg-slate-800/80 text-slate-200 border border-slate-700 backdrop-blur-sm'}
            `}>
              {msg.text.split('\n').map((line, i) => (
                <React.Fragment key={i}>
                  {line}
                  {i !== msg.text.split('\n').length - 1 && <br />}
                </React.Fragment>
              ))}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center flex-shrink-0">
               <Bot size={14} className="text-indigo-400" />
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-2xl px-5 py-3 flex items-center gap-3">
              <Loader2 className="animate-spin text-indigo-400" size={16} />
              <span className="text-xs text-slate-400 italic">
                {useThinking ? 'Performing Deep Reason Analysis (32k tokens)...' : 'Processing...'}
              </span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSend} className="p-4 border-t border-slate-800 bg-slate-900">
        <div className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={useThinking ? "Ask a complex reasoning query..." : "Ask about strategy details..."}
            className={`w-full bg-slate-800 border-2 rounded-xl pl-4 pr-12 py-3.5 text-sm text-white placeholder-slate-500 focus:outline-none transition-all ${
              useThinking ? 'border-purple-500/30 focus:border-purple-500 ring-2 ring-purple-500/10' : 'border-slate-700 focus:border-indigo-500'
            }`}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={`absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-all ${
              useThinking 
              ? 'bg-purple-600 hover:bg-purple-500 text-white shadow-lg shadow-purple-500/20' 
              : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {useThinking ? <Zap size={18} fill="currentColor" /> : <Send size={18} />}
          </button>
        </div>
        {useThinking && (
           <div className="mt-2 flex items-center gap-1.5 text-[9px] text-purple-400 font-bold uppercase tracking-widest px-1">
              <AlertCircle size={10} /> Maximum intelligence mode enabled
           </div>
        )}
      </form>
    </div>
  );
};

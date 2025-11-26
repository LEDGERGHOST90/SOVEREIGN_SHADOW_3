import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface TradeCondition {
  condition: string;
  importance: 'High' | 'Medium' | 'Low';
}

export interface StrategyAnalysis {
  name: string;
  description: string;
  riskLevel: 'Low' | 'Medium' | 'High' | 'Degen';
  timeframe: string;
  assets: string[];
  buyConditions: string[];
  sellConditions: string[];
  stopLoss: string;
  takeProfit: string;
  indicators: string[];
  overallSentiment: number; // 0 to 100
}

export interface Strategy {
  id: string;
  title: string;
  videoUrl: string;
  transcriptSnippet: string;
  analysis: StrategyAnalysis;
  createdAt: number;
  model: string; // 'gemini-2.5-flash' | 'gemini-3-pro-preview'
  validated?: boolean;
  shadeScore?: number;
  rlScore?: number;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'model';
  text: string;
  timestamp: number;
}

interface StrategyStore {
  strategies: Strategy[];
  addStrategy: (strategy: Strategy) => void;
  updateStrategy: (id: string, updates: Partial<Strategy>) => void;
  deleteStrategy: (id: string) => void;
  getStrategy: (id: string) => Strategy | undefined;
  clearStrategies: () => void;
}

export const useStrategyStore = create<StrategyStore>()(
  persist(
    (set, get) => ({
      strategies: [],

      addStrategy: (strategy) =>
        set((state) => ({
          strategies: [strategy, ...state.strategies]
        })),

      updateStrategy: (id, updates) =>
        set((state) => ({
          strategies: state.strategies.map((s) =>
            s.id === id ? { ...s, ...updates } : s
          ),
        })),

      deleteStrategy: (id) =>
        set((state) => ({
          strategies: state.strategies.filter((s) => s.id !== id),
        })),

      getStrategy: (id) =>
        get().strategies.find((s) => s.id === id),

      clearStrategies: () =>
        set({ strategies: [] }),
    }),
    {
      name: 'sovereign-strategy-storage',
      version: 1,
    }
  )
);

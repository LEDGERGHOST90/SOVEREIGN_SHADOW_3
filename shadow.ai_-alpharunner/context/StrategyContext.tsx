
import React, { createContext, useContext, useState, ReactNode } from 'react';
import { Strategy } from '../types';

interface StrategyContextType {
  strategies: Strategy[];
  addStrategy: (strategy: Strategy) => void;
  updateStrategy: (id: string, updates: Partial<Strategy>) => void;
  deleteStrategy: (id: string) => void;
  overrideStrategies: (strategies: Strategy[]) => void; // New bulk import method
}

const StrategyContext = createContext<StrategyContextType | undefined>(undefined);

export const StrategyProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);

  const addStrategy = (strategy: Strategy) => {
    setStrategies(prev => [strategy, ...prev]);
  };

  const updateStrategy = (id: string, updates: Partial<Strategy>) => {
    setStrategies(prev => prev.map(s => s.id === id ? { ...s, ...updates } : s));
  };

  const deleteStrategy = (id: string) => {
    setStrategies(prev => prev.filter(s => s.id !== id));
  };
  
  const overrideStrategies = (newStrategies: Strategy[]) => {
      setStrategies(newStrategies);
  };

  return (
    <StrategyContext.Provider value={{ strategies, addStrategy, updateStrategy, deleteStrategy, overrideStrategies }}>
      {children}
    </StrategyContext.Provider>
  );
};

export const useStrategies = () => {
  const context = useContext(StrategyContext);
  if (!context) {
    throw new Error("useStrategies must be used within a StrategyProvider");
  }
  return context;
};

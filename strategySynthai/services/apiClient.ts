
import { LegacyLoopData, TradingAlert } from '../types';

const API_BASE = 'http://localhost:8000/api';

export interface BridgeHealth {
  status: 'online' | 'offline';
  latency: number;
}

export const checkBridgeHealth = async (): Promise<BridgeHealth> => {
  const start = Date.now();
  try {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), 2000);
    
    // Attempt to hit the root or a health endpoint
    const response = await fetch(`${API_BASE}/`, { 
        method: 'GET',
        signal: controller.signal
    });
    clearTimeout(id);
    
    if (response.ok) {
      return { status: 'online', latency: Date.now() - start };
    }
    return { status: 'offline', latency: 0 };
  } catch (e) {
    return { status: 'offline', latency: 0 };
  }
};

export const fetchLivePortfolio = async (): Promise<LegacyLoopData | null> => {
  try {
    const response = await fetch(`${API_BASE}/portfolio`);
    if (!response.ok) throw new Error("Failed to fetch portfolio");
    return await response.json();
  } catch (e) {
    console.error("Bridge Error (Portfolio):", e);
    return null;
  }
};

export const fetchLiveSignals = async (): Promise<TradingAlert[]> => {
  try {
    const response = await fetch(`${API_BASE}/signals`);
    if (!response.ok) throw new Error("Failed to fetch signals");
    return await response.json();
  } catch (e) {
    console.error("Bridge Error (Signals):", e);
    return [];
  }
};

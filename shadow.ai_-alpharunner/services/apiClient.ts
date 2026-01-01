
import { LegacyLoopData, TradingAlert } from '../types';

// Uses Vite proxy in dev (/api -> localhost:8000)
// In production, set to your dedicated IP
export const DEDICATED_IP = '68.165.100.178';
const API_BASE = process.env.NODE_ENV === 'production'
  ? `http://${DEDICATED_IP}:8000/api`
  : '/api';  // Vite proxies this to localhost:8000

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

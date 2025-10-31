
export interface Portfolio {
  id: string;
  asset: string;
  balance: number;
  hotBalance: number;
  coldBalance: number;
  avgBuyPrice: number;
  totalInvested: number;
  currentValue: number;
  pnl: number;
  pnlPercentage: number;
}

export interface Trade {
  id: string;
  asset: string;
  type: string;
  side: string;
  amount: number;
  price: number;
  fee: number;
  pnl?: number;
  strategy?: string;
  status: string;
  executedAt?: string;
  createdAt: string;
}

export interface VaultLog {
  id: string;
  asset: string;
  amount: number;
  type: string;
  fromWallet: string;
  toWallet: string;
  status: string;
  createdAt: string;
  completedAt?: string;
}

export interface AgentMilestone {
  id: string;
  title: string;
  description?: string;
  category: string;
  achieved: boolean;
  achievedAt?: string;
  createdAt: string;
}

export interface AgentReflection {
  id: string;
  content: string;
  mood?: string;
  tags: string[];
  createdAt: string;
}

export interface AgentHighlight {
  id: string;
  component: string;
  issue: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  status: 'OPEN' | 'RESOLVED' | 'DISMISSED';
  resolvedAt?: string;
  createdAt: string;
}

export interface UserSettings {
  id: string;
  liveTrading: boolean;
  dailyLimit: number;
  siphonRatio: number;
  graduationThreshold: number;
  agentReviewInterval: number;
  agentStrictMode: boolean;
  riskLevel: string;
}

export interface SystemHealth {
  binanceStatus: boolean;
  databaseStatus: boolean;
  aiAdvisorStatus: boolean;
  vaultStatus: boolean;
  lastCheck: string;
  shadowAI?: {
    darkPoolActivity?: string;
    whaleMovements?: string;
    riskLevel?: string;
    recommendation?: string;
  };
}

export interface WealthSummary {
  totalValue: number;
  totalPnL: number;
  dailyChange: number;
  monthlyReturn?: number;
  tier1: {
    name: string;
    value: number;
    allocation: Array<{
      asset: string;
      percentage: number;
      value: number;
      change: number;
    }>;
  };
  tier2: {
    name: string;
    value: number;
    allocation: Array<{
      asset: string;
      percentage: number;
      value: number;
      change: number;
    }>;
  };
}

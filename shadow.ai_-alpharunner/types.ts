
export interface TradeCondition {
  condition: string;
  importance: 'High' | 'Medium' | 'Low';
}

export interface StrategyArtifacts {
  pythonCode: string;
  pineScript: string;
  configJson: string;
  narrative: string;
}

export interface Strategy {
  id: string;
  title: string;
  videoUrl: string;
  transcriptSnippet: string;
  analysis: StrategyAnalysis;
  createdAt: number;
  model: string; // 'gemini-2.5-flash' | 'gemini-3-pro-preview'
  pipelineStatus: 'draft' | 'certified';
  artifacts?: StrategyArtifacts;
  code?: string; // Deprecated in favor of artifacts, kept for backward compat
}

export interface StrategyAnalysis {
  name: string;
  description: string;
  riskLevel: 'Low' | 'Medium' | 'High' | 'Degen';
  // Sovereign Classification
  sovereignCategory: 'Vault' | 'Sniper' | 'Ladder' | 'MENACE' | 'TP_Structure' | 'Unknown';
  assetTier: 'Tier_A' | 'Tier_B' | 'Tier_C';
  
  timeframe: string;
  assets: string[];
  
  // Logic
  buyConditions: string[]; // Entry Logic
  sellConditions: string[]; // Exit Logic
  stopLoss: string;
  takeProfit: string;
  indicators: string[];
  
  // Deep Intelligence
  exampleScenario: string;
  failureModes: string[];
  improvements: string[];
  
  overallSentiment: number; // 0 to 100
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'model';
  text: string;
  timestamp: number;
}

export type SovereignCategory = 'Financial_Analytics' | 'NeverNest' | 'VA_Caregiving' | 'Home_Management' | 'AI_Innovation' | 'Uncategorized';

export type Era = 'Legacy_Loop' | 'Sovereign_Shadow' | 'Gemini_Current';

export interface LocalFile {
  name: string;
  path: string;
  lastModified: number;
  created?: number; 
  size: number;
  type: 'code' | 'text' | 'image' | 'video' | 'audio' | 'pdf' | 'unknown';
  category: SovereignCategory;
  era?: Era;
  content?: string;
}

export interface TimelineEntry {
  date: string;
  new_files: LocalFile[];
  modified_files: LocalFile[];
}

export interface ModuleAOutput {
  scanned_at: string;
  root_folder: string;
  files: LocalFile[];
  timeline_view: TimelineEntry[];
}

export interface EcosystemAnalysis {
  projectName: string;
  summary: string;
  modules: any[];
  architectureDiagram: string;
  timelineAnalysis: string;
}

export interface StructureAnalysis {
  projectType: string;
  techStack: string[];
  keyModulesDetected: string[];
  architectureSummary: string;
  suggestedNextSteps: string[];
}

export interface TriEraAnalysis {
  evolutionSummary: string;
  legacyStrengths: string;
  sovereignInnovations: string;
  geminiPotential: string;
  unifiedArchitecturePlan: string;
  suggestedModules: string[];
}

// --- MODULE B: SUMMARIZER ---
export interface FileSummary {
  meaningSummary: string;
  keyFunctions: string[];
  keyVariables: string[];
  dependencies: {
    internal: string[];
    external: string[];
  };
  risks: string[];
  connections: {
    moduleA?: string;
    strategyScout?: string;
    moduleC?: string;
    moduleD?: string;
    tradingSystems?: string[];
  };
  suggestedNextSteps: string[];
}

// --- MODULE C: DAILY RECORDER ---
export interface DailyRecord {
  id: string;
  date: string;
  reportMarkdown: string;
  timestamp: number;
}

// --- MODULE D: KNOWLEDGE GRAPH ---
export interface KnowledgeNode {
  id: string;
  type: 'strategy' | 'file' | 'concept' | 'module' | 'asset';
  label: string;
  data: any; // Store original object
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  color?: string;
  radius?: number;
}

export interface KnowledgeEdge {
  source: string; // Node ID
  target: string; // Node ID
  relationship: string;
}

export interface KnowledgeGraph {
  nodes: KnowledgeNode[];
  edges: KnowledgeEdge[];
}

// --- LEGACY LOOP / SOVEREIGN SHADOW 3 DATA ---
export interface ActiveOrder {
  id: string;
  market: string;
  side: 'Buy' | 'Sell';
  type: 'Limit' | 'Market';
  price: number;
  amount: number;
  total: number;
  status: 'Open' | 'Filled' | 'Cancelled';
  date: string;
}

export interface LegacyLoopData {
  version: string;
  last_updated: string;
  portfolio: {
    net_worth: number;
    aave: {
      collateral: number;
      debt: number;
      net: number;
      health_factor: number;
      status: string;
    };
    allocation: {
      current: { [key: string]: number };
      target: { [key: string]: number };
    };
  };
  trading: {
    last_trade: {
      symbol: string;
      type: string;
      pnl: number;
      notes: string;
      date: string;
    };
    active_orders: ActiveOrder[];
  };
  december_campaign: {
    debt_repayment: number;
    start_date: string;
  };
}

// --- THE BRAIN STATE (Single Source of Truth) ---
export interface BrainState {
  timestamp: string;
  version: string; // "3.0"
  legacyLoop: LegacyLoopData;
  strategies: Strategy[];
  dailyRecords: DailyRecord[];
  moduleAScan: ModuleAOutput | null;
}

export interface TradingAlert {
  id: string;
  source: 'TradingView' | 'Python' | 'Claude' | 'Manual';
  symbol: string;
  message: string;
  severity: 'Info' | 'Warning' | 'Critical';
  timestamp: number;
  actionRequired?: string;
}

export type BridgeStatus = 'online' | 'offline' | 'connecting';

// --- DS-STAR / DATA SCIENCE LAB ---
export interface DSAnalysis {
  asset: string;
  smartScore: number;
  technicalSignal: string;
  fundamentalSignal: string;
  sentimentSignal: string;
  unifiedVerdict: string;
  keyRisks: string[];
  suggestedAction: string;
}

export interface DataSet {
  id: string;
  name: string;
  type: 'technical' | 'fundamental' | 'sentiment';
  content: string;
  size: number;
}

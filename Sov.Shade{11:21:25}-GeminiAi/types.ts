
export interface TradeCondition {
  condition: string;
  importance: 'High' | 'Medium' | 'Low';
}

export interface Strategy {
  id: string;
  title: string;
  videoUrl: string;
  transcriptSnippet: string;
  analysis: StrategyAnalysis;
  createdAt: number;
  model: string; // 'gemini-2.5-flash' | 'gemini-3-pro-preview'
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

export interface TriEraAnalysis {
  evolutionSummary: string;
  legacyStrengths: string;
  sovereignInnovations: string;
  geminiPotential: string;
  unifiedArchitecturePlan: string;
  suggestedModules: string[];
}

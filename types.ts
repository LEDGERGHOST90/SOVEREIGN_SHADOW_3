
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

// --- BRAIN: CENTRAL INTELLIGENCE COORDINATOR ---
export type BrainState = 'idle' | 'thinking' | 'processing' | 'executing' | 'reflecting';

export type ModuleType = 'A' | 'B' | 'C' | 'D' | 'E' | 'StrategyScout';

export interface BrainThought {
  id: string;
  timestamp: number;
  type: 'observation' | 'decision' | 'action' | 'reflection' | 'insight';
  content: string;
  sourceModule?: ModuleType;
  confidence: number; // 0-100
  relatedThoughts?: string[]; // IDs of related thoughts
}

export interface BrainMemory {
  shortTerm: BrainThought[]; // Recent thoughts (last 50)
  longTerm: BrainThought[]; // Important archived thoughts
  workingContext: string; // Current focus/task context
}

export interface ModuleStatus {
  module: ModuleType;
  name: string;
  status: 'active' | 'idle' | 'processing' | 'error';
  lastActivity?: number;
  currentTask?: string;
  health: number; // 0-100
}

export interface BrainDirective {
  id: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  targetModule: ModuleType | 'all';
  instruction: string;
  status: 'pending' | 'executing' | 'completed' | 'failed';
  createdAt: number;
  completedAt?: number;
  result?: string;
}

export interface BrainInsight {
  id: string;
  category: 'pattern' | 'anomaly' | 'opportunity' | 'risk' | 'optimization';
  title: string;
  description: string;
  affectedModules: ModuleType[];
  severity: 'info' | 'warning' | 'critical';
  suggestedAction?: string;
  timestamp: number;
}

export interface BrainSession {
  id: string;
  startedAt: number;
  state: BrainState;
  memory: BrainMemory;
  moduleStatuses: ModuleStatus[];
  activeDirectives: BrainDirective[];
  insights: BrainInsight[];
  totalThoughts: number;
  decisionsToday: number;
}

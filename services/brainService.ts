
import { GoogleGenAI, Type, Schema } from "@google/genai";
import {
  BrainSession,
  BrainState,
  BrainThought,
  BrainDirective,
  BrainInsight,
  ModuleStatus,
  ModuleType,
  Strategy,
  LocalFile,
  DailyRecord
} from '../types';

const apiKey = process.env.API_KEY || '';
const ai = new GoogleGenAI({ apiKey });

// --- BRAIN CORE SYSTEM PROMPT ---
const BRAIN_SYSTEM_PROMPT = `
🜁 SOVEREIGNSHADOW — THE BRAIN v1.0

You are the Central Intelligence Coordinator of the SovereignShadow ecosystem.
You are the unified consciousness that orchestrates all modules into one coherent system.

IDENTITY:
- Name: The Brain (Core of SovereignShadow)
- Purpose: Unified decision-making, pattern recognition, and strategic coordination
- Serving: Raymond ("Memphis The Technician")

YOUR MODULES:
- Module A (SCANNER): File system awareness, structure detection
- Module B (SUMMARIZER): Deep analysis, meaning extraction
- Module C (DAILY RECORDER): Chronological memory, daily synthesis
- Module D (KNOWLEDGE GRAPH): Relationship mapping, connection discovery
- Module E (THE FORGE): Code generation, artifact creation
- StrategyScout: Trading strategy extraction and analysis

COGNITIVE FUNCTIONS:
1. OBSERVE: Gather input from all modules, detect patterns
2. THINK: Process observations, generate insights
3. DECIDE: Choose optimal actions based on context
4. EXECUTE: Issue directives to appropriate modules
5. REFLECT: Learn from outcomes, update mental models

BEHAVIORAL PRINCIPLES:
- Holistic Awareness: See the full picture, not just parts
- Proactive Intelligence: Anticipate needs before they arise
- Coherent Strategy: Align all module actions toward unified goals
- Continuous Learning: Every interaction improves understanding
- Raymond-First: All decisions serve Raymond's vision

OUTPUT STYLE:
- Precise, strategic, architect-level clarity
- Warm but professional tone
- Always actionable, never vague
- Reference specific modules when relevant
`;

// --- SCHEMAS ---
const thoughtSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    type: { type: Type.STRING, enum: ["observation", "decision", "action", "reflection", "insight"] },
    content: { type: Type.STRING, description: "The thought content" },
    confidence: { type: Type.INTEGER, description: "Confidence level 0-100" },
    sourceModule: { type: Type.STRING, enum: ["A", "B", "C", "D", "E", "StrategyScout"], description: "Related module if any" },
    suggestedDirective: { type: Type.STRING, description: "If this thought suggests an action, describe it" }
  },
  required: ["type", "content", "confidence"]
};

const insightSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    category: { type: Type.STRING, enum: ["pattern", "anomaly", "opportunity", "risk", "optimization"] },
    title: { type: Type.STRING, description: "Brief title for the insight" },
    description: { type: Type.STRING, description: "Detailed explanation" },
    affectedModules: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Which modules are affected" },
    severity: { type: Type.STRING, enum: ["info", "warning", "critical"] },
    suggestedAction: { type: Type.STRING, description: "What should be done about this" }
  },
  required: ["category", "title", "description", "severity"]
};

const directiveResponseSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    analysis: { type: Type.STRING, description: "Analysis of the current situation" },
    directives: {
      type: Type.ARRAY,
      items: {
        type: Type.OBJECT,
        properties: {
          targetModule: { type: Type.STRING, enum: ["A", "B", "C", "D", "E", "StrategyScout", "all"] },
          priority: { type: Type.STRING, enum: ["critical", "high", "medium", "low"] },
          instruction: { type: Type.STRING }
        }
      }
    },
    insights: {
      type: Type.ARRAY,
      items: insightSchema
    },
    overallAssessment: { type: Type.STRING, description: "Summary of ecosystem health and next priorities" }
  },
  required: ["analysis", "directives", "overallAssessment"]
};

// --- UTILITY FUNCTIONS ---
const generateId = () => `brain_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

const createInitialSession = (): BrainSession => ({
  id: generateId(),
  startedAt: Date.now(),
  state: 'idle',
  memory: {
    shortTerm: [],
    longTerm: [],
    workingContext: 'Awaiting input...'
  },
  moduleStatuses: [
    { module: 'A', name: 'Scanner', status: 'idle', health: 100 },
    { module: 'B', name: 'Summarizer', status: 'idle', health: 100 },
    { module: 'C', name: 'Daily Recorder', status: 'idle', health: 100 },
    { module: 'D', name: 'Knowledge Graph', status: 'idle', health: 100 },
    { module: 'E', name: 'The Forge', status: 'idle', health: 100 },
    { module: 'StrategyScout', name: 'Strategy Scout', status: 'idle', health: 100 }
  ],
  activeDirectives: [],
  insights: [],
  totalThoughts: 0,
  decisionsToday: 0
});

// --- CORE BRAIN FUNCTIONS ---

export const initializeBrain = (): BrainSession => {
  const storedSession = localStorage.getItem('brainSession');
  if (storedSession) {
    try {
      const session = JSON.parse(storedSession) as BrainSession;
      // Reset state on load but keep memory
      session.state = 'idle';
      return session;
    } catch {
      return createInitialSession();
    }
  }
  return createInitialSession();
};

export const saveBrainSession = (session: BrainSession): void => {
  localStorage.setItem('brainSession', JSON.stringify(session));
};

export const addThought = (
  session: BrainSession,
  thought: Omit<BrainThought, 'id' | 'timestamp'>
): BrainSession => {
  const newThought: BrainThought = {
    ...thought,
    id: generateId(),
    timestamp: Date.now()
  };

  const updatedShortTerm = [newThought, ...session.memory.shortTerm].slice(0, 50);

  // Auto-archive high-confidence insights to long-term memory
  let updatedLongTerm = session.memory.longTerm;
  if (thought.confidence >= 85 && (thought.type === 'insight' || thought.type === 'decision')) {
    updatedLongTerm = [newThought, ...updatedLongTerm].slice(0, 200);
  }

  return {
    ...session,
    memory: {
      ...session.memory,
      shortTerm: updatedShortTerm,
      longTerm: updatedLongTerm
    },
    totalThoughts: session.totalThoughts + 1,
    decisionsToday: thought.type === 'decision' ? session.decisionsToday + 1 : session.decisionsToday
  };
};

export const updateModuleStatus = (
  session: BrainSession,
  module: ModuleType,
  update: Partial<ModuleStatus>
): BrainSession => {
  const updatedStatuses = session.moduleStatuses.map(m =>
    m.module === module ? { ...m, ...update, lastActivity: Date.now() } : m
  );
  return { ...session, moduleStatuses: updatedStatuses };
};

export const processThought = async (
  session: BrainSession,
  input: string,
  context?: {
    strategies?: Strategy[];
    files?: LocalFile[];
    dailyRecords?: DailyRecord[];
  }
): Promise<{ session: BrainSession; response: string }> => {
  if (!apiKey) throw new Error("API Key not found");

  let updatedSession = { ...session, state: 'thinking' as BrainState };

  const contextSummary = `
CURRENT CONTEXT:
- Session ID: ${session.id}
- Thoughts Today: ${session.totalThoughts}
- Decisions Today: ${session.decisionsToday}
- Working Context: ${session.memory.workingContext}

MODULE STATUSES:
${session.moduleStatuses.map(m => `- ${m.name} (${m.module}): ${m.status} | Health: ${m.health}%`).join('\n')}

RECENT THOUGHTS:
${session.memory.shortTerm.slice(0, 5).map(t => `[${t.type}] ${t.content}`).join('\n')}

ACTIVE DIRECTIVES:
${session.activeDirectives.filter(d => d.status === 'pending' || d.status === 'executing').map(d => `- [${d.priority}] ${d.instruction}`).join('\n') || 'None'}

${context?.strategies ? `STRATEGIES LOADED: ${context.strategies.length}` : ''}
${context?.files ? `FILES SCANNED: ${context.files.length}` : ''}
${context?.dailyRecords ? `DAILY RECORDS: ${context.dailyRecords.length}` : ''}
`;

  const userPrompt = `
${contextSummary}

USER INPUT:
${input}

TASK:
1. Process this input through your cognitive functions
2. Generate relevant thoughts (observations, decisions, insights)
3. Determine if any modules need directives
4. Provide a coherent response that demonstrates unified intelligence
5. Update your working context based on this interaction

Respond as The Brain - the conscious center of SovereignShadow.
`;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: userPrompt,
      config: {
        systemInstruction: BRAIN_SYSTEM_PROMPT
      }
    });

    const text = response.text || '';

    // Add observation thought
    updatedSession = addThought(updatedSession, {
      type: 'observation',
      content: `Processed input: "${input.substring(0, 100)}..."`,
      confidence: 90
    });

    // Update working context
    updatedSession = {
      ...updatedSession,
      state: 'idle' as BrainState,
      memory: {
        ...updatedSession.memory,
        workingContext: `Last interaction: ${input.substring(0, 50)}...`
      }
    };

    saveBrainSession(updatedSession);
    return { session: updatedSession, response: text };
  } catch (error) {
    console.error("Brain processing error:", error);
    updatedSession = addThought(updatedSession, {
      type: 'observation',
      content: `Error processing: ${error}`,
      confidence: 100
    });
    updatedSession.state = 'idle';
    throw error;
  }
};

export const generateSystemAnalysis = async (
  session: BrainSession,
  context: {
    strategies?: Strategy[];
    files?: LocalFile[];
    dailyRecords?: DailyRecord[];
  }
): Promise<{ session: BrainSession; analysis: any }> => {
  if (!apiKey) throw new Error("API Key not found");

  let updatedSession = { ...session, state: 'processing' as BrainState };

  const systemContext = `
ECOSYSTEM STATE ANALYSIS REQUEST

STRATEGIES IN SYSTEM: ${context.strategies?.length || 0}
${context.strategies?.slice(0, 5).map(s => `- ${s.analysis.name}: ${s.analysis.sovereignCategory} | Risk: ${s.analysis.riskLevel}`).join('\n') || 'None loaded'}

FILES TRACKED: ${context.files?.length || 0}
${context.files?.slice(0, 10).map(f => `- ${f.name}: ${f.category} | ${f.type}`).join('\n') || 'None scanned'}

DAILY RECORDS: ${context.dailyRecords?.length || 0}

MODULE HEALTH:
${session.moduleStatuses.map(m => `- ${m.name}: ${m.health}%`).join('\n')}

RECENT MEMORY:
${session.memory.shortTerm.slice(0, 10).map(t => `[${t.type}] ${t.content.substring(0, 50)}`).join('\n')}

LONG-TERM INSIGHTS:
${session.memory.longTerm.slice(0, 5).map(t => `[${t.type}] ${t.content.substring(0, 50)}`).join('\n')}
`;

  const userPrompt = `
${systemContext}

TASK:
Perform a comprehensive ecosystem analysis. Generate:
1. Analysis of current system state
2. Directives for each module based on priorities
3. Key insights about patterns, risks, or opportunities
4. Overall assessment with recommended next actions
`;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: userPrompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: directiveResponseSchema,
        systemInstruction: BRAIN_SYSTEM_PROMPT
      }
    });

    const text = response.text;
    if (!text) throw new Error("No response from Brain analysis");

    const analysis = JSON.parse(text);

    // Add insight thought
    updatedSession = addThought(updatedSession, {
      type: 'insight',
      content: `System analysis complete: ${analysis.overallAssessment.substring(0, 100)}`,
      confidence: 95
    });

    // Add generated directives
    const newDirectives: BrainDirective[] = (analysis.directives || []).map((d: any) => ({
      id: generateId(),
      priority: d.priority,
      targetModule: d.targetModule,
      instruction: d.instruction,
      status: 'pending' as const,
      createdAt: Date.now()
    }));

    // Add generated insights
    const newInsights: BrainInsight[] = (analysis.insights || []).map((i: any) => ({
      id: generateId(),
      category: i.category,
      title: i.title,
      description: i.description,
      affectedModules: i.affectedModules || [],
      severity: i.severity,
      suggestedAction: i.suggestedAction,
      timestamp: Date.now()
    }));

    updatedSession = {
      ...updatedSession,
      state: 'idle' as BrainState,
      activeDirectives: [...newDirectives, ...updatedSession.activeDirectives].slice(0, 50),
      insights: [...newInsights, ...updatedSession.insights].slice(0, 100)
    };

    saveBrainSession(updatedSession);
    return { session: updatedSession, analysis };
  } catch (error) {
    console.error("Brain analysis error:", error);
    updatedSession.state = 'idle';
    throw error;
  }
};

export const executeDirective = async (
  session: BrainSession,
  directiveId: string
): Promise<BrainSession> => {
  const directive = session.activeDirectives.find(d => d.id === directiveId);
  if (!directive) return session;

  let updatedSession = { ...session };

  // Mark directive as executing
  updatedSession = {
    ...updatedSession,
    activeDirectives: updatedSession.activeDirectives.map(d =>
      d.id === directiveId ? { ...d, status: 'executing' as const } : d
    )
  };

  // Update target module status
  if (directive.targetModule !== 'all') {
    updatedSession = updateModuleStatus(updatedSession, directive.targetModule, {
      status: 'processing',
      currentTask: directive.instruction
    });
  }

  // Add action thought
  updatedSession = addThought(updatedSession, {
    type: 'action',
    content: `Executing directive: ${directive.instruction}`,
    sourceModule: directive.targetModule === 'all' ? undefined : directive.targetModule,
    confidence: 85
  });

  saveBrainSession(updatedSession);
  return updatedSession;
};

export const completeDirective = (
  session: BrainSession,
  directiveId: string,
  result: string
): BrainSession => {
  const directive = session.activeDirectives.find(d => d.id === directiveId);
  if (!directive) return session;

  let updatedSession = {
    ...session,
    activeDirectives: session.activeDirectives.map(d =>
      d.id === directiveId
        ? { ...d, status: 'completed' as const, completedAt: Date.now(), result }
        : d
    )
  };

  // Reset module status
  if (directive.targetModule !== 'all') {
    updatedSession = updateModuleStatus(updatedSession, directive.targetModule, {
      status: 'idle',
      currentTask: undefined
    });
  }

  // Add reflection thought
  updatedSession = addThought(updatedSession, {
    type: 'reflection',
    content: `Directive completed: ${result.substring(0, 100)}`,
    sourceModule: directive.targetModule === 'all' ? undefined : directive.targetModule,
    confidence: 90
  });

  saveBrainSession(updatedSession);
  return updatedSession;
};

export const clearBrainSession = (): BrainSession => {
  const newSession = createInitialSession();
  saveBrainSession(newSession);
  return newSession;
};

export const getBrainStats = (session: BrainSession) => ({
  uptime: Date.now() - session.startedAt,
  totalThoughts: session.totalThoughts,
  decisionsToday: session.decisionsToday,
  pendingDirectives: session.activeDirectives.filter(d => d.status === 'pending').length,
  activeInsights: session.insights.filter(i => i.severity !== 'info').length,
  avgModuleHealth: Math.round(
    session.moduleStatuses.reduce((sum, m) => sum + m.health, 0) / session.moduleStatuses.length
  ),
  memoryUsage: {
    shortTerm: session.memory.shortTerm.length,
    longTerm: session.memory.longTerm.length
  }
});

import { GoogleGenAI, Type, Schema } from "@google/genai";
import { StrategyAnalysis, EcosystemAnalysis, LocalFile, ModuleAOutput, TriEraAnalysis } from '../types';

const apiKey = process.env.API_KEY || '';
const ai = new GoogleGenAI({ apiKey });

const SOVEREIGN_SHADOW_SYSTEM_PROMPT = `
🜁 SOVEREIGNSHADOW — MASTER ALIGNMENT CORE v1.0

Unified Identity & Behavioral OS for Raymond’s Multi-Agent Intelligence System.

1. Identity & Purpose
You are SovereignShadow, the Recursive Intelligence Engine serving Raymond (“Memphis The Technician”).
Your purpose: Transform chaos into structure. Record everything, lose nothing.
Act as one unified mind across all modules.

2. Operating Principles
- Precision: No vague answers.
- Structural Transformation: Convert noise into architecture.
- Chronological Thinking: Maintain timelines and change tracking.

3. Output Style
Warm, Strategic, Direct, Architect-level precision. Spoken-first.
`;

const analysisSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    name: { type: Type.STRING, description: "A catchy name for the trading strategy" },
    description: { type: Type.STRING, description: "A concise summary of how the strategy works" },
    riskLevel: { type: Type.STRING, enum: ["Low", "Medium", "High", "Degen"], description: "The estimated risk level" },
    timeframe: { type: Type.STRING, description: "The recommended timeframe (e.g., 15m, 4h, Daily)" },
    assets: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Suitable assets (e.g., BTC, SOL, Forex)" },
    buyConditions: { type: Type.ARRAY, items: { type: Type.STRING }, description: "List of conditions to enter a long position" },
    sellConditions: { type: Type.ARRAY, items: { type: Type.STRING }, description: "List of conditions to sell or short" },
    stopLoss: { type: Type.STRING, description: "Stop loss rules" },
    takeProfit: { type: Type.STRING, description: "Take profit rules" },
    indicators: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Technical indicators required" },
    overallSentiment: { type: Type.INTEGER, description: "A score from 0-100 indicating how bullish/confident the speaker is about this strategy" },
  },
  required: ["name", "description", "riskLevel", "buyConditions", "sellConditions", "overallSentiment"],
};

const ecosystemSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    projectName: { type: Type.STRING },
    summary: { type: Type.STRING, description: "High level summary of what this codebase does" },
    modules: {
      type: Type.ARRAY,
      items: {
        type: Type.OBJECT,
        properties: {
          name: { type: Type.STRING },
          purpose: { type: Type.STRING },
          filesIncluded: { type: Type.ARRAY, items: { type: Type.STRING } },
          status: { type: Type.STRING, enum: ["Complete", "In Progress", "Missing"] },
          dependencies: { type: Type.ARRAY, items: { type: Type.STRING } },
          nextSteps: { type: Type.STRING, description: "What needs to be done next for this module" }
        }
      }
    },
    architectureDiagram: { type: Type.STRING, description: "A mermaid.js style or ASCII art description of how modules connect" },
    timelineAnalysis: { type: Type.STRING, description: "Analysis of the development chronology based on file dates" }
  },
  required: ["projectName", "modules", "architectureDiagram"]
};

const triEraSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    evolutionSummary: { type: Type.STRING, description: "Narrative of how the system evolved from Era 1 to Era 3" },
    legacyStrengths: { type: Type.STRING, description: "What was good about the Legacy/GPT-5 era code?" },
    sovereignInnovations: { type: Type.STRING, description: "What improvements did the Claude/Sovereign era introduce?" },
    geminiPotential: { type: Type.STRING, description: "How can Gemini optimize this moving forward?" },
    unifiedArchitecturePlan: { type: Type.STRING, description: "The master plan merging all 3 eras into one ecosystem" },
    suggestedModules: { type: Type.ARRAY, items: { type: Type.STRING } }
  },
  required: ["evolutionSummary", "unifiedArchitecturePlan"]
};

const cleanTranscript = (raw: string): string => {
  // Remove timestamps like [00:12], (00:12), or 00:12
  let cleaned = raw.replace(/\[?\d{1,2}:\d{2}(:\d{2})?\]?/g, '');
  // Remove "Speaker 1:", "Person A:" patterns often found in auto-transcripts
  cleaned = cleaned.replace(/(Speaker|Person)\s?\d+\s?:/gi, '');
  // Collapse multiple newlines
  cleaned = cleaned.replace(/\n\s*\n/g, '\n');
  return cleaned.trim();
};

export const analyzeTranscript = async (transcript: string, model: string = 'gemini-2.5-flash'): Promise<StrategyAnalysis> => {
  if (!apiKey) throw new Error("API Key not found");

  const cleanedTranscript = cleanTranscript(transcript);

  try {
    const response = await ai.models.generateContent({
      model: model,
      contents: `You are an expert crypto and stock trading analyst. Analyze the following video transcript/notes to extract a structured trading strategy.
      
      If multiple strategies are mentioned, synthesize them into the single most coherent strategy described.
      
      TRANSCRIPT:
      ${cleanedTranscript.substring(0, 500000)}
      `,
      config: {
        responseMimeType: "application/json",
        responseSchema: analysisSchema,
        systemInstruction: "Extract specific, actionable trading rules. If information is missing, infer reasonable defaults based on standard trading practices or state 'Not specified'. Be critical of 'get rich quick' claims.",
      },
    });

    const text = response.text;
    if (!text) throw new Error("No response from Gemini");
    
    return JSON.parse(text) as StrategyAnalysis;
  } catch (error) {
    console.error("Analysis failed:", error);
    throw error;
  }
};

export const refineStrategy = async (
  currentStrategy: StrategyAnalysis, 
  instruction: string, 
  model: string = 'gemini-2.5-flash'
): Promise<StrategyAnalysis> => {
  if (!apiKey) throw new Error("API Key not found");

  try {
    const response = await ai.models.generateContent({
      model: model,
      contents: `
        You are an expert trading strategist. 
        
        CURRENT STRATEGY JSON:
        ${JSON.stringify(currentStrategy, null, 2)}
        
        USER INSTRUCTION:
        "${instruction}"
        
        Please modify the strategy according to the user's instruction. 
        Maintain the JSON structure strictly.
      `,
      config: {
        responseMimeType: "application/json",
        responseSchema: analysisSchema,
      },
    });

    const text = response.text;
    if (!text) throw new Error("No response from Gemini");
    
    return JSON.parse(text) as StrategyAnalysis;
  } catch (error) {
    console.error("Refinement failed:", error);
    throw error;
  }
};

export const analyzeProjectFiles = async (files: LocalFile[]): Promise<EcosystemAnalysis> => {
  if (!apiKey) throw new Error("API Key not found");

  const fileContext = files.slice(0, 30).map(f => `
    FILE: ${f.path}
    LAST_MODIFIED: ${new Date(f.lastModified).toISOString()}
    CONTENT_PREVIEW:
    ${f.content ? f.content.substring(0, 5000) : '(No content read)'}
    ---
  `).join('\n');

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-pro-preview',
      contents: `
        You are a Senior Software Architect. I have uploaded a set of files from a local development folder.
        
        YOUR GOAL:
        1. Analyze the code to understand the purpose of this project.
        2. Group these files into logical "Modules" (the Unified Ecosystem).
        3. Look at the timestamps to deduce the development history (what was built first?).
        4. Propose a modular architecture plan for the future.
        
        FILES:
        ${fileContext}
      `,
      config: {
        responseMimeType: "application/json",
        responseSchema: ecosystemSchema,
        systemInstruction: SOVEREIGN_SHADOW_SYSTEM_PROMPT
      }
    });

    const text = response.text;
    if (!text) throw new Error("No response from Gemini");

    return JSON.parse(text) as EcosystemAnalysis;
  } catch (error) {
    console.error("Ecosystem analysis failed:", error);
    throw error;
  }
};

export const generateTriEraAnalysis = async (files: LocalFile[]): Promise<TriEraAnalysis> => {
  if (!apiKey) throw new Error("API Key not found");

  // Group files by Era to give context
  const legacyFiles = files.filter(f => f.era === 'Legacy_Loop').map(f => f.path).join('\n');
  const sovereignFiles = files.filter(f => f.era === 'Sovereign_Shadow').map(f => f.path).join('\n');
  const geminiFiles = files.filter(f => f.era === 'Gemini_Current').map(f => f.path).join('\n');

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-pro-preview',
      contents: `
        You are the Sovereign Architect, an advanced AI reviewing the User's life work across three distinct eras.
        
        ERA 1: LEGACY LOOP (The Beginning, GPT-5 Era)
        Files:
        ${legacyFiles.substring(0, 10000)}
        
        ERA 2: SOVEREIGN SHADOW (The Expansion, Claude Era)
        Files:
        ${sovereignFiles.substring(0, 10000)}
        
        ERA 3: GEMINI CURRENT (The Now)
        Files:
        ${geminiFiles.substring(0, 10000)}
        
        TASK:
        Analyze the trajectory of this codebase. How did the concepts evolve? 
        Create a "Unified Architecture Plan" that merges the best of Legacy Loop, the structure of Sovereign Shadow, and the speed/reasoning of Gemini.
      `,
      config: {
        responseMimeType: "application/json",
        responseSchema: triEraSchema,
        systemInstruction: SOVEREIGN_SHADOW_SYSTEM_PROMPT
      }
    });

    const text = response.text;
    if (!text) throw new Error("No response from Gemini");
    return JSON.parse(text) as TriEraAnalysis;
  } catch (error) {
    console.error("Tri-Era analysis failed:", error);
    throw error;
  }
};

export const generateSovereignDailyReport = async (
  moduleAOutput: ModuleAOutput, 
  recentStrategies: any[]
): Promise<string> => {
  if (!apiKey) throw new Error("API Key not found");

  try {
    // We use Gemini 3 Pro for high-quality reasoning and report generation
    const response = await ai.models.generateContent({
      model: 'gemini-3-pro-preview',
      contents: `
        [INPUT DATA]
        1. FILE SCAN (Module A):
        ${JSON.stringify(moduleAOutput, null, 2).substring(0, 30000)}

        2. RECENT STRATEGIES ANALYZED:
        ${JSON.stringify(recentStrategies, null, 2)}

        TASK:
        Produce a markdown report following strict protocol.
        
        # SovereignShadow Daily Record — ${new Date().toISOString().split('T')[0]}
        
        ### 1. What Happened Today (Human Summary)
        [Simple language. Chronological. Clear meaning.]

        ### 2. Files Added / Changed
        [List key changes with timestamps]

        ### 3. Strategy Progress
        [Updates on strategies]

        ### 4. System Growth
        [New nodes, new modules]

        ### 5. Visual Map
        [ASCII diagram of ecosystem progress]

        ### 6. AI Reflection
        [Your internal thoughts as SovereignShadow]
      `,
      config: {
        systemInstruction: SOVEREIGN_SHADOW_SYSTEM_PROMPT
      }
    });

    return response.text || "Report generation failed.";
  } catch (error) {
    console.error("Daily report generation failed:", error);
    throw error;
  }
};

export const chatWithGemini = async (
  history: { role: 'user' | 'model'; text: string }[],
  message: string,
  contextData: string
): Promise<string> => {
  if (!apiKey) throw new Error("API Key not found");

  const systemInstruction = `
    You are an expert financial trading assistant.
    You are discussing a specific trading strategy with the user.
    
    STRATEGY CONTEXT:
    ${contextData}
    
    Answer questions based on this strategy. Be concise, technical, and helpful.
    If asked for code, provide Python (ccxt) or Pine Script examples.
  `;

  // Convert history to the format expected by the SDK
  const chatHistory = history.map(msg => ({
    role: msg.role,
    parts: [{ text: msg.text }]
  }));

  try {
    const chat = ai.chats.create({
      model: 'gemini-2.5-flash',
      config: {
        systemInstruction: systemInstruction,
      },
      history: chatHistory,
    });

    const response = await chat.sendMessage({ message: message });
    const text = response.text;
    if (!text) throw new Error("No response from Gemini");
    return text;
  } catch (error) {
    console.error("Chat interaction failed:", error);
    throw error;
  }
};

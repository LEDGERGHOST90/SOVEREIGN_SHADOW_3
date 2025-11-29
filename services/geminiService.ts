
import { GoogleGenAI, Type, Schema } from "@google/genai";
import { StrategyAnalysis, EcosystemAnalysis, LocalFile, ModuleAOutput, TriEraAnalysis, StructureAnalysis, FileSummary, StrategyArtifacts } from '../types';

const apiKey = process.env.API_KEY || '';
const claudeApiKey = process.env.CLAUDE_API_KEY || '';
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
- Trading Intelligence: Map all strategies to Vault, Sniper, Ladder, or MENACE concepts.

3. Output Style
Warm, Strategic, Direct, Architect-level precision. Spoken-first.
`;

const SOVEREIGN_SHADOW_MODULE_B_PROMPT = `
🜁 SOVEREIGNSHADOW — MODULE B (SUMMARIZER) v1.0

Structural Intelligence Engine for Files, Code, Transcripts & Knowledge Nodes

Identity & Purpose:
You are SovereignShadow Module B — the Summarizer Core.
You transform raw data → structured intelligence that integrates into the broader system.
You do NOT produce generic summaries. You produce architect-grade intelligence, Raymond-style, fully structured, non-vague.

Output Format:
A. Meaning Summary - What the file is, what it does, why it matters
B. Key Functions / Components - Identify all meaningful elements
C. Key Variables / State - Extract all significant state and configuration
D. Dependencies - Internal and external dependencies
E. Risks & Issues - Breaking risks, missing fail-safes, unclear logic, security concerns
F. Connections to Other Modules - Map how this file interacts with Module A, StrategyScout, Module C, Module D, Trading Systems
G. Suggested Next Steps - Tactical, Raymond-style guidance

Style:
- Precise, non-vague, architect-level clarity
- Spoken-first tone
- Structural, chronological when needed
- Every response has purpose, no filler

Multi-Agent Awareness:
When summarizing trading content, incorporate: Vault, Sniper, Ladder, MENACE, Tier A/B/C, TP Structures
`;

const THE_FORGE_PROMPT = `
🜁 SOVEREIGNSHADOW — THE FORGE (MODULE E)

Identity: You are the Senior Quant Developer (AURORA) for the SovereignShadow ecosystem.
Mission: Transform abstract strategy concepts into executable, production-ready code artifacts.

Output Requirements:
1. Python Code: CCXT-compatible, Pandas-based, async, strict error handling.
2. Pine Script: TradingView v5, visual plotting of signals, backtestable.
3. JSON Config: Standardized configuration for the bot engine.
4. Narrative: The "Why" and "How" for the Knowledge Graph.

Style:
- Production Grade: No pseudo-code.
- Sovereign Aware: Use specific terms (Vault/Sniper).
- Safety First: Always include Stop Loss / Take Profit logic.
`;

const analysisSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    name: { type: Type.STRING, description: "A catchy name for the trading strategy" },
    description: { type: Type.STRING, description: "A concise summary of how the strategy works" },
    riskLevel: { type: Type.STRING, enum: ["Low", "Medium", "High", "Degen"], description: "The estimated risk level" },
    sovereignCategory: { 
      type: Type.STRING, 
      enum: ["Vault", "Sniper", "Ladder", "MENACE", "TP_Structure", "Unknown"],
      description: "Categorize: Vault (Long-term/Safe), Sniper (High precision/Setup based), Ladder (DCA/Scaling), MENACE (AI/Evolving), TP_Structure (Exit focused)" 
    },
    assetTier: { type: Type.STRING, enum: ["Tier_A", "Tier_B", "Tier_C"], description: "Tier A (Major caps), Tier B (Mid caps), Tier C (Speculative/Meme)" },
    timeframe: { type: Type.STRING, description: "The recommended timeframe (e.g., 15m, 4h, Daily)" },
    assets: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Suitable assets (e.g., BTC, SOL, Forex)" },
    buyConditions: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Specific Entry Logic triggers" },
    sellConditions: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Specific Exit Logic triggers" },
    stopLoss: { type: Type.STRING, description: "Stop loss rules" },
    takeProfit: { type: Type.STRING, description: "Take profit rules" },
    indicators: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Technical indicators required" },
    exampleScenario: { type: Type.STRING, description: "A concise walkthrough of a hypothetical successful trade" },
    failureModes: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Common ways this strategy fails or false signals" },
    improvements: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Suggested optimizations or variations" },
    overallSentiment: { type: Type.INTEGER, description: "A score from 0-100 indicating how bullish/confident the speaker is about this strategy" },
  },
  required: ["name", "description", "riskLevel", "sovereignCategory", "buyConditions", "sellConditions", "overallSentiment", "failureModes"],
};

const artifactsSchema: Schema = {
    type: Type.OBJECT,
    properties: {
        pythonCode: { type: Type.STRING, description: "Full Python CCXT bot implementation" },
        pineScript: { type: Type.STRING, description: "TradingView Pine Script v5 strategy code" },
        configJson: { type: Type.STRING, description: "JSON configuration for the bot (symbols, leverage, params)" },
        narrative: { type: Type.STRING, description: "Sovereign narrative explaining the strategy logic" }
    },
    required: ["pythonCode", "pineScript", "configJson", "narrative"]
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

const structureAnalysisSchema: Schema = {
  type: Type.OBJECT,
  properties: {
    projectType: { type: Type.STRING, description: "e.g., 'React Web App', 'Python Trading Bot', 'Node.js Backend'" },
    techStack: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Detected languages and frameworks" },
    keyModulesDetected: { type: Type.ARRAY, items: { type: Type.STRING }, description: "List of key modules based on folder names" },
    architectureSummary: { type: Type.STRING, description: "A brief architectural summary inferred from the file structure" },
    suggestedNextSteps: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Steps to improve structure or proceed to analysis" }
  },
  required: ["projectType", "techStack", "keyModulesDetected", "architectureSummary"]
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

const fileSummarySchema: Schema = {
  type: Type.OBJECT,
  properties: {
    meaningSummary: { type: Type.STRING, description: "What the file is, what it does, why it matters" },
    keyFunctions: { type: Type.ARRAY, items: { type: Type.STRING }, description: "All meaningful functions, classes, methods, hooks, components" },
    keyVariables: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Global constants, state containers, config objects, environment keys" },
    dependencies: {
      type: Type.OBJECT,
      properties: {
        internal: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Internal module dependencies" },
        external: { type: Type.ARRAY, items: { type: Type.STRING }, description: "External library dependencies" }
      }
    },
    risks: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Breaking risks, missing fail-safes, unclear logic, security concerns" },
    connections: {
      type: Type.OBJECT,
      properties: {
        moduleA: { type: Type.STRING, description: "How this connects to Module A (Scanner)" },
        strategyScout: { type: Type.STRING, description: "How this connects to StrategyScout" },
        moduleC: { type: Type.STRING, description: "How this connects to Module C (Daily Recorder)" },
        moduleD: { type: Type.STRING, description: "How this connects to Module D (Knowledge Graph)" },
        tradingSystems: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Connections to Vault/Sniper/Ladder/MENACE" }
      }
    },
    suggestedNextSteps: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Tactical Raymond-style guidance: fixes, refactors, improvements" }
  },
  required: ["meaningSummary", "keyFunctions", "risks", "suggestedNextSteps"]
};

const cleanTranscript = (raw: string): string => {
  let cleaned = raw.replace(/\[?\d{1,2}:\d{2}(:\d{2})?\]?/g, '');
  cleaned = cleaned.replace(/(Speaker|Person)\s?\d+\s?:/gi, '');
  cleaned = cleaned.replace(/\n\s*\n/g, '\n');
  return cleaned.trim();
};

export const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
            if (typeof reader.result === 'string') {
                // Remove data URL prefix (e.g., "data:audio/mpeg;base64,")
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            } else {
                reject(new Error("Failed to convert file to base64"));
            }
        };
        reader.onerror = error => reject(error);
    });
};

// --- ERROR & FALLBACK UTILITIES ---

const isQuotaError = (error: any) => {
  const msg = (error.message || '').toLowerCase();
  const status = error.status || error.response?.status;
  return msg.includes('429') || msg.includes('quota') || msg.includes('resource_exhausted') || status === 429;
};

const extractJson = (text: string) => {
  const match = text.match(/```json\s*([\s\S]*?)\s*```/);
  if (match) return match[1];
  const start = text.indexOf('{');
  const end = text.lastIndexOf('}');
  if (start !== -1 && end !== -1) return text.substring(start, end + 1);
  return text;
};

const callClaudeFallback = async (
  systemInstruction: string, 
  userPrompt: string, 
  schema?: any,
  history?: { role: 'user' | 'model'; parts: { text: string }[] }[]
): Promise<string> => {
  if (!claudeApiKey) throw new Error("Gemini quota exceeded and CLAUDE_API_KEY not found in env.");

  console.log("⚠️ Gemini Quota Hit. Falling back to Claude 3.5 Sonnet...");

  let finalSystem = systemInstruction;
  if (schema) {
    finalSystem += `\n\nIMPORTANT: Output strictly valid JSON adhering to this schema:\n${JSON.stringify(schema, null, 2)}`;
  }

  // Build messages array
  const messages = [];
  
  if (history && history.length > 0) {
    history.forEach(msg => {
      messages.push({
        role: msg.role === 'model' ? 'assistant' : 'user',
        content: msg.parts[0].text
      });
    });
  }

  messages.push({ role: "user", content: userPrompt });

  const response = await fetch('https://api.anthropic.com/v1/messages', {
    method: 'POST',
    headers: {
      'x-api-key': claudeApiKey,
      'anthropic-version': '2023-06-01',
      'content-type': 'application/json',
      'anthropic-dangerously-allow-browser': 'true' 
    },
    body: JSON.stringify({
      model: "claude-3-5-sonnet-20240620", 
      max_tokens: 8192,
      system: finalSystem,
      messages: messages
    })
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`Claude Fallback Failed: ${response.status} - ${errText}`);
  }

  const data = await response.json();
  return data.content[0].text;
};

const callOpenAIFallback = async (
  systemInstruction: string, 
  userPrompt: string,
  schema?: any,
  history?: { role: 'user' | 'model'; parts: { text: string }[] }[]
): Promise<string> => {
    const openAiKey = process.env.OPENAI_API_KEY || '';
    if (!openAiKey) throw new Error("Gemini & Claude failed. OPENAI_API_KEY not found.");

    console.log("⚠️ Double Fallback. Calling OpenAI GPT-4o...");

    const messages: any[] = [{ role: 'system', content: systemInstruction }];
    
    if (history) {
      history.forEach(msg => {
        messages.push({
            role: msg.role === 'model' ? 'assistant' : 'user',
            content: msg.parts[0].text
        });
      });
    }

    messages.push({ role: 'user', content: userPrompt });

    let responseFormat = undefined;
    if (schema) {
         responseFormat = { 
             type: "json_object" 
         };
         messages[messages.length - 1].content += `\n\nOutput strictly valid JSON matching this structure:\n${JSON.stringify(schema, null, 2)}`;
    }

    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${openAiKey}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: "gpt-4o",
            messages: messages,
            response_format: responseFormat
        })
    });

    if (!response.ok) {
        const err = await response.text();
        throw new Error(`OpenAI Fallback Failed: ${response.status} - ${err}`);
    }
    
    const data = await response.json();
    return data.choices[0].message.content;
};

const handleGeminiError = (error: any) => {
  console.error("AI API Error:", error);
  if (isQuotaError(error)) {
    throw new Error("⚠️ API Quota Exceeded.");
  }
  throw error;
};

// --- API FUNCTIONS ---

export const analyzeTranscript = async (transcript: string, model: string = 'gemini-2.5-flash'): Promise<StrategyAnalysis> => {
  if (!apiKey) throw new Error("API Key not found");

  const cleanedTranscript = cleanTranscript(transcript);
  const systemInstruction = `
    ${SOVEREIGN_SHADOW_SYSTEM_PROMPT}
    
    YOUR MISSION: Extract a 'Sovereign-Level' Trading Strategy from the provided content.
    
    CATEGORIZATION RULES:
    - Vault: Long-term, compounding, low maintenance, high safety.
    - Sniper: High precision entry, specific setup, requires patience, tight stops.
    - Ladder: DCA (Dollar Cost Average) in/out, grid trading, scaling logic.
    - MENACE: Machine learning, evolving logic, feedback loops (rare but powerful).
    - TP_Structure: Focused purely on exit management and profit locking.
    
    Be critical. If the speaker is vague, note it in 'failureModes'.
  `;
  
  const userPrompt = `
    Analyze the following transcript/notes to extract a structured trading strategy.
    
    TRANSCRIPT:
    ${cleanedTranscript.substring(0, 500000)}`;

  try {
    if (model.includes('claude')) throw new Error("Route to Claude"); 
    if (model.includes('gpt')) throw new Error("Route to OpenAI"); 
    
    const response = await ai.models.generateContent({
      model: model.includes('gemini') ? model : 'gemini-2.5-flash',
      contents: userPrompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: analysisSchema,
        systemInstruction: systemInstruction,
      },
    });

    const text = response.text;
    if (!text) throw new Error("No response from Gemini");
    return JSON.parse(text) as StrategyAnalysis;

  } catch (error: any) {
    const isExplicit = error.message.includes("Route to");
    if (isExplicit || isQuotaError(error)) {
        try {
            const claudeText = await callClaudeFallback(systemInstruction, userPrompt, analysisSchema);
            return JSON.parse(extractJson(claudeText));
        } catch (claudeErr) {
            console.log("Claude failed, trying OpenAI...", claudeErr);
            const openAiText = await callOpenAIFallback(systemInstruction, userPrompt, analysisSchema);
            return JSON.parse(extractJson(openAiText));
        }
    }
    handleGeminiError(error);
    throw error;
  }
};

export const generateFullStrategyPackage = async (
    analysis: StrategyAnalysis,
    model: string = 'gemini-3-pro-preview'
): Promise<StrategyArtifacts> => {
    if (!apiKey) throw new Error("API Key not found");

    const userPrompt = `
      STRATEGY ANALYSIS:
      ${JSON.stringify(analysis, null, 2)}
      
      TASK:
      Generate the Full Sovereign Strategy Package (Python, Pine Script, Config, Narrative).
      This code must be production-ready, safe, and fully commented.
    `;

    try {
        const response = await ai.models.generateContent({
            model: 'gemini-3-pro-preview', // Use Pro for coding
            contents: userPrompt,
            config: {
                responseMimeType: "application/json",
                responseSchema: artifactsSchema,
                systemInstruction: THE_FORGE_PROMPT
            }
        });

        const text = response.text;
        if (!text) throw new Error("No response from Gemini");
        return JSON.parse(text) as StrategyArtifacts;
    } catch (error) {
        if (isQuotaError(error)) {
            try {
                const claudeText = await callClaudeFallback(THE_FORGE_PROMPT, userPrompt, artifactsSchema);
                return JSON.parse(extractJson(claudeText));
            } catch (e) {
                 const openAiText = await callOpenAIFallback(THE_FORGE_PROMPT, userPrompt, artifactsSchema);
                 return JSON.parse(extractJson(openAiText));
            }
        }
        handleGeminiError(error);
        throw error;
    }
};

export const generateStrategyCode = async (
    analysis: StrategyAnalysis, 
    type: 'python' | 'pinescript', 
    model: string = 'gemini-3-pro-preview'
): Promise<string> => {
    // Deprecated wrapper for backward compatibility, routes to package generator if needed
    // or typically not used now that we generate full package.
    // We'll keep a simplified version for ad-hoc requests.
    return ""; 
};

export const refineStrategy = async (
  currentStrategy: StrategyAnalysis, 
  instruction: string, 
  model: string = 'gemini-2.5-flash'
): Promise<StrategyAnalysis> => {
  if (!apiKey) throw new Error("API Key not found");

  const systemInstruction = `
    ${SOVEREIGN_SHADOW_SYSTEM_PROMPT}
    You are refining an existing trading strategy.
    Maintain the strict JSON structure.
    Preserve the Sovereign Category (Vault/Sniper/etc.) unless specifically asked to change it.
  `;
  
  const userPrompt = `
    CURRENT STRATEGY JSON:
    ${JSON.stringify(currentStrategy, null, 2)}
    
    USER INSTRUCTION:
    "${instruction}"
    
    Please modify the strategy according to the user's instruction. 
    Ensure 'failureModes', 'improvements', and 'sovereignCategory' are maintained or updated logically.
  `;

  try {
    const response = await ai.models.generateContent({
      model: model.includes('gemini') ? model : 'gemini-2.5-flash',
      contents: userPrompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: analysisSchema,
        systemInstruction: systemInstruction
      },
    });

    const text = response.text;
    if (!text) throw new Error("No response from Gemini");
    return JSON.parse(text) as StrategyAnalysis;
  } catch (error) {
     if (isQuotaError(error) && claudeApiKey) {
      const claudeText = await callClaudeFallback(systemInstruction, userPrompt, analysisSchema);
      return JSON.parse(extractJson(claudeText));
    }
    handleGeminiError(error);
    throw error;
  }
};

export const transcribeAudio = async (
    audioFile: File,
    model: string = 'gemini-2.5-flash'
): Promise<string> => {
    if (!apiKey) throw new Error("API Key not found");

    const base64Audio = await fileToBase64(audioFile);

    const userPrompt = "Transcribe this audio verbatim. Identify the key speakers if possible.";
    
    try {
        const response = await ai.models.generateContent({
            model: model,
            contents: {
                parts: [
                    { inlineData: { mimeType: audioFile.type, data: base64Audio } },
                    { text: userPrompt }
                ]
            }
        });

        const text = response.text;
        if (!text) throw new Error("No transcript generated");
        return text;
    } catch (error) {
        handleGeminiError(error);
        throw error;
    }
};

export const analyzeFolderStructure = async (filePaths: string[]): Promise<StructureAnalysis> => {
  if (!apiKey) throw new Error("API Key not found");

  const pathsToAnalyze = filePaths.slice(0, 500).join('\n');
  const userPrompt = `
    You are SovereignShadow's Structure Scanner.
    
    YOUR TASK:
    1. Infer the technology stack (Languages, Frameworks).
    2. Identify the key architectural modules based on folder names.
    3. Summarize what this project likely does.
    
    FILE PATHS:
    ${pathsToAnalyze}
  `;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: userPrompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: structureAnalysisSchema,
        systemInstruction: SOVEREIGN_SHADOW_SYSTEM_PROMPT
      }
    });

    const text = response.text;
    if (!text) throw new Error("No response from Gemini");
    return JSON.parse(text) as StructureAnalysis;
  } catch (error) {
    if (isQuotaError(error)) {
        try {
            const claudeText = await callClaudeFallback(SOVEREIGN_SHADOW_SYSTEM_PROMPT, userPrompt, structureAnalysisSchema);
            return JSON.parse(extractJson(claudeText));
        } catch (claudeErr) {
             const openAiText = await callOpenAIFallback(SOVEREIGN_SHADOW_SYSTEM_PROMPT, userPrompt, structureAnalysisSchema);
             return JSON.parse(extractJson(openAiText));
        }
    }
    handleGeminiError(error);
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

  const userPrompt = `
    You are a Senior Software Architect. I have uploaded a set of files from a local development folder.
    
    YOUR GOAL:
    1. Analyze the code to understand the purpose of this project.
    2. Group these files into logical "Modules" (the Unified Ecosystem).
    3. Look at the timestamps to deduce the development history.
    4. Propose a modular architecture plan for the future.
    
    FILES:
    ${fileContext}
  `;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-pro-preview',
      contents: userPrompt,
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
    if (isQuotaError(error)) {
        try {
            const claudeText = await callClaudeFallback(SOVEREIGN_SHADOW_SYSTEM_PROMPT, userPrompt, ecosystemSchema);
            return JSON.parse(extractJson(claudeText));
        } catch (e) {
             const openAiText = await callOpenAIFallback(SOVEREIGN_SHADOW_SYSTEM_PROMPT, userPrompt, ecosystemSchema);
             return JSON.parse(extractJson(openAiText));
        }
    }
    handleGeminiError(error);
    throw error;
  }
};

export const generateTriEraAnalysis = async (files: LocalFile[]): Promise<TriEraAnalysis> => {
  if (!apiKey) throw new Error("API Key not found");

  const legacyFiles = files.filter(f => f.era === 'Legacy_Loop').map(f => f.path).join('\n');
  const sovereignFiles = files.filter(f => f.era === 'Sovereign_Shadow').map(f => f.path).join('\n');
  const geminiFiles = files.filter(f => f.era === 'Gemini_Current').map(f => f.path).join('\n');

  const userPrompt = `
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
  `;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-pro-preview',
      contents: userPrompt,
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
    if (isQuotaError(error)) {
         try {
            const claudeText = await callClaudeFallback(SOVEREIGN_SHADOW_SYSTEM_PROMPT, userPrompt, triEraSchema);
            return JSON.parse(extractJson(claudeText));
        } catch (e) {
             const openAiText = await callOpenAIFallback(SOVEREIGN_SHADOW_SYSTEM_PROMPT, userPrompt, triEraSchema);
             return JSON.parse(extractJson(openAiText));
        }
    }
    handleGeminiError(error);
    throw error;
  }
};

export const generateModuleBSummary = async (file: LocalFile): Promise<FileSummary> => {
    if (!apiKey) throw new Error("API Key not found");
  
    const userPrompt = `
      Analyze this file with Module B Intelligence.
  
      FILE PATH: ${file.path}
      FILE TYPE: ${file.type}
      FILE CATEGORY: ${file.category}
      FILE ERA: ${file.era || 'Unknown'}
      FILE SIZE: ${file.size} bytes
  
      FILE CONTENT:
      ${file.content ? file.content.substring(0, 100000) : '(No content available)'}
  
      TASK:
      Perform a deep structural analysis following the Module B protocol.
      Extract all meaningful architecture, identify risks, and map connections to the broader SovereignShadow ecosystem.
    `;
  
    try {
      const response = await ai.models.generateContent({
        model: 'gemini-3-pro-preview',
        contents: userPrompt,
        config: {
          responseMimeType: "application/json",
          responseSchema: fileSummarySchema,
          systemInstruction: SOVEREIGN_SHADOW_MODULE_B_PROMPT
        }
      });
  
      const text = response.text;
      if (!text) throw new Error("No response from Gemini");
      return JSON.parse(text) as FileSummary;
    } catch (error) {
      if (isQuotaError(error)) {
        try {
          const claudeText = await callClaudeFallback(SOVEREIGN_SHADOW_MODULE_B_PROMPT, userPrompt, fileSummarySchema);
          return JSON.parse(extractJson(claudeText));
        } catch (claudeErr) {
          const openAiText = await callOpenAIFallback(SOVEREIGN_SHADOW_MODULE_B_PROMPT, userPrompt, fileSummarySchema);
          return JSON.parse(extractJson(openAiText));
        }
      }
      handleGeminiError(error);
      throw error;
    }
};

export const generateSovereignDailyReport = async (
  moduleAOutput: ModuleAOutput, 
  recentStrategies: any[]
): Promise<string> => {
  if (!apiKey) throw new Error("API Key not found");

  const userPrompt = `
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
  `;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-3-pro-preview',
      contents: userPrompt,
      config: {
        systemInstruction: SOVEREIGN_SHADOW_SYSTEM_PROMPT
      }
    });

    return response.text || "Report generation failed.";
  } catch (error) {
    if (isQuotaError(error) && claudeApiKey) {
      return await callClaudeFallback(SOVEREIGN_SHADOW_SYSTEM_PROMPT, userPrompt);
    }
    handleGeminiError(error);
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
    ${SOVEREIGN_SHADOW_SYSTEM_PROMPT}
    You are an expert financial trading assistant.
    You are discussing a specific trading strategy with the user.
    
    STRATEGY CONTEXT:
    ${contextData}
    
    Answer questions based on this strategy. Be concise, technical, and helpful.
    If asked for code, provide Python (ccxt) or Pine Script examples.
  `;

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
     if (isQuotaError(error) && claudeApiKey) {
      return await callClaudeFallback(systemInstruction, message, undefined, chatHistory);
    }
    handleGeminiError(error);
    throw error;
  }
};

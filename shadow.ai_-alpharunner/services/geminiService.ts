
import { GoogleGenAI, Type } from "@google/genai";
import { 
  StrategyAnalysis, 
  StrategyArtifacts, 
  TradingAlert, 
  ModuleAOutput, 
  Strategy, 
  StructureAnalysis, 
  TriEraAnalysis, 
  LocalFile, 
  FileSummary,
  LegacyLoopData,
  DSAnalysis
} from '../types';

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

// Helper to convert file to base64 for Gemini
const fileToPart = async (file: File) => {
    return new Promise<{ inlineData: { data: string; mimeType: string } }>((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
            const base64String = (reader.result as string).split(',')[1];
            resolve({
                inlineData: {
                    data: base64String,
                    mimeType: file.type
                }
            });
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
};

export const transcribeAudio = async (file: File, modelName: string = 'gemini-3-flash-preview'): Promise<string> => {
    try {
        const audioPart = await fileToPart(file);
        const response = await ai.models.generateContent({
            model: modelName,
            contents: {
                parts: [
                    audioPart,
                    { text: "Transcribe this audio file into a clear, readable text transcript. Identify speakers if possible." }
                ]
            }
        });
        return response.text || "No transcription generated.";
    } catch (error: any) {
        console.error("Transcription error:", error);
        throw new Error("Failed to transcribe audio: " + error.message);
    }
};

export const analyzeTranscript = async (transcript: string, modelName: string = 'gemini-3-pro-preview'): Promise<StrategyAnalysis> => {
    const response = await ai.models.generateContent({
        model: modelName,
        contents: `Analyze this trading strategy transcript and extract structured data.
        
        Transcript: "${transcript}"
        
        Provide the output in JSON format matching the schema.`,
        config: {
            responseMimeType: "application/json",
            thinkingConfig: modelName === 'gemini-3-pro-preview' ? { thinkingBudget: 32768 } : undefined,
            responseSchema: {
                type: Type.OBJECT,
                properties: {
                    name: { type: Type.STRING },
                    description: { type: Type.STRING },
                    riskLevel: { type: Type.STRING, enum: ['Low', 'Medium', 'High', 'Degen'] },
                    sovereignCategory: { type: Type.STRING, enum: ['Vault', 'Sniper', 'Ladder', 'MENACE', 'TP_Structure', 'Unknown'] },
                    assetTier: { type: Type.STRING, enum: ['Tier_A', 'Tier_B', 'Tier_C'] },
                    timeframe: { type: Type.STRING },
                    assets: { type: Type.ARRAY, items: { type: Type.STRING } },
                    buyConditions: { type: Type.ARRAY, items: { type: Type.STRING } },
                    sellConditions: { type: Type.ARRAY, items: { type: Type.STRING } },
                    stopLoss: { type: Type.STRING },
                    takeProfit: { type: Type.STRING },
                    indicators: { type: Type.ARRAY, items: { type: Type.STRING } },
                    exampleScenario: { type: Type.STRING },
                    failureModes: { type: Type.ARRAY, items: { type: Type.STRING } },
                    improvements: { type: Type.ARRAY, items: { type: Type.STRING } },
                    overallSentiment: { type: Type.NUMBER },
                }
            }
        }
    });

    if (!response.text) throw new Error("No analysis generated");
    return JSON.parse(response.text) as StrategyAnalysis;
};

export const synthesizeMultiAnalysis = async (
    developerName: string, 
    inputs: { url: string, content: string }[], 
    modelName: string = 'gemini-3-pro-preview'
): Promise<StrategyAnalysis> => {
    let combinedPrompt = `You are a Trading Strategy Architect. 
    I have provided multiple transcripts/notes from a specific developer named "${developerName}".
    
    Your goal is to synthesize a "Unified Master Strategy" that represents their core trading philosophy.
    Look for patterns across the videos. Resolve any contradictions by prioritizing the most recent or robust logic.
    
    INPUTS:
    `;

    inputs.forEach((input, index) => {
        combinedPrompt += `\n--- SOURCE ${index + 1} (${input.url || 'No URL'}) ---\n${input.content.substring(0, 15000)}\n`;
    });

    combinedPrompt += `\n\nGenerate a single, cohesive StrategyAnalysis JSON object.`;

    const response = await ai.models.generateContent({
        model: modelName,
        contents: combinedPrompt,
        config: {
            responseMimeType: "application/json",
            thinkingConfig: modelName === 'gemini-3-pro-preview' ? { thinkingBudget: 32768 } : undefined,
            responseSchema: {
                type: Type.OBJECT,
                properties: {
                    name: { type: Type.STRING },
                    description: { type: Type.STRING },
                    riskLevel: { type: Type.STRING, enum: ['Low', 'Medium', 'High', 'Degen'] },
                    sovereignCategory: { type: Type.STRING, enum: ['Vault', 'Sniper', 'Ladder', 'MENACE', 'TP_Structure', 'Unknown'] },
                    assetTier: { type: Type.STRING, enum: ['Tier_A', 'Tier_B', 'Tier_C'] },
                    timeframe: { type: Type.STRING },
                    assets: { type: Type.ARRAY, items: { type: Type.STRING } },
                    buyConditions: { type: Type.ARRAY, items: { type: Type.STRING } },
                    sellConditions: { type: Type.ARRAY, items: { type: Type.STRING } },
                    stopLoss: { type: Type.STRING },
                    takeProfit: { type: Type.STRING },
                    indicators: { type: Type.ARRAY, items: { type: Type.STRING } },
                    exampleScenario: { type: Type.STRING },
                    failureModes: { type: Type.ARRAY, items: { type: Type.STRING } },
                    improvements: { type: Type.ARRAY, items: { type: Type.STRING } },
                    overallSentiment: { type: Type.NUMBER },
                }
            }
        }
    });

    if (!response.text) throw new Error("Synthesis failed");
    return JSON.parse(response.text) as StrategyAnalysis;
};

export const generateFullStrategyPackage = async (analysis: StrategyAnalysis, modelName: string = 'gemini-3-pro-preview'): Promise<StrategyArtifacts> => {
    // Attempt to pull user context from local storage to personalize the bot
    const userFinancialsStr = localStorage.getItem('sovereignState');
    let userContext = "";
    if (userFinancialsStr) {
        try {
            const data = JSON.parse(userFinancialsStr) as LegacyLoopData;
            const assets = Object.keys(data.portfolio.allocation.current);
            userContext = `\nUSER HOLDINGS: The user currently has positions in ${assets.join(', ')}. Customize the logic to prioritize these assets for execution.`;
        } catch (e) {}
    }

    const prompt = `
    Forge a professional-grade trading package based on this strategy.
    ${userContext}
    
    Strategy Data: ${JSON.stringify(analysis)}
    
    Deliver:
    1. Python Code: CCXT + AsyncIO, error handling, leverage settings.
    2. Pine Script v5: Full TradingView strategy with visual labels.
    3. JSON Config: System parameters for a local execution runner.
    4. Narrative: A "G.I.O." persona breakdown of how this integrates with the Sovereign Shadow 3 architecture.
    `;

    const response = await ai.models.generateContent({
        model: modelName,
        contents: prompt,
        config: {
            responseMimeType: "application/json",
            thinkingConfig: { thinkingBudget: 32768 },
            responseSchema: {
                type: Type.OBJECT,
                properties: {
                    pythonCode: { type: Type.STRING },
                    pineScript: { type: Type.STRING },
                    configJson: { type: Type.STRING },
                    narrative: { type: Type.STRING }
                }
            }
        }
    });

    if (!response.text) throw new Error("Artifact generation failed");
    return JSON.parse(response.text) as StrategyArtifacts;
};

export const chatWithGemini = async (history: {role: 'user'|'model', text: string}[], message: string, context: string, useThinking: boolean = false): Promise<string> => {
    const systemInstruction = `You are the Google Interface Operator (G.I.O.). You are part of the Sovereign Shadow 3 swarm. Answer queries about strategy entry/exit logic, coding, and market regimes based on this context: ${context}`;
    
    const chat = ai.chats.create({
        model: 'gemini-3-pro-preview',
        config: {
            systemInstruction,
            thinkingConfig: useThinking ? { thinkingBudget: 32768 } : undefined
        },
        history: history.map(h => ({
            role: h.role,
            parts: [{ text: h.text }]
        }))
    });

    const result = await chat.sendMessage({ message });
    return result.text || "Communication error.";
};

export const refineStrategy = async (currentAnalysis: StrategyAnalysis, refinementPrompt: string, modelName: string): Promise<StrategyAnalysis> => {
    const prompt = `
    Refine the following strategy analysis based on this directive: "${refinementPrompt}".
    
    Current State: ${JSON.stringify(currentAnalysis)}
    
    Return the updated JSON.
    `;

    const response = await ai.models.generateContent({
        model: modelName,
        contents: prompt,
        config: {
            responseMimeType: "application/json",
            thinkingConfig: modelName === 'gemini-3-pro-preview' ? { thinkingBudget: 32768 } : undefined,
            responseSchema: {
                type: Type.OBJECT,
                properties: {
                    name: { type: Type.STRING },
                    description: { type: Type.STRING },
                    riskLevel: { type: Type.STRING, enum: ['Low', 'Medium', 'High', 'Degen'] },
                    sovereignCategory: { type: Type.STRING, enum: ['Vault', 'Sniper', 'Ladder', 'MENACE', 'TP_Structure', 'Unknown'] },
                    assetTier: { type: Type.STRING, enum: ['Tier_A', 'Tier_B', 'Tier_C'] },
                    timeframe: { type: Type.STRING },
                    assets: { type: Type.ARRAY, items: { type: Type.STRING } },
                    buyConditions: { type: Type.ARRAY, items: { type: Type.STRING } },
                    sellConditions: { type: Type.ARRAY, items: { type: Type.STRING } },
                    stopLoss: { type: Type.STRING },
                    takeProfit: { type: Type.STRING },
                    indicators: { type: Type.ARRAY, items: { type: Type.STRING } },
                    exampleScenario: { type: Type.STRING },
                    failureModes: { type: Type.ARRAY, items: { type: Type.STRING } },
                    improvements: { type: Type.ARRAY, items: { type: Type.STRING } },
                    overallSentiment: { type: Type.NUMBER },
                }
            }
        }
    });

    if (!response.text) throw new Error("Refinement failed");
    return JSON.parse(response.text) as StrategyAnalysis;
};

export const generateSovereignDailyReport = async (
    moduleAData: ModuleAOutput | null, 
    strategies: Strategy[],
    legacyData?: LegacyLoopData
): Promise<string> => {
    const filesContext = moduleAData 
        ? `- Files Scanned: ${moduleAData.files.length}\n- Timeline Snippet: ${JSON.stringify(moduleAData.timeline_view.slice(0, 2))}`
        : "- File Scan: Blind";

    const financialContext = legacyData
        ? `- NW: $${legacyData.portfolio.net_worth}\n- AAVE Health: ${legacyData.portfolio.aave.health_factor}`
        : "- Financials: Offline";

    const prompt = `
    Generate a "Shadow Log Entry" for today.
    
    CONTEXT:
    ${filesContext}
    ${financialContext}
    - Strategies: ${strategies.map(s => s.analysis.name).join(', ')}
    
    Tone: Cyberpunk/Autonomous Agent. Voice: SovereignShadow.
    Sections: System Health, Intel Progress, Tactical Directives.
    `;

    const response = await ai.models.generateContent({
        model: 'gemini-3-pro-preview',
        contents: prompt,
        config: {
            thinkingConfig: { thinkingBudget: 32768 }
        }
    });

    return response.text || "Daily log failed.";
};

export const analyzeFolderStructure = async (filePaths: string[]): Promise<StructureAnalysis> => {
    const response = await ai.models.generateContent({
        model: 'gemini-3-pro-preview',
        contents: `Analyze these file paths for architectural patterns: ${JSON.stringify(filePaths.slice(0, 400))}`,
        config: {
            responseMimeType: "application/json",
            thinkingConfig: { thinkingBudget: 32768 },
            responseSchema: {
                type: Type.OBJECT,
                properties: {
                    projectType: { type: Type.STRING },
                    techStack: { type: Type.ARRAY, items: { type: Type.STRING } },
                    keyModulesDetected: { type: Type.ARRAY, items: { type: Type.STRING } },
                    architectureSummary: { type: Type.STRING },
                    suggestedNextSteps: { type: Type.ARRAY, items: { type: Type.STRING } },
                }
            }
        }
    });

    if (!response.text) throw new Error("Architecture scan failed");
    return JSON.parse(response.text) as StructureAnalysis;
};

export const generateTriEraAnalysis = async (files: LocalFile[]): Promise<TriEraAnalysis> => {
    const response = await ai.models.generateContent({
        model: 'gemini-3-pro-preview',
        contents: `Analyze system evolution across eras. Files: ${files.length}`,
        config: {
            responseMimeType: "application/json",
            thinkingConfig: { thinkingBudget: 32768 },
            responseSchema: {
                type: Type.OBJECT,
                properties: {
                    evolutionSummary: { type: Type.STRING },
                    legacyStrengths: { type: Type.STRING },
                    sovereignInnovations: { type: Type.STRING },
                    geminiPotential: { type: Type.STRING },
                    unifiedArchitecturePlan: { type: Type.STRING },
                    suggestedModules: { type: Type.ARRAY, items: { type: Type.STRING } },
                }
            }
        }
    });

    if (!response.text) throw new Error("Evolution analysis failed");
    return JSON.parse(response.text) as TriEraAnalysis;
};

export const runDSStarAnalysis = async (
    technicalData: string,
    fundamentalData: string,
    sentimentData: string
): Promise<DSAnalysis> => {
    const prompt = `
    DS-STAR Fusion Engine: Heterogeneous Data Synthesis.
    Inputs: Tech(${technicalData.length} bytes), Fund(${fundamentalData.length} bytes), Sent(${sentimentData.length} bytes).
    Synthesize into a unified alpha signal.
    `;

    const response = await ai.models.generateContent({
        model: 'gemini-3-pro-preview',
        contents: prompt,
        config: {
            responseMimeType: "application/json",
            thinkingConfig: { thinkingBudget: 32768 },
            responseSchema: {
                type: Type.OBJECT,
                properties: {
                    asset: { type: Type.STRING },
                    smartScore: { type: Type.NUMBER },
                    technicalSignal: { type: Type.STRING },
                    fundamentalSignal: { type: Type.STRING },
                    sentimentSignal: { type: Type.STRING },
                    unifiedVerdict: { type: Type.STRING },
                    keyRisks: { type: Type.ARRAY, items: { type: Type.STRING } },
                    suggestedAction: { type: Type.STRING }
                }
            }
        }
    });

    if (!response.text) throw new Error("DS-Star failed");
    return JSON.parse(response.text) as DSAnalysis;
};

export const generateModuleBSummary = async (file: LocalFile): Promise<FileSummary> => {
    const response = await ai.models.generateContent({
        model: 'gemini-3-flash-preview',
        contents: `Summarize this file: ${file.name}\nPath: ${file.path}\nContent: ${file.content?.substring(0, 4000)}`,
        config: {
            responseMimeType: "application/json",
            responseSchema: {
                type: Type.OBJECT,
                properties: {
                    meaningSummary: { type: Type.STRING },
                    keyFunctions: { type: Type.ARRAY, items: { type: Type.STRING } },
                    keyVariables: { type: Type.ARRAY, items: { type: Type.STRING } },
                    dependencies: {
                        type: Type.OBJECT,
                        properties: {
                            internal: { type: Type.ARRAY, items: { type: Type.STRING } },
                            external: { type: Type.ARRAY, items: { type: Type.STRING } },
                        }
                    },
                    risks: { type: Type.ARRAY, items: { type: Type.STRING } },
                    connections: {
                        type: Type.OBJECT,
                        properties: {
                            moduleA: { type: Type.STRING },
                            strategyScout: { type: Type.STRING },
                            moduleC: { type: Type.STRING },
                            moduleD: { type: Type.STRING },
                            tradingSystems: { type: Type.ARRAY, items: { type: Type.STRING } },
                        }
                    },
                    suggestedNextSteps: { type: Type.ARRAY, items: { type: Type.STRING } },
                }
            }
        }
    });

    if (!response.text) throw new Error("Summarization failed");
    return JSON.parse(response.text) as FileSummary;
};

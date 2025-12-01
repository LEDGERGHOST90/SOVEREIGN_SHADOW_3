
import { GoogleGenAI, Type, Schema } from "@google/genai";
import { 
  StrategyAnalysis, 
  StrategyArtifacts, 
  TradingAlert, 
  ModuleAOutput, 
  Strategy, 
  StructureAnalysis, 
  TriEraAnalysis, 
  LocalFile, 
  FileSummary 
} from '../types';

const apiKey = process.env.API_KEY || '';
const ai = new GoogleGenAI({ apiKey });

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

export const transcribeAudio = async (file: File, modelName: string = 'gemini-2.5-flash'): Promise<string> => {
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

export const generateFullStrategyPackage = async (analysis: StrategyAnalysis, modelName: string = 'gemini-3-pro-preview'): Promise<StrategyArtifacts> => {
    const prompt = `
    Based on the following strategy analysis, generate a complete code package.
    
    Strategy: ${JSON.stringify(analysis)}
    
    1. Python Code: Use CCXT library for a robust trading bot.
    2. Pine Script: Version 5 strategy for TradingView.
    3. Config JSON: A parameter file for the bot.
    4. Narrative: A short "Sovereign" style description of how this strategy fits into the ecosystem.
    `;

    const response = await ai.models.generateContent({
        model: modelName,
        contents: prompt,
        config: {
            responseMimeType: "application/json",
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

    if (!response.text) throw new Error("No artifacts generated");
    return JSON.parse(response.text) as StrategyArtifacts;
};

export const chatWithGemini = async (history: {role: 'user'|'model', text: string}[], message: string, context: string): Promise<string> => {
    const systemInstruction = `You are a specialized Trading Strategy Assistant. You have context about a specific strategy. Answer questions based on this context: ${context}`;
    
    const chat = ai.chats.create({
        model: 'gemini-3-pro-preview',
        config: {
            systemInstruction
        },
        history: history.map(h => ({
            role: h.role,
            parts: [{ text: h.text }]
        }))
    });

    const result = await chat.sendMessage({ message });
    return result.text || "I couldn't generate a response.";
};

export const refineStrategy = async (currentAnalysis: StrategyAnalysis, refinementPrompt: string, modelName: string): Promise<StrategyAnalysis> => {
    const prompt = `
    Refine the following strategy analysis based on this user request: "${refinementPrompt}".
    
    Current Analysis: ${JSON.stringify(currentAnalysis)}
    
    Return the updated analysis in the same JSON format.
    `;

    const response = await ai.models.generateContent({
        model: modelName,
        contents: prompt,
        config: {
            responseMimeType: "application/json",
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

export const generateSovereignDailyReport = async (moduleAData: ModuleAOutput, strategies: Strategy[]): Promise<string> => {
    const prompt = `
    Generate a "Sovereign Shadow Daily Record" (Module C).
    
    Context:
    - Files Scanned: ${moduleAData.files.length}
    - Recent File Changes: ${JSON.stringify(moduleAData.timeline_view.slice(0, 3))}
    - Active Strategies: ${strategies.map(s => s.analysis.name).join(', ')}
    
    Write a daily log entry in Markdown format. Use a sci-fi / cyberpunk "system log" tone.
    Include sections: 
    1. System Status
    2. Codebase Evolution (based on file changes)
    3. Strategy Grid Update
    4. Directives for the User
    `;

    const response = await ai.models.generateContent({
        model: 'gemini-3-pro-preview',
        contents: prompt
    });

    return response.text || "Report generation failed.";
};

export const analyzeFolderStructure = async (filePaths: string[]): Promise<StructureAnalysis> => {
    const truncatedPaths = filePaths.slice(0, 500); 
    
    const prompt = `
    Analyze this list of file paths to determine the project structure.
    Paths: ${JSON.stringify(truncatedPaths)}
    `;

    const response = await ai.models.generateContent({
        model: 'gemini-3-pro-preview',
        contents: prompt,
        config: {
            responseMimeType: "application/json",
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

    if (!response.text) throw new Error("Structure analysis failed");
    return JSON.parse(response.text) as StructureAnalysis;
};

export const analyzeProjectFiles = async (files: LocalFile[]): Promise<StructureAnalysis> => {
    return analyzeFolderStructure(files.map(f => f.path));
};

export const generateTriEraAnalysis = async (files: LocalFile[]): Promise<TriEraAnalysis> => {
    const eraCounts = {
        Legacy_Loop: files.filter(f => f.era === 'Legacy_Loop').length,
        Sovereign_Shadow: files.filter(f => f.era === 'Sovereign_Shadow').length,
        Gemini_Current: files.filter(f => f.era === 'Gemini_Current').length,
    };
    
    const prompt = `
    Perform a Tri-Era Evolution Analysis on this codebase.
    Stats: ${JSON.stringify(eraCounts)}
    
    Provide insights on how the system is evolving from Legacy Loop (GPT-5 era) through Sovereign Shadow (Claude era) to Gemini Current (Google era).
    `;

    const response = await ai.models.generateContent({
        model: 'gemini-3-pro-preview',
        contents: prompt,
        config: {
            responseMimeType: "application/json",
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

export const generateModuleBSummary = async (file: LocalFile): Promise<FileSummary> => {
    const prompt = `
    Analyze this file.
    Name: ${file.name}
    Path: ${file.path}
    Content Snippet: ${file.content?.substring(0, 3000) || "No content"}
    
    Provide a functional summary.
    `;

    const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: prompt,
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
                             tradingSystems: { type: Type.ARRAY, items: { type: Type.STRING } }
                        }
                    },
                    suggestedNextSteps: { type: Type.ARRAY, items: { type: Type.STRING } },
                }
            }
        }
    });

    if (!response.text) throw new Error("File summary failed");
    return JSON.parse(response.text) as FileSummary;
};

export const parseTradingAlert = async (rawText: string): Promise<TradingAlert> => {
    const lower = rawText.toLowerCase();
    let source: TradingAlert['source'] = 'Manual';
    if (lower.includes('tradingview')) source = 'TradingView';
    if (lower.includes('python')) source = 'Python';
    if (lower.includes('claude')) source = 'Claude';

    let severity: TradingAlert['severity'] = 'Info';
    if (lower.includes('stop loss') || lower.includes('liquidation') || lower.includes('critical')) severity = 'Critical';
    else if (lower.includes('alert') || lower.includes('warning')) severity = 'Warning';

    if (apiKey) {
        try {
            const response = await ai.models.generateContent({
                model: 'gemini-2.5-flash',
                contents: `Parse this trading alert into JSON: "${rawText}"`,
                config: {
                    responseMimeType: "application/json",
                    responseSchema: {
                        type: Type.OBJECT,
                        properties: {
                            id: { type: Type.STRING },
                            source: { type: Type.STRING, enum: ['TradingView', 'Python', 'Claude', 'Manual'] },
                            symbol: { type: Type.STRING },
                            message: { type: Type.STRING },
                            severity: { type: Type.STRING, enum: ['Info', 'Warning', 'Critical'] },
                            actionRequired: { type: Type.STRING }
                        }
                    }
                }
            });
            if (response.text) {
                const data = JSON.parse(response.text);
                return { ...data, timestamp: Date.now() };
            }
        } catch (e) {
            console.warn("Gemini parse failed, falling back to manual");
        }
    }

    return {
        id: crypto.randomUUID(),
        source,
        symbol: "UNKNOWN",
        message: rawText,
        severity,
        timestamp: Date.now()
    };
};

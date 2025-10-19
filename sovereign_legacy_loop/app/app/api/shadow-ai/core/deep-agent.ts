/**
 * 🧠 DEEP AGENT API - SHADOW.AI
 * Multi-AI orchestration endpoint with recursive ML
 */

import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import DeepAgent from "@/lib/shadow-ai/deep-agent/deep-agent-core";
import BTCBreakoutMission from "@/lib/shadow-ai/missions/btc-breakout-mission";

export const dynamic = "force-dynamic";

// Global Deep Agent instance
let deepAgent: DeepAgent | null = null;
let btcMission: BTCBreakoutMission | null = null;

/**
 * POST /api/shadow-ai/deep-agent
 * Execute Deep Agent with BTC Breakout Mission
 */
export async function POST(req: NextRequest) {
  try {
    // 1. AUTHENTICATION
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json(
        { error: "Unauthorized - Authentication required" },
        { status: 401 }
      );
    }

    // 2. VALIDATE REQUEST
    const body = await req.json();
    const action = body.action || 'analyze';
    const input = body.input || {};

    // 3. INITIALIZE DEEP AGENT
    if (!deepAgent) {
      console.log('🧠 INITIALIZING DEEP AGENT...');
      deepAgent = new DeepAgent();
      
      // Setup event listeners
      deepAgent.on('brainInitialized', (data) => {
        console.log('✅ Deep Agent Brain Initialized:', data);
      });
      
      deepAgent.on('learned', (data) => {
        console.log('🎓 Deep Agent Learned:', data);
      });
    }

    // 4. EXECUTE ACTION
    let result;
    switch (action) {
      case 'analyze':
        result = await analyzeMarket(input);
        break;
        
      case 'execute_btc_breakout':
        result = await executeBTCBreakoutWithDeepAgent(input);
        break;
        
      case 'learn':
        result = await learnFromExperience(input);
        break;
        
      case 'metrics':
        result = await getDeepAgentMetrics();
        break;
        
      case 'export_brain':
        result = await exportBrainState();
        break;
        
      default:
        return NextResponse.json(
          { error: "Invalid action" },
          { status: 400 }
        );
    }

    // 5. RETURN RESULT
    return NextResponse.json({
      success: true,
      action,
      data: result,
      timestamp: new Date().toISOString(),
      user: session.user.id
    });

  } catch (error) {
    console.error("Deep Agent API error:", error);
    return NextResponse.json(
      { error: "Deep Agent execution failed", details: error },
      { status: 500 }
    );
  }
}

/**
 * Analyze Market with Deep Agent
 */
async function analyzeMarket(input: any): Promise<any> {
  if (!deepAgent) {
    throw new Error('Deep Agent not initialized');
  }

  console.log('🧠 DEEP AGENT ANALYZING MARKET...');

  // Prepare input for Deep Agent
  const analysisInput = {
    marketData: input.marketData || 0.5,
    portfolioState: input.portfolioState || 0.5,
    riskLevel: input.riskLevel || 0.5,
    symbol: input.symbol || 'BTCUSDT',
    currentPrice: input.currentPrice || 119000,
    targetPrice: input.targetPrice || 120000
  };

  // Recursive processing with Deep Agent
  const decision = await deepAgent.processRecursively(analysisInput);

  return {
    decision,
    analysisInput,
    deepAgentMetrics: deepAgent.getPerformanceMetrics(),
    timestamp: new Date().toISOString()
  };
}

/**
 * Execute BTC Breakout with Deep Agent Intelligence
 */
async function executeBTCBreakoutWithDeepAgent(input: any): Promise<any> {
  if (!deepAgent) {
    throw new Error('Deep Agent not initialized');
  }

  console.log('🎯 EXECUTING BTC BREAKOUT WITH DEEP AGENT...');

  // 1. DEEP AGENT ANALYSIS
  const marketAnalysis = await deepAgent.processRecursively({
    marketData: 0.7, // BTC at $119K, approaching $120K breakout
    portfolioState: 0.6, // Engine has 0.05 BTC position
    riskLevel: 0.5, // Moderate risk
    symbol: 'BTCUSDT',
    currentPrice: 119000,
    targetPrice: 120000
  });

  console.log('🧠 Deep Agent Decision:', marketAnalysis);

  // 2. INITIALIZE BTC MISSION
  if (!btcMission) {
    btcMission = new BTCBreakoutMission();
    
    // Setup BTC Mission event listeners
    btcMission.on('orderFilled', async (data) => {
      console.log('✅ Order Filled - Learning from experience...');
      
      // Calculate reward based on profit
      const reward = data.fillPrice > 119000 ? 1.0 : 0.5;
      
      // Deep Agent learns from this experience
      await deepAgent!.learn(
        { action: 'SELL', price: data.fillPrice },
        { success: true, order: data.order },
        reward
      );
    });
    
    btcMission.on('siphonExecuted', async (data) => {
      console.log('💰 Siphon Executed - Deep Agent learning...');
      
      // Reward for successful siphon
      await deepAgent!.learn(
        { action: 'SIPHON', amounts: data },
        { success: true },
        0.8
      );
    });
  }

  // 3. EXECUTE BTC MISSION
  if (marketAnalysis.confidence > 0.6) {
    console.log('✅ Deep Agent confidence sufficient - Executing mission...');
    await btcMission.executeOCOLadder();
    
    return {
      executed: true,
      marketAnalysis,
      missionStatus: btcMission.getMissionStatus(),
      deepAgentRecommendation: 'Execute BTC breakout mission with high confidence',
      confidence: marketAnalysis.confidence,
      reasoning: marketAnalysis.reasoning
    };
  } else {
    console.log('⚠️  Deep Agent confidence insufficient - Holding...');
    
    return {
      executed: false,
      marketAnalysis,
      deepAgentRecommendation: 'Hold position - Market conditions not optimal',
      confidence: marketAnalysis.confidence,
      reasoning: marketAnalysis.reasoning
    };
  }
}

/**
 * Learn from Experience
 */
async function learnFromExperience(input: any): Promise<any> {
  if (!deepAgent) {
    throw new Error('Deep Agent not initialized');
  }

  console.log('🎓 DEEP AGENT LEARNING FROM EXPERIENCE...');

  const { inputData, outputData, reward } = input;

  await deepAgent.learn(inputData, outputData, reward);

  return {
    learned: true,
    reward,
    metrics: deepAgent.getPerformanceMetrics(),
    timestamp: new Date().toISOString()
  };
}

/**
 * Get Deep Agent Metrics
 */
async function getDeepAgentMetrics(): Promise<any> {
  if (!deepAgent) {
    return {
      initialized: false,
      message: 'Deep Agent not initialized'
    };
  }

  const metrics = deepAgent.getPerformanceMetrics();

  return {
    initialized: true,
    metrics,
    btcMissionStatus: btcMission ? btcMission.getMissionStatus() : null,
    timestamp: new Date().toISOString()
  };
}

/**
 * Export Brain State
 */
async function exportBrainState(): Promise<any> {
  if (!deepAgent) {
    return {
      exported: false,
      message: 'Deep Agent not initialized'
    };
  }

  const brainState = deepAgent.exportBrainState();

  return {
    exported: true,
    brainState: JSON.parse(brainState),
    filename: `deep_agent_brain_${new Date().toISOString().split('T')[0]}.json`,
    timestamp: new Date().toISOString()
  };
}

/**
 * GET /api/shadow-ai/deep-agent
 * Get Deep Agent information
 */
export async function GET(req: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  return NextResponse.json({
    system: "SHADOW.AI Deep Agent",
    description: "Multi-AI orchestration with recursive machine learning",
    version: "1.0.0",
    capabilities: [
      "Recursive neural network processing",
      "Multi-AI consensus (Claude + GPT-5 + Manus + Abacus)",
      "Reinforcement learning from trading experience",
      "Automatic weight adjustment and optimization",
      "Safety guards: circuit breakers, rollback, validation",
      "BTC Breakout Mission integration"
    ],
    actions: [
      "analyze - Analyze market with Deep Agent",
      "execute_btc_breakout - Execute BTC breakout with AI intelligence",
      "learn - Learn from trading experience",
      "metrics - Get performance metrics",
      "export_brain - Export brain state"
    ],
    aiAgents: [
      "Claude SDK - Deep reasoning and code analysis",
      "GPT-5 Pro - Market prediction and strategy",
      "Manus AI - Automation and execution",
      "Abacus.AI - Market intelligence"
    ],
    safetyFeatures: [
      "Max recursion depth: 10",
      "Max memory size: 1000 experiences",
      "Execution timeout: 5 seconds",
      "Weight bounds: -10 to +10",
      "Output validation enabled",
      "Automatic snapshots and rollback"
    ],
    initialized: deepAgent !== null,
    timestamp: new Date().toISOString()
  });
}

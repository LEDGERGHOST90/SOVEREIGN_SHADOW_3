/**
 * 🌟 SHADOW.AI MASTER API - Complete System
 * The ultimate endpoint for your fully integrated SHADOW.AI ecosystem
 */

import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import FullSystemIntegration from "@/lib/shadow-ai/core/full-system-integration";

export const dynamic = "force-dynamic";

// Global master system instance
let masterSystem: FullSystemIntegration | null = null;

/**
 * POST /api/shadow-ai/master
 * Master SHADOW.AI system operations
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

    // 2. RATE LIMITING
    const rateLimitOk = await checkRateLimit(session.user.id);
    if (!rateLimitOk) {
      return NextResponse.json(
        { error: "Too many requests - Rate limited" },
        { status: 429 }
      );
    }

    // 3. VALIDATE REQUEST
    const body = await req.json();
    const { command, parameters, message } = body;

    // 4. INITIALIZE MASTER SYSTEM
    if (!masterSystem) {
      await initializeMasterSystem();
    }

    // 5. EXECUTE COMMAND
    let result;
    switch (command) {
      case 'initialize':
        result = await handleInitializeCommand();
        break;
        
      case 'status':
        result = await handleStatusCommand();
        break;
        
      case 'chat':
        result = await handleChatCommand(message, session.user.id);
        break;
        
      case 'full_analysis':
        result = await handleFullAnalysisCommand();
        break;
        
      case 'optimize_portfolio':
        result = await handleOptimizePortfolioCommand(parameters);
        break;
        
      case 'risk_assessment':
        result = await handleRiskAssessmentCommand();
        break;
        
      case 'trading_analysis':
        result = await handleTradingAnalysisCommand();
        break;
        
      case 'emergency_stop':
        result = await handleEmergencyStopCommand();
        break;
        
      case 'system_health':
        result = await handleSystemHealthCommand();
        break;
        
      case 'performance_metrics':
        result = await handlePerformanceMetricsCommand();
        break;
        
      default:
        // Try unified command execution
        result = await masterSystem!.executeUnifiedCommand(command, parameters);
        break;
    }

    // 6. RETURN RESULT
    return NextResponse.json({
      success: true,
      command,
      data: result,
      timestamp: new Date().toISOString(),
      user: session.user.id,
      system: "SHADOW.AI Master"
    });

  } catch (error) {
    console.error("SHADOW.AI Master API error:", error);
    return NextResponse.json(
      { 
        error: "Command execution failed", 
        details: error instanceof Error ? error.message : "Unknown error",
        system: "SHADOW.AI Master"
      },
      { status: 500 }
    );
  }
}

/**
 * Initialize Master System
 */
async function initializeMasterSystem(): Promise<void> {
  console.log('🌟 Initializing SHADOW.AI Master System...');
  
  masterSystem = new FullSystemIntegration();
  
  // Setup event listeners
  masterSystem.on('systemReady', (data) => {
    console.log('🚀 SHADOW.AI Master System Ready:', data);
  });
  
  masterSystem.on('criticalAlert', (alert) => {
    console.log('🚨 Critical Alert:', alert);
    // Could trigger notifications, emergency procedures, etc.
  });
  
  masterSystem.on('tradingExecution', (decision) => {
    console.log('💹 Trading Execution:', decision);
    // Could trigger actual trade execution
  });
  
  masterSystem.on('eventProcessed', (event) => {
    console.log(`📡 Event Processed: ${event.source} → ${event.target}: ${event.event}`);
  });
  
  // Initialize all systems
  await masterSystem.initializeAllSystems();
  
  console.log('✅ SHADOW.AI Master System initialized successfully!');
}

/**
 * Handle Initialize Command
 */
async function handleInitializeCommand(): Promise<any> {
  if (!masterSystem) {
    await initializeMasterSystem();
  }
  
  return {
    message: "SHADOW.AI Master System initialized successfully",
    systemState: masterSystem!.getSystemState(),
    metrics: masterSystem!.getSystemMetrics(),
    components: [
      "Enhanced Shadow AI - Recursive learning",
      "ChatLLM Interface - Natural language processing",
      "Advanced Monitoring - System health tracking", 
      "Performance Optimizer - Speed optimization",
      "Portfolio Deep Agent - Investment optimization",
      "Risk Deep Agent - Risk management",
      "Trading Deep Agent - Trading decisions",
      "Full Integration - Unified orchestration"
    ],
    timestamp: new Date()
  };
}

/**
 * Handle Status Command
 */
async function handleStatusCommand(): Promise<any> {
  if (!masterSystem) {
    return {
      status: "NOT_INITIALIZED",
      message: "SHADOW.AI Master System not started"
    };
  }
  
  const systemHealth = masterSystem.getSystemHealth();
  
  return {
    status: "ACTIVE",
    health: systemHealth,
    summary: {
      systemsActive: Object.values(systemHealth.systemState).filter(Boolean).length,
      totalSystems: Object.keys(systemHealth.systemState).length,
      integrationHealth: systemHealth.metrics.integrationHealth,
      uptime: systemHealth.metrics.systemUptime,
      eventQueue: systemHealth.eventQueueSize
    },
    timestamp: new Date()
  };
}

/**
 * Handle Chat Command
 */
async function handleChatCommand(message: string, userId: string): Promise<any> {
  if (!masterSystem) {
    throw new Error("Master system not initialized");
  }
  
  const response = await masterSystem.processUserMessage(message, userId);
  
  return {
    message: response,
    timestamp: new Date(),
    user: userId,
    processed_by: "SHADOW.AI Master System"
  };
}

/**
 * Handle Full Analysis Command
 */
async function handleFullAnalysisCommand(): Promise<any> {
  if (!masterSystem) {
    throw new Error("Master system not initialized");
  }
  
  const analysis = await masterSystem.executeUnifiedCommand('full_analysis');
  
  return {
    analysis,
    summary: {
      portfolio: analysis.portfolio ? "✅ Analyzed" : "❌ Not available",
      risk: analysis.risk ? "✅ Assessed" : "❌ Not available", 
      trading: analysis.trading ? "✅ Analyzed" : "❌ Not available"
    },
    recommendations: generateRecommendations(analysis),
    timestamp: new Date()
  };
}

/**
 * Handle Optimize Portfolio Command
 */
async function handleOptimizePortfolioCommand(parameters: any): Promise<any> {
  if (!masterSystem) {
    throw new Error("Master system not initialized");
  }
  
  const optimization = await masterSystem.executeUnifiedCommand('optimize_portfolio', {
    strategyId: parameters?.strategyId || 'balanced_crypto',
    maxAmount: parameters?.maxAmount || 10000
  });
  
  return {
    optimization: optimization.optimization,
    summary: optimization.optimization ? {
      strategy: optimization.optimization.strategy?.name,
      actionsExecuted: optimization.optimization.actionsExecuted,
      totalActions: optimization.optimization.totalActions,
      status: "completed"
    } : null,
    timestamp: new Date()
  };
}

/**
 * Handle Risk Assessment Command
 */
async function handleRiskAssessmentCommand(): Promise<any> {
  if (!masterSystem) {
    throw new Error("Master system not initialized");
  }
  
  // Force risk assessment across all systems
  const analysis = await masterSystem.executeUnifiedCommand('full_analysis');
  
  return {
    riskAssessment: analysis.risk,
    riskLevel: analysis.risk ? determineRiskLevel(analysis.risk) : "unknown",
    alerts: analysis.risk?.alerts || [],
    recommendations: generateRiskRecommendations(analysis.risk),
    timestamp: new Date()
  };
}

/**
 * Handle Trading Analysis Command
 */
async function handleTradingAnalysisCommand(): Promise<any> {
  if (!masterSystem) {
    throw new Error("Master system not initialized");
  }
  
  const analysis = await masterSystem.executeUnifiedCommand('full_analysis');
  
  return {
    tradingAnalysis: analysis.trading,
    opportunities: analysis.trading || [],
    marketSignals: "Available via unified system",
    summary: {
      totalOpportunities: analysis.trading?.length || 0,
      highProbability: analysis.trading?.filter((op: any) => op.probability > 0.8).length || 0,
      recommendations: analysis.trading?.filter((op: any) => op.urgency >= 7).length || 0
    },
    timestamp: new Date()
  };
}

/**
 * Handle Emergency Stop Command
 */
async function handleEmergencyStopCommand(): Promise<any> {
  if (!masterSystem) {
    throw new Error("Master system not initialized");
  }
  
  const result = await masterSystem.executeUnifiedCommand('emergency_stop');
  
  return {
    emergencyStop: result.emergencyStop,
    message: "🚨 EMERGENCY STOP EXECUTED - All automated trading paused",
    actions: [
      "All trading activities suspended",
      "Risk monitoring continues",
      "Portfolio monitoring active",
      "Manual approval required for new trades"
    ],
    timestamp: new Date()
  };
}

/**
 * Handle System Health Command
 */
async function handleSystemHealthCommand(): Promise<any> {
  if (!masterSystem) {
    throw new Error("Master system not initialized");
  }
  
  const health = masterSystem.getSystemHealth();
  
  return {
    systemHealth: health,
    status: health.metrics.integrationHealth > 80 ? "EXCELLENT" : 
            health.metrics.integrationHealth > 60 ? "GOOD" : 
            health.metrics.integrationHealth > 40 ? "FAIR" : "POOR",
    details: {
      activeComponents: Object.values(health.systemState).filter(Boolean).length,
      totalComponents: Object.keys(health.systemState).length,
      eventProcessingRate: health.metrics.processedEvents / Math.max(1, health.metrics.totalEvents) * 100,
      avgResponseTime: health.metrics.avgProcessingTime
    },
    timestamp: new Date()
  };
}

/**
 * Handle Performance Metrics Command
 */
async function handlePerformanceMetricsCommand(): Promise<any> {
  if (!masterSystem) {
    throw new Error("Master system not initialized");
  }
  
  const metrics = masterSystem.getSystemMetrics();
  
  return {
    performanceMetrics: metrics,
    analysis: {
      efficiency: metrics.processedEvents / Math.max(1, metrics.totalEvents) * 100,
      reliability: (metrics.totalEvents - metrics.failedEvents) / Math.max(1, metrics.totalEvents) * 100,
      speed: metrics.avgProcessingTime < 100 ? "EXCELLENT" : 
             metrics.avgProcessingTime < 500 ? "GOOD" : "NEEDS_IMPROVEMENT"
    },
    recommendations: generatePerformanceRecommendations(metrics),
    timestamp: new Date()
  };
}

/**
 * Helper Functions
 */
function generateRecommendations(analysis: any): string[] {
  const recommendations: string[] = [];
  
  if (analysis.portfolio) {
    recommendations.push("Portfolio analysis complete - consider optimization opportunities");
  }
  
  if (analysis.risk && analysis.risk.overallRiskScore > 70) {
    recommendations.push("High risk detected - consider reducing position sizes");
  }
  
  if (analysis.trading && analysis.trading.length > 0) {
    recommendations.push(`${analysis.trading.length} trading opportunities identified - review for execution`);
  }
  
  return recommendations;
}

function determineRiskLevel(risk: any): string {
  if (!risk || !risk.overallRiskScore) return "unknown";
  
  if (risk.overallRiskScore > 80) return "HIGH";
  if (risk.overallRiskScore > 60) return "MEDIUM";
  if (risk.overallRiskScore > 40) return "LOW";
  return "VERY_LOW";
}

function generateRiskRecommendations(risk: any): string[] {
  const recommendations: string[] = [];
  
  if (risk?.concentrationRisk > 0.6) {
    recommendations.push("Diversify portfolio to reduce concentration risk");
  }
  
  if (risk?.volatility > 0.4) {
    recommendations.push("Consider adding stable assets to reduce volatility");
  }
  
  if (risk?.liquidityRisk > 0.3) {
    recommendations.push("Increase allocation to liquid assets");
  }
  
  return recommendations;
}

function generatePerformanceRecommendations(metrics: any): string[] {
  const recommendations: string[] = [];
  
  if (metrics.avgProcessingTime > 500) {
    recommendations.push("Consider optimizing processing speed");
  }
  
  if (metrics.failedEvents / Math.max(1, metrics.totalEvents) > 0.05) {
    recommendations.push("Review and fix event processing failures");
  }
  
  if (metrics.integrationHealth < 90) {
    recommendations.push("Check system component health and connectivity");
  }
  
  return recommendations;
}

async function checkRateLimit(userId: string): Promise<boolean> {
  // Simple rate limiting - in production, use Redis or similar
  return true; // Simplified for now
}

/**
 * GET /api/shadow-ai/master
 * Get SHADOW.AI Master system information
 */
export async function GET(req: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  return NextResponse.json({
    system: "SHADOW.AI Master",
    description: "Complete SHADOW.AI ecosystem integration - Your ultimate crypto trading AI",
    version: "2.0.0",
    phase: "2 - Complete Deep Agent Integration",
    components: {
      phase1: [
        "Enhanced Shadow AI - Recursive learning intelligence",
        "ChatLLM Interface - Natural language command processing",
        "Advanced Monitoring - Real-time system health tracking",
        "Performance Optimizer - Speed and efficiency optimization"
      ],
      phase2: [
        "Portfolio Deep Agent - Advanced investment optimization",
        "Risk Deep Agent - Comprehensive risk management",
        "Trading Deep Agent - Intelligent trading decisions",
        "Full System Integration - Unified orchestration"
      ]
    },
    commands: [
      "initialize - Initialize all SHADOW.AI systems",
      "status - Get complete system status",
      "chat - Process natural language commands",
      "full_analysis - Complete portfolio, risk, and trading analysis",
      "optimize_portfolio - Execute portfolio optimization",
      "risk_assessment - Comprehensive risk evaluation",
      "trading_analysis - Market analysis and trading opportunities",
      "emergency_stop - Emergency halt all automated trading",
      "system_health - Detailed system health report",
      "performance_metrics - System performance analytics"
    ],
    features: [
      "🧠 Recursive Machine Learning - Continuously improving AI",
      "💬 Natural Language Interface - Just talk to your AI",
      "📊 Advanced Analytics - Deep portfolio and market analysis",
      "🛡️ Risk Management - Comprehensive protection systems",
      "⚡ Intelligent Trading - AI-driven trading decisions",
      "🔄 Real-time Integration - All systems working together",
      "📈 Performance Optimization - Maximum speed and efficiency",
      "🚨 Advanced Monitoring - Complete system visibility"
    ],
    capabilities: {
      learning: "Recursive machine learning from every operation",
      communication: "Natural language processing and response",
      analysis: "Multi-dimensional portfolio and market analysis",
      optimization: "AI-driven portfolio and performance optimization",
      trading: "Intelligent trading signal analysis and decision making",
      risk: "Comprehensive risk assessment and management",
      integration: "Unified system orchestration and coordination",
      monitoring: "Real-time system health and performance tracking"
    },
    example_usage: {
      initialize: {
        command: "initialize",
        description: "Start up all SHADOW.AI systems"
      },
      chat: {
        command: "chat",
        message: "Analyze my portfolio and suggest optimizations",
        description: "Natural language interface to all systems"
      },
      full_analysis: {
        command: "full_analysis",
        description: "Complete analysis across portfolio, risk, and trading"
      },
      optimize: {
        command: "optimize_portfolio",
        parameters: { strategyId: "aggressive_growth", maxAmount: 5000 },
        description: "Execute AI-driven portfolio optimization"
      }
    },
    architecture: {
      design: "Hybrid approach with incremental improvements",
      philosophy: "80% of benefit with 20% of risk",
      integration: "Event-driven inter-system communication",
      learning: "Continuous improvement through recursive ML",
      security: "Complete local processing with maximum privacy"
    },
    timestamp: new Date().toISOString()
  });
}


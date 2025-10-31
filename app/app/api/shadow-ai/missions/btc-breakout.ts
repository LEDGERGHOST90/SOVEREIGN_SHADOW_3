/**
 * 🎯 BTC BREAKOUT API - SHADOW.AI Trading Mission
 * Execute OCO ladder with profit-siphon automation
 */

import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import BTCBreakoutMission from "@/lib/shadow-ai/missions/btc-breakout-mission";

export const dynamic = "force-dynamic";

// Global mission instance
let btcMission: BTCBreakoutMission | null = null;

/**
 * POST /api/shadow-ai/btc-breakout
 * Execute BTC breakout mission
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

    // 2. RATE LIMITING (prevent abuse)
    const rateLimitOk = await checkRateLimit(session.user.id);
    if (!rateLimitOk) {
      return NextResponse.json(
        { error: "Too many requests - Rate limited" },
        { status: 429 }
      );
    }

    // 3. VALIDATE REQUEST
    const body = await req.json();
    const action = body.action || 'execute';

    // 4. EXECUTE MISSION
    let result;
    switch (action) {
      case 'execute':
        result = await executeBTCBreakout();
        break;
        
      case 'status':
        result = await getMissionStatus();
        break;
        
      case 'logs':
        result = await getTradeLogs();
        break;
        
      case 'export':
        result = await exportTradeLogs();
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
    console.error("BTC Breakout API error:", error);
    return NextResponse.json(
      { error: "Mission execution failed" },
      { status: 500 }
    );
  }
}

/**
 * Execute BTC Breakout Mission
 */
async function executeBTCBreakout(): Promise<any> {
  try {
    // Initialize mission if not exists
    if (!btcMission) {
      btcMission = new BTCBreakoutMission();
      
      // Setup event listeners
      btcMission.on('missionInitialized', (data) => {
        console.log('🎯 BTC Mission Initialized:', data);
      });
      
      btcMission.on('orderFilled', (data) => {
        console.log('✅ Order Filled:', data);
      });
      
      btcMission.on('siphonExecuted', (data) => {
        console.log('💰 Siphon Executed:', data);
      });
      
      btcMission.on('graduationComplete', (data) => {
        console.log('🎓 Graduation Complete:', data);
      });
    }

    // Execute OCO ladder
    await btcMission.executeOCOLadder();

    // Get mission status
    const status = btcMission.getMissionStatus();

    return {
      message: "BTC Breakout Mission Executed Successfully",
      mission: {
        id: "btc_breakout_" + Date.now(),
        status: "ACTIVE",
        orders: status.ocoOrders.length,
        engineState: status.engineState,
        siphonPolicy: status.siphonPolicy,
        isLiveTrading: status.isLiveTrading
      },
      nextSteps: [
        "Monitor OCO orders for fills",
        "Siphon policy will auto-execute on fills",
        "Graduation threshold monitoring active",
        "Dry powder levels being maintained"
      ]
    };

  } catch (error) {
    console.error('BTC Breakout execution error:', error);
    throw error;
  }
}

/**
 * Get Mission Status
 */
async function getMissionStatus(): Promise<any> {
  if (!btcMission) {
    return {
      status: "NOT_INITIALIZED",
      message: "BTC Breakout Mission not started"
    };
  }

  const status = btcMission.getMissionStatus();
  
  return {
    status: "ACTIVE",
    mission: status,
    summary: {
      totalOrders: status.ocoOrders.length,
      pendingOrders: status.ocoOrders.filter((o: any) => o.status === 'PENDING').length,
      filledOrders: status.ocoOrders.filter((o: any) => o.status === 'FILLED').length,
      btcBalance: status.engineState.btcBalance,
      usdtBalance: status.engineState.usdtBalance,
      ethBalance: status.engineState.ethBalance,
      totalValue: status.engineState.totalEngineValue
    }
  };
}

/**
 * Get Trade Logs
 */
async function getTradeLogs(): Promise<any> {
  if (!btcMission) {
    return {
      logs: [],
      message: "No mission active"
    };
  }

  const logs = btcMission.getTradeLogs();
  
  return {
    totalLogs: logs.length,
    logs: logs,
    lastUpdate: logs.length > 0 ? logs[logs.length - 1].timestamp : null
  };
}

/**
 * Export Trade Logs
 */
async function exportTradeLogs(): Promise<any> {
  if (!btcMission) {
    return {
      export: null,
      message: "No mission active"
    };
  }

  const exportData = btcMission.exportTradeLogs();
  
  return {
    export: exportData,
    filename: `btc_breakout_trades_${new Date().toISOString().split('T')[0]}.json`,
    format: "JSON",
    totalTrades: JSON.parse(exportData).length
  };
}

/**
 * Rate Limiting Check
 */
async function checkRateLimit(userId: string): Promise<boolean> {
  // Simple rate limiting - in production, use Redis or similar
  // Allow 10 requests per minute for trading operations
  return true; // Simplified for now
}

/**
 * GET /api/shadow-ai/btc-breakout
 * Get mission information
 */
export async function GET(req: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  return NextResponse.json({
    mission: "BTC Breakout Trading",
    description: "Advanced OCO ladder with profit-siphon automation",
    version: "1.0.0",
    actions: [
      "execute - Execute BTC breakout mission",
      "status - Get mission status",
      "logs - Get trade logs",
      "export - Export trade logs"
    ],
    features: [
      "OCO ladder orders at $120K, $125K, $130K",
      "Stop-loss protection at $114.5K",
      "70% USDT / 30% ETH siphon policy",
      "Graduation threshold monitoring",
      "Dry powder maintenance",
      "Real-time trade logging"
    ],
    constraints: [
      "Ledger vault remains untouched",
      "Minimum engine balance maintained",
      "ΩSIGIL passphrase required for graduation",
      "DISABLE_REAL_EXCHANGES=1 for simulation"
    ],
    timestamp: new Date().toISOString()
  });
}

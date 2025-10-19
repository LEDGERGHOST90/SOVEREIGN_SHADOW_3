import { NextRequest, NextResponse } from "next/server";
import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { deepAgentAbacus } from "@/lib/claude-agent";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { action, parameters } = await req.json();

    if (!action) {
      return NextResponse.json(
        { error: "Action is required" },
        { status: 400 }
      );
    }

    let result;
    
    switch (action) {
      case 'analyze_portfolio':
        result = await deepAgentAbacus.analyzePortfolio(session.user.id);
        break;
        
      case 'execute_trading':
        const { strategy, riskProfile } = parameters;
        result = await deepAgentAbacus.executeTradingStrategy(strategy, riskProfile);
        break;
        
      case 'manage_vault':
        const { operation } = parameters;
        result = await deepAgentAbacus.manageVaultOperations(operation);
        break;
        
      case 'optimize_tax':
        result = await deepAgentAbacus.optimizeTaxStrategy(session.user.id);
        break;
        
      default:
        return NextResponse.json(
          { error: "Unknown action" },
          { status: 400 }
        );
    }

    return NextResponse.json({
      success: true,
      data: result,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error("Deep Agent Abacus error:", error);
    return NextResponse.json(
      { error: "Agent service unavailable" },
      { status: 500 }
    );
  }
}

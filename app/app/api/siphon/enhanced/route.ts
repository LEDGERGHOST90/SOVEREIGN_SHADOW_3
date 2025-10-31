
import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { EnhancedHybridSiphonEngine } from '@/lib/enhanced-siphon-engine';

export const dynamic = "force-dynamic";

const enhancedSiphonEngine = new EnhancedHybridSiphonEngine();

export async function POST(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { manualTrigger = false } = await req.json();

    // Get enhanced configuration
    const config = await EnhancedHybridSiphonEngine.getEnhancedConfig(session.user.id);
    
    // Override auto-trigger if manual execution requested
    if (manualTrigger) {
      config.autoTrigger = true;
    }

    // Execute enhanced siphon
    const result = await enhancedSiphonEngine.executeEnhancedSiphon(
      session.user.id, 
      config
    );

    return NextResponse.json({
      success: true,
      result,
      timestamp: new Date().toISOString(),
      source: 'Enhanced Siphon Engine v2.0'
    });

  } catch (error) {
    console.error('Enhanced siphon execution error:', error);
    return NextResponse.json(
      { error: 'Enhanced siphon execution failed', details: error instanceof Error ? error.message : 'Unknown error' },
      { status: 500 }
    );
  }
}

export async function GET(req: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Get real-time portfolio data
    const portfolioData = await enhancedSiphonEngine.getRealTimePortfolioData(session.user.id);
    
    // Get configuration
    const config = await EnhancedHybridSiphonEngine.getEnhancedConfig(session.user.id);

    return NextResponse.json({
      portfolioData,
      config,
      lastUpdated: new Date().toISOString(),
      features: {
        realTimeTracking: config.realTimeTracking,
        feeOptimization: config.feeOptimization,
        autoTrigger: config.autoTrigger
      }
    });

  } catch (error) {
    console.error('Enhanced siphon status error:', error);
    return NextResponse.json(
      { error: 'Failed to get enhanced siphon status' },
      { status: 500 }
    );
  }
}

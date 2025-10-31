
/**
 * 📊 RWA ANALYTICS API
 * Advanced portfolio analytics and Oracle comparison
 */

import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { RWAEngineFactory } from '@/lib/rwa-integrations';
import { prisma } from '@/lib/db';

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession();
    if (!session?.user?.email) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const user = await prisma.user.findUnique({
      where: { email: session.user.email },
    });

    if (!user) {
      return NextResponse.json({ error: 'User not found' }, { status: 404 });
    }

    // Create RWA engine instance
    const rwaEngine = RWAEngineFactory.createEngine(user.id);

    // Generate comprehensive analytics
    const analytics = await rwaEngine.generateRWAAnalytics();

    // Get available assets
    const ondoAssets = await rwaEngine.getOndoAssets();
    const robinhoodAssets = await rwaEngine.getRobinhoodAssets();

    return NextResponse.json({
      success: true,
      data: {
        analytics,
        availableAssets: {
          ondo: ondoAssets,
          robinhood: robinhoodAssets
        },
        timestamp: new Date().toISOString()
      }
    });

  } catch (error) {
    console.error('RWA analytics error:', error);
    return NextResponse.json({ 
      error: 'Internal server error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

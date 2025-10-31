
import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { generateRealTimePortfolioData } from '@/lib/load-user-data';

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Generate real-time portfolio data based on user's actual trade history
    const portfolioData = generateRealTimePortfolioData();
    
    return NextResponse.json({
      success: true,
      data: portfolioData,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('Error fetching real portfolio data:', error);
    return NextResponse.json(
      { 
        error: 'Failed to fetch portfolio data',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

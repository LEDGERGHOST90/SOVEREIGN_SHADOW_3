
import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

// Mock settings storage
let settings = {
  reviewInterval: "2h",
  strictMode: false
};

export async function GET(request: NextRequest) {
  try {
    return NextResponse.json(settings);
    
  } catch (error) {
    console.error('Error fetching settings:', error);
    return NextResponse.json(
      { error: 'Failed to fetch settings' },
      { status: 500 }
    );
  }
}

export async function PUT(request: NextRequest) {
  try {
    const { reviewInterval, strictMode } = await request.json();

    if (reviewInterval !== undefined) {
      settings.reviewInterval = reviewInterval;
    }
    
    if (strictMode !== undefined) {
      settings.strictMode = strictMode;
    }

    return NextResponse.json({
      success: true,
      updated: settings
    });
    
  } catch (error) {
    console.error('Error updating settings:', error);
    return NextResponse.json(
      { error: 'Failed to update settings' },
      { status: 500 }
    );
  }
}

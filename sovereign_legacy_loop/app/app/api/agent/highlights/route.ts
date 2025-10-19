
import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

// Mock highlights data
let highlights = [
  {
    id: 1,
    filePath: "/components/glassmorphic-auth.tsx",
    snippetRef: "Authentication flow",
    tag: "review" as const,
    created_at: new Date()
  },
  {
    id: 2,
    filePath: "/lib/trade-data-parser.ts",
    snippetRef: "CSV parsing logic",
    tag: "polish" as const,
    created_at: new Date(Date.now() - 3600000)
  },
  {
    id: 3,
    filePath: "/api/portfolio/real-data/route.ts",
    snippetRef: "Data security validation",
    tag: "risk" as const,
    created_at: new Date(Date.now() - 7200000)
  }
];

export async function GET(request: NextRequest) {
  try {
    return NextResponse.json({
      success: true,
      highlights
    });
    
  } catch (error) {
    console.error('Error fetching highlights:', error);
    return NextResponse.json(
      { error: 'Failed to fetch highlights' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const { filePath, snippetRef, tag } = await request.json();

    if (!filePath || !snippetRef || !tag) {
      return NextResponse.json(
        { error: 'Missing required fields' },
        { status: 400 }
      );
    }

    const newHighlight = {
      id: Date.now(),
      filePath,
      snippetRef,
      tag,
      created_at: new Date()
    };

    highlights.push(newHighlight);

    return NextResponse.json({
      success: true,
      highlight: newHighlight
    });
    
  } catch (error) {
    console.error('Error creating highlight:', error);
    return NextResponse.json(
      { error: 'Failed to create highlight' },
      { status: 500 }
    );
  }
}


import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';

// Mock data storage
let reflections = [
  {
    id: 1,
    milestoneId: 1,
    text: "Successfully implemented the core architecture with all major components integrated. The system now reflects the user's vision of a unified crypto wealth management platform.",
    timestamp: new Date(Date.now() - 1800000)
  }
];

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions);
    
    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const { milestoneId, text } = await request.json();

    if (!milestoneId || !text) {
      return NextResponse.json(
        { error: 'Missing milestoneId or text' },
        { status: 400 }
      );
    }

    const newReflection = {
      id: Date.now(),
      milestoneId: parseInt(milestoneId),
      text: text.trim(),
      timestamp: new Date()
    };

    reflections.push(newReflection);

    return NextResponse.json({
      success: true,
      reflection: newReflection
    });
    
  } catch (error) {
    console.error('Error creating reflection:', error);
    return NextResponse.json(
      { error: 'Failed to create reflection' },
      { status: 500 }
    );
  }
}

/**
 * Empire API - Connected to MCP
 * GET /api/empire - Returns complete empire data
 */
import { NextResponse } from 'next/server';
import { getEmpireData, getVaultData } from '@/lib/mcp-bridge';

export async function GET() {
  try {
    const empire = await getEmpireData();
    const vault = await getVaultData();
    
    return NextResponse.json({
      success: true,
      empire,
      vault,
      source: 'mcp-bridge',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error' 
      },
      { status: 500 }
    );
  }
}

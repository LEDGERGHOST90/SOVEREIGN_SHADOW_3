
// Oracle RWA Vaults API - Vault management and rebalancing

import { NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import { authOptions } from '@/lib/auth';
import { RWAVaultManager } from '@/lib/rwa-vault-manager';

export async function GET() {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const vaultManager = new RWAVaultManager(session.user.id);
    const performance = await vaultManager.getVaultPerformance();

    return NextResponse.json({
      success: true,
      data: {
        vaults: performance,
        totalVaults: performance.length,
        totalValue: performance.reduce((sum, v) => sum + v.currentValue, 0),
        averageYield: performance.length > 0 
          ? performance.reduce((sum, v) => sum + v.averageYield, 0) / performance.length
          : 0,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('RWA Vaults API error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch vault data' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const session = await getServerSession(authOptions);
    if (!session?.user?.id) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { action, vaultId, name, strategy } = await request.json();
    const vaultManager = new RWAVaultManager(session.user.id);

    let result;

    switch (action) {
      case 'create':
        if (!name || !strategy) {
          return NextResponse.json(
            { error: 'Missing required fields for vault creation' },
            { status: 400 }
          );
        }
        result = await vaultManager.createOracleVault(name, strategy);
        break;
        
      case 'rebalance':
        if (!vaultId) {
          return NextResponse.json(
            { error: 'Missing vaultId for rebalancing' },
            { status: 400 }
          );
        }
        result = await vaultManager.rebalanceVault(vaultId);
        break;
        
      case 'check_graduation':
        result = await vaultManager.checkVaultGraduation();
        break;
        
      default:
        return NextResponse.json(
          { error: 'Invalid action. Use "create", "rebalance", or "check_graduation"' },
          { status: 400 }
        );
    }

    return NextResponse.json({
      success: true,
      data: {
        result,
        action,
        timestamp: new Date().toISOString()
      }
    });
  } catch (error) {
    console.error('RWA Vaults POST API error:', error);
    return NextResponse.json(
      { error: 'Failed to process vault action' },
      { status: 500 }
    );
  }
}

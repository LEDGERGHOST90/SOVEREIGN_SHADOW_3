import { NextRequest, NextResponse } from 'next/server';
import { ledgerLiveMetrics } from '@/lib/ledger/ledger-live-metrics';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const action = searchParams.get('action') || 'metrics';

    switch (action) {
      case 'metrics':
        const metrics = ledgerLiveMetrics.getMetrics();
        return NextResponse.json({
          success: true,
          data: metrics,
          timestamp: new Date().toISOString()
        });

      case 'devices':
        const devices = ledgerLiveMetrics.getDevices();
        return NextResponse.json({
          success: true,
          data: devices,
          count: devices.length,
          timestamp: new Date().toISOString()
        });

      case 'connected-devices':
        const connectedDevices = ledgerLiveMetrics.getConnectedDevices();
        return NextResponse.json({
          success: true,
          data: connectedDevices,
          count: connectedDevices.length,
          timestamp: new Date().toISOString()
        });

      case 'security-summary':
        const securitySummary = ledgerLiveMetrics.getSecuritySummary();
        return NextResponse.json({
          success: true,
          data: securitySummary,
          timestamp: new Date().toISOString()
        });

      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid action parameter'
        }, { status: 400 });
    }
  } catch (error) {
    console.error('Ledger metrics API error:', error);
    return NextResponse.json({
      success: false,
      error: 'Internal server error'
    }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, coldStoragePercentage, totalAssets, trade } = body;

    switch (action) {
      case 'update-asset-distribution':
        if (typeof coldStoragePercentage !== 'number') {
          return NextResponse.json({
            success: false,
            error: 'coldStoragePercentage must be a number'
          }, { status: 400 });
        }

        ledgerLiveMetrics.updateAssetDistribution(coldStoragePercentage);
        return NextResponse.json({
          success: true,
          message: 'Asset distribution updated successfully',
          timestamp: new Date().toISOString()
        });

      case 'update-total-assets':
        if (typeof totalAssets !== 'number') {
          return NextResponse.json({
            success: false,
            error: 'totalAssets must be a number'
          }, { status: 400 });
        }

        ledgerLiveMetrics.updateTotalAssets(totalAssets);
        return NextResponse.json({
          success: true,
          message: 'Total assets updated successfully',
          timestamp: new Date().toISOString()
        });

      case 'execute-trade':
        if (!trade) {
          return NextResponse.json({
            success: false,
            error: 'trade object is required'
          }, { status: 400 });
        }

        const result = await ledgerLiveMetrics.executeTradeWithHardwareConfirmation(trade);
        return NextResponse.json({
          success: result.success,
          data: result,
          timestamp: new Date().toISOString()
        });

      default:
        return NextResponse.json({
          success: false,
          error: 'Invalid action'
        }, { status: 400 });
    }
  } catch (error) {
    console.error('Ledger metrics API error:', error);
    return NextResponse.json({
      success: false,
      error: 'Internal server error'
    }, { status: 500 });
  }
}

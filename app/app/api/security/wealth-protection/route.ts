import { NextRequest, NextResponse } from 'next/server';
import { wealthProtection } from '@/lib/security/wealth-protection';

export async function GET() {
  try {
    const securityReport = wealthProtection.generateSecurityReport();
    
    return NextResponse.json({
      success: true,
      security: securityReport,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Failed to generate security report' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, data } = body;

    switch (action) {
      case 'monitor_wealth':
        const { currentWealth, previousWealth } = data;
        const wealthStatus = await wealthProtection.monitorWealthChanges(currentWealth, previousWealth);
        
        return NextResponse.json({
          success: true,
          wealthStatus,
          timestamp: new Date().toISOString()
        });

      case 'validate_position':
        const { symbol, amount, price } = data;
        const positionValidation = wealthProtection.validatePositionSize(symbol, amount, price);
        
        return NextResponse.json({
          success: true,
          validation: positionValidation,
          timestamp: new Date().toISOString()
        });

      case 'detect_suspicious':
        const { activity, context } = data;
        wealthProtection.detectSuspiciousActivity(activity, context);
        
        return NextResponse.json({
          success: true,
          message: 'Suspicious activity monitoring active',
          timestamp: new Date().toISOString()
        });

      case 'validate_2fa':
        const { token, operation } = data;
        const isValid2FA = wealthProtection.validate2FA(token, operation);
        
        return NextResponse.json({
          success: true,
          valid2FA: isValid2FA,
          timestamp: new Date().toISOString()
        });

      default:
        return NextResponse.json(
          { success: false, error: 'Invalid security action' },
          { status: 400 }
        );
    }
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Security operation failed' },
      { status: 500 }
    );
  }
}

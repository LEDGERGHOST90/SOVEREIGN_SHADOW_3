import { NextRequest, NextResponse } from 'next/server';
import { healthCheckSystem } from '@/lib/monitoring/health-checks';

export async function GET() {
  try {
    // Run all health checks
    await Promise.all([
      healthCheckSystem.checkPrimaryAI(),
      healthCheckSystem.checkSecondaryNode(),
      healthCheckSystem.checkMCPServer(),
      healthCheckSystem.checkDataFeeds()
    ]);

    const systemHealth = healthCheckSystem.getSystemHealth();

    return NextResponse.json({
      success: true,
      systemHealth,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Health check failed' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, component } = body;

    switch (action) {
      case 'check_component':
        let healthStatus;
        switch (component) {
          case 'primaryAI':
            healthStatus = await healthCheckSystem.checkPrimaryAI();
            break;
          case 'secondaryNode':
            healthStatus = await healthCheckSystem.checkSecondaryNode();
            break;
          case 'mcpServer':
            healthStatus = await healthCheckSystem.checkMCPServer();
            break;
          case 'dataFeeds':
            healthStatus = await healthCheckSystem.checkDataFeeds();
            break;
          default:
            return NextResponse.json(
              { success: false, error: 'Invalid component' },
              { status: 400 }
            );
        }

        return NextResponse.json({
          success: true,
          component,
          healthStatus,
          timestamp: new Date().toISOString()
        });

      case 'activate_secondary':
        // Trigger secondary node activation
        healthCheckSystem.emit('secondaryNodeActivation', {
          timestamp: new Date().toISOString(),
          action: 'manual_activation'
        });

        return NextResponse.json({
          success: true,
          message: 'Secondary node activation triggered',
          timestamp: new Date().toISOString()
        });

      case 'reset_circuit_breaker':
        // Reset circuit breaker for component
        const circuitBreaker = healthCheckSystem['circuitBreakers'];
        circuitBreaker.set(component, false);
        
        return NextResponse.json({
          success: true,
          message: `Circuit breaker reset for ${component}`,
          timestamp: new Date().toISOString()
        });

      default:
        return NextResponse.json(
          { success: false, error: 'Invalid health check action' },
          { status: 400 }
        );
    }
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Health check operation failed' },
      { status: 500 }
    );
  }
}

/**
 * EMERGENCY HEDGE EXECUTOR
 * ========================
 * Immediate protection for portfolio positions using live API integration
 * Ported from Python emergency_hedge_executor.py
 */

import { placeHedge } from './binanceUS';
import { placeOKXHedge } from './okx';

// Portfolio configuration (will be dynamic in production)
const PORTFOLIO_CONFIG = {
  totalValue: 12725.00,
  ethExposure: 6500.00,
  defaultHedgeRatio: 0.8,
  maxPositionSize: 10000,
  stopLossPct: 0.05
};

/**
 * Calculate optimal hedge parameters
 */
function calculateHedgeParameters(portfolioValue, ethExposure, hedgeRatio = 0.8) {
  const hedgeValue = ethExposure * hedgeRatio;
  const ethPrice = 2650.00; // Will be fetched from live API
  const hedgeSize = hedgeValue / ethPrice;
  
  return {
    hedgeValue,
    hedgeSize: parseFloat(hedgeSize.toFixed(4)),
    ethPrice,
    hedgeRatio
  };
}

/**
 * Execute emergency hedge across multiple platforms
 */
export async function executeEmergencyHedge(asset, customHedgeRatio = null) {
  try {
    console.log("🚨 EMERGENCY HEDGE EXECUTION INITIATED");
    console.log("=" * 50);
    
    // Use asset-specific data or portfolio defaults
    const portfolioValue = asset?.value || PORTFOLIO_CONFIG.totalValue;
    const ethExposure = asset?.symbol === 'ETH' ? asset.value : PORTFOLIO_CONFIG.ethExposure;
    const hedgeRatio = customHedgeRatio || asset?.hedgeRatio || PORTFOLIO_CONFIG.defaultHedgeRatio;
    
    // Calculate hedge parameters
    const hedgeParams = calculateHedgeParameters(portfolioValue, ethExposure, hedgeRatio);
    
    console.log(`💰 Portfolio Value: $${portfolioValue.toFixed(2)}`);
    console.log(`📊 ${asset?.symbol || 'ETH'} Exposure: $${ethExposure.toFixed(2)}`);
    console.log(`🎯 Hedge Value: $${hedgeParams.hedgeValue.toFixed(2)}`);
    console.log(`⚡ Hedge Size: ${hedgeParams.hedgeSize} ${asset?.symbol || 'ETH'}`);
    
    // Prepare hedge order
    const hedgeOrder = {
      timestamp: new Date().toISOString(),
      action: "SHORT",
      symbol: `${asset?.symbol || 'ETH'}-PERP`,
      size: hedgeParams.hedgeSize,
      value: hedgeParams.hedgeValue,
      purpose: `${asset?.symbol || 'STETH'}_HEDGE`,
      platforms: ["BINANCE_US", "OKX"],
      status: "EXECUTING"
    };
    
    console.log("🎯 HEDGE ORDER PREPARED:");
    console.log(`   Action: SHORT ${hedgeOrder.size} ${asset?.symbol || 'ETH'}`);
    console.log(`   Value: $${hedgeOrder.value.toFixed(2)}`);
    console.log(`   Purpose: Protect ${asset?.name || 'ETH'} position`);
    
    // Execute on multiple platforms simultaneously
    const executionPromises = [
      placeHedge({
        symbol: asset?.symbol || 'ETH',
        side: 'SELL',
        quantity: hedgeParams.hedgeSize.toString(),
        orderType: 'MARKET'
      }),
      placeOKXHedge({
        symbol: asset?.symbol || 'ETH',
        side: 'sell',
        quantity: hedgeParams.hedgeSize.toString(),
        orderType: 'market'
      })
    ];
    
    console.log("⚡ EXECUTING HEDGE ON MULTIPLE PLATFORMS...");
    
    const results = await Promise.allSettled(executionPromises);
    
    // Process results
    const binanceResult = results[0];
    const okxResult = results[1];
    
    const executionSummary = {
      hedgeOrder,
      results: {
        binanceUS: binanceResult.status === 'fulfilled' ? binanceResult.value : { success: false, error: binanceResult.reason },
        okx: okxResult.status === 'fulfilled' ? okxResult.value : { success: false, error: okxResult.reason }
      },
      totalSuccess: binanceResult.status === 'fulfilled' && okxResult.status === 'fulfilled',
      partialSuccess: binanceResult.status === 'fulfilled' || okxResult.status === 'fulfilled'
    };
    
    // Log execution results
    console.log("✅ HEDGE EXECUTION COMPLETE!");
    console.log(`📊 Binance.US: ${executionSummary.results.binanceUS.success ? 'SUCCESS' : 'FAILED'}`);
    console.log(`📊 OKX: ${executionSummary.results.okx.success ? 'SUCCESS' : 'FAILED'}`);
    
    if (executionSummary.totalSuccess) {
      console.log("🎉 FULL HEDGE PROTECTION ACTIVATED!");
    } else if (executionSummary.partialSuccess) {
      console.log("⚠️ PARTIAL HEDGE PROTECTION ACTIVATED");
    } else {
      console.log("❌ HEDGE EXECUTION FAILED");
    }
    
    return executionSummary;
    
  } catch (error) {
    console.error("❌ EMERGENCY HEDGE FAILED:", error);
    return {
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    };
  }
}

/**
 * Calculate dynamic hedge ratio based on market conditions
 */
export function calculateDynamicHedgeRatio(asset) {
  const volatility = Math.abs(asset.changeDay) / 100;
  const momentum = asset.changeWeek / 100;
  
  // Base hedge ratio
  let hedgeRatio = 0.5;
  
  // Increase hedge ratio for high volatility
  if (volatility > 0.05) hedgeRatio += 0.2;
  if (volatility > 0.10) hedgeRatio += 0.2;
  
  // Adjust for negative momentum
  if (momentum < -0.05) hedgeRatio += 0.1;
  
  // Cap at 90%
  return Math.min(0.9, hedgeRatio);
}

/**
 * Monitor existing hedge positions
 */
export async function monitorHedgePositions() {
  try {
    // This would fetch actual positions from exchanges
    // For now, return simulated monitoring data
    return {
      activeHedges: [
        {
          platform: "Binance.US",
          symbol: "ETHUSDT",
          side: "SELL",
          size: 1.2381,
          entryPrice: 2650.45,
          currentPnL: 125.50,
          status: "ACTIVE"
        },
        {
          platform: "OKX",
          symbol: "ETH-USDT",
          side: "sell",
          size: 1.2381,
          entryPrice: 2648.20,
          currentPnL: 118.75,
          status: "ACTIVE"
        }
      ],
      totalHedgeValue: 5200.0,
      totalPnL: 244.25,
      hedgeEffectiveness: 0.85
    };
  } catch (error) {
    console.error("❌ HEDGE MONITORING FAILED:", error);
    return { error: error.message };
  }
}


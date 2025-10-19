#!/bin/bash

################################################################################
# 🏴 SOVEREIGN LEGACY LOOP - LEAN FORTRESS BUILDER
# Creates fee-conscious structure for solo systematic trader
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
PROJECT_ROOT="/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]/sovereign_legacy_loop"
BACKUP_DIR="/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]/lean_backup_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$HOME/Desktop/LEAN_BUILD_LOG_$(date +%Y%m%d_%H%M%S).txt"

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}🏴 SOVEREIGN LEGACY LOOP - LEAN FORTRESS BUILDER${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

# Check if project exists
if [ ! -d "$PROJECT_ROOT" ]; then
    echo -e "${RED}❌ Project directory not found: $PROJECT_ROOT${NC}"
    exit 1
fi

echo -e "${YELLOW}📍 Project: $PROJECT_ROOT${NC}"
echo -e "${YELLOW}💾 Backup: $BACKUP_DIR${NC}"
echo -e "${YELLOW}📄 Log: $LOG_FILE${NC}"
echo ""

# Function to log
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo -e "$1"
}

# Confirmation
echo -e "${YELLOW}This will create a lean, fee-conscious structure for solo trading.${NC}"
echo ""
read -p "$(echo -e ${CYAN}Continue? [y/N]: ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Aborted.${NC}"
    exit 0
fi

log "${GREEN}Starting lean fortress build...${NC}"

# Backup
echo ""
log "${BLUE}[1/5] Creating backup...${NC}"
mkdir -p "$BACKUP_DIR"
if [ -d "$PROJECT_ROOT" ]; then
    cp -R "$PROJECT_ROOT" "$BACKUP_DIR/"
    log "${GREEN}✅ Backup created${NC}"
fi

cd "$PROJECT_ROOT"

# Create lean directory structure
echo ""
log "${BLUE}[2/5] Creating lean directory structure...${NC}"

directories=(
    # Core logic
    "lib/portfolio"
    "lib/exchanges"
    "lib/strategies/arbitrage"
    "lib/strategies/rebalancing"
    "lib/strategies/dca"
    "lib/defi/lido"
    "lib/defi/aave"
    "lib/defi/curve"
    "lib/vaults"
    "lib/analytics"
    "lib/utils"
    
    # Components
    "components/portfolio"
    "components/trading"
    "components/defi"
    "components/ui"
    
    # Hooks
    "hooks"
    
    # Types
    "types"
    
    # Config
    "config"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    log "  Created: $dir"
done

log "${GREEN}✅ Directory structure created${NC}"

# Create base classes
echo ""
log "${BLUE}[3/5] Creating base classes and utilities...${NC}"

# BaseExchange.ts
cat > lib/exchanges/BaseExchange.ts << 'EOF'
/**
 * Base Exchange Client
 * All exchange integrations extend this class
 */

export interface ExchangeConfig {
  apiKey: string;
  apiSecret: string;
  testnet?: boolean;
}

export interface Balance {
  asset: string;
  free: number;
  locked: number;
  total: number;
}

export interface Order {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  type: 'market' | 'limit';
  price: number;
  amount: number;
  filled: number;
  status: 'open' | 'filled' | 'cancelled';
  timestamp: Date;
}

export interface Ticker {
  symbol: string;
  bid: number;
  ask: number;
  last: number;
  volume: number;
  timestamp: Date;
}

export abstract class BaseExchange {
  protected config: ExchangeConfig;
  protected name: string;

  constructor(name: string, config: ExchangeConfig) {
    this.name = name;
    this.config = config;
  }

  abstract connect(): Promise<void>;
  abstract disconnect(): Promise<void>;
  
  abstract getBalances(): Promise<Balance[]>;
  abstract getTicker(symbol: string): Promise<Ticker>;
  
  abstract createOrder(
    symbol: string,
    side: 'buy' | 'sell',
    type: 'market' | 'limit',
    amount: number,
    price?: number
  ): Promise<Order>;
  
  abstract cancelOrder(orderId: string): Promise<boolean>;
  abstract getOrder(orderId: string): Promise<Order>;
  
  getName(): string {
    return this.name;
  }
  
  /**
   * Get trading fees for this exchange
   */
  abstract getTradingFees(symbol: string): Promise<{
    maker: number;
    taker: number;
  }>;
  
  /**
   * Get withdrawal fees
   */
  abstract getWithdrawalFee(asset: string): Promise<number>;
}
EOF
log "  Created: lib/exchanges/BaseExchange.ts"

# Fee calculator
cat > lib/utils/fee-calculator.ts << 'EOF'
/**
 * Fee Calculator
 * Calculate all-in transaction costs
 */

export interface FeeBreakdown {
  tradingFee: number;        // Maker/taker fee
  withdrawalFee: number;     // Withdrawal fee (if moving assets)
  gasCost: number;           // Gas cost (if on-chain)
  slippage: number;          // Estimated slippage
  totalFee: number;          // Sum of all fees
  totalFeePercent: number;   // As percentage of trade size
}

export class FeeCalculator {
  /**
   * Calculate all-in fees for an arbitrage trade
   */
  static calculateArbitrageFees(
    tradeSize: number,
    buyExchangeFees: { maker: number; taker: number },
    sellExchangeFees: { maker: number; taker: number },
    withdrawalFee: number,
    estimatedSlippage: number = 0.001  // 0.1% default
  ): FeeBreakdown {
    const buyFee = tradeSize * buyExchangeFees.taker;
    const sellFee = tradeSize * sellExchangeFees.taker;
    const slippageCost = tradeSize * estimatedSlippage;
    
    const totalFee = buyFee + sellFee + withdrawalFee + slippageCost;
    const totalFeePercent = totalFee / tradeSize;
    
    return {
      tradingFee: buyFee + sellFee,
      withdrawalFee,
      gasCost: 0,
      slippage: slippageCost,
      totalFee,
      totalFeePercent
    };
  }
  
  /**
   * Calculate fees for a rebalancing trade
   */
  static calculateRebalanceFees(
    tradeSize: number,
    makerFee: number,
    takerFee: number,
    useMarketOrder: boolean = false
  ): FeeBreakdown {
    const feeRate = useMarketOrder ? takerFee : makerFee;
    const tradingFee = tradeSize * feeRate;
    
    return {
      tradingFee,
      withdrawalFee: 0,
      gasCost: 0,
      slippage: 0,
      totalFee: tradingFee,
      totalFeePercent: feeRate
    };
  }
  
  /**
   * Calculate DeFi transaction costs
   */
  static calculateDeFiFees(
    tradeSize: number,
    gasPrice: number,           // in gwei
    gasLimit: number = 200000,  // estimated gas limit
    ethPrice: number,           // ETH price in USD
    protocolFee: number = 0     // Protocol fee (if any)
  ): FeeBreakdown {
    const gasCostEth = (gasPrice * gasLimit) / 1e9;
    const gasCostUsd = gasCostEth * ethPrice;
    const protocolFeeUsd = tradeSize * protocolFee;
    
    const totalFee = gasCostUsd + protocolFeeUsd;
    
    return {
      tradingFee: protocolFeeUsd,
      withdrawalFee: 0,
      gasCost: gasCostUsd,
      slippage: 0,
      totalFee,
      totalFeePercent: totalFee / tradeSize
    };
  }
}
EOF
log "  Created: lib/utils/fee-calculator.ts"

# Arbitrage detector
cat > lib/strategies/arbitrage/detector.ts << 'EOF'
/**
 * Arbitrage Opportunity Detector
 * Fee-conscious arbitrage detection
 */

import type { BaseExchange, Ticker } from '../../exchanges/BaseExchange';
import { FeeCalculator } from '../../utils/fee-calculator';

export interface ArbitrageOpportunity {
  symbol: string;
  buyExchange: string;
  sellExchange: string;
  buyPrice: number;
  sellPrice: number;
  
  // Profitability
  spreadPercent: number;        // Raw spread
  estimatedFees: number;        // Total fees
  netProfitPercent: number;     // spread - fees
  
  // Execution
  isExecutable: boolean;        // Only true if profitable
  minProfitableSize: number;    // Minimum size to be profitable
  recommendedSize: number;      // Optimal size
  
  timestamp: Date;
}

export class ArbitrageDetector {
  private exchanges: BaseExchange[];
  private minNetProfit: number;
  
  constructor(exchanges: BaseExchange[], minNetProfit: number = 0.005) {
    this.exchanges = exchanges;
    this.minNetProfit = minNetProfit;  // 0.5% default minimum
  }
  
  /**
   * Detect arbitrage opportunities across all exchange pairs
   */
  async detectOpportunities(symbols: string[]): Promise<ArbitrageOpportunity[]> {
    const opportunities: ArbitrageOpportunity[] = [];
    
    for (const symbol of symbols) {
      // Get tickers from all exchanges
      const tickers = await this.getTickersForSymbol(symbol);
      
      // Compare all pairs
      for (let i = 0; i < tickers.length; i++) {
        for (let j = i + 1; j < tickers.length; j++) {
          const opp1 = await this.analyzeOpportunity(tickers[i], tickers[j]);
          const opp2 = await this.analyzeOpportunity(tickers[j], tickers[i]);
          
          if (opp1.isExecutable) opportunities.push(opp1);
          if (opp2.isExecutable) opportunities.push(opp2);
        }
      }
    }
    
    return opportunities.sort((a, b) => b.netProfitPercent - a.netProfitPercent);
  }
  
  private async getTickersForSymbol(symbol: string): Promise<Array<{ exchange: BaseExchange; ticker: Ticker }>> {
    const tickers = await Promise.all(
      this.exchanges.map(async (exchange) => {
        try {
          const ticker = await exchange.getTicker(symbol);
          return { exchange, ticker };
        } catch (error) {
          return null;
        }
      })
    );
    
    return tickers.filter((t) => t !== null) as Array<{ exchange: BaseExchange; ticker: Ticker }>;
  }
  
  private async analyzeOpportunity(
    buy: { exchange: BaseExchange; ticker: Ticker },
    sell: { exchange: BaseExchange; ticker: Ticker }
  ): Promise<ArbitrageOpportunity> {
    const spreadPercent = (sell.ticker.bid - buy.ticker.ask) / buy.ticker.ask;
    
    // Get fees
    const buyFees = await buy.exchange.getTradingFees(buy.ticker.symbol);
    const sellFees = await sell.exchange.getTradingFees(sell.ticker.symbol);
    const withdrawalFee = await buy.exchange.getWithdrawalFee(buy.ticker.symbol.split('/')[0]);
    
    // Calculate all-in fees
    const tradeSize = 10000; // Estimate for $10k trade
    const feeBreakdown = FeeCalculator.calculateArbitrageFees(
      tradeSize,
      buyFees,
      sellFees,
      withdrawalFee
    );
    
    const netProfitPercent = spreadPercent - feeBreakdown.totalFeePercent;
    const isExecutable = netProfitPercent > this.minNetProfit;
    
    return {
      symbol: buy.ticker.symbol,
      buyExchange: buy.exchange.getName(),
      sellExchange: sell.exchange.getName(),
      buyPrice: buy.ticker.ask,
      sellPrice: sell.ticker.bid,
      spreadPercent,
      estimatedFees: feeBreakdown.totalFeePercent,
      netProfitPercent,
      isExecutable,
      minProfitableSize: withdrawalFee / spreadPercent,  // Rough estimate
      recommendedSize: 0,  // TODO: Calculate based on liquidity
      timestamp: new Date()
    };
  }
}
EOF
log "  Created: lib/strategies/arbitrage/detector.ts"

# Portfolio aggregator
cat > lib/portfolio/aggregator.ts << 'EOF'
/**
 * Portfolio Aggregator
 * Combine positions from all exchanges and DeFi protocols
 */

import type { BaseExchange, Balance } from '../exchanges/BaseExchange';

export interface Position {
  asset: string;
  amount: number;
  valueUSD: number;
  location: string;  // Exchange or wallet name
  type: 'exchange' | 'defi' | 'cold_storage';
}

export interface AggregatedPortfolio {
  positions: Position[];
  totalValueUSD: number;
  allocation: Record<string, number>;  // asset → percentage
  timestamp: Date;
}

export class PortfolioAggregator {
  private exchanges: BaseExchange[];
  
  constructor(exchanges: BaseExchange[]) {
    this.exchanges = exchanges;
  }
  
  /**
   * Get all positions across all exchanges
   */
  async aggregatePositions(prices: Record<string, number>): Promise<AggregatedPortfolio> {
    const positions: Position[] = [];
    
    // Get exchange balances
    for (const exchange of this.exchanges) {
      const balances = await exchange.getBalances();
      
      for (const balance of balances) {
        if (balance.total > 0) {
          const price = prices[balance.asset] || 0;
          positions.push({
            asset: balance.asset,
            amount: balance.total,
            valueUSD: balance.total * price,
            location: exchange.getName(),
            type: 'exchange'
          });
        }
      }
    }
    
    // Calculate totals
    const totalValueUSD = positions.reduce((sum, p) => sum + p.valueUSD, 0);
    
    // Calculate allocation
    const allocation: Record<string, number> = {};
    for (const position of positions) {
      if (!allocation[position.asset]) {
        allocation[position.asset] = 0;
      }
      allocation[position.asset] += position.valueUSD / totalValueUSD;
    }
    
    return {
      positions,
      totalValueUSD,
      allocation,
      timestamp: new Date()
    };
  }
}
EOF
log "  Created: lib/portfolio/aggregator.ts"

# Types
cat > types/portfolio.ts << 'EOF'
export interface Position {
  asset: string;
  amount: number;
  valueUSD: number;
  location: string;
  type: 'exchange' | 'defi' | 'cold_storage';
}

export interface Allocation {
  asset: string;
  current: number;
  target: number;
  drift: number;
}

export interface RebalancePlan {
  allocations: Allocation[];
  trades: Trade[];
  estimatedFees: number;
  estimatedTime: number;
}

export interface Trade {
  symbol: string;
  side: 'buy' | 'sell';
  amount: number;
  estimatedPrice: number;
  estimatedFee: number;
  exchange: string;
}
EOF
log "  Created: types/portfolio.ts"

cat > types/exchange.ts << 'EOF'
export type OrderSide = 'buy' | 'sell';
export type OrderType = 'market' | 'limit' | 'stop';
export type OrderStatus = 'open' | 'filled' | 'cancelled';

export interface Order {
  id: string;
  symbol: string;
  side: OrderSide;
  type: OrderType;
  price: number;
  amount: number;
  filled: number;
  status: OrderStatus;
  timestamp: Date;
}

export interface Balance {
  asset: string;
  free: number;
  locked: number;
  total: number;
}
EOF
log "  Created: types/exchange.ts"

# Config
cat > config/thresholds.ts << 'EOF'
/**
 * Trading Thresholds Configuration
 * Fee-conscious thresholds for systematic trading
 */

export const THRESHOLDS = {
  // Arbitrage
  arbitrage: {
    minNetProfit: 0.005,        // 0.5% minimum after all fees
    minTradeSize: 1000,         // $1000 minimum
    maxTradeSize: 50000,        // $50k maximum per trade
    maxSlippage: 0.002,         // 0.2% maximum slippage
  },
  
  // Rebalancing
  rebalancing: {
    driftThreshold: 0.05,       // 5% drift triggers rebalance
    minTradeSize: 500,          // Don't trade < $500
    maxTradesPerRebalance: 5,   // Limit total trades (fees!)
  },
  
  // DCA
  dca: {
    frequency: 'weekly' as const,  // Weekly buys
    amountUSD: 500,                // $500 per buy
    maxGasPrice: 50,               // Only buy when gas < 50 gwei
  },
  
  // DeFi
  defi: {
    minYieldDifferential: 0.02,  // 2% APY difference to move funds
    maxGasPrice: 30,             // Only execute when gas < 30 gwei
    minPositionSize: 5000,       // $5k minimum for DeFi positions
  },
  
  // Risk
  risk: {
    coldStoragePercent: 0.70,    // 70% in cold storage
    maxPositionSize: 0.10,       // 10% max per position
    maxDrawdown: 0.20,           // 20% max drawdown
  }
} as const;
EOF
log "  Created: config/thresholds.ts"

# README
cat > lib/README.md << 'EOF'
# Sovereign Legacy Loop - Core Library

This is your trading brain. All business logic lives here.

## Structure

- `portfolio/` - Position aggregation, allocation, rebalancing
- `exchanges/` - Binance, OKX, Kraken client implementations
- `strategies/` - Arbitrage, rebalancing, DCA strategies
- `defi/` - LIDO, AAVE, Curve integrations
- `vaults/` - Ledger monitor, hot wallet management
- `analytics/` - Performance tracking, cost basis, risk metrics
- `utils/` - Fee calculator, gas tracker, slippage estimator

## Principles

1. **Fee-Conscious:** Every strategy considers fees explicitly
2. **Threshold-Based:** Trade on drift, not time
3. **Single Source of Truth:** One implementation per concept
4. **Type-Safe:** Full TypeScript, strict mode enabled

## Quick Start

```typescript
import { PortfolioAggregator } from '@/lib/portfolio/aggregator';
import { ArbitrageDetector } from '@/lib/strategies/arbitrage/detector';
import { BinanceClient } from '@/lib/exchanges/BinanceClient';

// Initialize
const binance = new BinanceClient({ apiKey: '...', apiSecret: '...' });
const aggregator = new PortfolioAggregator([binance]);

// Get portfolio
const portfolio = await aggregator.aggregatePositions(prices);

// Find arbitrage
const detector = new ArbitrageDetector([binance, okx]);
const opportunities = await detector.detectOpportunities(['BTC/USDT']);
```

## Fee-Conscious By Default

```typescript
// Arbitrage only executed if profitable after ALL fees
const opportunities = await detector.detectOpportunities(['BTC/USDT']);
const profitable = opportunities.filter(o => o.isExecutable);

// Rebalancing only when drift exceeds threshold
const drift = calculateDrift(current, target);
if (drift > 0.05) {  // 5% threshold
  const plan = generateRebalancePlan(current, target);
}
```
EOF
log "  Created: lib/README.md"

log "${GREEN}✅ Base files created${NC}"

# Create documentation
echo ""
log "${BLUE}[4/5] Creating documentation...${NC}"

cat > LEAN_MIGRATION_GUIDE.md << 'EOF'
# Lean Migration Guide

## Quick Migration

### 1. Move Exchange Clients

```bash
# Find your exchange files
find . -name "*binance*" -o -name "*okx*" -o -name "*kraken*"

# Move to lib/exchanges/
mv your-binance-file.ts lib/exchanges/BinanceClient.ts
mv your-okx-file.ts lib/exchanges/OKXClient.ts

# Make them extend BaseExchange
```

### 2. Move Trading Logic

```bash
# Find trading/arbitrage logic
find . -name "*arbitrage*" -o -name "*trading*" -o -name "*strategy*"

# Move to appropriate strategy folder
mv arbitrage-logic.ts lib/strategies/arbitrage/
```

### 3. Move Portfolio Logic

```bash
# Find portfolio management
find . -name "*portfolio*" -o -name "*balance*" -o -name "*allocation*"

# Move to lib/portfolio/
```

### 4. Move DeFi Integrations

```bash
# Find DeFi files
find . -name "*lido*" -o -name "*aave*" -o -name "*curve*"

# Move to lib/defi/[protocol]/
```

### 5. Organize Components

```bash
# Move portfolio UI
mv PortfolioCard.tsx components/portfolio/

# Move trading UI
mv TradeForm.tsx components/trading/

# Move DeFi UI
mv LidoStaking.tsx components/defi/
```

## Validation

```bash
npm run type-check  # TypeScript compilation
npm run lint        # Code quality
npm run build       # Production build
```

## Questions?

Share your specific files with Claude for custom migration steps.
EOF
log "  Created: LEAN_MIGRATION_GUIDE.md"

log "${GREEN}✅ Documentation created${NC}"

# Summary
echo ""
log "${BLUE}[5/5] Generating summary...${NC}"

{
    echo "# LEAN FORTRESS BUILD COMPLETE"
    echo ""
    echo "**Generated:** $(date)"
    echo ""
    echo "## What Was Created"
    echo ""
    echo "### Directory Structure"
    echo "- ✅ lib/portfolio/ - Position aggregation & rebalancing"
    echo "- ✅ lib/exchanges/ - Exchange client implementations"
    echo "- ✅ lib/strategies/ - Arbitrage, rebalancing, DCA"
    echo "- ✅ lib/defi/ - DeFi protocol integrations"
    echo "- ✅ lib/vaults/ - Wallet management"
    echo "- ✅ lib/analytics/ - Performance tracking"
    echo "- ✅ lib/utils/ - Fee calculator, gas tracker"
    echo "- ✅ components/ - UI components by domain"
    echo "- ✅ types/ - TypeScript definitions"
    echo "- ✅ config/ - Configuration & thresholds"
    echo ""
    echo "### Base Classes"
    echo "- ✅ BaseExchange.ts - All exchanges extend this"
    echo "- ✅ FeeCalculator - All-in fee calculation"
    echo "- ✅ ArbitrageDetector - Fee-conscious arbitrage"
    echo "- ✅ PortfolioAggregator - Position aggregation"
    echo ""
    echo "### Configuration"
    echo "- ✅ thresholds.ts - Trading thresholds (5% rebalance, 0.5% arbitrage)"
    echo ""
    echo "## Next Steps"
    echo ""
    echo "1. Review lib/README.md for architecture overview"
    echo "2. Review LEAN_MIGRATION_GUIDE.md for migration steps"
    echo "3. Implement exchange clients (extend BaseExchange)"
    echo "4. Move existing logic to appropriate domains"
    echo "5. Build UI components"
    echo "6. Test thoroughly"
    echo ""
    echo "## Backup Location"
    echo ""
    echo "$BACKUP_DIR"
    echo ""
} > LEAN_BUILD_SUMMARY.md

log "${GREEN}✅ Summary created: LEAN_BUILD_SUMMARY.md${NC}"

echo ""
log "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
log "${GREEN}✅ LEAN FORTRESS BUILD COMPLETE${NC}"
log "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
log "${CYAN}📦 What was created:${NC}"
log "   • Lean directory structure (portfolio, exchanges, strategies, defi)"
log "   • Base classes (BaseExchange, FeeCalculator, ArbitrageDetector)"
log "   • Type definitions and configuration"
log "   • Migration guide and documentation"
echo ""
log "${YELLOW}📋 Next steps:${NC}"
log "   1. Review LEAN_BUILD_SUMMARY.md"
log "   2. Review lib/README.md for architecture"
log "   3. Implement your exchange clients"
log "   4. Move existing code to new structure"
log "   5. Build and test"
echo ""
log "${PURPLE}💾 Backup: $BACKUP_DIR${NC}"
log "${PURPLE}📄 Log: $LOG_FILE${NC}"
echo ""
log "${GREEN}🏴 Ready to build your fee-conscious trading empire!${NC}"
echo ""


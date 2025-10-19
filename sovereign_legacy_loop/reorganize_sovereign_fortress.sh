#!/bin/bash

################################################################################
# SOVEREIGN SHADOW AI - FORTRESS REORGANIZATION SCRIPT
# Systematically reorganizes the project into domain-driven architecture
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]/sovereign_legacy_loop"
BACKUP_DIR="/Volumes/LegacySafe/SovereignShadow.Ai[LegacyLoop]/reorganization_backup_$(date +%Y%m%d_%H%M%S)"
LOG_FILE="$HOME/Desktop/REORGANIZATION_LOG_$(date +%Y%m%d_%H%M%S).txt"

echo -e "${CYAN}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}🏴 SOVEREIGN SHADOW AI - FORTRESS REORGANIZATION${NC}"
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

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
    echo -e "$1"
}

# Confirmation prompt
echo -e "${RED}⚠️  WARNING: This will restructure your entire project!${NC}"
echo -e "${YELLOW}📋 Before proceeding, ensure you have:${NC}"
echo -e "   1. Run the scan script and reviewed the audit"
echo -e "   2. Committed all changes to git"
echo -e "   3. Understand the target architecture"
echo ""
read -p "$(echo -e ${CYAN}Continue with reorganization? [y/N]: ${NC})" -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Aborted.${NC}"
    exit 0
fi

log "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
log "${GREEN}Starting reorganization...${NC}"
log "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"

# Phase 1: Backup
echo ""
log "${BLUE}[Phase 1/6] Creating backup...${NC}"
mkdir -p "$BACKUP_DIR"
cp -R "$PROJECT_ROOT" "$BACKUP_DIR/"
log "${GREEN}✅ Backup created: $BACKUP_DIR${NC}"

# Change to project directory
cd "$PROJECT_ROOT"

# Phase 2: Create new directory structure
echo ""
log "${BLUE}[Phase 2/6] Creating fortress directory structure...${NC}"

# Create main directories
directories=(
    # Trading domain
    "lib/trading/engines/base"
    "lib/trading/engines/spot"
    "lib/trading/engines/arbitrage"
    "lib/trading/engines/futures"
    "lib/trading/exchanges"
    "lib/trading/strategies"
    "lib/trading/risk"
    
    # Portfolio domain
    "lib/portfolio"
    
    # AI domain
    "lib/ai/agents"
    "lib/ai/models"
    "lib/ai/orchestrator"
    
    # Blockchain domain
    "lib/blockchain/wallets"
    "lib/blockchain/onchain"
    
    # Analytics domain
    "lib/analytics"
    
    # Data layer
    "lib/data/database/queries"
    "lib/data/database/migrations"
    "lib/data/cache"
    "lib/data/api-clients"
    
    # Utils
    "lib/utils"
    
    # Components
    "components/ui"
    "components/dashboard"
    "components/trading"
    "components/portfolio"
    "components/ai"
    
    # Hooks
    "hooks"
    
    # Types
    "types"
    
    # Config
    "config"
    
    # Scripts (Python backend)
    "scripts/backend/engines"
    "scripts/backend/exchanges"
    "scripts/backend/strategies"
    "scripts/deployment"
    "scripts/maintenance"
    
    # Tests
    "tests/unit"
    "tests/integration"
    "tests/e2e"
    
    # Docs
    "docs/api"
    "docs/architecture"
    "docs/guides"
)

for dir in "${directories[@]}"; do
    mkdir -p "$dir"
    log "  Created: $dir"
done

log "${GREEN}✅ Directory structure created${NC}"

# Phase 3: Create base classes and types
echo ""
log "${BLUE}[Phase 3/6] Creating foundation files...${NC}"

# Create BaseEngine.ts
cat > lib/trading/engines/base/BaseEngine.ts << 'EOF'
/**
 * Base Trading Engine
 * All trading engines must extend this class
 */

export interface EngineConfig {
  exchange: string;
  symbol: string;
  timeframe?: string;
  maxPositionSize?: number;
  riskPerTrade?: number;
}

export interface TradeSignal {
  type: 'buy' | 'sell' | 'hold';
  price: number;
  amount: number;
  timestamp: Date;
  confidence: number;
}

export abstract class BaseEngine {
  protected config: EngineConfig;
  protected isRunning: boolean = false;

  constructor(config: EngineConfig) {
    this.config = config;
  }

  /**
   * Initialize the engine
   */
  abstract initialize(): Promise<void>;

  /**
   * Start the engine
   */
  async start(): Promise<void> {
    if (this.isRunning) {
      throw new Error('Engine is already running');
    }
    
    await this.initialize();
    this.isRunning = true;
    console.log(`[${this.constructor.name}] Started`);
  }

  /**
   * Stop the engine
   */
  async stop(): Promise<void> {
    this.isRunning = false;
    console.log(`[${this.constructor.name}] Stopped`);
  }

  /**
   * Generate trading signal
   */
  abstract generateSignal(): Promise<TradeSignal>;

  /**
   * Execute trade
   */
  abstract executeTrade(signal: TradeSignal): Promise<boolean>;

  /**
   * Get current status
   */
  getStatus() {
    return {
      name: this.constructor.name,
      running: this.isRunning,
      config: this.config,
    };
  }
}
EOF
log "  Created: lib/trading/engines/base/BaseEngine.ts"

# Create EngineTypes.ts
cat > lib/trading/engines/base/EngineTypes.ts << 'EOF'
/**
 * Shared types for all trading engines
 */

export type OrderSide = 'buy' | 'sell';
export type OrderType = 'market' | 'limit' | 'stop';
export type OrderStatus = 'pending' | 'filled' | 'cancelled' | 'rejected';

export interface Order {
  id: string;
  symbol: string;
  side: OrderSide;
  type: OrderType;
  price: number;
  amount: number;
  status: OrderStatus;
  timestamp: Date;
}

export interface Position {
  symbol: string;
  side: OrderSide;
  entryPrice: number;
  currentPrice: number;
  amount: number;
  unrealizedPnL: number;
  realizedPnL: number;
  openedAt: Date;
}

export interface MarketData {
  symbol: string;
  price: number;
  volume: number;
  timestamp: Date;
}
EOF
log "  Created: lib/trading/engines/base/EngineTypes.ts"

# Create SpotEngine.ts
cat > lib/trading/engines/spot/SpotEngine.ts << 'EOF'
/**
 * Spot Trading Engine
 * Handles spot market trading
 */

import { BaseEngine, EngineConfig, TradeSignal } from '../base/BaseEngine';
import type { Order, Position } from '../base/EngineTypes';

export class SpotEngine extends BaseEngine {
  private positions: Map<string, Position> = new Map();

  constructor(config: EngineConfig) {
    super(config);
  }

  async initialize(): Promise<void> {
    console.log('[SpotEngine] Initializing...');
    // Load existing positions, connect to exchange, etc.
  }

  async generateSignal(): Promise<TradeSignal> {
    // Implement spot trading signal generation logic
    return {
      type: 'hold',
      price: 0,
      amount: 0,
      timestamp: new Date(),
      confidence: 0,
    };
  }

  async executeTrade(signal: TradeSignal): Promise<boolean> {
    console.log('[SpotEngine] Executing trade:', signal);
    // Implement trade execution logic
    return true;
  }

  getPositions(): Position[] {
    return Array.from(this.positions.values());
  }
}
EOF
log "  Created: lib/trading/engines/spot/SpotEngine.ts"

# Create ArbitrageEngine.ts
cat > lib/trading/engines/arbitrage/ArbitrageEngine.ts << 'EOF'
/**
 * Arbitrage Trading Engine
 * Identifies and executes arbitrage opportunities across exchanges
 */

import { BaseEngine, EngineConfig, TradeSignal } from '../base/BaseEngine';

export interface ArbitrageOpportunity {
  buyExchange: string;
  sellExchange: string;
  symbol: string;
  buyPrice: number;
  sellPrice: number;
  profit: number;
  profitPercentage: number;
}

export class ArbitrageEngine extends BaseEngine {
  private opportunities: ArbitrageOpportunity[] = [];

  constructor(config: EngineConfig) {
    super(config);
  }

  async initialize(): Promise<void> {
    console.log('[ArbitrageEngine] Initializing...');
    // Connect to multiple exchanges
  }

  async generateSignal(): Promise<TradeSignal> {
    // Scan for arbitrage opportunities
    await this.scanOpportunities();
    
    if (this.opportunities.length > 0) {
      const best = this.opportunities[0];
      return {
        type: 'buy',
        price: best.buyPrice,
        amount: this.config.maxPositionSize || 0,
        timestamp: new Date(),
        confidence: best.profitPercentage,
      };
    }

    return {
      type: 'hold',
      price: 0,
      amount: 0,
      timestamp: new Date(),
      confidence: 0,
    };
  }

  async executeTrade(signal: TradeSignal): Promise<boolean> {
    console.log('[ArbitrageEngine] Executing arbitrage:', signal);
    // Execute simultaneous buy/sell on different exchanges
    return true;
  }

  private async scanOpportunities(): Promise<void> {
    // Implement opportunity scanning logic
    this.opportunities = [];
  }

  getOpportunities(): ArbitrageOpportunity[] {
    return this.opportunities;
  }
}
EOF
log "  Created: lib/trading/engines/arbitrage/ArbitrageEngine.ts"

# Create BaseExchange.ts
cat > lib/trading/exchanges/BaseExchange.ts << 'EOF'
/**
 * Base Exchange Adapter
 * All exchange adapters must implement this interface
 */

import type { Order, OrderSide, OrderType } from '../engines/base/EngineTypes';

export interface ExchangeConfig {
  apiKey: string;
  apiSecret: string;
  testnet?: boolean;
}

export interface Ticker {
  symbol: string;
  bid: number;
  ask: number;
  last: number;
  volume: number;
  timestamp: Date;
}

export interface Balance {
  asset: string;
  free: number;
  locked: number;
  total: number;
}

export abstract class BaseExchange {
  protected config: ExchangeConfig;
  protected isConnected: boolean = false;

  constructor(config: ExchangeConfig) {
    this.config = config;
  }

  abstract connect(): Promise<void>;
  abstract disconnect(): Promise<void>;
  
  abstract getTicker(symbol: string): Promise<Ticker>;
  abstract getBalance(asset?: string): Promise<Balance[]>;
  
  abstract createOrder(
    symbol: string,
    side: OrderSide,
    type: OrderType,
    amount: number,
    price?: number
  ): Promise<Order>;
  
  abstract cancelOrder(orderId: string): Promise<boolean>;
  abstract getOrder(orderId: string): Promise<Order>;
  abstract getOpenOrders(symbol?: string): Promise<Order[]>;

  getName(): string {
    return this.constructor.name;
  }

  isReady(): boolean {
    return this.isConnected;
  }
}
EOF
log "  Created: lib/trading/exchanges/BaseExchange.ts"

# Create trading types
cat > types/trading.ts << 'EOF'
/**
 * Shared trading types
 */

export * from '../lib/trading/engines/base/EngineTypes';

export interface TradingAccount {
  id: string;
  exchange: string;
  balance: number;
  equity: number;
  marginUsed: number;
  marginAvailable: number;
}

export interface TradingConfig {
  maxRiskPerTrade: number;
  maxDailyLoss: number;
  maxPositions: number;
  allowedSymbols: string[];
}
EOF
log "  Created: types/trading.ts"

# Create portfolio types
cat > types/portfolio.ts << 'EOF'
/**
 * Portfolio types
 */

export interface Asset {
  symbol: string;
  name: string;
  amount: number;
  price: number;
  value: number;
  allocation: number;
}

export interface Portfolio {
  id: string;
  name: string;
  totalValue: number;
  assets: Asset[];
  performance: PerformanceMetrics;
}

export interface PerformanceMetrics {
  dayChange: number;
  dayChangePercent: number;
  weekChange: number;
  weekChangePercent: number;
  monthChange: number;
  monthChangePercent: number;
  allTimeHigh: number;
  allTimeLow: number;
}
EOF
log "  Created: types/portfolio.ts"

# Create README in lib directory
cat > lib/README.md << 'EOF'
# Sovereign Shadow AI - Core Library

This directory contains all business logic for the Sovereign Shadow AI trading platform.

## Architecture

```
lib/
├── trading/     # Trading domain - All trading engines, exchanges, strategies
├── portfolio/   # Portfolio management - Asset allocation, tracking, performance
├── ai/          # AI agents - Trading agents, analysis, orchestration
├── blockchain/  # Blockchain integration - Wallets, on-chain operations
├── analytics/   # Analytics - Metrics, performance analysis, reporting
├── data/        # Data access layer - Database, cache, API clients
└── utils/       # Shared utilities - Logger, validation, formatting
```

## Design Principles

1. **Single Source of Truth**: Each concept has ONE canonical implementation
2. **Composition over Inheritance**: Prefer composing smaller pieces
3. **Domain-Driven**: Code organized by business domain, not technical layer
4. **Type-Safe**: Full TypeScript with strict mode enabled
5. **Testable**: Pure functions, dependency injection, clear interfaces

## Import Guidelines

Always use absolute imports from `@/lib/`:

```typescript
// ✅ Correct
import { SpotEngine } from '@/lib/trading/engines/spot/SpotEngine';
import { BaseExchange } from '@/lib/trading/exchanges/BaseExchange';

// ❌ Wrong
import { SpotEngine } from '../../../lib/trading/engines/spot/SpotEngine';
```

## Adding New Features

1. Identify the domain (trading, portfolio, ai, etc.)
2. Create files in the appropriate domain directory
3. Extend base classes where applicable
4. Add types to `types/` directory
5. Write tests in `tests/` mirroring the source structure
6. Update documentation

## Questions?

See `/docs/architecture/` for detailed design documentation.
EOF
log "  Created: lib/README.md"

log "${GREEN}✅ Foundation files created${NC}"

# Phase 4: Create README for the reorganization
echo ""
log "${BLUE}[Phase 4/6] Creating migration guide...${NC}"

cat > MIGRATION_GUIDE.md << 'EOF'
# Migration Guide - Fortress Reorganization

## Overview

This guide helps you migrate existing files into the new fortress architecture.

## Quick Reference

### Where Files Go

| Old Location | New Location | Why |
|-------------|--------------|-----|
| Root `.ts` files | `lib/[domain]/` | Business logic belongs in domain |
| Components | `components/[domain]/` | Organize by feature area |
| API routes | `app/api/[domain]/` | Group by domain |
| Utilities | `lib/utils/` | Shared utilities |
| Types | `types/` | Centralized type definitions |
| Python scripts | `scripts/backend/` | Backend logic |

### Import Path Updates

After moving files, update imports:

```typescript
// Old
import { TradingEngine } from '../../trading/engine';

// New
import { SpotEngine } from '@/lib/trading/engines/spot/SpotEngine';
```

### Trading Engine Migration

If you have existing trading engines:

1. Identify the type (spot, arbitrage, futures)
2. Extend `BaseEngine` from `lib/trading/engines/base/BaseEngine.ts`
3. Implement required methods: `initialize()`, `generateSignal()`, `executeTrade()`
4. Move to appropriate directory: `lib/trading/engines/[type]/`

Example:

```typescript
import { BaseEngine, EngineConfig, TradeSignal } from '../base/BaseEngine';

export class MyCustomEngine extends BaseEngine {
  async initialize(): Promise<void> {
    // Your initialization logic
  }

  async generateSignal(): Promise<TradeSignal> {
    // Your signal generation logic
  }

  async executeTrade(signal: TradeSignal): Promise<boolean> {
    // Your trade execution logic
  }
}
```

## Step-by-Step Migration

### 1. Trading Engines

```bash
# Find all trading engine files
find . -type f -name "*engine*.ts" -o -name "*Engine*.ts"

# For each engine:
# 1. Determine type (spot/arbitrage/futures)
# 2. Refactor to extend BaseEngine
# 3. Move to lib/trading/engines/[type]/
# 4. Update all imports
```

### 2. Exchange Adapters

```bash
# Find exchange-related files
find . -type f -name "*exchange*.ts" -o -name "*binance*.ts" -o -name "*okx*.ts"

# For each adapter:
# 1. Refactor to extend BaseExchange
# 2. Move to lib/trading/exchanges/
# 3. Update all imports
```

### 3. Components

```bash
# Find all component files
find . -type f -name "*.tsx" -not -path "*/node_modules/*"

# Organize by domain:
# - Trading UI → components/trading/
# - Portfolio UI → components/portfolio/
# - Dashboard → components/dashboard/
# - Base UI → components/ui/
```

### 4. Utilities

```bash
# Find utility files
find . -type f -name "*util*.ts" -o -name "*helper*.ts"

# Move to lib/utils/
# Update imports to @/lib/utils/
```

## Validation Checklist

After migration:

- [ ] Run TypeScript compiler: `npm run type-check`
- [ ] Run linter: `npm run lint`
- [ ] Run tests: `npm test`
- [ ] Build project: `npm run build`
- [ ] Start dev server: `npm run dev`
- [ ] Manually test key features

## Common Issues

### Circular Dependencies

If you encounter circular dependency errors:

1. Check import chain: A → B → C → A
2. Extract shared types to `types/` directory
3. Use dependency injection instead of direct imports

### Cannot Find Module

Update your `tsconfig.json`:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./*"],
      "@/lib/*": ["lib/*"],
      "@/components/*": ["components/*"],
      "@/types/*": ["types/*"]
    }
  }
}
```

### Tests Failing

Update test imports and mock paths to match new structure.

## Need Help?

Share your migration issues with Claude along with:
1. The error message
2. The file you're trying to migrate
3. The current import structure

Claude will provide specific migration steps for your situation.
EOF

log "  Created: MIGRATION_GUIDE.md"
log "${GREEN}✅ Migration guide created${NC}"

# Phase 5: Analysis and recommendations
echo ""
log "${BLUE}[Phase 5/6] Analyzing existing files...${NC}"

log "Scanning for trading engines..."
find . -type f \( -name "*engine*.ts" -o -name "*Engine*.ts" \) -not -path "*/node_modules/*" -not -path "*/.next/*" -not -path "*/lib/trading/engines/*" > /tmp/engines_to_migrate.txt || true

log "Scanning for exchange adapters..."
find . -type f \( -name "*exchange*.ts" -o -name "*binance*.ts" -o -name "*okx*.ts" -o -name "*kraken*.ts" -o -name "*coinbase*.ts" \) -not -path "*/node_modules/*" -not -path "*/.next/*" -not -path "*/lib/trading/exchanges/*" > /tmp/exchanges_to_migrate.txt || true

log "Scanning for loose components..."
find . -maxdepth 1 -type f -name "*.tsx" > /tmp/components_to_migrate.txt || true

log "Scanning for loose TypeScript files..."
find . -maxdepth 1 -type f \( -name "*.ts" -o -name "*.tsx" \) > /tmp/loose_files.txt || true

log "${GREEN}✅ Analysis complete${NC}"

# Phase 6: Create migration commands
echo ""
log "${BLUE}[Phase 6/6] Generating migration commands...${NC}"

{
    echo "# AUTOMATED MIGRATION COMMANDS"
    echo "# Generated: $(date)"
    echo ""
    echo "# =================================================="
    echo "# These commands will help you migrate existing files"
    echo "# =================================================="
    echo ""
    
    if [ -s /tmp/engines_to_migrate.txt ]; then
        echo "# Trading Engines to Migrate:"
        while IFS= read -r file; do
            filename=$(basename "$file")
            echo "# - $file → lib/trading/engines/[spot|arbitrage|futures]/$filename"
            echo "# mv \"$file\" lib/trading/engines/spot/$filename  # Adjust directory as needed"
        done < /tmp/engines_to_migrate.txt
        echo ""
    fi
    
    if [ -s /tmp/exchanges_to_migrate.txt ]; then
        echo "# Exchange Adapters to Migrate:"
        while IFS= read -r file; do
            filename=$(basename "$file")
            echo "# - $file → lib/trading/exchanges/$filename"
            echo "# mv \"$file\" lib/trading/exchanges/$filename"
        done < /tmp/exchanges_to_migrate.txt
        echo ""
    fi
    
    if [ -s /tmp/components_to_migrate.txt ]; then
        echo "# Loose Components to Organize:"
        while IFS= read -r file; do
            filename=$(basename "$file")
            echo "# - $file → components/[domain]/$filename"
            echo "# mv \"$file\" components/dashboard/$filename  # Adjust directory as needed"
        done < /tmp/components_to_migrate.txt
        echo ""
    fi
    
    echo "# =================================================="
    echo "# NEXT STEPS"
    echo "# =================================================="
    echo "#"
    echo "# 1. Review the migration commands above"
    echo "# 2. Execute commands one by one (or in batches)"
    echo "# 3. Update imports in affected files"
    echo "# 4. Run: npm run type-check"
    echo "# 5. Fix any TypeScript errors"
    echo "# 6. Test your application"
    echo ""
    
} > MIGRATION_COMMANDS.sh

log "  Created: MIGRATION_COMMANDS.sh"
log "${GREEN}✅ Migration commands generated${NC}"

# Cleanup temp files
rm -f /tmp/engines_to_migrate.txt /tmp/exchanges_to_migrate.txt /tmp/components_to_migrate.txt /tmp/loose_files.txt

# Final summary
echo ""
log "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
log "${GREEN}✅ FORTRESS STRUCTURE CREATED${NC}"
log "${GREEN}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
log "${CYAN}📦 What was created:${NC}"
log "   • Complete domain-driven directory structure"
log "   • Base classes (BaseEngine, BaseExchange)"
log "   • Example implementations (SpotEngine, ArbitrageEngine)"
log "   • Type definitions and shared interfaces"
log "   • Migration guide and commands"
echo ""
log "${YELLOW}📋 Next steps:${NC}"
log "   1. Review MIGRATION_GUIDE.md"
log "   2. Check MIGRATION_COMMANDS.sh for suggested file moves"
log "   3. Migrate your existing files systematically"
log "   4. Update imports to use @/lib/... paths"
log "   5. Run type-check and fix any errors"
log "   6. Test thoroughly before committing"
echo ""
log "${CYAN}📄 Files created:${NC}"
log "   • lib/trading/engines/base/BaseEngine.ts"
log "   • lib/trading/engines/base/EngineTypes.ts"
log "   • lib/trading/engines/spot/SpotEngine.ts"
log "   • lib/trading/engines/arbitrage/ArbitrageEngine.ts"
log "   • lib/trading/exchanges/BaseExchange.ts"
log "   • types/trading.ts"
log "   • types/portfolio.ts"
log "   • lib/README.md"
log "   • MIGRATION_GUIDE.md"
log "   • MIGRATION_COMMANDS.sh"
echo ""
log "${PURPLE}💾 Backup location: $BACKUP_DIR${NC}"
log "${PURPLE}📄 Full log: $LOG_FILE${NC}"
echo ""
log "${GREEN}🏴 Fortress foundation is ready. Time to migrate your empire!${NC}"
echo ""


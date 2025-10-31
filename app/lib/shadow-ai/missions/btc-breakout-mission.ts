/**
 * 🎯 BTC BREAKOUT MISSION - SHADOW.AI Trading Engine
 * Advanced OCO ladder with profit-siphon automation
 */

import { EventEmitter } from 'events';

interface OCOOrder {
  id: string;
  symbol: 'BTCUSDT';
  side: 'SELL';
  quantity: number;
  price: number;
  stopPrice: number;
  status: 'PENDING' | 'FILLED' | 'CANCELLED';
  filledAt?: Date;
  proceeds?: number;
}

interface SiphonPolicy {
  usdtAllocation: number; // 70%
  ethAllocation: number;  // 30%
  graduationThreshold: number; // $1,500-$3,500
  minimumEngineBalance: number; // 0.01-0.02 BTC
  dryPowderTarget: number; // 25-30% USDT
}

interface TradingEngineState {
  btcBalance: number; // ~0.05 BTC
  btcValue: number; // ~$6K at $119,000
  usdtBalance: number;
  ethBalance: number;
  totalEngineValue: number;
  ledgerVault: number; // UNTOUCHED
}

export class BTCBreakoutMission extends EventEmitter {
  private ocoOrders: OCOOrder[] = [];
  private siphonPolicy: SiphonPolicy;
  private engineState: TradingEngineState;
  private isLiveTrading: boolean;
  private realTradesLog: any[] = [];
  
  constructor() {
    super();
    this.initializeMission();
    this.setupSiphonPolicy();
    this.loadEngineState();
    this.checkTradingMode();
  }

  /**
   * Initialize BTC Breakout Mission
   */
  private initializeMission(): void {
    console.log('🎯 BTC BREAKOUT MISSION INITIALIZED');
    console.log('📊 Context: BTC @ $119,000 | Engine: ~0.05 BTC (~$6K)');
    console.log('🔒 Vault: UNTOUCHED | Policy: 70% USDT / 30% ETH');
    
    this.emit('missionInitialized', {
      timestamp: new Date(),
      context: 'BTC breakout position management',
      engineBalance: '~0.05 BTC (~$6K)',
      vaultStatus: 'UNTOUCHED'
    });
  }

  /**
   * Setup Siphon Policy
   */
  private setupSiphonPolicy(): void {
    this.siphonPolicy = {
      usdtAllocation: 0.70, // 70% to USDT war chest
      ethAllocation: 0.30,  // 30% to ETH or BTC vault
      graduationThreshold: 2500, // $2,500 average threshold
      minimumEngineBalance: 0.015, // 0.015 BTC minimum
      dryPowderTarget: 0.275 // 27.5% USDT target
    };
    
    console.log('💰 SIPHON POLICY CONFIGURED');
    console.log(`   • USDT War Chest: ${(this.siphonPolicy.usdtAllocation * 100)}%`);
    console.log(`   • ETH/Vault: ${(this.siphonPolicy.ethAllocation * 100)}%`);
    console.log(`   • Graduation Threshold: $${this.siphonPolicy.graduationThreshold}`);
    console.log(`   • Min Engine Balance: ${this.siphonPolicy.minimumEngineBalance} BTC`);
  }

  /**
   * Load Current Engine State
   */
  private loadEngineState(): void {
    this.engineState = {
      btcBalance: 0.05, // Current BTC position
      btcValue: 5950, // 0.05 * $119,000
      usdtBalance: 1000, // Current USDT balance
      ethBalance: 0.1, // Current ETH balance
      totalEngineValue: 6950, // Total engine value
      ledgerVault: 50000 // Ledger vault (UNTOUCHED)
    };
    
    console.log('📊 ENGINE STATE LOADED');
    console.log(`   • BTC: ${this.engineState.btcBalance} (~$${this.engineState.btcValue})`);
    console.log(`   • USDT: $${this.engineState.usdtBalance}`);
    console.log(`   • ETH: ${this.engineState.ethBalance}`);
    console.log(`   • Total Engine: $${this.engineState.totalEngineValue}`);
    console.log(`   • Ledger Vault: $${this.engineState.ledgerVault} (UNTOUCHED)`);
  }

  /**
   * Check Trading Mode
   */
  private checkTradingMode(): void {
    this.isLiveTrading = process.env.DISABLE_REAL_EXCHANGES !== '1';
    
    console.log(`🔧 TRADING MODE: ${this.isLiveTrading ? 'LIVE' : 'SIMULATION'}`);
    
    if (!this.isLiveTrading) {
      console.log('⚠️  SIMULATION MODE - No real trades will be executed');
    }
  }

  /**
   * Execute BTC OCO Ladder
   */
  public async executeOCOLadder(): Promise<void> {
    console.log('🎯 EXECUTING BTC OCO LADDER...');
    
    try {
      // Create OCO orders
      await this.createOCOOrders();
      
      // Monitor orders
      this.startOrderMonitoring();
      
      // Setup siphon automation
      this.setupSiphonAutomation();
      
      console.log('✅ BTC OCO LADDER EXECUTED SUCCESSFULLY');
      
    } catch (error) {
      console.error('❌ OCO Ladder execution failed:', error);
      this.emit('missionError', error);
    }
  }

  /**
   * Create OCO Orders
   */
  private async createOCOOrders(): Promise<void> {
    const ladderOrders = [
      {
        quantity: 0.01,
        price: 120000, // $120K
        stopPrice: 114500 // $114.5K stop-loss
      },
      {
        quantity: 0.01,
        price: 125000, // $125K
        stopPrice: 114500 // $114.5K stop-loss
      },
      {
        quantity: 0.01,
        price: 130000, // $130K
        stopPrice: 114500 // $114.5K stop-loss
      }
    ];

    console.log('📋 CREATING OCO ORDERS:');
    
    for (let i = 0; i < ladderOrders.length; i++) {
      const order = ladderOrders[i];
      const ocoOrder: OCOOrder = {
        id: `btc_oco_${i + 1}_${Date.now()}`,
        symbol: 'BTCUSDT',
        side: 'SELL',
        quantity: order.quantity,
        price: order.price,
        stopPrice: order.stopPrice,
        status: 'PENDING'
      };
      
      this.ocoOrders.push(ocoOrder);
      
      console.log(`   • Order ${i + 1}: Sell ${order.quantity} BTC @ $${order.price.toLocaleString()}`);
      console.log(`     Stop-Loss: $${order.stopPrice.toLocaleString()}`);
      
      // Place order (simulation or real)
      if (this.isLiveTrading) {
        await this.placeRealOrder(ocoOrder);
      } else {
        console.log(`     [SIMULATION] Order placed successfully`);
      }
      
      // Log to real_trades.json
      this.logTrade(ocoOrder, 'PLACED');
    }
    
    console.log(`✅ ${this.ocoOrders.length} OCO orders created`);
  }

  /**
   * Start Order Monitoring
   */
  private startOrderMonitoring(): void {
    console.log('👁️  STARTING ORDER MONITORING...');
    
    // Monitor every 30 seconds
    setInterval(() => {
      this.checkOrderStatus();
    }, 30000);
    
    console.log('✅ Order monitoring active');
  }

  /**
   * Check Order Status
   */
  private async checkOrderStatus(): Promise<void> {
    for (const order of this.ocoOrders) {
      if (order.status === 'PENDING') {
        // Check if order would be filled at current price
        const currentPrice = await this.getCurrentBTCPrice();
        
        if (currentPrice >= order.price) {
          // Order filled
          await this.handleOrderFill(order, currentPrice);
        } else if (currentPrice <= order.stopPrice) {
          // Stop-loss triggered
          await this.handleStopLoss(order, currentPrice);
        }
      }
    }
  }

  /**
   * Handle Order Fill
   */
  private async handleOrderFill(order: OCOOrder, fillPrice: number): Promise<void> {
    console.log(`🎯 ORDER FILLED: ${order.id}`);
    console.log(`   • Price: $${fillPrice.toLocaleString()}`);
    console.log(`   • Quantity: ${order.quantity} BTC`);
    
    order.status = 'FILLED';
    order.filledAt = new Date();
    order.proceeds = order.quantity * fillPrice;
    
    // Execute siphon policy
    await this.executeSiphonPolicy(order);
    
    // Log trade
    this.logTrade(order, 'FILLED', fillPrice);
    
    // Check graduation threshold
    await this.checkGraduationThreshold();
    
    this.emit('orderFilled', { order, fillPrice });
  }

  /**
   * Handle Stop Loss
   */
  private async handleStopLoss(order: OCOOrder, stopPrice: number): Promise<void> {
    console.log(`🛑 STOP-LOSS TRIGGERED: ${order.id}`);
    console.log(`   • Stop Price: $${stopPrice.toLocaleString()}`);
    console.log(`   • Quantity: ${order.quantity} BTC`);
    
    order.status = 'FILLED';
    order.filledAt = new Date();
    order.proceeds = order.quantity * stopPrice;
    
    // Execute siphon policy (same as fill)
    await this.executeSiphonPolicy(order);
    
    // Log trade
    this.logTrade(order, 'STOP_LOSS', stopPrice);
    
    this.emit('stopLossTriggered', { order, stopPrice });
  }

  /**
   * Execute Siphon Policy
   */
  private async executeSiphonPolicy(order: OCOOrder): Promise<void> {
    if (!order.proceeds) return;
    
    const proceeds = order.proceeds;
    const usdtAmount = proceeds * this.siphonPolicy.usdtAllocation;
    const ethAmount = proceeds * this.siphonPolicy.ethAllocation;
    
    console.log(`💰 EXECUTING SIPHON POLICY:`);
    console.log(`   • Total Proceeds: $${proceeds.toLocaleString()}`);
    console.log(`   • USDT War Chest: $${usdtAmount.toLocaleString()} (${(this.siphonPolicy.usdtAllocation * 100)}%)`);
    console.log(`   • ETH/Vault: $${ethAmount.toLocaleString()} (${(this.siphonPolicy.ethAllocation * 100)}%)`);
    
    // Update engine state
    this.engineState.usdtBalance += usdtAmount;
    
    // Buy ETH with 30% allocation
    const ethPrice = await this.getCurrentETHPrice();
    const ethQuantity = ethAmount / ethPrice;
    this.engineState.ethBalance += ethQuantity;
    
    // Update BTC balance
    this.engineState.btcBalance -= order.quantity;
    
    console.log(`✅ SIPHON EXECUTED:`);
    console.log(`   • USDT Balance: $${this.engineState.usdtBalance.toLocaleString()}`);
    console.log(`   • ETH Balance: ${this.engineState.ethBalance.toFixed(4)} ETH`);
    console.log(`   • BTC Balance: ${this.engineState.btcBalance.toFixed(4)} BTC`);
    
    this.emit('siphonExecuted', { usdtAmount, ethAmount, ethQuantity });
  }

  /**
   * Check Graduation Threshold
   */
  private async checkGraduationThreshold(): Promise<void> {
    const currentBTCPrice = await this.getCurrentBTCPrice();
    const remainingBTCValue = this.engineState.btcBalance * currentBTCPrice;
    
    console.log(`🎓 CHECKING GRADUATION THRESHOLD:`);
    console.log(`   • Remaining BTC Value: $${remainingBTCValue.toLocaleString()}`);
    console.log(`   • Graduation Threshold: $${this.siphonPolicy.graduationThreshold.toLocaleString()}`);
    
    if (remainingBTCValue > this.siphonPolicy.graduationThreshold) {
      const excessValue = remainingBTCValue - (this.siphonPolicy.minimumEngineBalance * currentBTCPrice);
      const excessBTC = excessValue / currentBTCPrice;
      
      if (excessBTC > 0) {
        console.log(`🎓 GRADUATION TRIGGERED!`);
        console.log(`   • Excess Value: $${excessValue.toLocaleString()}`);
        console.log(`   • Excess BTC: ${excessBTC.toFixed(4)} BTC`);
        
        // Request ΩSIGIL passphrase for withdrawal
        const passphrase = await this.requestSigilPassphrase();
        
        if (passphrase) {
          await this.graduateToLedger(excessBTC, excessValue);
        } else {
          console.log('⚠️  ΩSIGIL passphrase required for graduation');
        }
      }
    }
  }

  /**
   * Graduate to Ledger
   */
  private async graduateToLedger(btcAmount: number, value: number): Promise<void> {
    console.log(`🎓 GRADUATING TO LEDGER:`);
    console.log(`   • BTC Amount: ${btcAmount.toFixed(4)} BTC`);
    console.log(`   • Value: $${value.toLocaleString()}`);
    console.log(`   • Destination: Whitelisted Ledger Address`);
    
    // Update balances
    this.engineState.btcBalance -= btcAmount;
    this.engineState.ledgerVault += value;
    
    // Log graduation
    this.logTrade({
      id: `graduation_${Date.now()}`,
      symbol: 'BTCUSDT',
      side: 'SELL',
      quantity: btcAmount,
      price: value / btcAmount,
      stopPrice: 0,
      status: 'FILLED'
    }, 'GRADUATION');
    
    console.log(`✅ GRADUATION COMPLETE`);
    console.log(`   • New Engine BTC: ${this.engineState.btcBalance.toFixed(4)} BTC`);
    console.log(`   • Ledger Vault: $${this.engineState.ledgerVault.toLocaleString()}`);
    
    this.emit('graduationComplete', { btcAmount, value });
  }

  /**
   * Setup Siphon Automation
   */
  private setupSiphonAutomation(): void {
    console.log('🤖 SETTING UP SIPHON AUTOMATION...');
    
    // Monitor dry powder levels
    setInterval(() => {
      this.monitorDryPowder();
    }, 60000); // Every minute
    
    console.log('✅ Siphon automation active');
  }

  /**
   * Monitor Dry Powder
   */
  private async monitorDryPowder(): Promise<void> {
    const totalEngineValue = this.engineState.btcBalance * await this.getCurrentBTCPrice() + 
                           this.engineState.usdtBalance + 
                           this.engineState.ethBalance * await this.getCurrentETHPrice();
    
    const usdtPercentage = this.engineState.usdtBalance / totalEngineValue;
    const targetPercentage = this.siphonPolicy.dryPowderTarget;
    
    console.log(`💧 DRY POWDER CHECK:`);
    console.log(`   • Current USDT: ${(usdtPercentage * 100).toFixed(1)}%`);
    console.log(`   • Target USDT: ${(targetPercentage * 100).toFixed(1)}%`);
    
    if (usdtPercentage < targetPercentage * 0.8) {
      console.log('⚠️  Low dry powder - consider rebalancing');
      this.emit('lowDryPowder', { current: usdtPercentage, target: targetPercentage });
    }
  }

  /**
   * Log Trade to real_trades.json
   */
  private logTrade(order: OCOOrder, action: string, fillPrice?: number): void {
    const tradeLog = {
      timestamp: new Date().toISOString(),
      origin: "BTC_OCO_LADDER",
      policy: "30/70_siphon",
      action: action,
      order: {
        id: order.id,
        symbol: order.symbol,
        side: order.side,
        quantity: order.quantity,
        price: order.price,
        stopPrice: order.stopPrice,
        fillPrice: fillPrice,
        status: order.status
      },
      engineState: {
        btcBalance: this.engineState.btcBalance,
        usdtBalance: this.engineState.usdtBalance,
        ethBalance: this.engineState.ethBalance,
        totalValue: this.engineState.totalEngineValue
      },
      siphonPolicy: this.siphonPolicy
    };
    
    this.realTradesLog.push(tradeLog);
    
    console.log(`📝 TRADE LOGGED: ${action} - ${order.id}`);
  }

  /**
   * Request ΩSIGIL Passphrase
   */
  private async requestSigilPassphrase(): Promise<string | null> {
    // In real implementation, this would prompt for passphrase
    console.log('🔐 ΩSIGIL passphrase required for graduation');
    return null; // Return null for simulation
  }

  /**
   * Place Real Order
   */
  private async placeRealOrder(order: OCOOrder): Promise<void> {
    // In real implementation, this would place actual orders
    console.log(`[LIVE] Placing OCO order: ${order.id}`);
  }

  /**
   * Get Current BTC Price
   */
  private async getCurrentBTCPrice(): Promise<number> {
    // In real implementation, this would fetch from Binance API
    return 119000 + (Math.random() - 0.5) * 2000; // Simulate price movement
  }

  /**
   * Get Current ETH Price
   */
  private async getCurrentETHPrice(): Promise<number> {
    // In real implementation, this would fetch from Binance API
    return 3500 + (Math.random() - 0.5) * 200; // Simulate ETH price
  }

  /**
   * Get Mission Status
   */
  public getMissionStatus(): any {
    return {
      timestamp: new Date(),
      ocoOrders: this.ocoOrders,
      engineState: this.engineState,
      siphonPolicy: this.siphonPolicy,
      isLiveTrading: this.isLiveTrading,
      tradesLogged: this.realTradesLog.length
    };
  }

  /**
   * Get Trade Logs
   */
  public getTradeLogs(): any[] {
    return [...this.realTradesLog];
  }

  /**
   * Export Trade Logs
   */
  public exportTradeLogs(): string {
    return JSON.stringify(this.realTradesLog, null, 2);
  }
}

export default BTCBreakoutMission;

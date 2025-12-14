# SS_III Advanced Trading Modules - Implementation Specifications

## Overview
These modules ENHANCE the existing system. DO NOT replace or modify existing files.
All modules should integrate with existing patterns from:
- `core/agents/base_agent.py` - Base class pattern
- `core/trading/tactical_risk_gate.py` - Risk validation pattern
- `core/risk/omega_enhanced_risk_manager.py` - Correlation risk pattern

---

## Module 1: Advanced Risk Module
**File:** `core/risk/advanced_risk_module.py`

### Purpose
Adds ATR-based position sizing, Kelly criterion, portfolio heat tracking, and circuit breakers.
Works ALONGSIDE `omega_enhanced_risk_manager.py` (sector correlation) and `tactical_risk_gate.py` (trade validation).

### Key Classes
```python
class AdvancedRiskManager:
    """
    Volatility-aware position sizing and portfolio heat management.

    Integration points:
    - Called by TacticalRiskGate before trade approval
    - Can be used standalone by any trading agent
    """

    def __init__(self, config_path: str = None):
        self.portfolio_equity = 0.0
        self.open_positions = {}  # {symbol: {'size': float, 'risk_amount': float}}
        self.trade_history = []   # For Kelly calculation
        self.consecutive_losses = 0
        self.circuit_breaker_active = False
        self.circuit_breaker_until = None

    def calculate_atr_position_size(
        self,
        symbol: str,
        equity: float,
        risk_pct: float,  # e.g., 0.02 for 2%
        atr_value: float,
        entry_price: float,
        atr_multiplier: float = 2.0
    ) -> dict:
        """
        Calculate position size based on ATR volatility.

        Returns: {
            'position_size': float,  # In units
            'position_value': float, # In USD
            'stop_loss': float,      # Price level
            'risk_amount': float     # USD at risk
        }
        """

    def get_kelly_fraction(
        self,
        win_rate: float = None,
        avg_win: float = None,
        avg_loss: float = None,
        atr_percentile: float = None  # 0-1, current ATR vs historical
    ) -> float:
        """
        Calculate modified Kelly fraction with volatility adjustment.

        Adjustments:
        - ATR > 75th percentile: 0.25 * base_kelly
        - ATR > 50th percentile: 0.50 * base_kelly
        - ATR <= 50th percentile: 0.75 * base_kelly
        - NEVER full Kelly

        Returns: Kelly fraction (0.0 to 0.75)
        """

    def check_portfolio_heat(self) -> dict:
        """
        Enforce 2%/6% portfolio heat rules (Alexander Elder).

        Returns: {
            'total_heat': float,      # Sum of all position risks
            'heat_pct': float,        # As percentage of equity
            'can_open_new': bool,     # True if < 6%
            'max_new_risk': float,    # Max USD risk for new trade
            'positions_at_risk': int  # Number of open positions
        }
        """

    def check_circuit_breaker(self, was_loss: bool = None) -> dict:
        """
        Consecutive loss circuit breaker.

        Rules:
        - 3 losses: risk_pct *= 0.5
        - 5 losses: pause trading 24 hours

        Returns: {
            'consecutive_losses': int,
            'risk_multiplier': float,
            'trading_paused': bool,
            'resume_at': datetime or None
        }
        """

    def record_trade_result(self, pnl: float):
        """Update trade history and circuit breaker state."""

    def get_optimal_position(
        self,
        symbol: str,
        entry_price: float,
        atr_value: float,
        regime: str = 'NEUTRAL'  # From HMM regime detector
    ) -> dict:
        """
        Master function combining all risk factors.

        Returns position size accounting for:
        - ATR-based sizing
        - Kelly fraction
        - Portfolio heat limits
        - Circuit breaker state
        - Regime adjustment
        """
```

### Integration Example
```python
# In trading_agent.py or tactical_risk_gate.py
from core.risk.advanced_risk_module import AdvancedRiskManager

risk_mgr = AdvancedRiskManager()
risk_mgr.portfolio_equity = 5000.0

# Before opening a trade
heat_check = risk_mgr.check_portfolio_heat()
if not heat_check['can_open_new']:
    print(f"Cannot open: heat at {heat_check['heat_pct']:.1f}%")
    return

breaker = risk_mgr.check_circuit_breaker()
if breaker['trading_paused']:
    print(f"Trading paused until {breaker['resume_at']}")
    return

position = risk_mgr.get_optimal_position(
    symbol='BTC',
    entry_price=100000,
    atr_value=2500,
    regime='LOW_VOL_BULLISH'
)
```

---

## Module 2: Market Filters
**File:** `core/filters/market_filters.py`

### Purpose
Fear & Greed index and DXY correlation filters as macro overlays.

### Key Classes
```python
class MarketFilters:
    """
    Macro market filters using Fear & Greed and DXY correlation.

    Usage: Call before considering any trade to get macro bias.
    """

    def __init__(self, cache_minutes: int = 60):
        self.fng_cache = {'value': None, 'timestamp': None}
        self.dxy_cache = {'value': None, 'timestamp': None}
        self.cache_minutes = cache_minutes

    def get_fear_greed(self, force_refresh: bool = False) -> dict:
        """
        Get Fear & Greed Index from alternative.me API.

        Returns: {
            'value': int,           # 0-100
            'classification': str,  # 'Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'
            'signal': str,          # 'BULLISH', 'BEARISH', 'NEUTRAL'
            'timestamp': datetime
        }

        Trading rules:
        - < 25: Extreme Fear = BULLISH (buy opportunity)
        - 25-45: Fear = SLIGHTLY_BULLISH
        - 45-55: Neutral = NEUTRAL
        - 55-75: Greed = SLIGHTLY_BEARISH
        - > 75: Extreme Greed = BEARISH (potential correction)
        """

    def get_dxy_signal(self, lookback_days: int = 5) -> dict:
        """
        Get DXY (US Dollar Index) trend signal.
        Uses yfinance for DXY data.

        Returns: {
            'current': float,
            'change_pct': float,   # % change over lookback
            'trend': str,          # 'UP', 'DOWN', 'FLAT'
            'btc_signal': str,     # 'BEARISH' if DXY up, 'BULLISH' if down
            'correlation': float   # Historical BTC-DXY correlation
        }

        Trading rules:
        - Rising DXY = Bitcoin weakness (BEARISH for crypto)
        - Falling DXY = Bitcoin strength (BULLISH for crypto)
        """

    def get_combined_filter(self) -> dict:
        """
        Combine Fear & Greed and DXY into single signal.

        Returns: {
            'fear_greed': {...},
            'dxy': {...},
            'combined_signal': str,  # 'STRONG_BULLISH', 'BULLISH', 'NEUTRAL', 'BEARISH', 'STRONG_BEARISH'
            'confidence': float,     # 0-1
            'should_trade': bool,    # False if conflicting signals
            'recommended_size_mult': float  # 0.5-1.5 multiplier
        }
        """
```

---

## Module 3: HMM Regime Detector
**File:** `core/regime/hmm_regime_detector.py`

### Purpose
Hidden Markov Model for market regime classification. 40-50% drawdown reduction.

### Key Classes
```python
class HMMRegimeDetector:
    """
    Gaussian HMM for market regime detection.

    Regimes:
    0: LOW_VOL - Low volatility (normal trading)
    1: HIGH_VOL - High volatility (reduce size 50%)
    2: TRANSITION - Regime changing (pause trading)
    """

    def __init__(self, n_regimes: int = 3, retrain_days: int = 90):
        self.model = None
        self.n_regimes = n_regimes
        self.retrain_days = retrain_days
        self.last_train_date = None
        self.regime_names = {
            0: 'LOW_VOL',
            1: 'HIGH_VOL',
            2: 'TRANSITION'
        }

    def prepare_features(self, ohlcv_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features for HMM.

        Features:
        - Log returns
        - Daily range: (high - low) / close
        - Rolling volatility (20-period std of returns)
        """

    def fit(self, ohlcv_df: pd.DataFrame):
        """
        Train HMM on historical data.

        Uses: hmmlearn.hmm.GaussianHMM
        - n_components=3
        - covariance_type="full"
        - n_iter=100
        """

    def predict_regime(self, ohlcv_df: pd.DataFrame) -> dict:
        """
        Predict current market regime.

        Returns: {
            'regime': int,          # 0, 1, or 2
            'regime_name': str,     # 'LOW_VOL', 'HIGH_VOL', 'TRANSITION'
            'probabilities': list,  # [p0, p1, p2]
            'confidence': float,    # Max probability
            'position_multiplier': float,  # 1.0 for LOW_VOL, 0.5 for HIGH_VOL, 0 for TRANSITION
            'allow_longs': bool,
            'allow_shorts': bool
        }
        """

    def get_trading_rules(self, regime: int) -> dict:
        """
        Get trading rules for current regime.

        Returns: {
            'position_size_mult': float,
            'allow_new_trades': bool,
            'tighten_stops': bool,
            'reduce_targets': bool
        }
        """

    def should_retrain(self) -> bool:
        """Check if model needs retraining (walk-forward)."""
```

---

## Module 4: Reflect Agent
**File:** `core/agents/reflect_agent.py`

### Purpose
Natural language self-critique of trading decisions. 31% improvement without model retraining.

### Key Classes
```python
class ReflectAgent:
    """
    Provides verbal feedback on proposed trades.
    Acts as a "second opinion" before execution.
    """

    def __init__(self, use_claude: bool = True):
        self.client = None  # Anthropic or OpenAI client
        self.critique_history = []

    def analyze_trade(
        self,
        proposed_trade: dict,  # {symbol, side, size, entry, stop, target}
        market_context: dict,  # {regime, fear_greed, dxy, recent_price_action}
        recent_trades: list    # Last 10 trades with outcomes
    ) -> dict:
        """
        Generate critique of proposed trade.

        Returns: {
            'decision': str,        # 'APPROVE', 'REJECT', 'MODIFY'
            'reasoning': str,       # Natural language explanation
            'risk_score': float,    # 0-10
            'emotional_flags': list,# ['FOMO', 'REVENGE', 'OVERCONFIDENCE']
            'modifications': dict,  # If MODIFY: suggested changes
            'confidence': float
        }
        """

    def get_critique_prompt(self, trade, context, history) -> str:
        """Build prompt for LLM critique."""

    def get_weekly_summary(self) -> dict:
        """
        Aggregate weekly critiques for pattern identification.

        Returns: {
            'total_critiques': int,
            'approved': int,
            'rejected': int,
            'modified': int,
            'common_rejection_reasons': list,
            'emotional_flags_count': dict,
            'recommendations': list
        }
        """
```

---

## Module 5: FreqAI Scaffold
**File:** `core/ml/freqai_scaffold.py`

### Purpose
Self-adaptive ML framework with continuous retraining.

### Key Classes
```python
class AdaptiveMLEngine:
    """
    FreqAI-inspired self-adaptive ML for trading signals.
    Models should be < 4 hours old for optimal performance.
    """

    def __init__(self, retrain_hours: float = 4.0, model_type: str = 'lightgbm'):
        self.model = None
        self.last_train_time = None
        self.retrain_hours = retrain_hours
        self.feature_pipeline = None
        self.model_type = model_type  # 'lightgbm', 'xgboost', 'catboost'

    def build_features(self, ohlcv_df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate 100+ features from OHLCV.

        Features:
        - Price-based: returns, log returns, momentum
        - Volatility: ATR, Bollinger width, range
        - Volume: VWAP, OBV, volume momentum
        - Indicators: RSI, MACD, Stoch, ADX, etc.
        """

    def should_retrain(self) -> bool:
        """Check if model is stale (> retrain_hours old)."""

    def train(self, features: pd.DataFrame, targets: pd.Series):
        """Train model and update timestamp."""

    def predict(self, features: pd.DataFrame) -> dict:
        """
        Make prediction, retraining if needed.

        Returns: {
            'signal': str,        # 'BUY', 'SELL', 'HOLD'
            'probability': float, # 0-1
            'feature_importance': dict,
            'model_age_hours': float
        }
        """
```

---

## Module 6: Order Book RL Scaffold
**File:** `core/ml/orderbook_rl_scaffold.py`

### Purpose
Order book feature extraction for future deep RL development.

### Key Classes
```python
class OrderBookCollector:
    """Collect and process order book snapshots."""

    def __init__(self, exchange: ccxt.Exchange):
        self.exchange = exchange

    def get_orderbook_features(self, symbol: str, depth: int = 20) -> dict:
        """
        Extract features from order book.

        Returns: {
            'spread': float,
            'spread_bps': float,
            'imbalance': float,  # (bid_vol - ask_vol) / (bid_vol + ask_vol)
            'bid_depth': list,   # Volume at each level
            'ask_depth': list,
            'vwmp': float,       # Volume-weighted mid price
            'pressure': str      # 'BUY', 'SELL', 'NEUTRAL'
        }
        """


class OrderBookEnv:
    """
    Gym-compatible environment for RL (scaffold).
    """

    def __init__(self):
        self.action_space = ['BUY', 'SELL', 'HOLD']

    def step(self, action) -> tuple:
        """Take action, return (state, reward, done, info)."""

    def reset(self):
        """Reset environment."""
```

---

## Module 7: On-Chain Signals
**File:** `core/signals/onchain_signals.py`

### Purpose
Exchange flow monitoring and enhanced whale tracking.
COMPLEMENTS existing `whale_agent.py`.

### Key Classes
```python
class OnChainSignals:
    """
    On-chain data signals for trading.
    Complements whale_agent.py with additional metrics.
    """

    def __init__(self):
        self.flow_cache = {}

    def get_exchange_flows(self, asset: str = 'BTC') -> dict:
        """
        Get exchange inflow/outflow data.

        Data sources (free tiers):
        - CoinGlass API
        - CryptoQuant (limited free)

        Returns: {
            'net_flow_24h': float,
            'inflow_24h': float,
            'outflow_24h': float,
            'flow_signal': str,    # 'ACCUMULATION', 'DISTRIBUTION', 'NEUTRAL'
            'signal_strength': float
        }

        Rules:
        - High inflows = selling pressure expected (BEARISH)
        - High outflows = accumulation (BULLISH)
        """

    def get_whale_movements(self, min_usd: float = 1000000) -> list:
        """
        Get recent whale movements.

        Returns list of: {
            'tx_hash': str,
            'amount_usd': float,
            'direction': str,  # 'TO_EXCHANGE', 'FROM_EXCHANGE', 'WALLET_TO_WALLET'
            'timestamp': datetime
        }
        """

    def get_onchain_score(self, asset: str = 'BTC') -> dict:
        """
        Combined on-chain score.

        Returns: {
            'exchange_flows': {...},
            'whale_activity': {...},
            'combined_score': float,  # -100 to 100
            'signal': str,            # 'BULLISH', 'BEARISH', 'NEUTRAL'
            'confidence': float
        }
        """
```

---

## Integration Architecture

All modules integrate via a central orchestrator:

```python
# core/orchestrator.py (to be created)

class TradingOrchestrator:
    """
    Orchestrates all trading modules.
    Single entry point for trade decisions.
    """

    def __init__(self):
        # Risk modules
        self.omega_risk = OmegaEnhancedRiskManager()
        self.advanced_risk = AdvancedRiskManager()
        self.tactical_gate = TacticalRiskGate()

        # Filters
        self.market_filters = MarketFilters()
        self.regime_detector = HMMRegimeDetector()

        # Agents
        self.reflect_agent = ReflectAgent()

        # ML (optional)
        self.ml_engine = AdaptiveMLEngine()

        # Signals
        self.onchain = OnChainSignals()

    def evaluate_trade(self, proposed_trade: dict) -> dict:
        """
        Full evaluation pipeline:
        1. Check regime (HMM)
        2. Check macro filters (F&G, DXY)
        3. Check on-chain signals
        4. Calculate position size (ATR, Kelly, heat)
        5. Validate via tactical gate
        6. Get reflect agent critique
        7. Return final decision
        """
```

---

## Dependencies

Add to requirements.txt:
```
hmmlearn>=0.3.0
lightgbm>=4.0.0
yfinance>=0.2.0
```

Optional:
```
xgboost>=2.0.0
catboost>=1.2.0
```

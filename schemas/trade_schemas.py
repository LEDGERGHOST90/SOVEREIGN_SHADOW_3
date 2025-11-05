#!/usr/bin/env python3
"""
🏴 Sovereign Shadow II - Trade Schemas
Pydantic models for standardized JSON I/O across all systems
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Any
from enum import Enum


class TradeDirection(str, Enum):
    """Trade direction"""
    LONG = "long"
    SHORT = "short"


class EmotionType(str, Enum):
    """Emotion states for psychology tracking"""
    CONFIDENT = "confident"
    NEUTRAL = "neutral"
    ANXIOUS = "anxious"
    FEARFUL = "fearful"
    GREEDY = "greedy"
    REVENGE = "revenge"
    FOMO = "fomo"
    SATISFIED = "satisfied"
    FRUSTRATED = "frustrated"
    REGRET = "regret"


class TradeStatus(str, Enum):
    """Trade outcome status"""
    TARGET_HIT = "target_hit"
    STOPPED = "stopped"
    MANUALLY_CLOSED = "manually_closed"
    BREAKEVEN = "breakeven"


class MistakeType(str, Enum):
    """Common trading mistakes"""
    NO_STOP_LOSS = "no_stop_loss"
    MOVED_STOP = "moved_stop"
    OVERLEVERAGED = "overleveraged"
    FOUGHT_TREND = "fought_trend"
    NO_SETUP = "no_setup"
    EMOTIONAL_ENTRY = "emotional_entry"
    EARLY_EXIT = "early_exit"
    LATE_EXIT = "late_exit"


# ============================================================================
# MARKET CONTEXT SCHEMAS
# ============================================================================

class IndicatorData(BaseModel):
    """Technical indicator readings"""
    ema_21: Optional[str] = Field(None, description="EMA 21 position (above/below)")
    ema_50: Optional[str] = Field(None, description="EMA 50 position (above/below)")
    ema_200: Optional[str] = Field(None, description="EMA 200 position (above/below)")
    rsi: Optional[float] = Field(None, ge=0, le=100, description="RSI value (0-100)")
    volume: Optional[str] = Field(None, description="Volume status (increasing/decreasing)")

    @field_validator('rsi')
    @classmethod
    def validate_rsi(cls, v):
        if v is not None and not (0 <= v <= 100):
            raise ValueError('RSI must be between 0 and 100')
        return v


class MarketContext(BaseModel):
    """Market context for trade validation"""
    trend_4h: str = Field(..., description="4H trend (bullish/bearish/sideways)")
    setup_15m: Optional[str] = Field(None, description="15M setup type")
    key_level: Optional[float] = Field(None, description="Key support/resistance level")
    confluences: Optional[int] = Field(None, ge=0, description="Number of confluences")
    indicators: IndicatorData = Field(default_factory=IndicatorData)

    @field_validator('trend_4h')
    @classmethod
    def validate_trend(cls, v):
        if v not in ['bullish', 'bearish', 'sideways']:
            raise ValueError('trend_4h must be bullish, bearish, or sideways')
        return v


# ============================================================================
# TRADE VALIDATION SCHEMAS
# ============================================================================

class TradeValidationRequest(BaseModel):
    """Request to validate a trade setup"""
    symbol: str = Field(..., description="Trading pair (e.g., BTC/USDT)")
    trade_type: TradeDirection = Field(..., description="Trade direction (long/short)")
    entry_price: float = Field(..., gt=0, description="Planned entry price")
    stop_loss: float = Field(..., gt=0, description="Stop loss price")
    take_profit: float = Field(..., gt=0, description="Take profit price")
    emotion_state: EmotionType = Field(..., description="Current emotional state")
    emotion_intensity: int = Field(..., ge=1, le=10, description="Emotion intensity (1-10)")
    market_context: MarketContext = Field(..., description="Market analysis context")
    notes: Optional[str] = Field(None, description="Additional trade notes")

    @field_validator('stop_loss')
    @classmethod
    def validate_stop_loss(cls, v, info):
        if 'entry_price' in info.data and 'trade_type' in info.data:
            entry = info.data['entry_price']
            direction = info.data['trade_type']

            if direction == TradeDirection.LONG and v >= entry:
                raise ValueError('For LONG, stop_loss must be below entry_price')
            elif direction == TradeDirection.SHORT and v <= entry:
                raise ValueError('For SHORT, stop_loss must be above entry_price')
        return v


class PositionSizing(BaseModel):
    """Position sizing calculations"""
    position_size: float = Field(..., description="Position size in coins")
    position_value: float = Field(..., description="Position value in USD")
    risk_amount: float = Field(..., description="Dollar amount at risk")
    risk_percent: float = Field(..., description="Risk as % of account")
    risk_reward_ratio: float = Field(..., description="Risk:Reward ratio")


class ValidationChecks(BaseModel):
    """Individual validation check results"""
    timeframe_alignment: str
    risk_management: str
    stop_loss_present: str
    risk_reward_ratio: str
    position_exposure: str
    trend_confirmation: str


class TradeValidationResponse(BaseModel):
    """Response from trade validation"""
    approved: bool = Field(..., description="Whether trade is approved")
    trade_id: Optional[str] = Field(None, description="Unique trade ID if approved")
    reasons: List[str] = Field(default_factory=list, description="Approval/rejection reasons")
    warnings: List[str] = Field(default_factory=list, description="Warning messages")
    validation: Optional[Dict[str, Any]] = Field(None, description="Detailed validation results")
    position_sizing: Optional[PositionSizing] = Field(None, description="Position sizing details")
    psychology: Optional[Dict[str, Any]] = Field(None, description="Psychology check results")
    system: Optional[str] = Field(None, description="System that rejected (if rejected)")
    step_failed: Optional[int] = Field(None, description="Validation step that failed (1-3)")


# ============================================================================
# TRADE EXECUTION SCHEMAS
# ============================================================================

class TradeExecutionRequest(BaseModel):
    """Request to execute an approved trade"""
    trade_id: str = Field(..., description="Trade ID from validation")
    actual_entry: float = Field(..., gt=0, description="Actual execution price")
    exchange: Optional[str] = Field(None, description="Exchange where executed")
    order_id: Optional[str] = Field(None, description="Exchange order ID")


class TradeExecutionResponse(BaseModel):
    """Response from trade execution"""
    success: bool = Field(..., description="Whether execution succeeded")
    trade_id: str = Field(..., description="Trade ID")
    executed_at: str = Field(..., description="Execution timestamp")
    actual_entry: float = Field(..., description="Actual entry price")
    message: str = Field(..., description="Execution status message")


# ============================================================================
# TRADE CLOSE SCHEMAS
# ============================================================================

class TradeCloseRequest(BaseModel):
    """Request to close a trade"""
    trade_id: str = Field(..., description="Trade ID to close")
    exit_price: float = Field(..., gt=0, description="Exit price")
    emotion_after: EmotionType = Field(..., description="Emotion after trade")
    status: TradeStatus = Field(..., description="How trade ended")
    mistakes: Optional[List[MistakeType]] = Field(None, description="Mistakes made")
    lessons_learned: Optional[str] = Field(None, description="Lessons from trade")


class TradeCloseResponse(BaseModel):
    """Response from closing a trade"""
    trade_id: str = Field(..., description="Trade ID")
    profitable: bool = Field(..., description="Whether trade was profitable")
    profit_loss: float = Field(..., description="P&L in dollars")
    psychology: Dict[str, Any] = Field(..., description="Psychology state after close")
    lessons: Optional[str] = Field(None, description="Lessons learned")
    lockout_triggered: bool = Field(False, description="Whether 3-strike lockout triggered")


# ============================================================================
# SYSTEM STATUS SCHEMAS
# ============================================================================

class PsychologyState(BaseModel):
    """Current psychology/emotion state"""
    trading_allowed: bool
    trades_today: int
    losses_today: int
    strikes_remaining: int
    dominant_emotion: str
    warnings: List[str] = Field(default_factory=list)


class JournalStats(BaseModel):
    """Trading journal statistics"""
    total_trades: int
    win_rate: float
    total_pnl: float
    expectancy: float
    system_adherence: float


class MentorProgress(BaseModel):
    """Learning progress"""
    current_chapter: int
    current_lesson: int
    total_progress: str
    paper_trades: int
    win_rate: str
    next_lesson: str


class SystemStatus(BaseModel):
    """Complete system status"""
    account_balance: float
    psychology: PsychologyState
    journal_stats: Optional[JournalStats] = None
    mentor_progress: MentorProgress
    active_trades: int
    total_exposure: float


# ============================================================================
# EXCHANGE SCHEMAS
# ============================================================================

class ExchangeBalance(BaseModel):
    """Exchange balance information"""
    exchange: str
    total_usd: float
    balances: Dict[str, float] = Field(default_factory=dict)
    last_updated: str


class ExchangeOrder(BaseModel):
    """Exchange order details"""
    order_id: str
    exchange: str
    symbol: str
    side: str  # buy/sell
    order_type: str  # market/limit
    amount: float
    price: Optional[float] = None
    status: str
    timestamp: str


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def example_trade_validation_request() -> Dict:
    """Example trade validation request"""
    return {
        "symbol": "BTC/USDT",
        "trade_type": "long",
        "entry_price": 99000,
        "stop_loss": 97000,
        "take_profit": 103000,
        "emotion_state": "confident",
        "emotion_intensity": 5,
        "market_context": {
            "trend_4h": "bullish",
            "setup_15m": "pullback_bounce",
            "key_level": 98500,
            "confluences": 5,
            "indicators": {
                "ema_21": "above",
                "ema_50": "above",
                "ema_200": "above",
                "rsi": 55,
                "volume": "increasing"
            }
        },
        "notes": "Clean 5-confluence setup at support"
    }


def validate_json_input(data: Dict, schema_class: BaseModel) -> tuple[bool, Optional[BaseModel], Optional[str]]:
    """
    Validate JSON input against a Pydantic schema

    Returns:
        (valid, parsed_model, error_message)
    """
    try:
        model = schema_class(**data)
        return True, model, None
    except Exception as e:
        return False, None, str(e)


if __name__ == "__main__":
    # Test schema validation
    print("🧪 Testing Trade Schemas\n")
    print("="*70)

    # Test valid request
    example = example_trade_validation_request()
    valid, model, error = validate_json_input(example, TradeValidationRequest)

    if valid:
        print("✅ Valid trade validation request")
        print(f"\nParsed Model:")
        print(model.model_dump_json(indent=2))
    else:
        print(f"❌ Invalid request: {error}")

    print("\n" + "="*70)

    # Test invalid request (stop loss wrong direction)
    invalid_example = example.copy()
    invalid_example["stop_loss"] = 101000  # Above entry for LONG (wrong!)

    valid, model, error = validate_json_input(invalid_example, TradeValidationRequest)

    if not valid:
        print("✅ Correctly rejected invalid stop loss")
        print(f"Error: {error}")
    else:
        print("❌ Should have rejected invalid stop loss")

    print("\n" + "="*70)
    print("✅ Schema validation tests complete")

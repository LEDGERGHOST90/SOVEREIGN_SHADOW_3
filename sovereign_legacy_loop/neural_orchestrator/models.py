"""
🧠 Neural Orchestrator - Data Models
====================================

Pydantic models for the neural consciousness dashboard API.
These models match the data structure expected by the frontend website.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SystemStatus(str, Enum):
    """System status enumeration."""
    ACTIVE = "ACTIVE"
    STANDBY = "STANDBY"
    ALERT = "ALERT"
    OFFLINE = "OFFLINE"
    ERROR = "ERROR"


class TierType(str, Enum):
    """Tier type enumeration."""
    PRESERVATION = "PRESERVATION"
    FLIP_ENGINE = "FLIP_ENGINE"
    SHADOW_AI = "SHADOW_AI"


class MigrationStatusType(str, Enum):
    """Migration status enumeration."""
    COMPLETE = "Complete"
    IN_PROGRESS = "In Progress"
    PLANNED = "Planned"
    FAILED = "Failed"


# ============================================================================
# CONSCIOUSNESS VALUE MODELS
# ============================================================================

class ConsciousnessValue(BaseModel):
    """Total consciousness value for the main dashboard display."""
    total: float = Field(..., description="Total portfolio value in USD")
    change_24h: float = Field(..., description="24-hour change percentage")
    change_7d: float = Field(..., description="7-day change percentage")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TierAData(BaseModel):
    """Tier A (Preservation) data - Ledger Live + Coinbase."""
    value: float = Field(..., description="Total value in USD")
    allocation: float = Field(..., description="Allocation percentage")
    breakdown: Dict[str, float] = Field(..., description="Breakdown by source")
    description: str = Field(default="Parasympathetic Nervous System")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TierBData(BaseModel):
    """Tier B (Flip Engine) data - ONDO + USDT."""
    value: float = Field(..., description="Total value in USD")
    allocation: float = Field(..., description="Allocation percentage")
    breakdown: Dict[str, float] = Field(..., description="Breakdown by asset")
    unlock_date: Optional[str] = Field(None, description="Unlock date if locked")
    description: str = Field(default="Sympathetic Nervous System")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ShadowAIStatus(BaseModel):
    """SHADOW.AI status and neural ganglion state."""
    status: SystemStatus = Field(..., description="Current system status")
    message: str = Field(..., description="Status message")
    neural_ganglion_status: str = Field(..., description="Neural ganglion state")
    consciousness_level: float = Field(..., description="Consciousness level (0-100)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# SYSTEM HEALTH MODELS
# ============================================================================

class SystemHealthInfo(BaseModel):
    """Individual system health information."""
    name: str = Field(..., description="System name")
    status: SystemStatus = Field(..., description="System status")
    last_heartbeat: Optional[datetime] = Field(None, description="Last heartbeat")
    error_count: int = Field(default=0, description="Error count")
    uptime_seconds: int = Field(default=0, description="Uptime in seconds")
    memory_usage_mb: float = Field(default=0.0, description="Memory usage in MB")
    cpu_usage_percent: float = Field(default=0.0, description="CPU usage percentage")


class SystemHealth(BaseModel):
    """Overall system health status."""
    overall_status: SystemStatus = Field(..., description="Overall system status")
    systems: List[SystemHealthInfo] = Field(..., description="Individual system health")
    total_systems: int = Field(..., description="Total number of systems")
    healthy_systems: int = Field(..., description="Number of healthy systems")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# MIGRATION MODELS
# ============================================================================

class MigrationStatus(BaseModel):
    """Migration status tracking."""
    source: str = Field(..., description="Source system/exchange")
    destination: str = Field(..., description="Destination system/exchange")
    status: MigrationStatusType = Field(..., description="Migration status")
    progress: float = Field(..., description="Progress percentage (0-100)")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    amount_migrated: Optional[float] = Field(None, description="Amount migrated")
    total_amount: Optional[float] = Field(None, description="Total amount to migrate")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# TRADING MODELS
# ============================================================================

class TradeSignal(BaseModel):
    """Trade signal from any system."""
    system: str = Field(..., description="Source system")
    action: str = Field(..., description="BUY, SELL, or HOLD")
    symbol: str = Field(..., description="Trading pair (e.g., BTC/USDT)")
    amount: float = Field(..., description="Amount to trade")
    confidence: float = Field(..., description="Confidence level (0-1)")
    reason: str = Field(..., description="Reason for the signal")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ExecutionResult(BaseModel):
    """Result of trade signal execution."""
    signal: TradeSignal = Field(..., description="Original signal")
    executed: bool = Field(..., description="Whether signal was executed")
    result: Optional[str] = Field(None, description="Execution result")
    conflicts: List[str] = Field(default_factory=list, description="Conflicts detected")
    system_used: str = Field(..., description="System that executed the trade")
    execution_time: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# POSITION MODELS
# ============================================================================

class Position(BaseModel):
    """Individual position across systems."""
    symbol: str = Field(..., description="Asset symbol")
    amount: float = Field(..., description="Amount held")
    value_usd: float = Field(..., description="Value in USD")
    system: str = Field(..., description="System holding the position")
    exchange: Optional[str] = Field(None, description="Exchange if applicable")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AggregatedPosition(BaseModel):
    """Aggregated position across all systems."""
    symbol: str = Field(..., description="Asset symbol")
    total_amount: float = Field(..., description="Total amount across all systems")
    total_value_usd: float = Field(..., description="Total value in USD")
    breakdown: Dict[str, float] = Field(..., description="Breakdown by system")
    exchanges: Dict[str, float] = Field(..., description="Breakdown by exchange")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# WEBSOCKET MODELS
# ============================================================================

class WebSocketMessage(BaseModel):
    """Base WebSocket message."""
    type: str = Field(..., description="Message type")
    data: Dict = Field(..., description="Message data")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConsciousnessUpdateMessage(WebSocketMessage):
    """Consciousness value update message."""
    type: str = Field(default="consciousness_update")
    data: ConsciousnessValue = Field(..., description="Updated consciousness value")


class HealthUpdateMessage(WebSocketMessage):
    """System health update message."""
    type: str = Field(default="health_update")
    data: SystemHealth = Field(..., description="Updated system health")


class EmergencyMessage(WebSocketMessage):
    """Emergency status message."""
    type: str = Field(default="emergency")
    data: Dict = Field(..., description="Emergency information")

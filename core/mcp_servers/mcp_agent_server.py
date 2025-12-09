"""
Enhanced MCP Server with AI Agent Integration
Integrates the agent swarm with Model Context Protocol for AI assistant interaction
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from mcp.server.fastmcp import FastMCP
from agent_integrated_system import AgentIntegratedSystem, TradingSignal
from enhanced_exchanges_fixed import ExchangeManager, ArbitrageOpportunity
from ledger_sovereign_integration import sovereign_ledger_security

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
mcp = FastMCP("AI Agent-Integrated Crypto Trading System")

# Global system instance
agent_system: Optional[AgentIntegratedSystem] = None
_initialized = False

async def ensure_agent_system_initialized():
    """Ensure the agent-integrated system is initialized"""
    global agent_system, _initialized
    
    if not _initialized or agent_system is None:
        logger.info("🤖 Initializing AI Agent-Integrated System...")
        agent_system = AgentIntegratedSystem()
        
        success = await agent_system.initialize()
        if not success:
            raise Exception("Failed to initialize agent system")
        
        _initialized = True
        logger.info("✅ AI Agent-Integrated System initialized successfully")

@mcp.tool()
async def get_agent_trading_signals() -> str:
    """
    Get current AI agent trading signals and recommendations.
    
    Returns:
        JSON string with active trading signals from AI agents
    """
    try:
        await ensure_agent_system_initialized()
        
        signals = await agent_system.get_active_signals()
        system_status = await agent_system.get_system_status()
        
        result = {
            "signals": signals,
            "system_status": system_status,
            "timestamp": datetime.now().isoformat(),
            "total_signals": len(signals)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting agent signals: {e}")
        return json.dumps({
            "error": str(e),
            "signals": [],
            "timestamp": datetime.now().isoformat()
        })

@mcp.tool()
async def get_agent_performance_metrics() -> str:
    """
    Get AI agent performance metrics and statistics.
    
    Returns:
        JSON string with agent performance data
    """
    try:
        await ensure_agent_system_initialized()
        
        performance = await agent_system.get_agent_performance()
        system_status = await agent_system.get_system_status()
        
        result = {
            "agent_performance": performance,
            "system_health": system_status["system_health"],
            "agents_active": system_status["agents_active"],
            "exchanges_connected": system_status["exchanges_connected"],
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting agent performance: {e}")
        return json.dumps({
            "error": str(e),
            "performance": {},
            "timestamp": datetime.now().isoformat()
        })

@mcp.tool()
async def execute_agent_signal(signal_id: str) -> str:
    """
    Execute a specific AI agent trading signal.
    
    Args:
        signal_id: ID of the signal to execute
    
    Returns:
        JSON string with execution results
    """
    try:
        await ensure_agent_system_initialized()
        
        # Find the signal by ID
        signals = await agent_system.get_active_signals()
        signal_to_execute = None
        
        for signal in signals:
            if signal.get('symbol') == signal_id or signal.get('agent_id') == signal_id:
                signal_to_execute = signal
                break
        
        if not signal_to_execute:
            return json.dumps({
                "error": f"Signal {signal_id} not found",
                "available_signals": [s.get('symbol') for s in signals],
                "timestamp": datetime.now().isoformat()
            })
        
        # Convert dict back to TradingSignal object
        signal_obj = TradingSignal(
            symbol=signal_to_execute['symbol'],
            action=signal_to_execute['action'],
            confidence=signal_to_execute['confidence'],
            price_target=signal_to_execute['price_target'],
            stop_loss=signal_to_execute.get('stop_loss'),
            take_profit=signal_to_execute.get('take_profit'),
            reasoning=signal_to_execute.get('reasoning', ''),
            agent_id=signal_to_execute.get('agent_id', ''),
            timestamp=datetime.fromisoformat(signal_to_execute['timestamp'])
        )
        
        # Execute the signal
        execution_result = await agent_system.execute_signal(signal_obj)
        
        return json.dumps(execution_result, indent=2)
        
    except Exception as e:
        logger.error(f"Error executing signal {signal_id}: {e}")
        return json.dumps({
            "error": str(e),
            "signal_id": signal_id,
            "timestamp": datetime.now().isoformat()
        })

@mcp.tool()
async def get_ai_arbitrage_analysis(symbols: str = "BTC/USDT,ETH/USDT,SOL/USDT") -> str:
    """
    Get AI-enhanced arbitrage analysis with agent insights.
    
    Args:
        symbols: Comma-separated list of symbols to analyze
    
    Returns:
        JSON string with AI-enhanced arbitrage analysis
    """
    try:
        await ensure_agent_system_initialized()
        
        symbol_list = [s.strip() for s in symbols.split(',')]
        
        # Get traditional arbitrage opportunities
        opportunities = await agent_system.get_opportunities()
        
        # Get agent signals for these symbols
        signals = await agent_system.get_active_signals()
        relevant_signals = [s for s in signals if s['symbol'] in symbol_list]
        
        # Get system status
        system_status = await agent_system.get_system_status()
        
        result = {
            "arbitrage_opportunities": opportunities,
            "agent_signals": relevant_signals,
            "analysis": {
                "total_opportunities": len(opportunities),
                "agent_signals_count": len(relevant_signals),
                "system_health": system_status["system_health"],
                "confidence_threshold": 0.7
            },
            "symbols_analyzed": symbol_list,
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting AI arbitrage analysis: {e}")
        return json.dumps({
            "error": str(e),
            "symbols": symbols,
            "timestamp": datetime.now().isoformat()
        })

@mcp.tool()
async def get_agent_swarm_status() -> str:
    """
    Get detailed status of the AI agent swarm.
    
    Returns:
        JSON string with swarm status and individual agent details
    """
    try:
        await ensure_agent_system_initialized()
        
        system_status = await agent_system.get_system_status()
        performance = await agent_system.get_agent_performance()
        signals = await agent_system.get_active_signals()
        
        result = {
            "swarm_status": {
                "total_agents": system_status["agents_active"],
                "active_signals": len(signals),
                "system_health": system_status["system_health"],
                "last_scan": system_status.get("last_scan_time"),
                "error_count": system_status.get("error_count", 0)
            },
            "performance_metrics": performance,
            "active_signals": signals,
            "system_metrics": {
                "exchanges_connected": system_status["exchanges_connected"],
                "portfolio_value": system_status["total_portfolio_value"],
                "opportunities": system_status["active_opportunities"]
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting swarm status: {e}")
        return json.dumps({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@mcp.tool()
async def run_agent_trading_cycle() -> str:
    """
    Manually trigger a complete AI agent trading cycle.
    
    Returns:
        JSON string with cycle results and agent decisions
    """
    try:
        await ensure_agent_system_initialized()
        
        # Run one complete trading cycle
        cycle_result = await agent_system.process(None)
        
        if cycle_result:
            return json.dumps(cycle_result, indent=2)
        else:
            return json.dumps({
                "error": "Trading cycle failed or system not running",
                "timestamp": datetime.now().isoformat()
            })
        
    except Exception as e:
        logger.error(f"Error running trading cycle: {e}")
        return json.dumps({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

# Keep existing tools from the original MCP server
@mcp.tool()
async def get_multi_exchange_prices(symbol: str = "BTC/USDT") -> str:
    """
    Get current prices for a symbol across all connected exchanges.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTC/USDT', 'ETH/USDT', 'SOL/USDT')
    
    Returns:
        JSON string with prices from each exchange and analysis
    """
    try:
        await ensure_agent_system_initialized()
        
        # Use the exchange manager from the agent system
        exchange_manager = agent_system.exchange_manager
        prices = await exchange_manager.get_price_map(symbol)
        
        if not prices:
            return json.dumps({
                "error": f"No prices available for {symbol}",
                "symbol": symbol,
                "timestamp": datetime.now().isoformat()
            })
        
        # Calculate spread analysis
        min_price = min(prices.values())
        max_price = max(prices.values())
        spread_percent = ((max_price - min_price) / min_price) * 100 if min_price > 0 else 0
        
        cheapest_exchange = min(prices, key=prices.get)
        most_expensive_exchange = max(prices, key=prices.get)
        
        result = {
            "symbol": symbol,
            "prices": prices,
            "analysis": {
                "cheapest_exchange": cheapest_exchange,
                "cheapest_price": min_price,
                "most_expensive_exchange": most_expensive_exchange,
                "most_expensive_price": max_price,
                "spread_percent": round(spread_percent, 4),
                "average_price": round(sum(prices.values()) / len(prices), 4)
            },
            "timestamp": datetime.now().isoformat(),
            "exchange_count": len(prices)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error fetching prices for {symbol}: {e}")
        return json.dumps({
            "error": str(e),
            "symbol": symbol,
            "timestamp": datetime.now().isoformat()
        })

@mcp.tool()
async def get_portfolio_aggregation() -> str:
    """
    Get aggregated portfolio balances across all connected exchanges.
    
    Returns:
        JSON string with portfolio balances from each exchange and totals
    """
    try:
        await ensure_agent_system_initialized()
        
        # Use the portfolio manager from the agent system
        portfolio_manager = agent_system.portfolio_manager
        portfolio = await portfolio_manager.get_portfolio_summary()
        
        return json.dumps(portfolio, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        return json.dumps({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@mcp.tool()
async def monitor_exchange_status() -> str:
    """
    Check the connection status and health of all configured exchanges.
    
    Returns:
        JSON string with exchange status and connectivity information
    """
    try:
        await ensure_agent_system_initialized()
        
        exchange_manager = agent_system.exchange_manager
        system_status = await agent_system.get_system_status()
        
        result = {
            "system_health": {
                "exchanges_connected": system_status["exchanges_connected"],
                "agents_active": system_status["agents_active"],
                "health_percentage": 100 if system_status["system_health"] == "healthy" else 50,
                "status": system_status["system_health"]
            },
            "connection_status": exchange_manager.connection_status,
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error monitoring exchange status: {e}")
        return json.dumps({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

if __name__ == "__main__":
    # Run the enhanced MCP server
    logger.info("🚀 Starting AI Agent-Integrated MCP Server...")
    mcp.run()

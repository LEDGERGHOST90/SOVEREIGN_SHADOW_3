"""
MCP Server for Multi-Exchange Crypto Portfolio Management
Integrates the enhanced exchange system with Model Context Protocol
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from mcp.server.fastmcp import FastMCP
from enhanced_exchanges import ExchangeManager, ArbitrageOpportunity
from ledger_sovereign_integration import sovereign_ledger_security

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the MCP server
mcp = FastMCP("Multi-Exchange Crypto Manager")

# Global exchange manager instance
exchange_manager = ExchangeManager()
_initialized = False

async def ensure_initialized():
    """Ensure exchange manager is initialized"""
    global _initialized
    if not _initialized:
        logger.info("🔄 Initializing exchange connections...")
        results = await exchange_manager.initialize_exchanges()
        connected_exchanges = [ex for ex, status in results.items() if status]
        
        if connected_exchanges:
            logger.info(f"✅ Connected to: {', '.join(connected_exchanges)}")
            _initialized = True
        else:
            logger.error("❌ No exchanges connected. Check API credentials.")
            raise Exception("No exchanges available")

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
        await ensure_initialized()
        
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
async def detect_arbitrage_opportunities(
    symbols: str = "BTC/USDT,ETH/USDT,SOL/USDT", 
    min_profit_percent: str = "0.2"
) -> str:
    """
    Scan for arbitrage opportunities across exchanges.
    
    Args:
        symbols: Comma-separated list of symbols to scan (e.g., 'BTC/USDT,ETH/USDT,SOL/USDT')
        min_profit_percent: Minimum profit percentage threshold (default: 0.2%)
    
    Returns:
        JSON string with detected arbitrage opportunities
    """
    try:
        await ensure_initialized()
        
        symbol_list = [s.strip() for s in symbols.split(',')]
        min_profit = float(min_profit_percent)
        
        opportunities = await exchange_manager.detect_arbitrage_opportunities(
            symbols=symbol_list,
            min_profit_percent=min_profit
        )
        
        # Convert opportunities to serializable format
        opportunities_data = []
        for opp in opportunities:
            opportunities_data.append({
                "symbol": opp.symbol,
                "buy_exchange": opp.buy_exchange,
                "sell_exchange": opp.sell_exchange,
                "buy_price": opp.buy_price,
                "sell_price": opp.sell_price,
                "spread_percent": round(opp.spread_percent, 4),
                "estimated_profit_percent": round(opp.estimated_profit_percent, 4),
                "min_order_size": opp.min_order_size,
                "max_order_size": opp.max_order_size,
                "timestamp": opp.timestamp.isoformat()
            })
        
        result = {
            "opportunities_found": len(opportunities_data),
            "opportunities": opportunities_data,
            "scan_parameters": {
                "symbols_scanned": symbol_list,
                "min_profit_threshold": min_profit,
                "scan_timestamp": datetime.now().isoformat()
            },
            "summary": {
                "best_opportunity": opportunities_data[0] if opportunities_data else None,
                "total_symbols_scanned": len(symbol_list),
                "profitable_opportunities": len(opportunities_data)
            }
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error detecting arbitrage: {e}")
        return json.dumps({
            "error": str(e),
            "scan_parameters": {
                "symbols": symbols,
                "min_profit_percent": min_profit_percent
            },
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
        await ensure_initialized()
        
        portfolio = await exchange_manager.get_portfolio_summary()
        
        # Aggregate balances by asset
        total_balances = {}
        exchange_details = {}
        
        for exchange_name, balances in portfolio.items():
            exchange_details[exchange_name] = {}
            
            for balance in balances:
                asset = balance.asset
                total = balance.total
                
                # Add to exchange details
                exchange_details[exchange_name][asset] = {
                    "free": balance.free,
                    "used": balance.used,
                    "total": balance.total
                }
                
                # Add to total balances
                if asset not in total_balances:
                    total_balances[asset] = 0
                total_balances[asset] += total
        
        # Filter out zero balances and sort by value
        significant_balances = {k: v for k, v in total_balances.items() if v > 0.0001}
        
        result = {
            "portfolio_summary": {
                "total_assets": len(significant_balances),
                "exchanges_connected": len([ex for ex, status in exchange_manager.connection_status.items() if status]),
                "total_balances": significant_balances
            },
            "exchange_breakdown": exchange_details,
            "connection_status": exchange_manager.connection_status,
            "timestamp": datetime.now().isoformat()
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        return json.dumps({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@mcp.tool()
async def get_best_execution_route(symbol: str = "BTC/USDT", side: str = "buy", amount: str = "0.01") -> str:
    """
    Find the best exchange for order execution based on current prices.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTC/USDT')
        side: Order side ('buy' or 'sell')
        amount: Order amount in base currency
    
    Returns:
        JSON string with best execution route and analysis
    """
    try:
        await ensure_initialized()
        
        amount_float = float(amount)
        
        routing_info = await exchange_manager.get_best_price_routing(symbol, side, amount_float)
        
        # Calculate savings compared to other exchanges
        all_prices = routing_info['all_prices']
        best_price = routing_info['price']
        
        savings_analysis = {}
        for exchange, price in all_prices.items():
            if exchange != routing_info['exchange']:
                if side.lower() == 'buy':
                    savings = (price - best_price) * amount_float
                    savings_percent = ((price - best_price) / price) * 100
                else:
                    savings = (best_price - price) * amount_float
                    savings_percent = ((best_price - price) / price) * 100
                
                savings_analysis[exchange] = {
                    "price_difference": round(abs(price - best_price), 6),
                    "savings_usd": round(savings, 4),
                    "savings_percent": round(savings_percent, 4)
                }
        
        result = {
            "recommendation": {
                "exchange": routing_info['exchange'],
                "price": routing_info['price'],
                "estimated_fee": routing_info['estimated_fee'],
                "fee_rate_percent": routing_info['fee_rate'] * 100,
                "total_cost": routing_info['price'] * amount_float + routing_info['estimated_fee']
            },
            "order_details": {
                "symbol": symbol,
                "side": side,
                "amount": amount_float,
                "estimated_total": routing_info['price'] * amount_float
            },
            "market_analysis": {
                "all_exchange_prices": all_prices,
                "price_spread": {
                    "min_price": min(all_prices.values()),
                    "max_price": max(all_prices.values()),
                    "spread_percent": ((max(all_prices.values()) - min(all_prices.values())) / min(all_prices.values())) * 100
                }
            },
            "savings_vs_other_exchanges": savings_analysis,
            "timestamp": routing_info['timestamp'].isoformat()
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting execution route: {e}")
        return json.dumps({
            "error": str(e),
            "parameters": {
                "symbol": symbol,
                "side": side,
                "amount": amount
            },
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
        # Test connections
        test_results = await exchange_manager.initialize_exchanges()
        
        status_details = {}
        for exchange_name in ["binanceus", "kraken", "okx"]:
            is_connected = test_results.get(exchange_name, False)
            
            status_details[exchange_name] = {
                "connected": is_connected,
                "last_check": datetime.now().isoformat(),
                "api_configured": bool(exchange_manager.exchanges.get(exchange_name)),
                "rate_limit": exchange_manager.exchanges[exchange_name].rateLimit if exchange_name in exchange_manager.exchanges else None
            }
            
            # Test with a simple price fetch if connected
            if is_connected:
                try:
                    prices = await exchange_manager.get_price_map('BTC/USDT', venues=(exchange_name,))
                    status_details[exchange_name]["test_price_fetch"] = "success"
                    status_details[exchange_name]["btc_price"] = prices.get(exchange_name)
                except Exception as e:
                    status_details[exchange_name]["test_price_fetch"] = f"failed: {str(e)}"
        
        # Overall system health
        connected_count = sum(1 for status in status_details.values() if status["connected"])
        
        result = {
            "system_health": {
                "exchanges_connected": connected_count,
                "total_exchanges": len(status_details),
                "health_percentage": (connected_count / len(status_details)) * 100,
                "status": "healthy" if connected_count >= 2 else "degraded" if connected_count >= 1 else "critical"
            },
            "exchange_details": status_details,
            "recommendations": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # Add recommendations based on status
        if connected_count == 0:
            result["recommendations"].append("Check API credentials for all exchanges")
        elif connected_count < 3:
            disconnected = [ex for ex, details in status_details.items() if not details["connected"]]
            result["recommendations"].append(f"Restore connection to: {', '.join(disconnected)}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Error monitoring exchange status: {e}")
        return json.dumps({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@mcp.tool()
async def execute_arbitrage_scan_report() -> str:
    """
    Execute a comprehensive arbitrage scan and generate a detailed report.
    
    Returns:
        Formatted report string with arbitrage opportunities and market analysis
    """
    try:
        await ensure_initialized()
        
        # Scan major trading pairs
        major_pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 'AVAX/USDT']
        
        opportunities = await exchange_manager.detect_arbitrage_opportunities(
            symbols=major_pairs,
            min_profit_percent=0.1  # Lower threshold for comprehensive scan
        )
        
        # Generate formatted report
        report = exchange_manager.format_arbitrage_report(opportunities)
        
        # Add market summary
        market_summary = "\n📊 **MARKET SUMMARY**\n"
        
        total_opportunities = len(opportunities)
        if total_opportunities > 0:
            avg_profit = sum(opp.estimated_profit_percent for opp in opportunities) / total_opportunities
            best_profit = max(opp.estimated_profit_percent for opp in opportunities)
            
            market_summary += f"• Total Opportunities: {total_opportunities}\n"
            market_summary += f"• Average Profit: {avg_profit:.2f}%\n"
            market_summary += f"• Best Opportunity: {best_profit:.2f}%\n"
            
            # Most active pairs
            pair_counts = {}
            for opp in opportunities:
                pair_counts[opp.symbol] = pair_counts.get(opp.symbol, 0) + 1
            
            most_active = max(pair_counts, key=pair_counts.get) if pair_counts else "None"
            market_summary += f"• Most Active Pair: {most_active}\n"
        else:
            market_summary += "• No profitable opportunities detected\n"
        
        # Exchange connectivity status
        connected_exchanges = [ex for ex, status in exchange_manager.connection_status.items() if status]
        market_summary += f"• Connected Exchanges: {', '.join(connected_exchanges)}\n"
        market_summary += f"• Scan Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        
        full_report = report + market_summary
        
        return full_report
        
    except Exception as e:
        logger.error(f"Error executing arbitrage scan: {e}")
        return f"❌ **ERROR EXECUTING ARBITRAGE SCAN**\n\nError: {str(e)}\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"

@mcp.tool()
async def connect_ledger_live() -> str:
    """
    Establish secure connection to Ledger Live hardware wallet.
    Performs comprehensive security audit before connection.
    
    Returns:
        JSON string with connection status and security details
    """
    try:
        logger.info("🔐 Initiating Ledger Live connection...")
        
        connection_result = await sovereign_ledger_security.secure_connect_ledger()
        
        if connection_result["status"] == "secure_connected":
            return json.dumps({
                "status": "connected",
                "message": "✅ Ledger Live: Secure connection established",
                "device_id": connection_result.get("device_id"),
                "security_level": "sovereign",
                "timestamp": datetime.now().isoformat()
            }, indent=2)
        else:
            return json.dumps({
                "status": "failed",
                "message": "❌ Ledger Live connection failed",
                "error": connection_result.get("error"),
                "timestamp": datetime.now().isoformat()
            }, indent=2)
            
    except Exception as e:
        logger.error(f"Ledger connection error: {e}")
        return json.dumps({
            "status": "error",
            "message": f"❌ Connection error: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }, indent=2)

@mcp.tool()
async def get_ledger_portfolio() -> str:
    """
    Get secure portfolio data from Ledger Live with encryption.
    Requires active Ledger connection.
    
    Returns:
        JSON string with encrypted portfolio data and security verification
    """
    try:
        logger.info("📊 Fetching secure portfolio from Ledger Live...")
        
        portfolio_data = await sovereign_ledger_security.get_secure_portfolio()
        
        return json.dumps({
            "status": "success",
            "message": "✅ Portfolio data retrieved securely",
            "total_value_usd": portfolio_data["total_value_usd"],
            "asset_count": portfolio_data["asset_count"],
            "verification_status": portfolio_data["verification_status"],
            "timestamp": portfolio_data["timestamp"],
            "security_hash": portfolio_data["security_hash"][:16] + "...",  # Truncated for security
            "encrypted_portfolio": "ENCRYPTED_DATA_AVAILABLE"
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Portfolio fetch error: {e}")
        return json.dumps({
            "status": "error",
            "message": f"❌ Portfolio fetch failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }, indent=2)

@mcp.tool()
async def execute_sovereign_trade(
    symbol: str,
    side: str,
    amount: float,
    price: float,
    amount_usd: float
) -> str:
    """
    Execute trade with Ledger Live hardware confirmation.
    Requires comprehensive security validation and hardware approval.
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTC', 'ETH', 'XRP')
        side: Trade direction ('buy' or 'sell')
        amount: Amount of cryptocurrency
        price: Price per unit
        amount_usd: Total value in USD
    
    Returns:
        JSON string with trade execution results and security confirmation
    """
    try:
        logger.info(f"🔐 Executing sovereign trade: {side} {amount} {symbol} @ ${price}")
        
        trade_params = {
            "symbol": symbol.upper(),
            "side": side.lower(),
            "amount": amount,
            "price": price,
            "amount_usd": amount_usd
        }
        
        trade_result = await sovereign_ledger_security.execute_sovereign_trade(trade_params)
        
        return json.dumps({
            "status": "executed",
            "message": "✅ Sovereign trade executed with hardware confirmation",
            "trade_id": trade_result["trade_id"],
            "symbol": trade_result["symbol"],
            "side": trade_result["side"],
            "amount": trade_result["amount"],
            "price": trade_result["price"],
            "value_usd": trade_result["value_usd"],
            "execution_time": trade_result["execution_time"],
            "hardware_confirmed": trade_result["hardware_confirmed"],
            "security_level": trade_result["security_level"],
            "timestamp": datetime.now().isoformat()
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Sovereign trade execution error: {e}")
        return json.dumps({
            "status": "failed",
            "message": f"❌ Trade execution failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }, indent=2)

@mcp.tool()
async def get_ledger_security_status() -> str:
    """
    Get comprehensive security status of Ledger Live integration.
    Includes connection status, session details, and audit trail.
    
    Returns:
        JSON string with detailed security status and metrics
    """
    try:
        logger.info("🔍 Checking Ledger Live security status...")
        
        security_status = sovereign_ledger_security.get_security_status()
        recent_audit_log = sovereign_ledger_security.get_security_audit_log(limit=10)
        
        return json.dumps({
            "status": "success",
            "message": "✅ Security status retrieved",
            "connection_status": "connected" if security_status["connected"] else "disconnected",
            "session_age_minutes": round(security_status["session_age_minutes"], 2),
            "security_events_count": security_status["security_events_count"],
            "last_portfolio_sync": security_status["last_portfolio_sync"],
            "max_trade_amount": security_status["max_trade_amount"],
            "pending_confirmations": security_status["pending_confirmations"],
            "recent_audit_events": len(recent_audit_log),
            "timestamp": datetime.now().isoformat()
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Security status error: {e}")
        return json.dumps({
            "status": "error",
            "message": f"❌ Security status check failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }, indent=2)

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()

#!/usr/bin/env python3
"""
🔥 TACTICAL API SERVER - ROI EXECUTION MODE
Serves the Ultimate Tactical Intelligence Engine via REST API endpoints
Optimized for $1000+ ROI per quarter with complete tactical soul extraction

This is the API backbone that powers the ShadowCommander UI
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import os
import traceback

# Import our Ultimate Tactical Intelligence Engine
from ultimate_tactical_intelligence import UltimateTacticalIntelligence

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins="*")  # Allow all origins for development

# Initialize the Ultimate Tactical Intelligence Engine
try:
    tactical_engine = UltimateTacticalIntelligence()
    logger.info("🔥 Ultimate Tactical Intelligence Engine loaded successfully")
except Exception as e:
    logger.error(f"Failed to initialize Tactical Intelligence Engine: {e}")
    tactical_engine = None

# Cache for tactical flow (refresh every 30 minutes)
tactical_flow_cache = {
    'data': None,
    'timestamp': None,
    'cache_duration': 1800  # 30 minutes in seconds
}

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    
    return jsonify({
        'status': 'operational',
        'service': 'Tactical API Server',
        'mode': 'ROI_EXECUTION_MODE::ENGAGED',
        'engine': 'Ultimate Tactical Intelligence' if tactical_engine else 'OFFLINE',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/tactical-flow', methods=['GET'])
def get_tactical_flow():
    """Get complete daily tactical flow - THE ULTIMATE ENDPOINT"""
    
    try:
        # Check cache first
        now = datetime.now()
        if (tactical_flow_cache['data'] and 
            tactical_flow_cache['timestamp'] and
            (now - tactical_flow_cache['timestamp']).seconds < tactical_flow_cache['cache_duration']):
            
            logger.info("🔥 Serving cached tactical flow")
            return jsonify(tactical_flow_cache['data'])
        
        if not tactical_engine:
            return jsonify({
                'error': 'Tactical Intelligence Engine not available',
                'status': 'offline'
            }), 503
        
        logger.info("🔥 Generating fresh tactical flow")
        
        # Generate complete tactical flow
        tactical_flow = tactical_engine.generate_complete_tactical_flow()
        
        # Format for JSON output
        json_output = tactical_engine.format_for_json(tactical_flow)
        
        # Update cache
        tactical_flow_cache['data'] = json_output
        tactical_flow_cache['timestamp'] = now
        
        logger.info(f"🔥 Tactical flow generated: {json_output['emotional_risk_signal']} {json_output['system_health']}")
        
        return jsonify(json_output)
        
    except Exception as e:
        logger.error(f"Error generating tactical flow: {e}")
        logger.error(traceback.format_exc())
        
        return jsonify({
            'error': 'Failed to generate tactical flow',
            'message': str(e),
            'status': 'error'
        }), 500

@app.route('/api/flip-recommendations', methods=['GET'])
def get_flip_recommendations():
    """Get tactical flip recommendations"""
    
    try:
        if not tactical_engine:
            return jsonify({'error': 'Engine not available'}), 503
        
        # Get vaultlog intelligence and market data
        vaultlog_intelligence = tactical_engine.extract_vaultlog_intelligence()
        market_data = tactical_engine._generate_market_data()
        
        # Generate flip recommendations
        recommendations = tactical_engine.generate_tactical_flip_recommendations(
            vaultlog_intelligence, market_data
        )
        
        # Convert to JSON
        json_recommendations = [tactical_engine.format_for_json(rec) for rec in recommendations]
        
        return jsonify({
            'flip_recommendations': json_recommendations,
            'count': len(recommendations),
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating flip recommendations: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/whale-watchlist', methods=['GET'])
def get_whale_watchlist():
    """Get whale-aligned watchlist with MENACE signals"""
    
    try:
        if not tactical_engine:
            return jsonify({'error': 'Engine not available'}), 503
        
        # Generate market data
        market_data = tactical_engine._generate_market_data()
        
        # Generate whale watchlist
        watchlist = tactical_engine.generate_whale_aligned_watchlist(market_data)
        
        # Convert to JSON
        json_watchlist = [tactical_engine.format_for_json(whale) for whale in watchlist]
        
        return jsonify({
            'whale_watchlist': json_watchlist,
            'count': len(watchlist),
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating whale watchlist: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/vault-alerts', methods=['GET'])
def get_vault_alerts():
    """Get vault aging alerts and reallocation suggestions"""
    
    try:
        if not tactical_engine:
            return jsonify({'error': 'Engine not available'}), 503
        
        # Get vaultlog intelligence
        vaultlog_intelligence = tactical_engine.extract_vaultlog_intelligence()
        
        # Generate vault alerts
        alerts = tactical_engine.generate_vault_aging_alerts(vaultlog_intelligence)
        
        # Convert to JSON
        json_alerts = [tactical_engine.format_for_json(alert) for alert in alerts]
        
        return jsonify({
            'vault_alerts': json_alerts,
            'count': len(alerts),
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating vault alerts: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/tile-heatmap', methods=['GET'])
def get_tile_heatmap():
    """Get tile-based heatmap scores per asset"""
    
    try:
        if not tactical_engine:
            return jsonify({'error': 'Engine not available'}), 503
        
        # Generate market data
        market_data = tactical_engine._generate_market_data()
        
        # Get flip recommendations and whale watchlist for heatmap
        vaultlog_intelligence = tactical_engine.extract_vaultlog_intelligence()
        flip_recommendations = tactical_engine.generate_tactical_flip_recommendations(
            vaultlog_intelligence, market_data
        )
        whale_watchlist = tactical_engine.generate_whale_aligned_watchlist(market_data)
        
        # Generate tile heatmap
        heatmap = tactical_engine.generate_tile_heatmap(
            market_data, flip_recommendations, whale_watchlist
        )
        
        # Convert to JSON
        json_heatmap = [tactical_engine.format_for_json(tile) for tile in heatmap]
        
        return jsonify({
            'tile_heatmap': json_heatmap,
            'count': len(heatmap),
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating tile heatmap: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/primary-directive', methods=['GET'])
def get_primary_directive():
    """Get the single most profitable move for the day"""
    
    try:
        if not tactical_engine:
            return jsonify({'error': 'Engine not available'}), 503
        
        # Generate all components needed for primary directive
        vaultlog_intelligence = tactical_engine.extract_vaultlog_intelligence()
        market_data = tactical_engine._generate_market_data()
        
        flip_recommendations = tactical_engine.generate_tactical_flip_recommendations(
            vaultlog_intelligence, market_data
        )
        whale_watchlist = tactical_engine.generate_whale_aligned_watchlist(market_data)
        vault_alerts = tactical_engine.generate_vault_aging_alerts(vaultlog_intelligence)
        
        # Generate primary directive
        primary_directive = tactical_engine.generate_primary_directive(
            flip_recommendations, whale_watchlist, vault_alerts
        )
        
        # Determine emotional risk signal
        emotional_risk_signal = tactical_engine.determine_emotional_risk_signal(
            flip_recommendations, vault_alerts, market_data
        )
        
        return jsonify({
            'primary_directive': primary_directive,
            'emotional_risk_signal': emotional_risk_signal,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating primary directive: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/roi-projections', methods=['GET'])
def get_roi_projections():
    """Get ROI projections for wealth optimization"""
    
    try:
        if not tactical_engine:
            return jsonify({'error': 'Engine not available'}), 503
        
        # Generate components needed for ROI calculations
        vaultlog_intelligence = tactical_engine.extract_vaultlog_intelligence()
        market_data = tactical_engine._generate_market_data()
        
        flip_recommendations = tactical_engine.generate_tactical_flip_recommendations(
            vaultlog_intelligence, market_data
        )
        vault_alerts = tactical_engine.generate_vault_aging_alerts(vaultlog_intelligence)
        
        # Calculate ROI projections
        roi_projections = tactical_engine.calculate_roi_projections(
            flip_recommendations, vault_alerts
        )
        
        return jsonify({
            'roi_projections': roi_projections,
            'target_quarterly': tactical_engine.roi_targets['quarterly_target'],
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error calculating ROI projections: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/notion-export', methods=['GET'])
def get_notion_export():
    """Get tactical flow formatted for Notion markdown"""
    
    try:
        if not tactical_engine:
            return jsonify({'error': 'Engine not available'}), 503
        
        # Generate complete tactical flow
        tactical_flow = tactical_engine.generate_complete_tactical_flow()
        
        # Format for Notion
        notion_markdown = tactical_engine.format_for_notion(tactical_flow)
        
        return jsonify({
            'notion_markdown': notion_markdown,
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating Notion export: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/system-status', methods=['GET'])
def get_system_status():
    """Get complete system status and health metrics"""
    
    try:
        system_status = {
            'tactical_engine': 'OPERATIONAL' if tactical_engine else 'OFFLINE',
            'mode': 'ROI_EXECUTION_MODE::ENGAGED',
            'cache_status': {
                'tactical_flow_cached': tactical_flow_cache['data'] is not None,
                'cache_age_minutes': 0 if not tactical_flow_cache['timestamp'] else 
                                   int((datetime.now() - tactical_flow_cache['timestamp']).seconds / 60)
            },
            'roi_targets': tactical_engine.roi_targets if tactical_engine else {},
            'system_health': 'OPTIMAL',
            'uptime': 'ACTIVE',
            'generated_at': datetime.now().isoformat()
        }
        
        return jsonify(system_status)
        
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh-cache', methods=['POST'])
def refresh_cache():
    """Force refresh of tactical flow cache"""
    
    try:
        # Clear cache
        tactical_flow_cache['data'] = None
        tactical_flow_cache['timestamp'] = None
        
        logger.info("🔥 Cache cleared - next request will generate fresh tactical flow")
        
        return jsonify({
            'message': 'Cache refreshed successfully',
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error refreshing cache: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/api/health',
            '/api/tactical-flow',
            '/api/flip-recommendations',
            '/api/whale-watchlist',
            '/api/vault-alerts',
            '/api/tile-heatmap',
            '/api/primary-directive',
            '/api/roi-projections',
            '/api/notion-export',
            '/api/system-status',
            '/api/refresh-cache'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'The tactical intelligence engine encountered an error',
        'status': 'error'
    }), 500

if __name__ == '__main__':
    logger.info("🔥 TACTICAL API SERVER - ROI EXECUTION MODE STARTING")
    logger.info("🎯 Ultimate Tactical Intelligence Engine - Ready for $1000+ ROI")
    
    # Run the server
    app.run(
        host='0.0.0.0',  # Allow external access
        port=5001,       # Use port 5001 to avoid conflicts
        debug=True,      # Enable debug mode for development
        threaded=True    # Enable threading for concurrent requests
    )


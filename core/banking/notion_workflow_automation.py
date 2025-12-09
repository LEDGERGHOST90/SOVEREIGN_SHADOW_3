#!/usr/bin/env python3
"""
LLF-ß Notion Bridge Integration
Advanced workflow automation with flip logs, vault signals, and Ray Rules
"""

import os
import json
import time
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/notion_bridge.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class FlipStatus(Enum):
    PENDING = "Pending"
    ACTIVE = "Active"
    COMPLETED = "Completed"
    STOPPED = "Stopped"

class VaultSignal(Enum):
    INJECT = "Inject"
    HOLD = "Hold"
    WITHDRAW = "Withdraw"

@dataclass
class FlipEntry:
    flip_id: str
    symbol: str
    entry_price: float
    target_price: float
    stop_loss: float
    quantity: float
    ray_score: float
    clarity_score: float
    frhi_score: float
    status: FlipStatus
    entry_time: datetime
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    notes: str = ""

@dataclass
class VaultOperation:
    operation_id: str
    operation_type: VaultSignal
    amount: float
    source_flip: Optional[str]
    ray_score: float
    confidence: float
    timestamp: datetime
    signature: str
    status: str = "Pending"

@dataclass
class RayRulesAssessment:
    flip_id: str
    rule_1_score: float  # Clarity of purpose
    rule_2_score: float  # Risk assessment
    rule_3_score: float  # Value alignment
    rule_4_score: float  # Emotional state
    rule_5_score: float  # 10-year regret test
    overall_clarity: float
    recommendation: str
    timestamp: datetime

class NotionBridge:
    """
    Advanced Notion integration for LLF-ß workflow automation
    """
    
    def __init__(self, notion_token: str = None, database_ids: Dict[str, str] = None):
        self.notion_token = notion_token or os.getenv('NOTION_TOKEN', 'demo_token')
        self.base_url = "https://api.notion.com/v1"
        
        # Database IDs for different tables
        self.database_ids = database_ids or {
            'flip_tracker': os.getenv('NOTION_FLIP_DB', 'demo_flip_db'),
            'vault_operations': os.getenv('NOTION_VAULT_DB', 'demo_vault_db'),
            'ray_rules': os.getenv('NOTION_RAY_DB', 'demo_ray_db'),
            'omega_sigil': os.getenv('NOTION_OMEGA_DB', 'demo_omega_db')
        }
        
        # Headers for Notion API
        self.headers = {
            'Authorization': f'Bearer {self.notion_token}',
            'Content-Type': 'application/json',
            'Notion-Version': '2022-06-28'
        }
        
        # Demo mode for testing
        self.demo_mode = self.notion_token == 'demo_token'
        
        logger.info("🔗 Notion Bridge initialized")
        logger.info(f"🔧 Demo mode: {self.demo_mode}")
        logger.info(f"📊 Database IDs: {list(self.database_ids.keys())}")

    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make authenticated request to Notion API"""
        if self.demo_mode:
            return self._get_mock_response(endpoint, data)
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method.upper() == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Notion API error: {e}")
            return {'error': str(e)}

    def _get_mock_response(self, endpoint: str, data: dict = None) -> dict:
        """Generate mock responses for demo mode"""
        if 'pages' in endpoint:
            return {
                'object': 'page',
                'id': f'demo-page-{int(time.time())}',
                'created_time': datetime.now().isoformat(),
                'last_edited_time': datetime.now().isoformat(),
                'properties': {}
            }
        elif 'databases' in endpoint and 'query' in endpoint:
            return {
                'object': 'list',
                'results': [],
                'next_cursor': None,
                'has_more': False
            }
        else:
            return {'success': True, 'demo': True}

    def create_flip_entry(self, flip: FlipEntry) -> bool:
        """Create new flip entry in Notion"""
        try:
            logger.info(f"📝 Creating flip entry: {flip.flip_id} - {flip.symbol}")
            
            # Prepare Notion page properties
            properties = {
                'Flip ID': {
                    'title': [{'text': {'content': flip.flip_id}}]
                },
                'Symbol': {
                    'rich_text': [{'text': {'content': flip.symbol}}]
                },
                'Entry Price': {
                    'number': flip.entry_price
                },
                'Target Price': {
                    'number': flip.target_price
                },
                'Stop Loss': {
                    'number': flip.stop_loss
                },
                'Quantity': {
                    'number': flip.quantity
                },
                'Ray Score': {
                    'number': flip.ray_score
                },
                'Clarity Score': {
                    'number': flip.clarity_score
                },
                'FRHI Score': {
                    'number': flip.frhi_score
                },
                'Status': {
                    'select': {'name': flip.status.value}
                },
                'Entry Time': {
                    'date': {'start': flip.entry_time.isoformat()}
                },
                'Notes': {
                    'rich_text': [{'text': {'content': flip.notes}}]
                }
            }
            
            # Add exit data if available
            if flip.exit_time:
                properties['Exit Time'] = {
                    'date': {'start': flip.exit_time.isoformat()}
                }
            if flip.exit_price:
                properties['Exit Price'] = {'number': flip.exit_price}
            if flip.pnl is not None:
                properties['PnL'] = {'number': flip.pnl}
            if flip.pnl_percent is not None:
                properties['PnL %'] = {'number': flip.pnl_percent}
            
            data = {
                'parent': {'database_id': self.database_ids['flip_tracker']},
                'properties': properties
            }
            
            response = self._make_request('POST', 'pages', data)
            
            if 'error' in response:
                logger.error(f"❌ Failed to create flip entry: {response['error']}")
                return False
            
            logger.info(f"✅ Flip entry created: {flip.flip_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating flip entry: {e}")
            return False

    def update_flip_entry(self, flip_id: str, updates: dict) -> bool:
        """Update existing flip entry"""
        try:
            logger.info(f"📝 Updating flip entry: {flip_id}")
            
            # Find the page first (in demo mode, we'll simulate this)
            if self.demo_mode:
                page_id = f"demo-page-{flip_id}"
            else:
                # In real mode, you'd query the database to find the page
                page_id = self._find_flip_page(flip_id)
                if not page_id:
                    logger.error(f"❌ Flip page not found: {flip_id}")
                    return False
            
            # Prepare update properties
            properties = {}
            for key, value in updates.items():
                if key == 'status':
                    properties['Status'] = {'select': {'name': value}}
                elif key == 'exit_price':
                    properties['Exit Price'] = {'number': value}
                elif key == 'exit_time':
                    properties['Exit Time'] = {'date': {'start': value.isoformat()}}
                elif key == 'pnl':
                    properties['PnL'] = {'number': value}
                elif key == 'pnl_percent':
                    properties['PnL %'] = {'number': value}
                elif key == 'notes':
                    properties['Notes'] = {'rich_text': [{'text': {'content': value}}]}
            
            data = {'properties': properties}
            response = self._make_request('PATCH', f'pages/{page_id}', data)
            
            if 'error' in response:
                logger.error(f"❌ Failed to update flip entry: {response['error']}")
                return False
            
            logger.info(f"✅ Flip entry updated: {flip_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error updating flip entry: {e}")
            return False

    def _find_flip_page(self, flip_id: str) -> Optional[str]:
        """Find Notion page ID for a flip"""
        try:
            query_data = {
                'filter': {
                    'property': 'Flip ID',
                    'title': {'equals': flip_id}
                }
            }
            
            response = self._make_request('POST', f'databases/{self.database_ids["flip_tracker"]}/query', query_data)
            
            if response.get('results'):
                return response['results'][0]['id']
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error finding flip page: {e}")
            return None

    def create_vault_operation(self, operation: VaultOperation) -> bool:
        """Create vault operation entry"""
        try:
            logger.info(f"🏦 Creating vault operation: {operation.operation_id}")
            
            properties = {
                'Operation ID': {
                    'title': [{'text': {'content': operation.operation_id}}]
                },
                'Type': {
                    'select': {'name': operation.operation_type.value}
                },
                'Amount': {
                    'number': operation.amount
                },
                'Ray Score': {
                    'number': operation.ray_score
                },
                'Confidence': {
                    'number': operation.confidence
                },
                'Timestamp': {
                    'date': {'start': operation.timestamp.isoformat()}
                },
                'Signature': {
                    'rich_text': [{'text': {'content': operation.signature}}]
                },
                'Status': {
                    'select': {'name': operation.status}
                }
            }
            
            if operation.source_flip:
                properties['Source Flip'] = {
                    'rich_text': [{'text': {'content': operation.source_flip}}]
                }
            
            data = {
                'parent': {'database_id': self.database_ids['vault_operations']},
                'properties': properties
            }
            
            response = self._make_request('POST', 'pages', data)
            
            if 'error' in response:
                logger.error(f"❌ Failed to create vault operation: {response['error']}")
                return False
            
            logger.info(f"✅ Vault operation created: {operation.operation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating vault operation: {e}")
            return False

    def create_ray_rules_assessment(self, assessment: RayRulesAssessment) -> bool:
        """Create Ray Rules assessment entry"""
        try:
            logger.info(f"🧠 Creating Ray Rules assessment: {assessment.flip_id}")
            
            properties = {
                'Flip ID': {
                    'title': [{'text': {'content': assessment.flip_id}}]
                },
                'Rule 1 - Clarity': {
                    'number': assessment.rule_1_score
                },
                'Rule 2 - Risk': {
                    'number': assessment.rule_2_score
                },
                'Rule 3 - Values': {
                    'number': assessment.rule_3_score
                },
                'Rule 4 - Emotion': {
                    'number': assessment.rule_4_score
                },
                'Rule 5 - Regret Test': {
                    'number': assessment.rule_5_score
                },
                'Overall Clarity': {
                    'number': assessment.overall_clarity
                },
                'Recommendation': {
                    'select': {'name': assessment.recommendation}
                },
                'Timestamp': {
                    'date': {'start': assessment.timestamp.isoformat()}
                }
            }
            
            data = {
                'parent': {'database_id': self.database_ids['ray_rules']},
                'properties': properties
            }
            
            response = self._make_request('POST', 'pages', data)
            
            if 'error' in response:
                logger.error(f"❌ Failed to create Ray Rules assessment: {response['error']}")
                return False
            
            logger.info(f"✅ Ray Rules assessment created: {assessment.flip_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating Ray Rules assessment: {e}")
            return False

    def sync_omega_sigil_data(self, omega_data: dict) -> bool:
        """Sync ΩSIGIL intelligence data to Notion"""
        try:
            logger.info("🧠 Syncing ΩSIGIL data to Notion")
            
            properties = {
                'Timestamp': {
                    'title': [{'text': {'content': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}}]
                },
                'Ray Score': {
                    'number': omega_data.get('ray_score', 0)
                },
                'MENACE Accuracy': {
                    'number': omega_data.get('menace_accuracy', 0)
                },
                'Win Rate': {
                    'number': omega_data.get('win_rate', 0)
                },
                'Total Trades': {
                    'number': omega_data.get('total_trades', 0)
                },
                'Total ROI': {
                    'number': omega_data.get('total_roi', 0)
                },
                'Sharpe Ratio': {
                    'number': omega_data.get('sharpe_ratio', 0)
                },
                'System Status': {
                    'select': {'name': omega_data.get('system_status', 'Unknown')}
                }
            }
            
            data = {
                'parent': {'database_id': self.database_ids['omega_sigil']},
                'properties': properties
            }
            
            response = self._make_request('POST', 'pages', data)
            
            if 'error' in response:
                logger.error(f"❌ Failed to sync ΩSIGIL data: {response['error']}")
                return False
            
            logger.info("✅ ΩSIGIL data synced to Notion")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error syncing ΩSIGIL data: {e}")
            return False

    def get_active_flips(self) -> List[dict]:
        """Get active flips from Notion"""
        try:
            query_data = {
                'filter': {
                    'property': 'Status',
                    'select': {'equals': 'Active'}
                }
            }
            
            response = self._make_request('POST', f'databases/{self.database_ids["flip_tracker"]}/query', query_data)
            
            if 'error' in response:
                logger.error(f"❌ Failed to get active flips: {response['error']}")
                return []
            
            active_flips = []
            for result in response.get('results', []):
                flip_data = self._extract_flip_data(result)
                if flip_data:
                    active_flips.append(flip_data)
            
            logger.info(f"📊 Retrieved {len(active_flips)} active flips")
            return active_flips
            
        except Exception as e:
            logger.error(f"❌ Error getting active flips: {e}")
            return []

    def _extract_flip_data(self, notion_page: dict) -> Optional[dict]:
        """Extract flip data from Notion page"""
        try:
            properties = notion_page.get('properties', {})
            
            flip_data = {
                'flip_id': self._get_property_value(properties, 'Flip ID', 'title'),
                'symbol': self._get_property_value(properties, 'Symbol', 'rich_text'),
                'entry_price': self._get_property_value(properties, 'Entry Price', 'number'),
                'target_price': self._get_property_value(properties, 'Target Price', 'number'),
                'stop_loss': self._get_property_value(properties, 'Stop Loss', 'number'),
                'quantity': self._get_property_value(properties, 'Quantity', 'number'),
                'ray_score': self._get_property_value(properties, 'Ray Score', 'number'),
                'status': self._get_property_value(properties, 'Status', 'select')
            }
            
            return flip_data
            
        except Exception as e:
            logger.error(f"❌ Error extracting flip data: {e}")
            return None

    def _get_property_value(self, properties: dict, prop_name: str, prop_type: str):
        """Extract property value from Notion properties"""
        try:
            prop = properties.get(prop_name, {})
            
            if prop_type == 'title':
                return prop.get('title', [{}])[0].get('text', {}).get('content', '')
            elif prop_type == 'rich_text':
                return prop.get('rich_text', [{}])[0].get('text', {}).get('content', '')
            elif prop_type == 'number':
                return prop.get('number', 0)
            elif prop_type == 'select':
                return prop.get('select', {}).get('name', '')
            elif prop_type == 'date':
                return prop.get('date', {}).get('start', '')
            
            return None
            
        except Exception:
            return None

    def process_flip_completion(self, flip_id: str, exit_price: float, pnl: float) -> bool:
        """Process flip completion and trigger vault signals"""
        try:
            logger.info(f"🎯 Processing flip completion: {flip_id}")
            
            # Update flip entry
            updates = {
                'status': FlipStatus.COMPLETED.value,
                'exit_price': exit_price,
                'exit_time': datetime.now(),
                'pnl': pnl,
                'pnl_percent': (pnl / (exit_price * 1000)) * 100  # Assuming 1000 quantity for demo
            }
            
            flip_updated = self.update_flip_entry(flip_id, updates)
            
            # Generate vault signal if profitable
            if pnl > 0 and pnl > 100:  # Minimum $100 profit for vault injection
                vault_operation = VaultOperation(
                    operation_id=f"VAULT_{flip_id}_{int(time.time())}",
                    operation_type=VaultSignal.INJECT,
                    amount=pnl * 0.3,  # 30% of profit to vault
                    source_flip=flip_id,
                    ray_score=0.85,  # High confidence for profitable flip
                    confidence=0.9,
                    timestamp=datetime.now(),
                    signature=f"AUTO_VAULT_{flip_id}"
                )
                
                vault_created = self.create_vault_operation(vault_operation)
                
                logger.info(f"💰 Vault injection triggered: ${vault_operation.amount:.2f}")
                return flip_updated and vault_created
            
            return flip_updated
            
        except Exception as e:
            logger.error(f"❌ Error processing flip completion: {e}")
            return False

def main():
    """Main Notion bridge demonstration"""
    print("🔗 NOTION BRIDGE INTEGRATION - PHASE 4")
    print("=" * 60)
    
    # Initialize Notion bridge
    bridge = NotionBridge()
    
    # Demo flip entry
    demo_flip = FlipEntry(
        flip_id="FLIP_WIF_20250804_001",
        symbol="WIF",
        entry_price=0.92,
        target_price=1.20,
        stop_loss=0.85,
        quantity=1000,
        ray_score=0.907,
        clarity_score=85,
        frhi_score=0.35,
        status=FlipStatus.ACTIVE,
        entry_time=datetime.now(),
        notes="ΩSIGIL high confidence signal"
    )
    
    print(f"\n📝 Creating demo flip entry...")
    flip_created = bridge.create_flip_entry(demo_flip)
    print(f"✅ Flip entry created: {flip_created}")
    
    # Demo vault operation
    demo_vault = VaultOperation(
        operation_id="VAULT_INJECT_001",
        operation_type=VaultSignal.INJECT,
        amount=500.0,
        source_flip="FLIP_WIF_20250804_001",
        ray_score=0.907,
        confidence=0.9,
        timestamp=datetime.now(),
        signature="0xcfe27072...40b0"
    )
    
    print(f"\n🏦 Creating demo vault operation...")
    vault_created = bridge.create_vault_operation(demo_vault)
    print(f"✅ Vault operation created: {vault_created}")
    
    # Demo Ray Rules assessment
    demo_ray_rules = RayRulesAssessment(
        flip_id="FLIP_WIF_20250804_001",
        rule_1_score=90,  # Clarity of purpose
        rule_2_score=85,  # Risk assessment
        rule_3_score=88,  # Value alignment
        rule_4_score=82,  # Emotional state
        rule_5_score=87,  # 10-year regret test
        overall_clarity=86.4,
        recommendation="PROCEED",
        timestamp=datetime.now()
    )
    
    print(f"\n🧠 Creating Ray Rules assessment...")
    ray_created = bridge.create_ray_rules_assessment(demo_ray_rules)
    print(f"✅ Ray Rules assessment created: {ray_created}")
    
    # Demo ΩSIGIL sync
    omega_data = {
        'ray_score': 0.907,
        'menace_accuracy': 87.2,
        'win_rate': 68.0,
        'total_trades': 1748,
        'total_roi': 15.0,
        'sharpe_ratio': 1.80,
        'system_status': 'OPERATIONAL'
    }
    
    print(f"\n🧠 Syncing ΩSIGIL data...")
    omega_synced = bridge.sync_omega_sigil_data(omega_data)
    print(f"✅ ΩSIGIL data synced: {omega_synced}")
    
    print("\n🔗 NOTION BRIDGE INTEGRATION STATUS: OPERATIONAL")
    print("Ready for Docker Container Packaging...")

if __name__ == "__main__":
    main()


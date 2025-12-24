import os
import json
import yaml
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

@dataclass
class ExchangeCredentials:
    """Exchange API credentials"""
    api_key: str
    api_secret: str
    passphrase: Optional[str] = None
    is_testnet: bool = True
    is_paper_trading: bool = True

@dataclass
class RiskConfig:
    """Risk management configuration"""
    max_daily_loss: float = 1000.0
    max_daily_trades: int = 10
    max_concurrent_positions: int = 5
    max_position_size: float = 500.0
    position_size_percentage: float = 2.0
    min_ray_score: float = 60.0
    ray_exit_threshold: float = 40.0
    min_risk_reward_ratio: float = 1.5
    max_risk_percentage: float = 2.0
    vault_siphon_enabled: bool = True
    vault_siphon_percentage: float = 30.0
    vault_siphon_threshold: float = 100.0
    emergency_stop: bool = False
    max_drawdown_percentage: float = 10.0

@dataclass
class VPNConfig:
    """VPN configuration"""
    enabled: bool = False
    provider: str = "custom"
    endpoints: list = None
    fallback_enabled: bool = True
    auto_rotate: bool = True
    test_interval: int = 300  # seconds

@dataclass
class SystemConfig:
    """System-wide configuration"""
    environment: str = "development"  # development, staging, production
    debug: bool = True
    log_level: str = "INFO"
    database_url: str = "sqlite:///database/app.db"
    secret_key: str = "default-secret-key"
    
    # Trading settings
    default_exchange: str = "binance_us"
    paper_trading_balance: float = 10000.0
    
    # API settings
    webhook_secret: Optional[str] = None
    rate_limit_per_minute: int = 60
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090

class ConfigManager:
    """Configuration management with encryption support"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "config.yaml")
        self.secrets_file = os.path.join(config_dir, "secrets.enc")
        self.env_file = os.path.join(config_dir, ".env")
        
        # Encryption key for sensitive data
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
        # Configuration cache
        self._config_cache = {}
        self._secrets_cache = {}
        
        # Ensure config directory exists
        os.makedirs(config_dir, exist_ok=True)
        
        # Load configurations
        self._load_configurations()
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for secrets"""
        key_file = os.path.join(self.config_dir, "encryption.key")
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            logger.info("Generated new encryption key for secrets")
            return key
    
    def _load_configurations(self):
        """Load all configuration files"""
        # Load environment variables
        self._load_env_file()
        
        # Load main configuration
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self._config_cache = yaml.safe_load(f) or {}
        else:
            self._config_cache = self._create_default_config()
            self.save_config(self._config_cache)
        
        # Load encrypted secrets
        if os.path.exists(self.secrets_file):
            try:
                with open(self.secrets_file, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.cipher.decrypt(encrypted_data)
                self._secrets_cache = json.loads(decrypted_data.decode())
            except Exception as e:
                logger.error(f"Failed to load secrets: {e}")
                self._secrets_cache = {}
        else:
            self._secrets_cache = {}
    
    def _load_env_file(self):
        """Load environment variables from .env file"""
        if os.path.exists(self.env_file):
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key] = value
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        system_config = SystemConfig()
        risk_config = RiskConfig()
        vpn_config = VPNConfig()
        
        return {
            'system': asdict(system_config),
            'risk': asdict(risk_config),
            'vpn': asdict(vpn_config),
            'exchanges': {
                'binance_us': {
                    'enabled': True,
                    'is_testnet': True,
                    'is_paper_trading': True,
                    'default_order_type': 'limit',
                    'max_slippage': 0.5
                },
                'kucoin': {
                    'enabled': False,
                    'is_testnet': True,
                    'is_paper_trading': True,
                    'default_order_type': 'limit',
                    'max_slippage': 0.5
                },
                'bybit': {
                    'enabled': False,
                    'is_testnet': True,
                    'is_paper_trading': True,
                    'default_order_type': 'limit',
                    'max_slippage': 0.5
                }
            },
            'ray_rules': {
                'enabled': True,
                'rules': [
                    {
                        'id': 1,
                        'name': 'Signal Quality',
                        'weight': 20,
                        'description': 'Complete signal data with TP/SL levels'
                    },
                    {
                        'id': 2,
                        'name': 'Risk/Reward Ratio',
                        'weight': 25,
                        'description': 'Minimum 1.5:1 risk/reward ratio'
                    },
                    {
                        'id': 3,
                        'name': 'Market Conditions',
                        'weight': 15,
                        'description': 'Favorable market conditions'
                    },
                    {
                        'id': 4,
                        'name': 'Position Size',
                        'weight': 15,
                        'description': 'Appropriate position sizing'
                    },
                    {
                        'id': 5,
                        'name': 'Long-term Alignment',
                        'weight': 25,
                        'description': 'No regret in 10 years test'
                    }
                ]
            }
        }
    
    def get_config(self, key: str = None) -> Any:
        """Get configuration value"""
        if key is None:
            return self._config_cache
        
        keys = key.split('.')
        value = self._config_cache
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def set_config(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self._config_cache
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to file"""
        if config is not None:
            self._config_cache = config
        
        with open(self.config_file, 'w') as f:
            yaml.dump(self._config_cache, f, default_flow_style=False)
        
        logger.info("Configuration saved")
    
    def get_secret(self, key: str) -> Optional[str]:
        """Get encrypted secret"""
        return self._secrets_cache.get(key)
    
    def set_secret(self, key: str, value: str):
        """Set encrypted secret"""
        self._secrets_cache[key] = value
        self._save_secrets()
    
    def _save_secrets(self):
        """Save encrypted secrets to file"""
        data = json.dumps(self._secrets_cache).encode()
        encrypted_data = self.cipher.encrypt(data)
        
        with open(self.secrets_file, 'wb') as f:
            f.write(encrypted_data)
        
        logger.info("Secrets saved")
    
    def get_exchange_credentials(self, exchange_name: str) -> Optional[ExchangeCredentials]:
        """Get exchange credentials"""
        api_key = self.get_secret(f"{exchange_name}_api_key")
        api_secret = self.get_secret(f"{exchange_name}_api_secret")
        passphrase = self.get_secret(f"{exchange_name}_passphrase")
        
        if not api_key or not api_secret:
            return None
        
        exchange_config = self.get_config(f"exchanges.{exchange_name}")
        
        return ExchangeCredentials(
            api_key=api_key,
            api_secret=api_secret,
            passphrase=passphrase,
            is_testnet=exchange_config.get('is_testnet', True),
            is_paper_trading=exchange_config.get('is_paper_trading', True)
        )
    
    def set_exchange_credentials(self, exchange_name: str, credentials: ExchangeCredentials):
        """Set exchange credentials"""
        self.set_secret(f"{exchange_name}_api_key", credentials.api_key)
        self.set_secret(f"{exchange_name}_api_secret", credentials.api_secret)
        
        if credentials.passphrase:
            self.set_secret(f"{exchange_name}_passphrase", credentials.passphrase)
        
        # Update exchange configuration
        self.set_config(f"exchanges.{exchange_name}.is_testnet", credentials.is_testnet)
        self.set_config(f"exchanges.{exchange_name}.is_paper_trading", credentials.is_paper_trading)
        self.save_config()
    
    def get_risk_config(self) -> RiskConfig:
        """Get risk management configuration"""
        risk_data = self.get_config('risk') or {}
        return RiskConfig(**risk_data)
    
    def get_vpn_config(self) -> VPNConfig:
        """Get VPN configuration"""
        vpn_data = self.get_config('vpn') or {}
        return VPNConfig(**vpn_data)
    
    def get_system_config(self) -> SystemConfig:
        """Get system configuration"""
        system_data = self.get_config('system') or {}
        return SystemConfig(**system_data)
    
    def create_env_template(self):
        """Create .env template file"""
        template = """# Ladder Sniper Engine Environment Configuration
# Copy this file to .env and fill in your values

# System Settings
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///database/app.db

# Webhook Settings
WEBHOOK_SECRET=your-webhook-secret

# Exchange API Keys (will be encrypted and stored separately)
# BINANCE_US_API_KEY=your-binance-api-key
# BINANCE_US_API_SECRET=your-binance-api-secret
# KUCOIN_API_KEY=your-kucoin-api-key
# KUCOIN_API_SECRET=your-kucoin-api-secret
# KUCOIN_PASSPHRASE=your-kucoin-passphrase
# BYBIT_API_KEY=your-bybit-api-key
# BYBIT_API_SECRET=your-bybit-api-secret

# VPN Settings
VPN_ENABLED=false
VPN_PROVIDER=custom

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
"""
        
        template_file = os.path.join(self.config_dir, ".env.template")
        with open(template_file, 'w') as f:
            f.write(template)
        
        logger.info(f"Created .env template at {template_file}")

# Global configuration manager instance
config_manager = ConfigManager()


import requests
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class VPNEndpoint:
    """VPN endpoint configuration"""
    name: str
    host: str
    port: int
    protocol: str  # http, https, socks5
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: bool = True
    latency_ms: Optional[float] = None
    last_tested: Optional[float] = None

class VPNRouter:
    """VPN routing manager for exchange connections"""
    
    def __init__(self):
        self.endpoints: List[VPNEndpoint] = []
        self.current_endpoint: Optional[VPNEndpoint] = None
        self.fallback_enabled = True
        self.test_timeout = 5.0
        
    def add_endpoint(self, endpoint: VPNEndpoint):
        """Add a VPN endpoint"""
        self.endpoints.append(endpoint)
        logger.info(f"Added VPN endpoint: {endpoint.name}")
    
    def add_endpoints_from_config(self, config: Dict[str, Any]):
        """Add VPN endpoints from configuration"""
        vpn_configs = config.get('vpn_endpoints', [])
        
        for vpn_config in vpn_configs:
            endpoint = VPNEndpoint(
                name=vpn_config.get('name', 'Unknown'),
                host=vpn_config.get('host'),
                port=vpn_config.get('port', 8080),
                protocol=vpn_config.get('protocol', 'http'),
                username=vpn_config.get('username'),
                password=vpn_config.get('password'),
                is_active=vpn_config.get('is_active', True)
            )
            self.add_endpoint(endpoint)
    
    async def test_endpoint(self, endpoint: VPNEndpoint) -> bool:
        """Test VPN endpoint connectivity"""
        try:
            start_time = time.time()
            
            # Create proxy configuration
            proxy_url = self._build_proxy_url(endpoint)
            proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            
            # Test with a simple HTTP request
            test_url = "https://httpbin.org/ip"
            response = requests.get(
                test_url,
                proxies=proxies,
                timeout=self.test_timeout
            )
            
            if response.status_code == 200:
                endpoint.latency_ms = (time.time() - start_time) * 1000
                endpoint.last_tested = time.time()
                logger.info(f"VPN endpoint {endpoint.name} test successful - {endpoint.latency_ms:.1f}ms")
                return True
            else:
                logger.warning(f"VPN endpoint {endpoint.name} test failed - HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"VPN endpoint {endpoint.name} test failed: {e}")
            return False
    
    def _build_proxy_url(self, endpoint: VPNEndpoint) -> str:
        """Build proxy URL from endpoint configuration"""
        if endpoint.username and endpoint.password:
            auth = f"{endpoint.username}:{endpoint.password}@"
        else:
            auth = ""
        
        return f"{endpoint.protocol}://{auth}{endpoint.host}:{endpoint.port}"
    
    async def find_best_endpoint(self) -> Optional[VPNEndpoint]:
        """Find the best available VPN endpoint"""
        if not self.endpoints:
            logger.warning("No VPN endpoints configured")
            return None
        
        active_endpoints = [ep for ep in self.endpoints if ep.is_active]
        if not active_endpoints:
            logger.warning("No active VPN endpoints available")
            return None
        
        # Test all endpoints
        working_endpoints = []
        for endpoint in active_endpoints:
            if await self.test_endpoint(endpoint):
                working_endpoints.append(endpoint)
        
        if not working_endpoints:
            logger.error("No working VPN endpoints found")
            return None
        
        # Sort by latency (lowest first)
        working_endpoints.sort(key=lambda ep: ep.latency_ms or float('inf'))
        best_endpoint = working_endpoints[0]
        
        logger.info(f"Selected best VPN endpoint: {best_endpoint.name} ({best_endpoint.latency_ms:.1f}ms)")
        return best_endpoint
    
    async def get_proxy_config(self, force_refresh: bool = False) -> Optional[Dict[str, str]]:
        """Get proxy configuration for requests"""
        if not self.current_endpoint or force_refresh:
            self.current_endpoint = await self.find_best_endpoint()
        
        if not self.current_endpoint:
            if self.fallback_enabled:
                logger.warning("No VPN available, using direct connection")
                return None
            else:
                raise Exception("No VPN endpoints available and fallback disabled")
        
        proxy_url = self._build_proxy_url(self.current_endpoint)
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    async def rotate_endpoint(self):
        """Rotate to next available endpoint"""
        if not self.endpoints:
            return
        
        current_index = -1
        if self.current_endpoint:
            try:
                current_index = self.endpoints.index(self.current_endpoint)
            except ValueError:
                pass
        
        # Try next endpoints
        for i in range(len(self.endpoints)):
            next_index = (current_index + 1 + i) % len(self.endpoints)
            next_endpoint = self.endpoints[next_index]
            
            if next_endpoint.is_active and await self.test_endpoint(next_endpoint):
                self.current_endpoint = next_endpoint
                logger.info(f"Rotated to VPN endpoint: {next_endpoint.name}")
                return
        
        logger.error("No working VPN endpoints found during rotation")
        self.current_endpoint = None
    
    def get_status(self) -> Dict[str, Any]:
        """Get VPN router status"""
        return {
            'total_endpoints': len(self.endpoints),
            'active_endpoints': len([ep for ep in self.endpoints if ep.is_active]),
            'current_endpoint': self.current_endpoint.name if self.current_endpoint else None,
            'fallback_enabled': self.fallback_enabled,
            'endpoints': [
                {
                    'name': ep.name,
                    'host': ep.host,
                    'port': ep.port,
                    'is_active': ep.is_active,
                    'latency_ms': ep.latency_ms,
                    'last_tested': ep.last_tested
                }
                for ep in self.endpoints
            ]
        }

# Global VPN router instance
vpn_router = VPNRouter()

# Default VPN configurations for common providers
DEFAULT_VPN_CONFIGS = {
    'nordvpn': [
        {
            'name': 'NordVPN-US1',
            'host': 'us1.nordvpn.com',
            'port': 1080,
            'protocol': 'socks5'
        },
        {
            'name': 'NordVPN-US2',
            'host': 'us2.nordvpn.com',
            'port': 1080,
            'protocol': 'socks5'
        }
    ],
    'expressvpn': [
        {
            'name': 'ExpressVPN-US',
            'host': 'us.expressvpn.com',
            'port': 1080,
            'protocol': 'socks5'
        }
    ],
    'surfshark': [
        {
            'name': 'Surfshark-US',
            'host': 'us.surfshark.com',
            'port': 1080,
            'protocol': 'socks5'
        }
    ]
}


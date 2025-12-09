#!/usr/bin/env python3
"""
LLF-ß Signature Replay Protection System
Module 5: Audit & Security Tools

This module provides comprehensive signature replay protection, nonce management,
and temporal signature binding for the LLF-ß sovereign banking system.

Author: Manus AI
Version: 1.0.0
Classification: Quantum Defense Grade
"""

import json
import hashlib
import datetime
import secrets
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import threading
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SignatureRecord:
    """Record of a cryptographic signature"""
    signature_id: str
    nonce: str
    timestamp: str
    operation_type: str
    signature_hash: str
    public_key_hash: str
    used: bool
    validity_window: int  # seconds
    metadata: Dict[str, Any]

@dataclass
class ReplayDetectionResult:
    """Result of replay detection analysis"""
    signature_id: str
    status: str  # VALID, REPLAY_DETECTED, EXPIRED, INVALID
    detection_timestamp: str
    threat_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    details: Dict[str, Any]
    recommendations: List[str]

class SignatureReplayProtection:
    """
    Comprehensive signature replay protection system
    
    Provides nonce management, temporal signature binding, and replay attack detection
    for all cryptographic operations in the LLF-ß system.
    """
    
    def __init__(self, config_path: str = "replay_protection_config.json"):
        """Initialize replay protection system"""
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # Initialize signature database
        self.signature_db_path = Path("signature_database.json")
        self.signature_db = self._load_signature_database()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Nonce tracking
        self.used_nonces: Set[str] = set()
        self._load_used_nonces()
        
        # Cleanup scheduler
        self._last_cleanup = datetime.datetime.now()
        
        logger.info("Signature Replay Protection System initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load replay protection configuration"""
        default_config = {
            "nonce_length": 32,  # bytes
            "default_validity_window": 300,  # 5 minutes
            "operation_validity_windows": {
                "high_value_transfer": 60,
                "vault_operation": 120,
                "routine_operation": 300,
                "emergency_operation": 30
            },
            "max_signature_age": 86400,  # 24 hours
            "cleanup_interval": 3600,  # 1 hour
            "ntp_tolerance": 30,  # 30 seconds
            "replay_detection_sensitivity": "HIGH",
            "threat_escalation": {
                "replay_attempts_threshold": 3,
                "suspicious_pattern_threshold": 5,
                "lockdown_threshold": 10
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.warning(f"Failed to load config: {e}. Using defaults.")
                return default_config
        else:
            # Create default config
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def _load_signature_database(self) -> Dict[str, SignatureRecord]:
        """Load signature database from storage"""
        if self.signature_db_path.exists():
            try:
                with open(self.signature_db_path, 'r') as f:
                    data = json.load(f)
                    # Convert to SignatureRecord objects
                    db = {}
                    for sig_id, record_data in data.get("signatures", {}).items():
                        db[sig_id] = SignatureRecord(**record_data)
                    return db
            except Exception as e:
                logger.error(f"Failed to load signature database: {e}")
                return {}
        return {}
    
    def _save_signature_database(self):
        """Save signature database to storage"""
        try:
            data = {
                "version": "1.0.0",
                "last_updated": datetime.datetime.now().isoformat(),
                "signatures": {
                    sig_id: asdict(record) 
                    for sig_id, record in self.signature_db.items()
                }
            }
            
            with open(self.signature_db_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save signature database: {e}")
    
    def _load_used_nonces(self):
        """Load used nonces from signature database"""
        for record in self.signature_db.values():
            if record.used:
                self.used_nonces.add(record.nonce)
    
    def generate_nonce(self) -> str:
        """
        Generate cryptographically secure nonce
        
        Returns:
            str: Unique nonce for signature operations
        """
        while True:
            # Generate random nonce
            nonce_bytes = secrets.token_bytes(self.config["nonce_length"])
            nonce = nonce_bytes.hex()
            
            # Ensure uniqueness
            if nonce not in self.used_nonces:
                return nonce
    
    def create_signature_record(self, operation_type: str, signature_hash: str, 
                              public_key_hash: str, metadata: Dict[str, Any] = None) -> SignatureRecord:
        """
        Create a new signature record with replay protection
        
        Args:
            operation_type: Type of operation being signed
            signature_hash: Hash of the cryptographic signature
            public_key_hash: Hash of the public key used
            metadata: Additional metadata for the operation
            
        Returns:
            SignatureRecord: New signature record with nonce and timestamp
        """
        with self._lock:
            # Generate unique nonce
            nonce = self.generate_nonce()
            self.used_nonces.add(nonce)
            
            # Create signature ID
            signature_id = f"SIG_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{nonce[:8]}"
            
            # Determine validity window
            validity_window = self.config["operation_validity_windows"].get(
                operation_type, 
                self.config["default_validity_window"]
            )
            
            # Create record
            record = SignatureRecord(
                signature_id=signature_id,
                nonce=nonce,
                timestamp=datetime.datetime.now().isoformat(),
                operation_type=operation_type,
                signature_hash=signature_hash,
                public_key_hash=public_key_hash,
                used=False,
                validity_window=validity_window,
                metadata=metadata or {}
            )
            
            # Store in database
            self.signature_db[signature_id] = record
            self._save_signature_database()
            
            logger.info(f"Created signature record: {signature_id}")
            return record
    
    def validate_signature_request(self, signature_id: str, signature_hash: str, 
                                 operation_context: Dict[str, Any] = None) -> ReplayDetectionResult:
        """
        Validate a signature request for replay attacks
        
        Args:
            signature_id: ID of the signature to validate
            signature_hash: Hash of the signature being validated
            operation_context: Context information for the operation
            
        Returns:
            ReplayDetectionResult: Validation result with threat assessment
        """
        detection_timestamp = datetime.datetime.now().isoformat()
        
        # Check if signature exists
        if signature_id not in self.signature_db:
            return ReplayDetectionResult(
                signature_id=signature_id,
                status="INVALID",
                detection_timestamp=detection_timestamp,
                threat_level="HIGH",
                details={"error": "Signature ID not found in database"},
                recommendations=["Investigate unauthorized signature", "Check signature generation process"]
            )
        
        record = self.signature_db[signature_id]
        
        # Check if already used
        if record.used:
            return ReplayDetectionResult(
                signature_id=signature_id,
                status="REPLAY_DETECTED",
                detection_timestamp=detection_timestamp,
                threat_level="CRITICAL",
                details={
                    "original_timestamp": record.timestamp,
                    "operation_type": record.operation_type,
                    "replay_attempt": True
                },
                recommendations=[
                    "IMMEDIATE: Block operation and alert security team",
                    "Investigate potential security breach",
                    "Review access controls and authentication"
                ]
            )
        
        # Check signature hash match
        if record.signature_hash != signature_hash:
            return ReplayDetectionResult(
                signature_id=signature_id,
                status="INVALID",
                detection_timestamp=detection_timestamp,
                threat_level="HIGH",
                details={
                    "error": "Signature hash mismatch",
                    "expected": record.signature_hash,
                    "received": signature_hash
                },
                recommendations=["Investigate signature tampering", "Verify signature generation"]
            )
        
        # Check temporal validity
        record_time = datetime.datetime.fromisoformat(record.timestamp)
        current_time = datetime.datetime.now()
        age_seconds = (current_time - record_time).total_seconds()
        
        if age_seconds > record.validity_window:
            return ReplayDetectionResult(
                signature_id=signature_id,
                status="EXPIRED",
                detection_timestamp=detection_timestamp,
                threat_level="MEDIUM",
                details={
                    "age_seconds": age_seconds,
                    "validity_window": record.validity_window,
                    "expired_by": age_seconds - record.validity_window
                },
                recommendations=["Generate new signature", "Check system time synchronization"]
            )
        
        # Check for suspicious patterns
        threat_level = self._assess_threat_level(record, operation_context)
        
        # Mark as used
        with self._lock:
            record.used = True
            self.signature_db[signature_id] = record
            self._save_signature_database()
        
        return ReplayDetectionResult(
            signature_id=signature_id,
            status="VALID",
            detection_timestamp=detection_timestamp,
            threat_level=threat_level,
            details={
                "operation_type": record.operation_type,
                "age_seconds": age_seconds,
                "validity_remaining": record.validity_window - age_seconds
            },
            recommendations=[] if threat_level == "LOW" else ["Monitor for additional suspicious activity"]
        )
    
    def _assess_threat_level(self, record: SignatureRecord, 
                           operation_context: Dict[str, Any] = None) -> str:
        """Assess threat level based on operation patterns"""
        threat_level = "LOW"
        
        # Check for rapid successive operations
        recent_operations = self._get_recent_operations(minutes=5)
        if len(recent_operations) > 10:
            threat_level = "MEDIUM"
        
        # Check for high-value operations
        if record.operation_type in ["high_value_transfer", "vault_operation"]:
            threat_level = "MEDIUM"
        
        # Check for emergency operations
        if record.operation_type == "emergency_operation":
            threat_level = "HIGH"
        
        # Check operation context for anomalies
        if operation_context:
            if operation_context.get("amount", 0) > 10000:  # High value threshold
                threat_level = "MEDIUM"
            
            if operation_context.get("unusual_time", False):
                threat_level = "MEDIUM"
        
        return threat_level
    
    def _get_recent_operations(self, minutes: int = 60) -> List[SignatureRecord]:
        """Get operations from the last N minutes"""
        cutoff_time = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
        
        recent = []
        for record in self.signature_db.values():
            record_time = datetime.datetime.fromisoformat(record.timestamp)
            if record_time > cutoff_time:
                recent.append(record)
        
        return recent
    
    def detect_replay_patterns(self) -> List[Dict[str, Any]]:
        """Detect patterns that might indicate replay attacks"""
        patterns = []
        
        # Group operations by type and time
        operations_by_hour = defaultdict(list)
        for record in self.signature_db.values():
            hour_key = record.timestamp[:13]  # YYYY-MM-DDTHH
            operations_by_hour[hour_key].append(record)
        
        # Look for unusual activity patterns
        for hour, operations in operations_by_hour.items():
            if len(operations) > 50:  # Threshold for suspicious activity
                patterns.append({
                    "type": "HIGH_VOLUME_HOUR",
                    "hour": hour,
                    "operation_count": len(operations),
                    "severity": "MEDIUM",
                    "description": f"Unusually high operation volume: {len(operations)} operations in hour {hour}"
                })
        
        # Look for repeated operation types
        operation_counts = defaultdict(int)
        for record in self.signature_db.values():
            operation_counts[record.operation_type] += 1
        
        for op_type, count in operation_counts.items():
            if count > 100:  # Threshold for repeated operations
                patterns.append({
                    "type": "REPEATED_OPERATION_TYPE",
                    "operation_type": op_type,
                    "count": count,
                    "severity": "LOW",
                    "description": f"High frequency of {op_type} operations: {count} total"
                })
        
        return patterns
    
    def cleanup_expired_signatures(self):
        """Clean up expired signatures from database"""
        if (datetime.datetime.now() - self._last_cleanup).total_seconds() < self.config["cleanup_interval"]:
            return  # Too soon for cleanup
        
        with self._lock:
            current_time = datetime.datetime.now()
            max_age = self.config["max_signature_age"]
            
            expired_signatures = []
            for sig_id, record in list(self.signature_db.items()):
                record_time = datetime.datetime.fromisoformat(record.timestamp)
                age_seconds = (current_time - record_time).total_seconds()
                
                if age_seconds > max_age:
                    expired_signatures.append(sig_id)
                    # Remove from used nonces if present
                    self.used_nonces.discard(record.nonce)
            
            # Remove expired signatures
            for sig_id in expired_signatures:
                del self.signature_db[sig_id]
            
            if expired_signatures:
                self._save_signature_database()
                logger.info(f"Cleaned up {len(expired_signatures)} expired signatures")
            
            self._last_cleanup = current_time
    
    def generate_security_report(self) -> str:
        """Generate comprehensive security report"""
        total_signatures = len(self.signature_db)
        used_signatures = len([r for r in self.signature_db.values() if r.used])
        recent_operations = self._get_recent_operations(24)  # Last 24 hours
        
        # Detect patterns
        patterns = self.detect_replay_patterns()
        
        report = f"""
SIGNATURE REPLAY PROTECTION SECURITY REPORT
==========================================

Report Generated: {datetime.datetime.now().isoformat()}

SIGNATURE STATISTICS:
--------------------
Total Signatures: {total_signatures}
Used Signatures: {used_signatures}
Unused Signatures: {total_signatures - used_signatures}
Operations (24h): {len(recent_operations)}

NONCE MANAGEMENT:
----------------
Active Nonces: {len(self.used_nonces)}
Nonce Length: {self.config['nonce_length']} bytes
Collision Risk: Negligible (2^{self.config['nonce_length'] * 8} space)

TEMPORAL PROTECTION:
-------------------
Default Validity: {self.config['default_validity_window']} seconds
NTP Tolerance: {self.config['ntp_tolerance']} seconds
Max Signature Age: {self.config['max_signature_age']} seconds

THREAT DETECTION:
----------------
"""
        
        if patterns:
            report += f"Patterns Detected: {len(patterns)}\n\n"
            for pattern in patterns:
                report += f"- [{pattern['severity']}] {pattern['description']}\n"
        else:
            report += "No suspicious patterns detected\n"
        
        report += f"""
OPERATION BREAKDOWN (24h):
-------------------------
"""
        
        # Count operations by type
        op_counts = defaultdict(int)
        for record in recent_operations:
            op_counts[record.operation_type] += 1
        
        for op_type, count in op_counts.items():
            report += f"{op_type}: {count}\n"
        
        report += f"""
RECOMMENDATIONS:
---------------
"""
        
        if total_signatures > 10000:
            report += "- Consider increasing cleanup frequency for large signature database\n"
        
        if len(recent_operations) > 1000:
            report += "- High operation volume detected - monitor for anomalies\n"
        
        if patterns:
            report += "- Investigate detected patterns for potential security issues\n"
        
        report += "- Regular security audits recommended\n"
        report += "- Monitor system time synchronization\n"
        
        return report
    
    def emergency_lockdown(self, reason: str):
        """Emergency lockdown of signature system"""
        logger.critical(f"EMERGENCY LOCKDOWN ACTIVATED: {reason}")
        
        # Mark all unused signatures as expired
        with self._lock:
            for record in self.signature_db.values():
                if not record.used:
                    record.used = True  # Effectively invalidates them
            
            self._save_signature_database()
        
        # Log security event
        security_event = {
            "event_type": "EMERGENCY_LOCKDOWN",
            "timestamp": datetime.datetime.now().isoformat(),
            "reason": reason,
            "signatures_invalidated": len([r for r in self.signature_db.values() if not r.used])
        }
        
        # Save security event
        events_file = Path("security_events.json")
        events = []
        if events_file.exists():
            try:
                with open(events_file, 'r') as f:
                    events = json.load(f)
            except:
                pass
        
        events.append(security_event)
        with open(events_file, 'w') as f:
            json.dump(events, f, indent=2)

def main():
    """Main execution function for replay protection testing"""
    rp = SignatureReplayProtection()
    
    # Generate test signature record
    test_record = rp.create_signature_record(
        operation_type="test_operation",
        signature_hash="test_signature_hash_123",
        public_key_hash="test_pubkey_hash_456",
        metadata={"test": True}
    )
    
    print(f"Created test signature: {test_record.signature_id}")
    
    # Test validation
    result = rp.validate_signature_request(
        test_record.signature_id,
        test_record.signature_hash
    )
    
    print(f"Validation result: {result.status} (Threat Level: {result.threat_level})")
    
    # Test replay detection
    replay_result = rp.validate_signature_request(
        test_record.signature_id,
        test_record.signature_hash
    )
    
    print(f"Replay test result: {replay_result.status}")
    
    # Generate security report
    report = rp.generate_security_report()
    print("\n" + report)

if __name__ == "__main__":
    main()


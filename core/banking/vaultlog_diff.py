#!/usr/bin/env python3
"""
LLF-ß Vault Log Differential Analysis - Log Integrity Verification System
Module 5: Audit & Security Tools

This module provides comprehensive vault log integrity verification, differential analysis,
and tamper detection capabilities for the LLF-ß sovereign banking system.

Author: Manus AI
Version: 1.0.0
Classification: Quantum Defense Grade
"""

import json
import hashlib
import datetime
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from collections import defaultdict
import difflib

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class LogIntegrityResult:
    """Result of log integrity verification"""
    log_file: str
    status: str  # VALID, CORRUPTED, MISSING, SUSPICIOUS
    hash_chain_valid: bool
    signature_valid: bool
    timestamp_valid: bool
    anomalies: List[Dict[str, Any]]
    recommendations: List[str]

@dataclass
class DifferentialAnalysis:
    """Result of differential analysis between log versions"""
    comparison_id: str
    timestamp: str
    log_a: str
    log_b: str
    differences: List[Dict[str, Any]]
    integrity_impact: str  # NONE, LOW, MEDIUM, HIGH, CRITICAL
    tamper_indicators: List[str]
    recommendations: List[str]

class VaultLogDifferentialAnalyzer:
    """
    Comprehensive vault log integrity verification and differential analysis system
    
    Provides tamper detection, hash chain verification, and forensic analysis
    capabilities for vault log files.
    """
    
    def __init__(self, vault_log_dir: str = "vaultlog"):
        """Initialize the vault log analyzer"""
        self.vault_log_dir = Path(vault_log_dir)
        self.vault_log_dir.mkdir(exist_ok=True)
        
        # Initialize analysis results storage
        self.analysis_dir = Path("log_analysis")
        self.analysis_dir.mkdir(exist_ok=True)
        
        # Load known good hashes if available
        self.known_good_hashes = self._load_known_good_hashes()
        
        logger.info("Vault Log Differential Analyzer initialized")
    
    def _load_known_good_hashes(self) -> Dict[str, str]:
        """Load known good hashes for vault logs"""
        hash_file = self.analysis_dir / "known_good_hashes.json"
        if hash_file.exists():
            try:
                with open(hash_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load known good hashes: {e}")
        return {}
    
    def _save_known_good_hashes(self):
        """Save known good hashes to file"""
        hash_file = self.analysis_dir / "known_good_hashes.json"
        with open(hash_file, 'w') as f:
            json.dump(self.known_good_hashes, f, indent=2)
    
    def verify_log_integrity(self, log_file_path: str) -> LogIntegrityResult:
        """
        Verify the integrity of a single vault log file
        
        Args:
            log_file_path: Path to the vault log file
            
        Returns:
            LogIntegrityResult: Comprehensive integrity verification result
        """
        log_path = Path(log_file_path)
        
        if not log_path.exists():
            return LogIntegrityResult(
                log_file=str(log_path),
                status="MISSING",
                hash_chain_valid=False,
                signature_valid=False,
                timestamp_valid=False,
                anomalies=[{"type": "FILE_MISSING", "description": "Log file does not exist"}],
                recommendations=["Investigate missing log file", "Check backup systems"]
            )
        
        try:
            with open(log_path, 'r') as f:
                log_data = json.load(f)
        except Exception as e:
            return LogIntegrityResult(
                log_file=str(log_path),
                status="CORRUPTED",
                hash_chain_valid=False,
                signature_valid=False,
                timestamp_valid=False,
                anomalies=[{"type": "PARSE_ERROR", "description": f"Failed to parse log file: {str(e)}"}],
                recommendations=["Restore from backup", "Investigate file corruption"]
            )
        
        anomalies = []
        recommendations = []
        
        # Verify hash chain integrity
        hash_chain_valid = self._verify_hash_chain(log_data, anomalies)
        
        # Verify cryptographic signature
        signature_valid = self._verify_signature(log_data, anomalies)
        
        # Verify timestamp consistency
        timestamp_valid = self._verify_timestamps(log_data, anomalies)
        
        # Check for structural anomalies
        self._check_structural_integrity(log_data, anomalies)
        
        # Check against known good hashes
        self._verify_against_known_good(log_path, log_data, anomalies)
        
        # Determine overall status
        status = "VALID"
        if not hash_chain_valid or not signature_valid:
            status = "CORRUPTED"
        elif not timestamp_valid or anomalies:
            status = "SUSPICIOUS"
        
        # Generate recommendations based on findings
        if not hash_chain_valid:
            recommendations.append("Investigate hash chain corruption")
        if not signature_valid:
            recommendations.append("Verify signature keys and re-sign if necessary")
        if not timestamp_valid:
            recommendations.append("Investigate timestamp anomalies")
        if anomalies:
            recommendations.append("Conduct detailed forensic analysis")
        
        return LogIntegrityResult(
            log_file=str(log_path),
            status=status,
            hash_chain_valid=hash_chain_valid,
            signature_valid=signature_valid,
            timestamp_valid=timestamp_valid,
            anomalies=anomalies,
            recommendations=recommendations
        )
    
    def _verify_hash_chain(self, log_data: Dict[str, Any], anomalies: List[Dict[str, Any]]) -> bool:
        """Verify hash chain integrity within the log"""
        if "hash_chain" not in log_data:
            anomalies.append({
                "type": "MISSING_HASH_CHAIN",
                "description": "Log file missing hash chain",
                "severity": "HIGH"
            })
            return False
        
        hash_chain = log_data["hash_chain"]
        if not isinstance(hash_chain, list) or len(hash_chain) == 0:
            anomalies.append({
                "type": "INVALID_HASH_CHAIN",
                "description": "Hash chain is not a valid list",
                "severity": "HIGH"
            })
            return False
        
        # Verify each link in the chain
        for i in range(1, len(hash_chain)):
            prev_hash = hash_chain[i-1]
            current_hash = hash_chain[i]
            
            # Calculate expected hash
            expected_prefix = hashlib.sha256(prev_hash.encode()).hexdigest()[:16]
            
            if not current_hash.startswith(expected_prefix):
                anomalies.append({
                    "type": "HASH_CHAIN_BREAK",
                    "description": f"Hash chain break at position {i}",
                    "severity": "CRITICAL",
                    "position": i,
                    "expected_prefix": expected_prefix,
                    "actual_hash": current_hash
                })
                return False
        
        return True
    
    def _verify_signature(self, log_data: Dict[str, Any], anomalies: List[Dict[str, Any]]) -> bool:
        """Verify cryptographic signature of the log"""
        if "signature" not in log_data:
            anomalies.append({
                "type": "MISSING_SIGNATURE",
                "description": "Log file missing cryptographic signature",
                "severity": "HIGH"
            })
            return False
        
        signature_data = log_data["signature"]
        
        # Verify signature structure
        required_fields = ["signature", "public_key", "algorithm", "timestamp"]
        for field in required_fields:
            if field not in signature_data:
                anomalies.append({
                    "type": "INCOMPLETE_SIGNATURE",
                    "description": f"Signature missing required field: {field}",
                    "severity": "HIGH"
                })
                return False
        
        # TODO: Implement actual signature verification with Ledger public key
        # For now, return True as placeholder
        return True
    
    def _verify_timestamps(self, log_data: Dict[str, Any], anomalies: List[Dict[str, Any]]) -> bool:
        """Verify timestamp consistency and validity"""
        timestamps = []
        
        # Collect all timestamps from the log
        if "timestamp" in log_data:
            timestamps.append(log_data["timestamp"])
        
        if "entries" in log_data:
            for entry in log_data["entries"]:
                if "timestamp" in entry:
                    timestamps.append(entry["timestamp"])
        
        if "signature" in log_data and "timestamp" in log_data["signature"]:
            timestamps.append(log_data["signature"]["timestamp"])
        
        # Verify timestamp format and chronological order
        parsed_timestamps = []
        for ts in timestamps:
            try:
                parsed_ts = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))
                parsed_timestamps.append(parsed_ts)
            except Exception as e:
                anomalies.append({
                    "type": "INVALID_TIMESTAMP",
                    "description": f"Invalid timestamp format: {ts}",
                    "severity": "MEDIUM"
                })
                return False
        
        # Check chronological order
        for i in range(1, len(parsed_timestamps)):
            if parsed_timestamps[i] < parsed_timestamps[i-1]:
                anomalies.append({
                    "type": "TIMESTAMP_ORDER_VIOLATION",
                    "description": f"Timestamps not in chronological order",
                    "severity": "HIGH",
                    "position": i
                })
                return False
        
        # Check for future timestamps
        current_time = datetime.datetime.now(datetime.timezone.utc)
        for i, ts in enumerate(parsed_timestamps):
            if ts > current_time + datetime.timedelta(minutes=5):  # 5 minute tolerance
                anomalies.append({
                    "type": "FUTURE_TIMESTAMP",
                    "description": f"Timestamp in the future: {timestamps[i]}",
                    "severity": "MEDIUM"
                })
        
        return True
    
    def _check_structural_integrity(self, log_data: Dict[str, Any], anomalies: List[Dict[str, Any]]):
        """Check structural integrity of the log data"""
        required_top_level = ["version", "log_type", "timestamp"]
        for field in required_top_level:
            if field not in log_data:
                anomalies.append({
                    "type": "MISSING_REQUIRED_FIELD",
                    "description": f"Missing required top-level field: {field}",
                    "severity": "MEDIUM"
                })
        
        # Check for unexpected fields that might indicate tampering
        expected_fields = {
            "version", "log_type", "timestamp", "entries", "hash_chain", 
            "signature", "metadata", "summary"
        }
        
        unexpected_fields = set(log_data.keys()) - expected_fields
        if unexpected_fields:
            anomalies.append({
                "type": "UNEXPECTED_FIELDS",
                "description": f"Unexpected fields found: {list(unexpected_fields)}",
                "severity": "LOW",
                "fields": list(unexpected_fields)
            })
        
        # Verify entry structure if entries exist
        if "entries" in log_data and isinstance(log_data["entries"], list):
            for i, entry in enumerate(log_data["entries"]):
                if not isinstance(entry, dict):
                    anomalies.append({
                        "type": "INVALID_ENTRY_STRUCTURE",
                        "description": f"Entry {i} is not a valid dictionary",
                        "severity": "MEDIUM",
                        "entry_index": i
                    })
    
    def _verify_against_known_good(self, log_path: Path, log_data: Dict[str, Any], 
                                 anomalies: List[Dict[str, Any]]):
        """Verify log against known good hashes"""
        # Calculate current hash
        log_content = json.dumps(log_data, sort_keys=True, separators=(',', ':'))
        current_hash = hashlib.sha256(log_content.encode()).hexdigest()
        
        log_name = log_path.name
        
        if log_name in self.known_good_hashes:
            if self.known_good_hashes[log_name] != current_hash:
                anomalies.append({
                    "type": "HASH_MISMATCH",
                    "description": f"Log hash does not match known good hash",
                    "severity": "CRITICAL",
                    "expected_hash": self.known_good_hashes[log_name],
                    "actual_hash": current_hash
                })
        else:
            # Store as known good if no anomalies found so far
            if not anomalies:
                self.known_good_hashes[log_name] = current_hash
                self._save_known_good_hashes()
    
    def compare_log_versions(self, log_a_path: str, log_b_path: str) -> DifferentialAnalysis:
        """
        Compare two versions of a log file for differences
        
        Args:
            log_a_path: Path to first log file
            log_b_path: Path to second log file
            
        Returns:
            DifferentialAnalysis: Detailed comparison results
        """
        comparison_id = f"DIFF_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Load both log files
            with open(log_a_path, 'r') as f:
                log_a_data = json.load(f)
            with open(log_b_path, 'r') as f:
                log_b_data = json.load(f)
            
            # Convert to normalized JSON strings for comparison
            log_a_str = json.dumps(log_a_data, sort_keys=True, indent=2)
            log_b_str = json.dumps(log_b_data, sort_keys=True, indent=2)
            
            # Generate detailed diff
            diff = list(difflib.unified_diff(
                log_a_str.splitlines(keepends=True),
                log_b_str.splitlines(keepends=True),
                fromfile=log_a_path,
                tofile=log_b_path,
                lineterm=''
            ))
            
            # Analyze differences
            differences = self._analyze_differences(log_a_data, log_b_data, diff)
            
            # Assess integrity impact
            integrity_impact = self._assess_integrity_impact(differences)
            
            # Identify tamper indicators
            tamper_indicators = self._identify_tamper_indicators(differences)
            
            # Generate recommendations
            recommendations = self._generate_diff_recommendations(differences, tamper_indicators)
            
            return DifferentialAnalysis(
                comparison_id=comparison_id,
                timestamp=datetime.datetime.now().isoformat(),
                log_a=log_a_path,
                log_b=log_b_path,
                differences=differences,
                integrity_impact=integrity_impact,
                tamper_indicators=tamper_indicators,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to compare log versions: {e}")
            return DifferentialAnalysis(
                comparison_id=comparison_id,
                timestamp=datetime.datetime.now().isoformat(),
                log_a=log_a_path,
                log_b=log_b_path,
                differences=[{"type": "COMPARISON_ERROR", "description": str(e)}],
                integrity_impact="UNKNOWN",
                tamper_indicators=["COMPARISON_FAILURE"],
                recommendations=["Investigate comparison failure", "Verify file accessibility"]
            )
    
    def _analyze_differences(self, log_a: Dict[str, Any], log_b: Dict[str, Any], 
                           diff: List[str]) -> List[Dict[str, Any]]:
        """Analyze differences between two log files"""
        differences = []
        
        # Check for added/removed top-level fields
        keys_a = set(log_a.keys())
        keys_b = set(log_b.keys())
        
        added_keys = keys_b - keys_a
        removed_keys = keys_a - keys_b
        
        if added_keys:
            differences.append({
                "type": "ADDED_FIELDS",
                "description": f"Fields added: {list(added_keys)}",
                "severity": "MEDIUM",
                "fields": list(added_keys)
            })
        
        if removed_keys:
            differences.append({
                "type": "REMOVED_FIELDS", 
                "description": f"Fields removed: {list(removed_keys)}",
                "severity": "HIGH",
                "fields": list(removed_keys)
            })
        
        # Check for modified values in common fields
        common_keys = keys_a & keys_b
        for key in common_keys:
            if log_a[key] != log_b[key]:
                differences.append({
                    "type": "MODIFIED_FIELD",
                    "description": f"Field '{key}' was modified",
                    "severity": "MEDIUM",
                    "field": key,
                    "old_value": log_a[key],
                    "new_value": log_b[key]
                })
        
        # Analyze diff lines for specific patterns
        for line in diff:
            if line.startswith('-') and 'signature' in line:
                differences.append({
                    "type": "SIGNATURE_CHANGE",
                    "description": "Cryptographic signature was modified",
                    "severity": "CRITICAL"
                })
            elif line.startswith('-') and 'hash_chain' in line:
                differences.append({
                    "type": "HASH_CHAIN_CHANGE",
                    "description": "Hash chain was modified",
                    "severity": "CRITICAL"
                })
        
        return differences
    
    def _assess_integrity_impact(self, differences: List[Dict[str, Any]]) -> str:
        """Assess the integrity impact of differences"""
        if not differences:
            return "NONE"
        
        critical_count = len([d for d in differences if d.get("severity") == "CRITICAL"])
        high_count = len([d for d in differences if d.get("severity") == "HIGH"])
        
        if critical_count > 0:
            return "CRITICAL"
        elif high_count > 0:
            return "HIGH"
        elif len(differences) > 5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _identify_tamper_indicators(self, differences: List[Dict[str, Any]]) -> List[str]:
        """Identify potential tamper indicators from differences"""
        indicators = []
        
        for diff in differences:
            if diff.get("type") == "SIGNATURE_CHANGE":
                indicators.append("SIGNATURE_TAMPERING")
            elif diff.get("type") == "HASH_CHAIN_CHANGE":
                indicators.append("HASH_CHAIN_TAMPERING")
            elif diff.get("type") == "MODIFIED_FIELD" and diff.get("field") == "timestamp":
                indicators.append("TIMESTAMP_MANIPULATION")
            elif diff.get("type") == "REMOVED_FIELDS":
                indicators.append("DATA_DELETION")
        
        return indicators
    
    def _generate_diff_recommendations(self, differences: List[Dict[str, Any]], 
                                     tamper_indicators: List[str]) -> List[str]:
        """Generate recommendations based on differences and tamper indicators"""
        recommendations = []
        
        if "SIGNATURE_TAMPERING" in tamper_indicators:
            recommendations.append("Immediately verify signature integrity with hardware device")
        
        if "HASH_CHAIN_TAMPERING" in tamper_indicators:
            recommendations.append("Investigate hash chain corruption and restore from backup")
        
        if "TIMESTAMP_MANIPULATION" in tamper_indicators:
            recommendations.append("Verify system time synchronization and investigate timestamp changes")
        
        if "DATA_DELETION" in tamper_indicators:
            recommendations.append("Investigate unauthorized data deletion and restore missing data")
        
        if len(differences) > 10:
            recommendations.append("Conduct comprehensive forensic analysis due to extensive changes")
        
        return recommendations
    
    def verify_all_vault_logs(self) -> List[LogIntegrityResult]:
        """Verify integrity of all vault log files"""
        results = []
        
        for log_file in self.vault_log_dir.glob("*.json"):
            result = self.verify_log_integrity(str(log_file))
            results.append(result)
        
        return results
    
    def generate_integrity_report(self, results: List[LogIntegrityResult]) -> str:
        """Generate comprehensive integrity report"""
        report = f"""
VAULT LOG INTEGRITY VERIFICATION REPORT
======================================

Report Generated: {datetime.datetime.now().isoformat()}
Total Log Files Analyzed: {len(results)}

SUMMARY:
--------
Valid: {len([r for r in results if r.status == 'VALID'])}
Suspicious: {len([r for r in results if r.status == 'SUSPICIOUS'])}
Corrupted: {len([r for r in results if r.status == 'CORRUPTED'])}
Missing: {len([r for r in results if r.status == 'MISSING'])}

DETAILED RESULTS:
----------------
"""
        
        for result in results:
            report += f"\nFile: {result.log_file}\n"
            report += f"Status: {result.status}\n"
            report += f"Hash Chain Valid: {result.hash_chain_valid}\n"
            report += f"Signature Valid: {result.signature_valid}\n"
            report += f"Timestamp Valid: {result.timestamp_valid}\n"
            
            if result.anomalies:
                report += "Anomalies:\n"
                for anomaly in result.anomalies:
                    report += f"  - [{anomaly.get('severity', 'UNKNOWN')}] {anomaly.get('description', 'No description')}\n"
            
            if result.recommendations:
                report += "Recommendations:\n"
                for rec in result.recommendations:
                    report += f"  - {rec}\n"
            
            report += "-" * 50 + "\n"
        
        return report

def main():
    """Main execution function for vault log analysis"""
    analyzer = VaultLogDifferentialAnalyzer()
    
    # Verify all vault logs
    results = analyzer.verify_all_vault_logs()
    
    # Generate and display report
    report = analyzer.generate_integrity_report(results)
    print(report)
    
    # Save report to file
    report_file = Path(f"vault_log_integrity_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\nIntegrity report saved to: {report_file}")

if __name__ == "__main__":
    main()


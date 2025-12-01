#!/usr/bin/env python3
"""
GATEKEEPER - Data Sanitation and Normalization Agent
Transforms raw CEX/DEX/blockchain data into Sovereign Standard Schema
"""

import json
import re
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

try:
    import pandas as pd
    import numpy as np
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False


@dataclass
class SovereignStandardRecord:
    """
    Sovereign Shadow Standard Schema for market/blockchain data

    All data flowing through SS3 should conform to this schema
    """
    ts: int  # Unix timestamp
    px: float  # Price
    vol: float  # Volume or size
    side: Optional[str] = None  # "buy" | "sell" | None
    from_addr: Optional[str] = None  # Source address
    to_addr: Optional[str] = None  # Destination address
    meta: Optional[Dict[str, Any]] = None  # Extra fields

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


class Gatekeeper:
    """
    Data normalization agent for Sovereign Shadow 3

    Responsibilities:
    - Detect schema of incoming data
    - Map fields to Sovereign Standard
    - Handle imperfections (missing values, format issues)
    - Validate data quality
    """

    # Known source schemas for common APIs
    KNOWN_SCHEMAS = {
        "binance_trades": {
            "timestamp": ["time", "T"],
            "price": ["price", "p"],
            "volume": ["qty", "q", "quantity"],
            "side": ["side", "m"],  # m: true = seller is maker
        },
        "uniswap_swaps": {
            "timestamp": ["timestamp", "blockTimestamp"],
            "price": ["amountOutUSD", "price"],
            "volume": ["amountInUSD", "amountIn"],
            "from_addr": ["sender", "from"],
            "to_addr": ["recipient", "to"],
        },
        "etherscan_txns": {
            "timestamp": ["timeStamp"],
            "price": ["value"],
            "from_addr": ["from"],
            "to_addr": ["to"],
        },
        "coingecko_ohlc": {
            "timestamp": [0],  # Index in array
            "price": [4],  # Close price
            "volume": [5] if len else None,
        }
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

        # Load system prompt
        self.system_prompt = self._load_system_prompt()

        # Stats
        self.stats = {
            "records_processed": 0,
            "records_cleaned": 0,
            "records_dropped": 0
        }

    def _load_system_prompt(self) -> str:
        """Load the Gatekeeper system prompt"""
        import yaml
        prompt_file = Path(__file__).parent.parent / "configs" / "system_prompts.yaml"
        if prompt_file.exists():
            with open(prompt_file, 'r') as f:
                prompts = yaml.safe_load(f)
                return prompts.get("gatekeeper", "")
        return ""

    def clean(
        self,
        raw_data: Union[List, Dict],
        source_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Clean and normalize raw data to Sovereign Standard

        Args:
            raw_data: Raw JSON/dict data from any source
            source_hint: Optional hint about data source (e.g., "binance", "uniswap")

        Returns:
            {
                "success": bool,
                "records": List[SovereignStandardRecord],
                "notes": str,
                "dropped_count": int
            }
        """
        # Ensure list format
        if isinstance(raw_data, dict):
            if "data" in raw_data:
                records = raw_data["data"]
            elif "result" in raw_data:
                records = raw_data["result"]
            else:
                records = [raw_data]
        else:
            records = raw_data

        if not records:
            return {
                "success": False,
                "records": [],
                "notes": "No data provided",
                "dropped_count": 0
            }

        # Infer schema from first record
        sample = records[0] if records else {}
        schema = self._infer_schema(sample, source_hint)

        if not schema:
            return {
                "success": False,
                "records": [],
                "notes": "Could not infer data schema. Data may be corrupted or unsupported format.",
                "dropped_count": len(records)
            }

        # Process all records
        cleaned = []
        dropped = 0
        notes = []

        for record in records:
            try:
                standard = self._normalize_record(record, schema)
                if standard:
                    cleaned.append(standard)
                    self.stats["records_cleaned"] += 1
                else:
                    dropped += 1
            except Exception as e:
                dropped += 1
                if dropped <= 5:
                    notes.append(f"Error processing record: {str(e)[:100]}")

        self.stats["records_processed"] += len(records)
        self.stats["records_dropped"] += dropped

        # Generate summary notes
        summary_notes = [
            f"Processed {len(records)} records",
            f"Cleaned: {len(cleaned)}, Dropped: {dropped}",
            f"Schema detected: {schema.get('_source', 'auto-inferred')}"
        ]
        summary_notes.extend(notes[:5])

        return {
            "success": len(cleaned) > 0,
            "records": [r.to_dict() for r in cleaned],
            "notes": " | ".join(summary_notes),
            "dropped_count": dropped
        }

    def clean_vectorized(
        self,
        raw_data: Union[List, Dict],
        source_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Vectorized cleaning using pandas for 10-100x performance on large datasets.

        Falls back to row-by-row processing if pandas not available.
        Use this method for datasets > 1000 records.
        """
        if not HAS_PANDAS:
            return self.clean(raw_data, source_hint)

        # Ensure list format
        if isinstance(raw_data, dict):
            if "data" in raw_data:
                records = raw_data["data"]
            elif "result" in raw_data:
                records = raw_data["result"]
            else:
                records = [raw_data]
        else:
            records = raw_data

        if not records:
            return {
                "success": False,
                "records": [],
                "notes": "No data provided",
                "dropped_count": 0
            }

        # Convert to DataFrame
        try:
            df = pd.DataFrame(records)
        except Exception as e:
            # Fall back to row-by-row if DataFrame creation fails
            return self.clean(raw_data, source_hint)

        original_count = len(df)

        # Infer schema from first record
        sample = records[0] if records else {}
        schema = self._infer_schema(sample, source_hint)

        if not schema:
            return {
                "success": False,
                "records": [],
                "notes": "Could not infer data schema",
                "dropped_count": original_count
            }

        # Vectorized timestamp parsing
        if "ts" in schema:
            ts_col = schema["ts"]
            if ts_col in df.columns:
                df["_ts"] = pd.to_numeric(df[ts_col], errors='coerce')
                # Handle milliseconds
                df.loc[df["_ts"] > 1e12, "_ts"] = df["_ts"] / 1000
                df["_ts"] = df["_ts"].astype('Int64')  # Nullable int

        # Vectorized price parsing
        if "px" in schema:
            px_col = schema["px"]
            if px_col in df.columns:
                df["_px"] = pd.to_numeric(
                    df[px_col].astype(str).str.replace(r'[$,€£]', '', regex=True),
                    errors='coerce'
                ).fillna(0.0)

        # Vectorized volume parsing
        if "vol" in schema:
            vol_col = schema["vol"]
            if vol_col in df.columns:
                df["_vol"] = pd.to_numeric(
                    df[vol_col].astype(str).str.replace(r'[$,€£]', '', regex=True),
                    errors='coerce'
                ).fillna(0.0)
            else:
                df["_vol"] = 0.0
        else:
            df["_vol"] = 0.0

        # Drop rows with invalid timestamps (CRITICAL: no time-travel)
        df = df.dropna(subset=["_ts"])

        dropped = original_count - len(df)

        # Convert to records
        cleaned_records = []
        for _, row in df.iterrows():
            record = SovereignStandardRecord(
                ts=int(row["_ts"]),
                px=float(row.get("_px", 0.0)),
                vol=float(row.get("_vol", 0.0))
            )
            cleaned_records.append(record)

        self.stats["records_processed"] += original_count
        self.stats["records_cleaned"] += len(cleaned_records)
        self.stats["records_dropped"] += dropped

        summary_notes = [
            f"Processed {original_count} records (vectorized)",
            f"Cleaned: {len(cleaned_records)}, Dropped: {dropped}",
            f"Schema detected: {schema.get('_source', 'auto-inferred')}"
        ]

        return {
            "success": len(cleaned_records) > 0,
            "records": [r.to_dict() for r in cleaned_records],
            "notes": " | ".join(summary_notes),
            "dropped_count": dropped
        }

    def _infer_schema(
        self,
        sample: Union[Dict, List],
        source_hint: Optional[str]
    ) -> Optional[Dict[str, str]]:
        """
        Infer field mappings from sample record

        Returns mapping: {"ts": "fieldname", "px": "fieldname", ...}
        """
        # If array format (like CoinGecko OHLC)
        if isinstance(sample, list):
            if len(sample) >= 5:
                return {
                    "ts": 0,
                    "px": 4,  # Close price
                    "vol": 5 if len(sample) > 5 else None,
                    "_source": "array_ohlc",
                    "_is_array": True
                }
            return None

        # Dict format
        keys = set(sample.keys())
        keys_lower = {k.lower(): k for k in keys}

        schema = {"_source": source_hint or "auto", "_is_array": False}

        # Timestamp detection
        ts_candidates = ["timestamp", "time", "t", "ts", "timstamp", "blocktimestamp", "createdat"]
        for candidate in ts_candidates:
            if candidate in keys_lower:
                schema["ts"] = keys_lower[candidate]
                break

        # Price detection
        px_candidates = ["price", "px", "p", "close", "last", "amount", "value", "amountoutusd"]
        for candidate in px_candidates:
            if candidate in keys_lower:
                schema["px"] = keys_lower[candidate]
                break

        # Volume detection
        vol_candidates = ["volume", "vol", "qty", "quantity", "size", "amount", "amountinusd"]
        for candidate in vol_candidates:
            if candidate in keys_lower and candidate != schema.get("px", "").lower():
                schema["vol"] = keys_lower[candidate]
                break

        # Side detection
        side_candidates = ["side", "type", "direction", "isbuyermaker", "m"]
        for candidate in side_candidates:
            if candidate in keys_lower:
                schema["side"] = keys_lower[candidate]
                break

        # Address detection
        addr_candidates = ["from", "sender", "source", "fromaddress"]
        for candidate in addr_candidates:
            if candidate in keys_lower:
                schema["from_addr"] = keys_lower[candidate]
                break

        to_candidates = ["to", "recipient", "destination", "toaddress"]
        for candidate in to_candidates:
            if candidate in keys_lower:
                schema["to_addr"] = keys_lower[candidate]
                break

        # Validate we have minimum required fields
        if "ts" not in schema and "px" not in schema:
            return None

        return schema

    def _normalize_record(
        self,
        record: Union[Dict, List],
        schema: Dict[str, Any]
    ) -> Optional[SovereignStandardRecord]:
        """Normalize a single record to Sovereign Standard"""

        # Handle array format
        if schema.get("_is_array"):
            try:
                ts = self._parse_timestamp(record[schema["ts"]])
                if ts is None:
                    return None  # Drop record - can't process without valid timestamp
                px = float(record[schema["px"]])
                vol = float(record[schema["vol"]]) if schema.get("vol") else 0.0

                return SovereignStandardRecord(ts=ts, px=px, vol=vol)
            except (IndexError, ValueError, TypeError):
                return None

        # Handle dict format
        try:
            # Timestamp - CRITICAL: Drop records with unparseable timestamps
            ts = None
            if "ts" in schema:
                ts = self._parse_timestamp(record.get(schema["ts"]))
                if ts is None:
                    return None  # Drop record - can't process without valid timestamp

            # Price
            px = 0.0
            if "px" in schema:
                px = self._parse_number(record.get(schema["px"]))

            # Volume
            vol = 0.0
            if "vol" in schema:
                vol = self._parse_number(record.get(schema["vol"], 0))

            # Side
            side = None
            if "side" in schema:
                side = self._parse_side(record.get(schema["side"]))

            # Addresses
            from_addr = None
            if "from_addr" in schema:
                from_addr = str(record.get(schema["from_addr"], "")) or None

            to_addr = None
            if "to_addr" in schema:
                to_addr = str(record.get(schema["to_addr"], "")) or None

            # Collect remaining fields as meta
            known_keys = set(v for k, v in schema.items() if not k.startswith("_"))
            meta = {k: v for k, v in record.items() if k not in known_keys}

            return SovereignStandardRecord(
                ts=ts,
                px=px,
                vol=vol,
                side=side,
                from_addr=from_addr,
                to_addr=to_addr,
                meta=meta if meta else None
            )

        except Exception:
            return None

    def _parse_timestamp(self, value: Any) -> Optional[int]:
        """
        Parse various timestamp formats to unix timestamp.

        CRITICAL: Returns None on failure instead of datetime.now()
        to prevent time-travel bugs in historical data analysis.
        Records with None timestamps should be dropped, not backdated.
        """
        if value is None:
            return None  # FIXED: Don't inject current time into historical data

        # Already unix timestamp (int)
        if isinstance(value, (int, float)):
            # Milliseconds?
            if value > 1e12:
                return int(value / 1000)
            return int(value)

        # String formats
        if isinstance(value, str):
            # ISO format
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return int(dt.timestamp())
            except ValueError:
                pass

            # Unix string
            try:
                v = float(value)
                return int(v) if v < 1e12 else int(v / 1000)
            except ValueError:
                pass

            # Common date formats
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y %H:%M:%S"]:
                try:
                    dt = datetime.strptime(value, fmt)
                    return int(dt.timestamp())
                except ValueError:
                    pass

        return None  # FIXED: Return None, let caller decide to drop or handle

    def _parse_number(self, value: Any) -> float:
        """Parse various number formats"""
        if value is None:
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            # Remove common formatting
            clean = re.sub(r'[,$€£]', '', value)
            try:
                return float(clean)
            except ValueError:
                return 0.0

        return 0.0

    def _parse_side(self, value: Any) -> Optional[str]:
        """Parse trade side to 'buy' or 'sell'"""
        if value is None:
            return None

        if isinstance(value, bool):
            return "sell" if value else "buy"  # Binance: m=true means seller is maker

        if isinstance(value, str):
            v = value.lower()
            if v in ["buy", "bid", "long"]:
                return "buy"
            if v in ["sell", "ask", "short"]:
                return "sell"

        return None

    def validate(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate a list of Sovereign Standard records

        Returns validation report
        """
        issues = []
        valid_count = 0

        for i, record in enumerate(records):
            record_issues = []

            # Check required fields
            if "ts" not in record or record["ts"] is None:
                record_issues.append("Missing timestamp")
            elif record["ts"] < 1000000000:
                record_issues.append("Timestamp appears invalid (too small)")

            if "px" not in record:
                record_issues.append("Missing price")
            elif record["px"] <= 0:
                record_issues.append("Price is zero or negative")

            if record_issues:
                issues.append({"index": i, "issues": record_issues})
            else:
                valid_count += 1

        return {
            "valid": len(issues) == 0,
            "total_records": len(records),
            "valid_count": valid_count,
            "invalid_count": len(issues),
            "issues": issues[:10]  # First 10 issues
        }


# CLI
if __name__ == "__main__":
    import sys

    gatekeeper = Gatekeeper()

    # Example: Clean some raw data
    example_data = [
        {"time": 1701388800000, "price": "95432.50", "qty": "0.5", "side": "buy"},
        {"time": 1701392400000, "price": "95500.00", "qty": "1.2", "side": "sell"},
        {"time": "2024-11-30T12:00:00Z", "price": 95600, "qty": 0.8},
    ]

    print(f"\n{'='*60}")
    print("GATEKEEPER - Data Normalization")
    print('='*60)
    print(f"Input records: {len(example_data)}")

    result = gatekeeper.clean(example_data)

    print(f"\nSuccess: {result['success']}")
    print(f"Cleaned records: {len(result['records'])}")
    print(f"Dropped: {result['dropped_count']}")
    print(f"Notes: {result['notes']}")

    print("\nCleaned data:")
    for record in result['records']:
        print(f"  {record}")

    # Validate
    validation = gatekeeper.validate(result['records'])
    print(f"\nValidation: {validation['valid_count']}/{validation['total_records']} valid")

    print('='*60)

"""
Manual Ledger Service for Portfolio Holdings
Stores and manages manual entries for wallets/holdings not on exchanges
"""

import os
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from threading import Lock

LEDGER_FILE = "ledger.json"
file_lock = Lock()


class LedgerService:
    """Service for managing manual portfolio ledger entries."""
    
    def __init__(self, ledger_path: str = LEDGER_FILE):
        self.ledger_path = ledger_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create ledger file if it doesn't exist."""
        if not os.path.exists(self.ledger_path):
            self._save_ledger({'entries': [], 'last_updated': datetime.now().isoformat()})
    
    def _load_ledger(self) -> Dict[str, Any]:
        """Load ledger from file."""
        with file_lock:
            try:
                with open(self.ledger_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {'entries': [], 'last_updated': datetime.now().isoformat()}
    
    def _save_ledger(self, data: Dict[str, Any]):
        """Save ledger to file."""
        with file_lock:
            data['last_updated'] = datetime.now().isoformat()
            with open(self.ledger_path, 'w') as f:
                json.dump(data, f, indent=2)
    
    def get_all_entries(self) -> List[Dict[str, Any]]:
        """Get all ledger entries."""
        ledger = self._load_ledger()
        return ledger.get('entries', [])
    
    def get_entry(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get a single entry by ID."""
        entries = self.get_all_entries()
        for entry in entries:
            if entry.get('id') == entry_id:
                return entry
        return None
    
    def add_entry(
        self,
        symbol: str,
        amount: float,
        source: str = 'manual',
        cost_basis: Optional[float] = None,
        date_acquired: Optional[str] = None,
        notes: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Add a new ledger entry."""
        entry = {
            'id': str(uuid.uuid4()),
            'symbol': symbol.upper(),
            'amount': amount,
            'source': source,
            'cost_basis': cost_basis,
            'date_acquired': date_acquired or datetime.now().isoformat()[:10],
            'notes': notes,
            'tags': tags or [],
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        ledger = self._load_ledger()
        ledger['entries'].append(entry)
        self._save_ledger(ledger)
        
        return entry
    
    def update_entry(self, entry_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing ledger entry."""
        ledger = self._load_ledger()
        entries = ledger.get('entries', [])
        
        for i, entry in enumerate(entries):
            if entry.get('id') == entry_id:
                allowed_fields = ['symbol', 'amount', 'source', 'cost_basis', 'date_acquired', 'notes', 'tags']
                for field in allowed_fields:
                    if field in updates:
                        if field == 'symbol':
                            entries[i][field] = updates[field].upper()
                        else:
                            entries[i][field] = updates[field]
                entries[i]['updated_at'] = datetime.now().isoformat()
                ledger['entries'] = entries
                self._save_ledger(ledger)
                return entries[i]
        
        return None
    
    def delete_entry(self, entry_id: str) -> bool:
        """Delete a ledger entry."""
        ledger = self._load_ledger()
        entries = ledger.get('entries', [])
        original_count = len(entries)
        
        entries = [e for e in entries if e.get('id') != entry_id]
        
        if len(entries) < original_count:
            ledger['entries'] = entries
            self._save_ledger(ledger)
            return True
        return False
    
    def get_by_symbol(self, symbol: str) -> List[Dict[str, Any]]:
        """Get all entries for a specific symbol."""
        entries = self.get_all_entries()
        return [e for e in entries if e.get('symbol', '').upper() == symbol.upper()]
    
    def get_by_source(self, source: str) -> List[Dict[str, Any]]:
        """Get all entries from a specific source."""
        entries = self.get_all_entries()
        return [e for e in entries if e.get('source', '').lower() == source.lower()]
    
    def get_aggregated_holdings(self) -> Dict[str, float]:
        """Get aggregated holdings by symbol."""
        entries = self.get_all_entries()
        holdings = {}
        for entry in entries:
            symbol = entry.get('symbol', '').upper()
            amount = entry.get('amount', 0)
            holdings[symbol] = holdings.get(symbol, 0) + amount
        return holdings
    
    def get_stats(self) -> Dict[str, Any]:
        """Get ledger statistics."""
        entries = self.get_all_entries()
        symbols = set(e.get('symbol', '') for e in entries)
        sources = set(e.get('source', '') for e in entries)
        
        total_cost_basis = sum(e.get('cost_basis', 0) or 0 for e in entries)
        
        return {
            'total_entries': len(entries),
            'unique_symbols': len(symbols),
            'unique_sources': len(sources),
            'symbols': list(symbols),
            'sources': list(sources),
            'total_cost_basis': total_cost_basis
        }

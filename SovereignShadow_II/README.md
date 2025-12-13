## SovereignShadow_II (isolated runtime)

This folder contains a clean, testable implementation of the **D.O.E. pattern**:

- **Directive**: `core/intelligence/regime_detector.py`
- **Orchestration**: `core/intelligence/strategy_selector.py`
- **Execution**: `core/orchestrator.py` (FAKE mode by default)
- **Learning/Tracking**: `core/intelligence/performance_tracker.py` (SQLite)

### Safety

Live trading is blocked unless both are true:

- `ENV=production`
- `ALLOW_LIVE_EXCHANGE=1`

### Quick smoke test

Run unit tests:

```bash
pytest -q
```

Run one FAKE orchestration tick:

```bash
python -m SovereignShadow_II.core.orchestrator
```

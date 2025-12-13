import pandas as pd

from SovereignShadow_II.core.intelligence.performance_tracker import PerformanceTracker
from SovereignShadow_II.core.intelligence.regime_detector import MarketRegimeDetector
from SovereignShadow_II.core.intelligence.strategy_selector import StrategySelector


def _df(n: int = 250) -> pd.DataFrame:
    close = pd.Series([100 + i * 0.1 for i in range(n)])
    return pd.DataFrame(
        {
            "timestamp": pd.RangeIndex(0, n),
            "open": close.shift(1).fillna(close.iloc[0]),
            "high": close + 0.2,
            "low": close - 0.2,
            "close": close,
            "volume": pd.Series([100] * n),
        }
    )


def test_regime_detector_returns_valid_regime(tmp_path):
    det = MarketRegimeDetector()
    res = det.detect(_df())
    assert res.regime in {"trending_bull", "trending_bear", "choppy_calm", "choppy_volatile"}
    assert isinstance(res.features, dict)


def test_strategy_selector_loads_metadata(tmp_path, monkeypatch):
    # Point selector at real modularized strategies.
    tracker = PerformanceTracker(db_path=str(tmp_path / "perf.db"))
    selector = StrategySelector(tracker=tracker, strategies_root="/workspace/strategies/modularized")
    all_strats = selector.list_strategies()
    assert "ElderReversion" in all_strats

    chosen = selector.select(regime="choppy_calm", limit=1)
    assert chosen
    assert isinstance(chosen[0][0], str)

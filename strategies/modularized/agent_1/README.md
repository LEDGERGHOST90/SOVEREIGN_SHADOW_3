## Agent 1 modularized strategies (1-10)

Each strategy is split into three skills:

- `entry.py` → `Entry.generate_signal(df)`
- `exit.py` → `Exit.generate_signal(df, entry_price)`
- `risk.py` → `Risk.calculate_position_size(portfolio_value, current_price, atr)`

Metadata is in each strategy folder as `metadata.json`.

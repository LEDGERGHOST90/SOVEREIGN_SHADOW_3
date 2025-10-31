# 🔧 Scripts Directory

Development and testing scripts for SovereignShadow

## Core Scripts

### slice.py
**Purpose**: Slice monolithic architecture into organized modules

**Usage**:
```bash
python3 slice.py
```

**What it does**:
- Creates module structure (ladder, tracking, safety, execution, storage)
- Moves files into appropriate modules
- Creates `__init__.py` files for imports
- Generates module manifest

---

### build.py
**Purpose**: Build unified system from modules

**Usage**:
```bash
python3 build.py
```

**What it does**:
- Validates module structure
- Tests module imports
- Creates unified `sovereign_system.py` interface
- Runs integration tests

---

## Testing Scripts

### test_autonomous_cycle.py
Test a single autonomous trading cycle

```bash
python3 test_autonomous_cycle.py
```

### test_all_exchanges.py
Test connectivity to all 5 exchanges

```bash
python3 test_all_exchanges.py
```

### test_apis.py
Test API credentials and permissions

```bash
python3 test_apis.py
```

---

## Setup Scripts

### setup_exchanges.py
Configure exchange API credentials

```bash
python3 setup_exchanges.py
```

---

## Workflow

1. **Development**: Edit files in `modules/`
2. **Build**: Run `python3 scripts/build.py`
3. **Test**: Run test scripts
4. **Deploy**: Use main scripts from root directory

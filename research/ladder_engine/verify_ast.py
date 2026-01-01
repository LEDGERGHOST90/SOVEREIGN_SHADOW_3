
import ast
import sys

def verify_with_ast(file_path):
    print(f"🧬 Verifying {file_path} using AST...")
    
    with open(file_path, "r") as f:
        tree = ast.parse(f.read())
        
    found_profiles = {}
    found_prices = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == 'MarketSimulator':
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == '__init__':
                    for stmt in item.body:
                        if isinstance(stmt, ast.Assign):
                            # Check active target: self.volatility_profiles
                            for target in stmt.targets:
                                if isinstance(target, ast.Attribute) and target.attr == 'volatility_profiles':
                                    if isinstance(stmt.value, ast.Dict):
                                        for k, v in zip(stmt.value.keys, stmt.value.values):
                                            if isinstance(k, ast.Constant): # Python 3.8+
                                                found_profiles[k.value] = v.value
                                            elif isinstance(k, ast.Str): # Older python
                                                found_profiles[k.s] = v.n
                                                
                            # Check active target: self.base_prices
                            for target in stmt.targets:
                                if isinstance(target, ast.Attribute) and target.attr == 'base_prices':
                                    if isinstance(stmt.value, ast.Dict):
                                        for k, v in zip(stmt.value.keys, stmt.value.values):
                                            if isinstance(k, ast.Constant):
                                                found_prices[k.value] = v.value
                                            elif isinstance(k, ast.Str):
                                                found_prices[k.s] = v.n

    expected_profiles = {
        'MASK': 0.07,
        'TRUMP': 0.15,
        'ARB': 0.05,
        'QNT': 0.04
    }
    
    all_passed = True
    print("\n🔍 Checking Volatility Profiles:")
    for token, val in expected_profiles.items():
        if token in found_profiles:
            if found_profiles[token] == val:
                print(f"✅ {token}: {val}")
            else:
                print(f"❌ {token}: Expected {val}, found {found_profiles[token]}")
                all_passed = False
        else:
            print(f"❌ {token}: Not found in volatility_profiles")
            all_passed = False
            
    print("\n🔍 Checking Base Prices:")
    for token in expected_profiles.keys():
        key = f"{token}USDT"
        if key in found_prices:
             print(f"✅ {key}: {found_prices[key]}")
        else:
             print(f"❌ {key}: Not found in base_prices")
             all_passed = False

    if all_passed:
        print("\n✨ AST Verification SUCCESS: All tokens correctly configured.")
    else:
        print("\n⚠️ AST Verification FAILED")
        sys.exit(1)

if __name__ == "__main__":
    verify_with_ast("/Volumes/LegacySafe/SS_III/research/ladder_engine/paper_trading_engine.py")

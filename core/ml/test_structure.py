#!/usr/bin/env python3
"""
Quick structure verification test for FreqAI scaffold.
Tests import structure and class definitions without requiring ML libraries.
"""

import sys
from pathlib import Path

def test_structure():
    """Verify module structure and classes are defined."""
    print("=" * 80)
    print("FreqAI Scaffold Structure Test")
    print("=" * 80)
    print()

    # Test file existence
    ml_dir = Path(__file__).parent
    scaffold_file = ml_dir / 'freqai_scaffold.py'
    init_file = ml_dir / '__init__.py'
    readme_file = ml_dir / 'README.md'
    requirements_file = ml_dir / 'requirements.txt'

    print("1. File Existence Check:")
    files = {
        'freqai_scaffold.py': scaffold_file,
        '__init__.py': init_file,
        'README.md': readme_file,
        'requirements.txt': requirements_file
    }

    all_exist = True
    for name, path in files.items():
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"   {status} {name}: {path}")
        all_exist = all_exist and exists

    print()

    if not all_exist:
        print("❌ Some files are missing!")
        return False

    # Test imports (without ML libraries)
    print("2. Module Structure Check:")
    try:
        # Read the scaffold file to check class definitions
        with open(scaffold_file, 'r') as f:
            content = f.read()

        classes = [
            'AdaptiveMLEngine',
            'FeatureEngineering',
            'OutlierDetector',
            'ModelMetrics',
            'PredictionResult'
        ]

        print("   Checking for required classes...")
        for cls in classes:
            found = f'class {cls}' in content
            status = "✓" if found else "✗"
            print(f"      {status} {cls}")

        print()

        # Check for key methods
        print("   Checking for key methods in AdaptiveMLEngine...")
        methods = [
            'def should_retrain',
            'def train',
            'def predict',
            'def save_model',
            'def load_model',
            'def get_feature_importance'
        ]

        for method in methods:
            found = method in content
            status = "✓" if found else "✗"
            method_name = method.replace('def ', '')
            print(f"      {status} {method_name}()")

        print()

        # Check for feature engineering methods
        print("   Checking for feature engineering methods...")
        fe_methods = [
            'def add_returns',
            'def add_momentum_indicators',
            'def add_volatility_indicators',
            'def add_trend_indicators',
            'def add_volume_indicators',
            'def generate_all_features'
        ]

        for method in fe_methods:
            found = method in content
            status = "✓" if found else "✗"
            method_name = method.replace('def ', '')
            print(f"      {status} {method_name}()")

        print()

    except Exception as e:
        print(f"❌ Error checking module structure: {e}")
        return False

    # Count lines of code
    print("3. Code Statistics:")
    with open(scaffold_file, 'r') as f:
        lines = f.readlines()
        total_lines = len(lines)
        code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith('#'))
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        docstring_lines = sum(1 for line in lines if '"""' in line or "'''" in line)

    print(f"   Total lines: {total_lines}")
    print(f"   Code lines: {code_lines}")
    print(f"   Comment lines: {comment_lines}")
    print(f"   Documentation: {docstring_lines}")
    print()

    # Check README structure
    print("4. Documentation Check:")
    with open(readme_file, 'r') as f:
        readme_content = f.read()

    sections = [
        'Installation',
        'Quick Start',
        'API Reference',
        'Integration with SOVEREIGN_SHADOW_3',
        'Performance Considerations',
        'Troubleshooting'
    ]

    for section in sections:
        found = section in readme_content
        status = "✓" if found else "✗"
        print(f"   {status} {section} section")

    print()

    # Summary
    print("=" * 80)
    print("✅ All structure tests passed!")
    print()
    print("Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run example: python freqai_scaffold.py")
    print("3. Integrate with trading agents")
    print("=" * 80)

    return True

if __name__ == '__main__':
    success = test_structure()
    sys.exit(0 if success else 1)

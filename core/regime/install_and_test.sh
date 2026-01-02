#!/bin/bash

# HMM Regime Detector - Installation and Test Script
# SOVEREIGN_SHADOW_3
# Created: 2025-12-14

echo "=========================================="
echo "HMM Regime Detector - Installation & Test"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python --version
echo ""

# Check current directory
SCRIPT_DIR="/Volumes/LegacySafe/SS_III/core/regime"
echo "Working directory: $SCRIPT_DIR"
echo ""

# Install dependencies
echo "Installing dependencies..."
echo "----------------------------------------"
pip install -r "$SCRIPT_DIR/requirements.txt"
echo ""

# Verify installations
echo "Verifying installations..."
echo "----------------------------------------"
python -c "import numpy; print('✓ numpy version:', numpy.__version__)"
python -c "import pandas; print('✓ pandas version:', pandas.__version__)"
python -c "import sklearn; print('✓ scikit-learn version:', sklearn.__version__)"
python -c "import hmmlearn; print('✓ hmmlearn version:', hmmlearn.__version__)"
echo ""

# Test syntax
echo "Testing Python syntax..."
echo "----------------------------------------"
python -m py_compile "$SCRIPT_DIR/hmm_regime_detector.py"
python -m py_compile "$SCRIPT_DIR/integration_example.py"
echo "✓ Syntax check passed"
echo ""

# Run main module test
echo "Running HMM detector test..."
echo "----------------------------------------"
python "$SCRIPT_DIR/hmm_regime_detector.py"
echo ""

# Run integration example
echo "Running integration example..."
echo "----------------------------------------"
python "$SCRIPT_DIR/integration_example.py"
echo ""

echo "=========================================="
echo "Installation and testing complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Train model with real BTC historical data"
echo "2. Integrate into launch_autonomous.py"
echo "3. Set up weekly retraining schedule"
echo ""
echo "Model will be saved to:"
echo "$SCRIPT_DIR/models/"
echo ""

#!/bin/bash
# Build script for Render deployment
# This ensures dependencies are installed correctly

echo "=========================================="
echo "AMABA Backend Build Script"
echo "=========================================="

# Update pip
echo "Updating pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Verify installation
echo "Verifying smolagents installation..."
python -c "import smolagents; print(f'✅ smolagents {smolagents.__version__} installed')" || {
    echo "⚠️  Installing smolagents from source..."
    pip install git+https://github.com/agenthub/smolagents.git
}

echo ""
echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="

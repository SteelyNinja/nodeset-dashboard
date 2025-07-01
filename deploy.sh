#!/bin/bash

echo "🔗 NodeSet Validator Dashboard Deployment Script"
echo "================================================"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
if ! command_exists python3; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check pip
if ! command_exists pip3; then
    echo "❌ pip3 is not installed"
    exit 1
fi

echo "✅ pip3 found"

# Create virtual environment
echo "📦 Setting up virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt

# Check for cache file
if [ ! -f "nodeset_validator_tracker_cache.json" ]; then
    echo "⚠️  Warning: Cache file not found"
    echo "   Make sure to run your validator tracker first"
    echo "   Expected: nodeset_validator_tracker_cache.json"
fi

# Create .streamlit directory if it doesn't exist
mkdir -p .streamlit

echo "🚀 Setup complete!"
echo ""
echo "To start the dashboard:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run: streamlit run app.py"
echo "  3. Open browser to: http://localhost:8501"
echo ""
echo "Or use the launcher: python run.py"

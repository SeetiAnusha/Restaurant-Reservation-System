#!/bin/bash

# Restaurant Reservation Agent - Setup Script

echo "🍽️  GoodFoods Reservation Agent Setup"
echo "======================================"
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "✅ Virtual environment created"
echo ""
echo "📦 Activating virtual environment..."

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your GROQ_API_KEY"
else
    echo ""
    echo "✅ .env file already exists"
fi

# Generate restaurant data
echo ""
echo "🎲 Generating restaurant data..."
python data/generator.py

echo ""
echo "======================================"
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your GROQ_API_KEY"
echo "2. Run: streamlit run frontend/streamlit_app.py"
echo ""
echo "For testing: python evaluation/test_scenarios.py"
echo "======================================"

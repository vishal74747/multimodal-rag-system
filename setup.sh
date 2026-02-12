#!/bin/bash

echo "🚀 Multi-Modal RAG System - Quick Start"
echo "======================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📥 Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt --quiet

echo ""
echo "✅ Installation complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Get your Groq API key from: https://console.groq.com"
echo "2. Run the app: streamlit run app.py"
echo "3. Open your browser at: http://localhost:8501"
echo ""
echo "📚 For deployment instructions, see DEPLOYMENT.md"
echo ""

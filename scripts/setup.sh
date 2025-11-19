#!/bin/bash

# Setup script for RAG System

echo "🚀 Setting up RAG System..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo "Creating directories..."
mkdir -p logs
mkdir -p data/raw
mkdir -p data/processed
mkdir -p data/uploads
mkdir -p chroma_db
mkdir -p evaluation_results

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
fi

# Check Ollama installation
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found. Install it from https://ollama.com/"
    echo "   Or run: curl -fsSL https://ollama.com/install.sh | sh"
else
    echo "✓ Ollama found"
    echo "Pulling llama2 model..."
    ollama pull llama2
fi

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Start the API: python -m uvicorn api.main:app --reload"
echo "4. Start the UI: streamlit run ui/app.py"
echo ""
echo "Or use Docker Compose: docker-compose up"


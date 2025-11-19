#!/bin/bash

# Start script for RAG System

echo "🚀 Starting RAG System..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Run setup.sh first."
    exit 1
fi

# Start services based on argument
case "$1" in
    "api")
        echo "Starting API server..."
        python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
        ;;
    "ui")
        echo "Starting Streamlit UI..."
        streamlit run ui/app.py
        ;;
    "all")
        echo "Starting all services with Docker Compose..."
        docker-compose up
        ;;
    "dev")
        echo "Starting in development mode..."
        echo "Starting API in background..."
        python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
        API_PID=$!
        echo "API PID: $API_PID"
        
        sleep 3
        
        echo "Starting UI..."
        streamlit run ui/app.py
        
        # Cleanup on exit
        kill $API_PID
        ;;
    *)
        echo "Usage: $0 {api|ui|all|dev}"
        echo ""
        echo "  api  - Start API server only"
        echo "  ui   - Start Streamlit UI only"
        echo "  all  - Start all services with Docker Compose"
        echo "  dev  - Start API and UI in development mode"
        exit 1
        ;;
esac


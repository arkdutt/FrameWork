#!/bin/bash

# Filmmaker AI App - Backend Startup Script

echo "🎬 Starting Filmmaker AI Backend..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists in project root
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "⚠️  No .env file found. Creating from .env.example..."
        cp .env.example .env
        echo "📝 Please edit .env with your configuration"
    else
        echo "⚠️  No .env or .env.example file found."
        echo "📝 Please create a .env file with your configuration"
    fi
fi

# Check if MongoDB is running
if ! pgrep -x "mongod" > /dev/null; then
    echo "⚠️  MongoDB doesn't appear to be running."
    echo "   Please start MongoDB before running the backend."
    echo "   Example: docker run -d -p 27017:27017 --name mongodb mongo:latest"
fi

# Start the backend
echo "🚀 Starting FastAPI server..."
python -m uvicorn app.backend.main:app --reload --host 0.0.0.0 --port 8000



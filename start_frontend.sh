#!/bin/bash

# Filmmaker AI App - Frontend Startup Script

echo "🎬 Starting Filmmaker AI Frontend..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Navigate to frontend directory
cd app/frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "⚠️  No .env.local file found. Creating one..."
    cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
EOF
    echo "✅ Created .env.local with default configuration"
fi

# Start the development server
echo "🚀 Starting Next.js development server..."
npm run dev



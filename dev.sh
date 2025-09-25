#!/bin/bash

# Candidate Evaluation Backend - Development Mode
# This script runs the application in development mode with auto-reload

set -e  # Exit on any error

echo "🔧 Starting Development Server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies including development tools
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install uvicorn[standard]  # For better development experience

# Create necessary directories
mkdir -p uploads
mkdir -p chroma_db

# Set environment variables for development
export DEBUG=true
export HOST=127.0.0.1
export PORT=8000

echo "🌟 Starting development server with auto-reload..."
echo "📖 API Documentation: http://localhost:8000/docs"
echo "🔗 Server: http://localhost:8000"
echo "🔄 Auto-reload enabled - changes will restart the server"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run with uvicorn for better development experience
uvicorn main:app --host 127.0.0.1 --port 8000 --reload --log-level info
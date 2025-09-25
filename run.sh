#!/bin/bash

# Candidate Evaluation Backend - Run Script
# This script sets up and runs the FastAPI application

set -e  # Exit on any error

echo "🚀 Starting Candidate Evaluation Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if requirements.txt is newer than last install
if [ ! -f ".last_install" ] || [ "requirements.txt" -nt ".last_install" ]; then
    echo "📚 Installing/updating dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch .last_install
else
    echo "✅ Dependencies are up to date"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p uploads
mkdir -p chroma_db

# Set environment variables if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating default .env file..."
    cat > .env << EOF
# API Keys (replace with your actual keys)
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true

# LLM Configuration
DEFAULT_LLM_PROVIDER=mock
OPENAI_MODEL=gpt-3.5-turbo
GEMINI_MODEL=gemini-pro

# File Upload Configuration
MAX_FILE_SIZE=10485760
UPLOAD_DIR=uploads

# Vector Database Configuration
CHROMA_PERSIST_DIR=chroma_db
EOF
    echo "📝 Please edit .env file with your actual API keys"
fi

echo "🌟 Starting FastAPI server..."
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🔗 Server will be running at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
python main.py
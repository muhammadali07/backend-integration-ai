#!/bin/bash

# Candidate Evaluation Backend - Initial Setup
# This script sets up the project for the first time

set -e  # Exit on any error

echo "🎯 Setting up Candidate Evaluation Backend..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.8+ is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p uploads
mkdir -p chroma_db
mkdir -p logs

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env configuration file..."
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
    echo "📝 Created .env file with default configuration"
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo "📄 Creating .gitignore file..."
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
.venv/
env/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Project specific
uploads/
chroma_db/
logs/
.last_install

# OS
.DS_Store
Thumbs.db
EOF
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x run.sh
chmod +x dev.sh
chmod +x setup.sh

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your actual API keys"
echo "2. Run './run.sh' to start the production server"
echo "3. Or run './dev.sh' to start the development server"
echo ""
echo "📖 API Documentation will be available at: http://localhost:8000/docs"
echo "🔗 Server will be running at: http://localhost:8000"
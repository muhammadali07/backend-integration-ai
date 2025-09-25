#!/bin/bash

# Candidate Evaluation Backend - Stop Script
# This script stops the running FastAPI server

echo "🛑 Stopping Candidate Evaluation Backend..."

# Find and kill processes running on port 8000
PIDS=$(lsof -ti:8000 2>/dev/null || true)

if [ -z "$PIDS" ]; then
    echo "ℹ️  No server running on port 8000"
else
    echo "🔍 Found processes running on port 8000: $PIDS"
    echo "🛑 Stopping server processes..."
    
    for PID in $PIDS; do
        echo "Killing process $PID..."
        kill -TERM $PID 2>/dev/null || true
        
        # Wait a bit for graceful shutdown
        sleep 2
        
        # Force kill if still running
        if kill -0 $PID 2>/dev/null; then
            echo "Force killing process $PID..."
            kill -KILL $PID 2>/dev/null || true
        fi
    done
    
    echo "✅ Server stopped successfully"
fi

# Also kill any python processes running main.py
PYTHON_PIDS=$(pgrep -f "python.*main.py" 2>/dev/null || true)

if [ ! -z "$PYTHON_PIDS" ]; then
    echo "🔍 Found Python processes running main.py: $PYTHON_PIDS"
    echo "🛑 Stopping Python processes..."
    
    for PID in $PYTHON_PIDS; do
        echo "Killing Python process $PID..."
        kill -TERM $PID 2>/dev/null || true
        
        # Wait a bit for graceful shutdown
        sleep 2
        
        # Force kill if still running
        if kill -0 $PID 2>/dev/null; then
            echo "Force killing Python process $PID..."
            kill -KILL $PID 2>/dev/null || true
        fi
    done
fi

echo "🎉 All server processes stopped!"
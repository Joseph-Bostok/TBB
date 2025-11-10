#!/bin/bash
# Therapy Bot - Quick Start Script

set -e  # Exit on error

echo "🧠 Therapy Bot - Starting..."
echo

# Check if we're in the right directory
if [ ! -f "python_ai/main.py" ]; then
    echo "❌ Error: Please run this script from the TTB directory"
    echo "   cd /home/jbostok/TTB && ./start.sh"
    exit 1
fi

# Check if dependencies are installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    python3 -m pip install -q -r python_ai/requirements.txt
    echo "✅ Dependencies installed"
    echo
fi

# Create directories
mkdir -p data logs

# Start the server
echo "🚀 Starting Therapy Bot server..."
echo "   Server will be available at: http://localhost:8000"
echo "   API docs: http://localhost:8000/docs"
echo
echo "Press Ctrl+C to stop the server"
echo

cd python_ai && python3 main.py

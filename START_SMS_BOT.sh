#!/bin/bash
# One-command SMS Bot Starter
# This script starts your SMS therapy bot and helps you set up ngrok

set -e

echo "🤖 Starting TBB Therapy SMS Bot..."
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -f "python_ai/main.py" ]; then
    echo -e "${RED}❌ Error: Please run this from the TBB directory${NC}"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found!${NC}"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please configure your Twilio credentials in .env${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r python_ai/requirements.txt

# Create necessary directories
mkdir -p python_ai/data
mkdir -p python_ai/logs

# Check if ngrok is installed
if command -v ngrok &> /dev/null; then
    echo -e "${GREEN}✓ ngrok is installed${NC}"
    NGROK_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️  ngrok not found${NC}"
    echo "For local testing, install ngrok: https://ngrok.com/download"
    NGROK_AVAILABLE=false
fi

echo ""
echo "===================================="
echo "🚀 Starting server..."
echo "===================================="
echo ""

# Start the server in background
cd python_ai
python main.py &
SERVER_PID=$!
cd ..

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Check if server is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✓ Server is running on http://localhost:8000${NC}"
else
    echo -e "${RED}❌ Server failed to start${NC}"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "===================================="
echo "📱 Next Steps"
echo "===================================="
echo ""

if [ "$NGROK_AVAILABLE" = true ]; then
    echo -e "${YELLOW}Starting ngrok...${NC}"
    echo ""
    echo "In a new terminal, run:"
    echo "  ngrok http 8000"
    echo ""
    echo "Then configure Twilio webhook with the ngrok URL:"
    echo "  https://YOUR-NGROK-URL.ngrok.io/sms/webhook"
else
    echo "1. Install ngrok: https://ngrok.com/download"
    echo "2. Run: ngrok http 8000"
    echo "3. Configure Twilio webhook with:"
    echo "   https://YOUR-NGROK-URL.ngrok.io/sms/webhook"
fi

echo ""
echo "4. Text your Twilio number to test!"
echo "   Phone: $(grep TWILIO_PHONE_NUMBER .env | cut -d '=' -f2)"
echo ""
echo "===================================="
echo "🛠  Useful Commands"
echo "===================================="
echo ""
echo "• Check setup: python test_twilio_setup.py"
echo "• View logs:   tail -f python_ai/logs/therapy_bot.log"
echo "• Stop server: kill $SERVER_PID"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Keep script running
wait $SERVER_PID

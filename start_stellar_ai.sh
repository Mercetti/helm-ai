#!/bin/bash

# Stellar Logic AI - LLM Integration Startup Script
# This script starts Ollama, the Stellar LLM server, and the dashboard

echo "🚀 Starting Stellar Logic AI with Ollama Integration..."

# Check if Ollama is running
echo "🔍 Checking Ollama status..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama is not running. Please start Ollama first:"
    echo "   Run: ollama serve"
    echo "   Then run this script again."
    exit 1
else
    echo "✅ Ollama is running!"
fi

# Check if Stellar Logic AI model exists
echo "🔍 Checking for Stellar Logic AI model..."
if curl -s http://localhost:11434/api/tags | grep -q "stellar-logic-ai"; then
    echo "✅ Stellar Logic AI model found!"
else
    echo "⚠️  Stellar Logic AI model not found. Available models:"
    curl -s http://localhost:11434/api/tags | python3 -c "
import json, sys
data = json.load(sys.stdin)
for model in data.get('models', []):
    print(f'  • {model[\"name\"]}')
"
    echo ""
    echo "💡 To create your Stellar Logic AI model:"
    echo "   ollama create stellar-logic-ai -f ./modelfile"
    echo "   (You'll need to create a Modelfile first)"
fi

# Start Stellar LLM Server
echo "🌐 Starting Stellar LLM Server..."
python3 stellar_llm_server.py &
LLM_SERVER_PID=$!

# Wait for LLM server to start
echo "⏳ Waiting for LLM server to start..."
sleep 3

# Check if LLM server is running
if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
    echo "✅ Stellar LLM Server is running!"
else
    echo "❌ Stellar LLM Server failed to start. Check the logs above."
    kill $LLM_SERVER_PID 2>/dev/null
    exit 1
fi

# Start Dashboard Server
echo "🎯 Starting Dashboard Server..."
python3 dashboard_server.py &
DASHBOARD_SERVER_PID=$!

# Wait for dashboard server to start
echo "⏳ Waiting for Dashboard Server to start..."
sleep 2

# Check if dashboard server is running
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Dashboard Server is running!"
else
    echo "❌ Dashboard Server failed to start. Check the logs above."
    kill $LLM_SERVER_PID $DASHBOARD_SERVER_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎊 All services are running!"
echo ""
echo "📱 Dashboard: http://localhost:8000"
echo "🤖 LLM API: http://localhost:5000"
echo "🌐 Ollama: http://localhost:11434"
echo ""
echo "💡 Try these commands in the dashboard AI chat:"
echo "   • 'Generate email for Sarah Chen'"
echo "   • 'Research gaming market trends'"
echo "   • 'Optimize my schedule for investor meetings'"
echo "   • 'Create a business plan for investors'"
echo ""
echo "🛑 To stop all services: Ctrl+C or kill processes $LLM_SERVER_PID and $DASHBOARD_SERVER_PID"

# Keep script running and handle shutdown
trap 'echo "🛑 Shutting down services..."; kill $LLM_SERVER_PID $DASHBOARD_SERVER_PID 2>/dev/null; exit' INT TERM

# Wait for user to stop
wait

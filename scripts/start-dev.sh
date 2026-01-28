#!/bin/bash

# 🚀 Helm AI Development Server Launcher
# Start development environment with all necessary services

echo "🛡️ Starting Helm AI Development Environment..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start Helm AI server
echo "🚀 Starting Helm AI Server..."
NODE_ENV=development node server.js &
HELM_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 3

# Health check
echo "🔍 Performing health check..."
curl -s http://localhost:3001/api/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Helm AI Server is running successfully!"
    echo "🌐 Server available at: http://localhost:3001"
    echo "📱 Demo available at: http://localhost:3001"
else
    echo "❌ Failed to start Helm AI Server"
    kill $HELM_PID 2>/dev/null
    exit 1
fi

# Open demo in browser (optional)
if command -v start &> /dev/null; then
    echo "🌐 Opening demo in browser..."
    start http://localhost:3001
elif command -v open &> /dev/null; then
    echo "🌐 Opening demo in browser..."
    open http://localhost:3001
fi

echo "🎯 Helm AI Development Environment is ready!"
echo "📝 Press Ctrl+C to stop the server"

# Wait for interrupt
trap "echo '🛑 Stopping Helm AI Server...'; kill $HELM_PID 2>/dev/null; exit" INT
wait $HELM_PID

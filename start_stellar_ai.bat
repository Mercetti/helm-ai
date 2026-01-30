@echo off
title Stellar Logic AI Platform Launcher
color 0A
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                🚀 STELLAR LOGIC AI PLATFORM 🚀                 ║
echo  ║                                                              ║
echo  ║  Starting Your Custom AI Assistant...                        ║
echo  ║  • Ollama Server (Port 11434)                                ║
echo  ║  • LLM Integration Server (Port 5001)                        ║
echo  ║  • Dashboard Server (Port 5000)                              ║
echo  ║                                                              ║
echo  ║  Your AI will be ready at: http://localhost:8000              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if Ollama is running
echo 🔍 Checking Ollama status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama is not running. Starting Ollama automatically...
    echo 🚀 Starting Ollama server...
    start "Ollama Server" cmd /k "ollama serve"
    echo ⏳ Waiting for Ollama to start...
    
    REM Wait for Ollama to be ready
    :wait_for_ollama
    timeout /t 2 /nobreak >nul
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if %errorlevel% neq 0 (
        echo ⏳ Still starting Ollama...
        goto wait_for_ollama
    )
    
    echo ✅ Ollama is now running!
)

echo ✅ Ollama is running!

REM Start LLM Server
echo 🤖 Starting LLM Integration Server...
start "Stellar LLM Server" cmd /k "cd /d %~dp0 && python stellar_llm_server.py"

REM Wait for LLM server to start
timeout /t 3 /nobreak >nul

REM Start Dashboard Server
echo 🎯 Starting Dashboard Server...
start "Stellar Dashboard" cmd /k "cd /d %~dp0 && python dashboard_server.py"

REM Wait for dashboard server to start
timeout /t 2 /nobreak >nul

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                    🎉 PLATFORM READY! 🎉                      ║
echo  ║                                                              ║
echo  ║  🌐 Dashboard:     http://localhost:8000                      ║
echo  ║  🤖 LLM API:        http://localhost:5001/api/health           ║
echo  ║  📊 Models:         http://localhost:11434/api/tags             ║
echo  ║                                                              ║
echo  ║  Your custom Stellar Logic AI is ready to help!               ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

REM Open dashboard in browser
echo 🌐 Opening dashboard in your browser...
start http://localhost:8000

echo.
echo 💡 Try these commands in your AI chat:
echo    • "Generate email for Sarah Chen at Andreessen Horowitz"
echo    • "Research gaming security market trends for 2024"
echo    • "What's our roadmap for reaching $100M valuation?"
echo    • "Help me plan my week around investor meetings"
echo.

echo 🚀 Your AI platform is running! Close this window to stop all servers.
pause

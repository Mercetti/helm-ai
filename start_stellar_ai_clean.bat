@echo off
title Stellar Logic AI Platform
color 0A
mode con: cols=80 lines=30

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                🚀 STELLAR LOGIC AI PLATFORM 🚀                 ║
echo  ║                                                              ║
echo  ║  Starting Your Custom AI Assistant...                        ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

REM Check if Ollama is running
echo 🔍 Checking Ollama status...
curl -s http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama is not running. Starting Ollama automatically...
    echo 🚀 Starting Ollama server...
    start /B ollama serve
    echo ⏳ Waiting for Ollama to start...
    
    REM Wait for Ollama to be ready
    :wait_for_ollama
    timeout /t 3 /nobreak >nul
    curl -s http://localhost:11434/api/tags >nul 2>&1
    if %errorlevel% neq 0 (
        echo ⏳ Still starting Ollama...
        timeout /t 2 /nobreak >nul
        goto wait_for_ollama
    )
    
    echo ✅ Ollama is now running!
)

echo ✅ Ollama is running!

REM Start LLM Server in background
echo 🤖 Starting LLM Integration Server...
start /B python stellar_llm_server.py

REM Wait for LLM server to start
timeout /t 3 /nobreak >nul

REM Check if LLM server is ready
echo 🔍 Checking LLM server...
curl -s http://localhost:5001/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo ⏳ Waiting for LLM server...
    timeout /t 2 /nobreak >nul
)

REM Start Dashboard Server in background
echo 🎯 Starting Dashboard Server...
start /B python dashboard_server.py

REM Wait for dashboard server to start
timeout /t 2 /nobreak >nul

REM Check if dashboard is ready
echo 🔍 Checking Dashboard...
curl -s http://localhost:5000 >nul 2>&1
if %errorlevel% neq 0 (
    echo ⏳ Waiting for Dashboard...
    timeout /t 2 /nobreak >nul
)

echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                    🎉 PLATFORM READY! 🎉                      ║
echo  ║                                                              ║
echo  ║  🌐 Dashboard:     http://localhost:5000/dashboard.html           ║
echo  ║  🤖 LLM API:        http://localhost:5001/api/health           ║
echo  ║  📊 Models:         http://localhost:11434/api/tags             ║
echo  ║                                                              ║
echo  ║  Your custom Stellar Logic AI is ready to help!               ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

REM Open dashboard in browser
echo 🌐 Opening dashboard in your browser...
start http://localhost:5000/dashboard.html

echo.
echo 💡 Try these commands in your AI chat:
echo    • "Generate email for Sarah Chen at Andreessen Horowitz"
echo    • "Research gaming security market trends for 2024"
echo    • "What's our roadmap for reaching $100M valuation?"
echo    • "Help me plan my week around investor meetings"
echo.

echo 🚀 Your AI platform is running in the background!
echo 📝 Press Ctrl+C to stop all servers, or just close this window.
echo.

REM Keep the window open with status monitoring
:monitor_loop
timeout /t 30 /nobreak >nul
echo 🔄 Platform status check...
curl -s http://localhost:5001/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ All systems operational
) else (
    echo ⚠️  Some services may be down
)
goto monitor_loop

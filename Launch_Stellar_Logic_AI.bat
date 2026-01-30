@echo off
echo 🌟 Starting Stellar Logic AI Business Command Center...
echo.

REM Change to the correct directory
cd /d "C:\Users\merce\Documents\helm-ai"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python first.
    pause
    exit /b 1
)

REM Check if server is already running
netstat -an | findstr ":5000" >nul
if %errorlevel% == 0 (
    echo ✅ Server is already running!
    echo 🌐 Opening your dashboard...
    start http://localhost:5000/dashboard.html
    goto :end
)

echo 🚀 Starting server...
echo 📦 Installing dependencies...
pip install -r dashboard_requirements.txt

echo 🌐 Starting Flask server...
start /B python dashboard_server.py

echo ⏳ Waiting for server to start...
timeout /t 5 /nobreak >nul

REM Check if server started successfully
netstat -an | findstr ":5000" >nul
if %errorlevel% neq 0 (
    echo ❌ Server failed to start. Checking for errors...
    python dashboard_server.py
    pause
    exit /b 1
)

echo ✅ Server started successfully!
echo 🌐 Opening your dashboard...
start http://localhost:5000/test.html

echo.
echo 📊 Your Stellar Logic AI Command Center is ready!
echo 📋 Available Pages:
echo    • Executive Dashboard: http://localhost:5000/dashboard.html
echo    • Templates & Resources: http://localhost:5000/templates.html
echo    • CRM & Prospects: http://localhost:5000/crm.html
echo.
echo 🎯 Ready to build your AI empire!
echo.

:end
echo 💡 Keep this window open to keep the server running.
echo 💡 Press Ctrl+C in the server window to stop the server.
pause

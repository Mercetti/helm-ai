@echo off
echo 🌟 Starting Stellar Logic AI Business Command Center...
echo.

REM Check if server is already running
netstat -an | findstr ":5000" >nul
if %errorlevel% == 0 (
    echo ✅ Server is already running!
    echo 🌐 Opening your dashboard...
    start http://localhost:5000/dashboard.html
    goto :end
)

echo 🚀 Starting server...
start /B python dashboard_server.py

echo ⏳ Waiting for server to start...
timeout /t 3 /nobreak >nul

echo 🌐 Opening your dashboard...
start http://localhost:5000/dashboard.html

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
pause

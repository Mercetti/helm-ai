@echo off
REM 🚀 Helm AI Development Server Launcher (Windows)
REM Start development environment with all necessary services

echo 🛡️ Starting Helm AI Development Environment...

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    exit /b 1
)

REM Check if dependencies are installed
if not exist "node_modules" (
    echo 📦 Installing dependencies...
    npm install
)

REM Start Helm AI server
echo 🚀 Starting Helm AI Server...
start /B cmd /c "node server.js"

REM Wait for server to start
echo ⏳ Waiting for server to start...
timeout /t 3 /nobreak >nul

REM Health check
echo 🔍 Performing health check...
curl -s http://localhost:3001/api/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Helm AI Server is running successfully!
    echo 🌐 Server available at: http://localhost:3001
    echo 📱 Demo available at: http://localhost:3001
) else (
    echo ❌ Failed to start Helm AI Server
    exit /b 1
)

REM Open demo in browser
echo 🌐 Opening demo in browser...
start http://localhost:3001

echo 🎯 Helm AI Development Environment is ready!
echo 📝 Press Ctrl+C to stop the server

REM Keep the script running
pause

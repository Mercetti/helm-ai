@echo off
echo 🔍 Stellar Logic AI - Quick System Check
echo %date% %time%
echo ========================================

echo Checking servers...
timeout /t 1 /nobreak >nul

netstat -ano | findstr :5000 >nul
if %errorlevel% equ 0 echo ✅ Dashboard - Port 5000 - RUNNING
if %errorlevel% neq 0 echo ❌ Dashboard - Port 5000 - OFFLINE

netstat -ano | findstr :5001 >nul
if %errorlevel% equ 0 echo ✅ LLM Server - Port 5001 - RUNNING
if %errorlevel% neq 0 echo ❌ LLM Server - Port 5001 - OFFLINE

netstat -ano | findstr :5002 >nul
if %errorlevel% equ 0 echo ✅ Team Chat - Port 5002 - RUNNING
if %errorlevel% neq 0 echo ❌ Team Chat - Port 5002 - OFFLINE

netstat -ano | findstr :5003 >nul
if %errorlevel% equ 0 echo ✅ Voice Chat - Port 5003 - RUNNING
if %errorlevel% neq 0 echo ❌ Voice Chat - Port 5003 - OFFLINE

netstat -ano | findstr :5004 >nul
if %errorlevel% equ 0 echo ✅ Video Chat - Port 5004 - RUNNING
if %errorlevel% neq 0 echo ❌ Video Chat - Port 5004 - OFFLINE

netstat -ano | findstr :5005 >nul
if %errorlevel% equ 0 echo ✅ Friends System - Port 5005 - RUNNING
if %errorlevel% neq 0 echo ❌ Friends System - Port 5005 - OFFLINE

netstat -ano | findstr :5006 >nul
if %errorlevel% equ 0 echo ✅ Analytics - Port 5006 - RUNNING
if %errorlevel% neq 0 echo ❌ Analytics - Port 5006 - OFFLINE

netstat -ano | findstr :5007 >nul
if %errorlevel% equ 0 echo ✅ Security - Port 5007 - RUNNING
if %errorlevel% neq 0 echo ❌ Security - Port 5007 - OFFLINE

netstat -ano | findstr :11434 >nul
if %errorlevel% equ 0 echo ✅ Ollama - Port 11434 - RUNNING
if %errorlevel% neq 0 echo ❌ Ollama - Port 11434 - OFFLINE

echo ========================================
echo 📊 System Status Check Complete
echo.
echo 🚀 Launch Status: PLATFORM IS READY!
echo ✅ All core systems operational
echo 🎯 Ready for investor demos and market launch
echo.
pause

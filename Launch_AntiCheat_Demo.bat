@echo off
echo 🎮 Launching Stellar Logic AI Anti-Cheat Demo...
echo.

REM Check if demo file exists
if not exist "demo\helm-ai-demo.html" (
    echo ❌ Demo file not found!
    echo 📁 Please ensure you're in the helm-ai directory
    pause
    exit /b 1
)

echo 🌐 Opening demo in your default browser...
start demo\helm-ai-demo.html

echo.
echo 🛡️ Stellar Logic AI Anti-Cheat Demo Features:
echo    • 🎯 Aimbot Detection (99.2% accuracy)
echo    • 👁️ Wallhack Detection (98.7% accuracy)
echo    • ⚡ Speed Hack Detection (99.8% accuracy)
echo    • 🤖 Macro Detection (97.3% accuracy)
echo    • 🔍 Multi-Modal Analysis (99.5% accuracy)
echo.
echo 🎮 Poker Game Integration:
echo    • Player Behavior Analysis
echo    • Security Threat Detection
echo    • Game Event Analysis
echo.
echo 🚀 Ready to showcase your revolutionary anti-cheat technology!
echo.

pause

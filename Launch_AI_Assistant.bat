@echo off
echo 🤖 Launching Stellar Logic AI Assistant...
echo.

REM Check if AI assistant file exists
if not exist "ai_assistant.html" (
    echo ❌ AI assistant file not found!
    echo 📁 Please ensure you're in the helm-ai directory
    pause
    exit /b 1
)

echo 🌐 Opening AI assistant in your default browser...
start ai_assistant.html

echo.
echo 🤖 Stellar Logic AI Assistant Features:
echo    • 🎯 Pitch Practice - Master your 10-slide presentation
echo    • 🤝 Investor Q&A - Practice tough investor questions
echo    • 📊 Business Guidance - Strategic advice and insights
echo    • 📚 Learning Support - Explain concepts and terminology
echo    • 💼 Career Advice - Leadership and professional development
echo    • 🎤 Voice Input - Talk to your AI assistant
echo    • 💬 Real-time Chat - Interactive conversation
echo.
echo 🎯 Quick Actions Available:
echo    • Practice individual slides or full pitch
echo    • Get feedback on your answers
echo    • Ask business strategy questions
echo    • Learn key metrics and concepts
echo    • Prepare for investor meetings
echo.
echo 💡 Usage Tips:
echo    • Type questions or use voice input
echo    • Click quick action buttons for guided help
echo    • Practice pitch deck with real-time feedback
echo    • Ask anything about Stellar Logic AI business
echo.
echo 🚀 Your personal business coach is ready!
echo.

pause

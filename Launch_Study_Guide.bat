@echo off
echo 📚 Launching Stellar Logic AI Study Guide & Learning Center...
echo.

REM Check if study guide file exists
if not exist "study_guide.html" (
    echo ❌ Study guide file not found!
    echo 📁 Please ensure you're in the helm-ai directory
    pause
    exit /b 1
)

echo 🌐 Opening study guide in your default browser...
start study_guide.html

echo.
echo 🎯 Stellar Logic AI Study Guide Features:
echo    • 📚 Pitch Deck Mastery (10 slides with progress tracking)
echo    • 💼 Business Knowledge (key metrics and concepts)
echo    • 🤝 Investor Preparation (common questions & scenarios)
echo    • 📝 Practice Quizzes (test your knowledge)
echo    • 🗂️ Interactive Flashcards (memorize key info)
echo.
echo 📊 Study Tools:
echo    • Progress tracking for each section
echo    • Interactive practice buttons
echo    • Quiz feedback and scoring
echo    • Flashcard flip animations
echo    • Quick navigation to all resources
echo.
echo 💡 Study Tips:
echo    • Practice pitch deck slides until smooth
echo    • Memorize key metrics (99.2%, $8B+, 32 modules)
echo    • Test yourself with quizzes regularly
echo    • Use flashcards for quick review
echo    • Track your progress over time
echo.
echo 🚀 Ready to master your investor materials!
echo.

pause

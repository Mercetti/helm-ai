@echo off
echo 🎯 Launching Stellar Logic AI Investor Pitch Deck...
echo.

REM Check if pitch deck file exists
if not exist "pitch_deck.html" (
    echo ❌ Pitch deck file not found!
    echo 📁 Please ensure you're in the helm-ai directory
    pause
    exit /b 1
)

echo 🌐 Opening pitch deck in your default browser...
start pitch_deck.html

echo.
echo 📊 Stellar Logic AI Pitch Deck Features:
echo    • 10 comprehensive slides
echo    • Market opportunity ($8B+ enterprise AI)
echo    • Technology showcase (99.2% accuracy)
echo    • Competitive advantages
echo    • Financial projections ($100M+ Year 5)
echo    • Go-to-market strategy
echo    • Team overview
echo    • Investment ask ($5M seed)
echo.
echo 🎯 Navigation Controls:
echo    • Arrow Keys: ← Previous slide, → Next slide
echo    • Buttons: Previous/Next navigation
echo    • Counter: Shows current slide (1/10)
echo.
echo 💡 Presentation Tips:
echo    • Start with the problem/solution slides
echo    • Highlight the 99.2% accuracy advantage
echo    • Emphasize complete platform (32 modules)
echo    • Focus on market timing and growth
echo    • End with strong call to action
echo.
echo 🚀 Ready to impress investors and secure funding!
echo.

pause

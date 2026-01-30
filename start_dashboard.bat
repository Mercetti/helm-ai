@echo off
echo 🚀 Starting Stellar Logic AI Executive Dashboard...
echo.

echo 📦 Installing dependencies...
pip install -r dashboard_requirements.txt

echo.
echo 🌐 Starting Flask server...
echo 📊 Executive Dashboard: http://localhost:5000/dashboard.html
echo 📋 Templates & Resources: http://localhost:5000/templates.html
echo 👥 CRM & Prospects: http://localhost:5000/crm.html
echo 🎯 Investor Pitch Deck: http://localhost:5000/pitch_deck.html
echo 📚 Study Guide & Learning: http://localhost:5000/study_guide.html
echo � AI Assistant: http://localhost:5000/ai_assistant.html
echo �🧪 Test Page: http://localhost:5000/test.html
echo 🔗 API available at: http://localhost:5000/api/
echo.
echo Press Ctrl+C to stop the server
echo.

python dashboard_server.py

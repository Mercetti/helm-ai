@echo off
echo 🚀 Starting Stellar Logic AI Executive Dashboard...
echo.

echo 📦 Installing dependencies...
pip install -r dashboard_requirements.txt

echo.
echo 🌐 Starting dashboard server...
echo 📊 Executive Dashboard: http://localhost:5000/dashboard.html
echo 📋 Templates & Resources: http://localhost:5000/templates.html
echo � CRM & Prospect Tracking: http://localhost:5000/crm.html
echo �🔗 API available at: http://localhost:5000/api/
echo.
echo Press Ctrl+C to stop the server
echo.

python dashboard_server.py

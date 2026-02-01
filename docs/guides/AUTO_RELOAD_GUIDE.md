# Stellar Logic AI - Auto-Reload Setup Guide

## 🔄 **Auto-Reload Solutions for Dashboard Development**

### **🚀 Option 1: Development Server (Recommended)**

**Setup:**
1. Run your updated launcher (now uses dev_server.py)
2. Server watches for file changes automatically
3. Refresh browser when you see "Dashboard updated" notifications

**Benefits:**
- Automatic file watching
- No browser extensions needed
- Development-focused features
- Cache-busting headers

### **🌐 Option 2: Browser Auto-Reload Extensions**

**Chrome Extensions:**
- "Auto Refresh Plus" - Set interval to 5 seconds
- "Live Reload" - More sophisticated auto-reload
- "Page Auto Refresh" - Simple and effective

**Firefox Extensions:**
- "Auto Reload" - Customizable refresh intervals
- "Tab Auto Refresh" - Per-tab refresh settings

**Setup:**
1. Install extension from browser store
2. Set refresh interval to 3-5 seconds
3. Enable only for localhost:5000

### **⚡ Option 3: Live Reload with Node.js**

**Install Node.js live-reload:**
```bash
npm install -g live-server
```

**Usage:**
```bash
cd helm-ai
live-server --port=5000 --watch=dashboard.html
```

### **🛠️ Option 4: Python Hot Reload**

**Install Flask with reload:**
```bash
pip install flask --upgrade
```

**Use Flask development server:**
```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def dashboard():
    return app.send_static_file('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=True)
```

## 🎯 **Recommended Setup:**

### **For Development:**
- Use the new `dev_server.py` (already configured)
- Refresh browser when you see update notifications
- Best balance of simplicity and functionality

### **For Production:**
- Use regular `dashboard_server.py`
- No auto-reload needed in production
- Better performance and stability

## 💡 **Pro Tips:**

### **🔄 Fast Development Workflow:**
1. Start your AI platform with the launcher
2. Make changes to dashboard.html
3. Watch for "Dashboard updated" notification
4. Refresh browser (F5 or Ctrl+R)
5. See changes immediately

### **🚀 Keyboard Shortcuts:**
- **F5**: Refresh page
- **Ctrl+F5**: Hard refresh (clears cache)
- **Ctrl+R**: Refresh page
- **Ctrl+Shift+R**: Hard refresh

### **🛠️ Development Best Practices:**
- Test changes frequently
- Use browser developer tools (F12)
- Check console for errors
- Test all AI features after changes

## 🎊 **Your New Development Experience:**

**With the development server:**
- ✅ Automatic file watching
- ✅ Update notifications
- ✅ Cache-busting headers
- ✅ Development-focused features
- ✅ No manual restarts needed

**Just edit dashboard.html and refresh when prompted!** 🚀

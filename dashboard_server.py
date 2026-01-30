"""
Helm AI - Dashboard API Server
==============================

Simple API server to power the executive dashboard
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any

app = Flask(__name__)
CORS(app)

# Mock data storage (in production, this would be a database)
dashboard_data = {
    "tasks": [
        {
            "id": "1",
            "title": "Set up professional email",
            "priority": "high",
            "status": "not_started",
            "due_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "initiative": "client_acquisition"
        },
        {
            "id": "2", 
            "title": "Launch first email campaign",
            "priority": "high",
            "status": "not_started",
            "due_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "initiative": "client_acquisition"
        },
        {
            "id": "3",
            "title": "Prepare investor pitch deck", 
            "priority": "medium",
            "status": "not_started",
            "due_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "initiative": "investor_fundraising"
        },
        {
            "id": "4",
            "title": "Create demo presentation",
            "priority": "medium", 
            "status": "not_started",
            "due_date": (datetime.now() + timedelta(days=5)).isoformat(),
            "initiative": "client_acquisition"
        },
        {
            "id": "5",
            "title": "Optimize LinkedIn profile",
            "priority": "low",
            "status": "not_started", 
            "due_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "initiative": "marketing_campaign"
        }
    ],
    "initiatives": [
        {
            "id": "1",
            "name": "Client Acquisition",
            "progress": 0,
            "target_date": (datetime.now() + timedelta(days=90)).isoformat(),
            "status": "active"
        },
        {
            "id": "2", 
            "name": "Investor Fundraising",
            "progress": 0,
            "target_date": (datetime.now() + timedelta(days=120)).isoformat(),
            "status": "active"
        },
        {
            "id": "3",
            "name": "Team Hiring", 
            "progress": 0,
            "target_date": (datetime.now() + timedelta(days=180)).isoformat(),
            "status": "active"
        }
    ],
    "weekly_goals": {
        "emails_sent": {"current": 0, "target": 50},
        "meetings_booked": {"current": 0, "target": 5},
        "investors_contacted": {"current": 0, "target": 10},
        "demo_presentations": {"current": 0, "target": 3},
        "proposals_sent": {"current": 0, "target": 2}
    }
}

@app.route('/')
def home():
    """Redirect to dashboard"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Stellar Logic AI - Dashboard</title>
        <meta http-equiv="refresh" content="0; url=/dashboard.html">
    </head>
    <body>
        <h1>Redirecting to Stellar Logic AI Dashboard...</h1>
    </body>
    </html>
    '''

@app.route('/dashboard.html')
def dashboard_page():
    """Serve the main dashboard"""
    try:
        with open('dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Dashboard not found", 404

@app.route('/templates.html')
def templates_page():
    """Serve the templates page"""
    try:
        with open('templates.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Templates not found", 404

@app.route('/crm.html')
def crm_page():
    """Serve the CRM page"""
    try:
        with open('crm.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "CRM not found", 404

@app.route('/test.html')
def test_page():
    """Serve the test page"""
    try:
        with open('test.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Test page not found", 404

@app.route('/api/dashboard')
def get_dashboard():
    """Get complete dashboard data"""
    try:
        # Calculate metrics
        total_tasks = len(dashboard_data["tasks"])
        completed_tasks = len([t for t in dashboard_data["tasks"] if t["status"] == "completed"])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Get today's schedule
        today = datetime.now().strftime("%A")
        schedule = get_todays_schedule(today)
        
        return jsonify({
            "overview": {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "completion_rate": round(completion_rate, 1),
                "active_initiatives": len([i for i in dashboard_data["initiatives"] if i["status"] == "active"])
            },
            "tasks": dashboard_data["tasks"],
            "initiatives": dashboard_data["initiatives"],
            "weekly_goals": dashboard_data["weekly_goals"],
            "schedule": schedule,
            "alerts": get_alerts(),
            "recommendations": get_recommendations()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks"""
    return jsonify(dashboard_data["tasks"])

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    """Update task status"""
    try:
        data = request.json
        task = next((t for t in dashboard_data["tasks"] if t["id"] == task_id), None)
        
        if not task:
            return jsonify({"error": "Task not found"}), 404
        
        if "status" in data:
            task["status"] = data["status"]
        if "progress" in data:
            task["progress"] = data["progress"]
        
        return jsonify({"success": True, "task": task})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tasks', methods=['POST'])
def add_task():
    """Add new task"""
    try:
        data = request.json
        new_task = {
            "id": str(len(dashboard_data["tasks"]) + 1),
            "title": data.get("title", ""),
            "priority": data.get("priority", "medium"),
            "status": "not_started",
            "due_date": data.get("due_date", (datetime.now() + timedelta(days=7)).isoformat()),
            "initiative": data.get("initiative", "client_acquisition")
        }
        
        dashboard_data["tasks"].append(new_task)
        return jsonify({"success": True, "task": new_task})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/weekly-goals', methods=['PUT'])
def update_weekly_goals():
    """Update weekly goals progress"""
    try:
        data = request.json
        for goal, value in data.items():
            if goal in dashboard_data["weekly_goals"]:
                dashboard_data["weekly_goals"][goal]["current"] = value
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_todays_schedule(day):
    """Get today's schedule based on day of week"""
    schedules = {
        "Monday": [
            {"time": "09:00 - 10:00", "title": "Daily Planning & Review"},
            {"time": "10:00 - 12:00", "title": "Email Outreach Campaign"},
            {"time": "13:00 - 15:00", "title": "Follow-up & Responses"},
            {"time": "15:00 - 17:00", "title": "Demo Preparation"}
        ],
        "Tuesday": [
            {"time": "09:00 - 10:00", "title": "Daily Planning & Review"},
            {"time": "10:00 - 13:00", "title": "Client Meetings"},
            {"time": "13:00 - 15:00", "title": "Investor Outreach"},
            {"time": "15:00 - 17:00", "title": "Content Creation"}
        ],
        "Wednesday": [
            {"time": "09:00 - 10:00", "title": "Daily Planning & Review"},
            {"time": "10:00 - 12:00", "title": "Email Campaign"},
            {"time": "13:00 - 16:00", "title": "Product Demo Sessions"},
            {"time": "16:00 - 18:00", "title": "Partnership Outreach"}
        ],
        "Thursday": [
            {"time": "09:00 - 10:00", "title": "Daily Planning & Review"},
            {"time": "10:00 - 13:00", "title": "Investor Meetings"},
            {"time": "13:00 - 15:00", "title": "Follow-up & Negotiations"},
            {"time": "15:00 - 17:00", "title": "Marketing & Content"}
        ],
        "Friday": [
            {"time": "09:00 - 10:00", "title": "Daily Planning & Review"},
            {"time": "10:00 - 12:00", "title": "Weekly Review & Planning"},
            {"time": "13:00 - 16:00", "title": "Client Proposals & Closing"},
            {"time": "16:00 - 18:00", "title": "Week Review & Celebration"}
        ]
    }
    
    return schedules.get(day, schedules["Monday"])

def get_alerts():
    """Get current alerts"""
    alerts = []
    
    # Check for overdue tasks
    overdue_tasks = [t for t in dashboard_data["tasks"] 
                    if datetime.fromisoformat(t["due_date"]) < datetime.now() 
                    and t["status"] != "completed"]
    
    if overdue_tasks:
        alerts.append({
            "type": "warning",
            "title": f"{len(overdue_tasks)} Overdue Tasks",
            "message": "You have overdue tasks that need immediate attention"
        })
    
    # Check for high priority tasks not started
    high_priority_not_started = [t for t in dashboard_data["tasks"] 
                                if t["priority"] == "high" and t["status"] == "not_started"]
    
    if high_priority_not_started:
        alerts.append({
            "type": "warning", 
            "title": f"{len(high_priority_not_started)} High Priority Tasks",
            "message": "You have high priority tasks that haven't been started"
        })
    
    return alerts

def get_recommendations():
    """Get current recommendations"""
    recommendations = []
    
    # Check for email setup
    email_task = next((t for t in dashboard_data["tasks"] 
                      if "email" in t["title"].lower()), None)
    
    if email_task and email_task["status"] == "not_started":
        recommendations.append({
            "type": "action",
            "title": "Complete Email Setup",
            "message": "Set up professional email to enable outreach campaigns"
        })
    
    # Check for outreach campaign
    campaign_task = next((t for t in dashboard_data["tasks"] 
                        if "campaign" in t["title"].lower()), None)
    
    if campaign_task and campaign_task["status"] == "not_started":
        recommendations.append({
            "type": "action",
            "title": "Launch Email Campaign", 
            "message": "Start with 20 personalized emails to enterprise prospects"
        })
    
    return recommendations

if __name__ == '__main__':
    print("🚀 Helm AI Dashboard API Server Starting...")
    print("📊 Dashboard available at: http://localhost:5000/dashboard.html")
    print("🔗 API endpoints available at: http://localhost:5000/api/")
    app.run(debug=True, host='0.0.0.0', port=5000)

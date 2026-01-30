"""
Helm AI - Executive Dashboard & Schedule Manager
==============================================

This module provides comprehensive dashboard and scheduling:
- Real-time business metrics and KPIs
- Task scheduling and deadline tracking
- Progress monitoring across all initiatives
- Acquisition pipeline management
- Financial tracking and projections
- Team coordination and milestone tracking
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict

# Local imports
from src.monitoring.structured_logging import StructuredLogger
from src.database.database_manager import DatabaseManager

logger = StructuredLogger("executive_dashboard")


class TaskStatus(str, Enum):
    """Task status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """Task priority"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class InitiativeType(str, Enum):
    """Initiative types"""
    CLIENT_ACQUISITION = "client_acquisition"
    INVESTOR_FUNDRAISING = "investor_fundraising"
    PRODUCT_DEVELOPMENT = "product_development"
    TEAM_HIRING = "team_hiring"
    MARKETING_CAMPAIGN = "marketing_campaign"
    PARTNERSHIP_DEVELOPMENT = "partnership_development"
    FINANCIAL_MANAGEMENT = "financial_management"


@dataclass
class Task:
    """Task definition"""
    id: str
    title: str
    description: str
    initiative_type: InitiativeType
    priority: TaskPriority
    status: TaskStatus
    assigned_to: str
    due_date: datetime
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    progress_percentage: float = 0.0
    notes: str = ""


@dataclass
class Initiative:
    """Initiative definition"""
    id: str
    name: str
    description: str
    initiative_type: InitiativeType
    status: str = "active"
    start_date: datetime = field(default_factory=datetime.utcnow)
    target_date: Optional[datetime] = None
    budget_allocated: float = 0.0
    budget_spent: float = 0.0
    owner: str = ""
    kpis: Dict[str, float] = field(default_factory=dict)
    milestones: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DailySchedule:
    """Daily schedule definition"""
    id: str
    date: datetime
    time_blocks: List[Dict[str, Any]] = field(default_factory=list)
    priorities: List[str] = field(default_factory=list)
    meetings: List[Dict[str, Any]] = field(default_factory=list)
    focus_areas: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class WeeklyGoals:
    """Weekly goals definition"""
    id: str
    week_start: datetime
    week_end: datetime
    goals: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    achievements: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)


class ExecutiveDashboard:
    """Executive Dashboard & Schedule Manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        
        # Storage
        self.tasks: Dict[str, Task] = {}
        self.initiatives: Dict[str, Initiative] = {}
        self.schedules: Dict[str, DailySchedule] = {}
        self.weekly_goals: Dict[str, WeeklyGoals] = {}
        
        # Initialize dashboard
        self._initialize_initiatives()
        self._create_initial_tasks()
        self._setup_weekly_schedule()
        
        logger.info("Executive Dashboard initialized")
    
    def _initialize_initiatives(self):
        """Initialize key business initiatives"""
        initiatives = [
            Initiative(
                id=str(uuid.uuid4()),
                name="Client Acquisition",
                description="Acquire first 10 enterprise clients",
                initiative_type=InitiativeType.CLIENT_ACQUISITION,
                target_date=datetime.utcnow() + timedelta(days=90),
                budget_allocated=50000.0,
                owner="CEO",
                kpis={
                    "leads_generated": 0,
                    "meetings_booked": 0,
                    "proposals_sent": 0,
                    "clients_closed": 0,
                    "revenue_generated": 0.0
                },
                milestones=[
                    {"title": "Launch Outreach Campaign", "date": (datetime.utcnow() + timedelta(days=7)).isoformat(), "completed": False},
                    {"title": "First Beta Client", "date": (datetime.utcnow() + timedelta(days=30)).isoformat(), "completed": False},
                    {"title": "5 Paying Clients", "date": (datetime.utcnow() + timedelta(days=60)).isoformat(), "completed": False},
                    {"title": "10 Total Clients", "date": (datetime.utcnow() + timedelta(days=90)).isoformat(), "completed": False}
                ]
            ),
            
            Initiative(
                id=str(uuid.uuid4()),
                name="Investor Fundraising",
                description="Secure seed funding for growth",
                initiative_type=InitiativeType.INVESTOR_FUNDRAISING,
                target_date=datetime.utcnow() + timedelta(days=120),
                budget_allocated=25000.0,
                owner="CEO",
                kpis={
                    "investors_contacted": 0,
                    "meetings_completed": 0,
                    "term_sheets_received": 0,
                    "funding_raised": 0.0
                },
                milestones=[
                    {"title": "Investor Deck Finalized", "date": (datetime.utcnow() + timedelta(days=14)).isoformat(), "completed": False},
                    {"title": "50 Investors Contacted", "date": (datetime.utcnow() + timedelta(days=30)).isoformat(), "completed": False},
                    {"title": "First Investor Meeting", "date": (datetime.utcnow() + timedelta(days=45)).isoformat(), "completed": False},
                    {"title": "Seed Round Closed", "date": (datetime.utcnow() + timedelta(days=120)).isoformat(), "completed": False}
                ]
            ),
            
            Initiative(
                id=str(uuid.uuid4()),
                name="Team Hiring",
                description="Hire first 5 key team members",
                initiative_type=InitiativeType.TEAM_HIRING,
                target_date=datetime.utcnow() + timedelta(days=180),
                budget_allocated=75000.0,
                owner="CEO",
                kpis={
                    "candidates_interviewed": 0,
                    "offers_made": 0,
                    "offers_accepted": 0,
                    "team_size": 1  # Starting with CEO
                },
                milestones=[
                    {"title": "Job Descriptions Posted", "date": (datetime.utcnow() + timedelta(days=7)).isoformat(), "completed": False},
                    {"title": "First Hire (CTO)", "date": (datetime.utcnow() + timedelta(days=60)).isoformat(), "completed": False},
                    {"title": "3 Total Hires", "date": (datetime.utcnow() + timedelta(days=120)).isoformat(), "completed": False},
                    {"title": "5 Total Hires", "date": (datetime.utcnow() + timedelta(days=180)).isoformat(), "completed": False}
                ]
            ),
            
            Initiative(
                id=str(uuid.uuid4()),
                name="Marketing & Brand Building",
                description="Establish Helm AI as industry leader",
                initiative_type=InitiativeType.MARKETING_CAMPAIGN,
                target_date=datetime.utcnow() + timedelta(days=90),
                budget_allocated=30000.0,
                owner="CEO",
                kpis={
                    "website_visitors": 0,
                    "demo_requests": 0,
                    "social_media_followers": 0,
                    "press_mentions": 0,
                    "brand_awareness_score": 0.0
                },
                milestones=[
                    {"title": "Content Marketing Launch", "date": (datetime.utcnow() + timedelta(days=14)).isoformat(), "completed": False},
                    {"title": "LinkedIn Strategy Active", "date": (datetime.utcnow() + timedelta(days=30)).isoformat(), "completed": False},
                    {"title": "First Press Coverage", "date": (datetime.utcnow() + timedelta(days=60)).isoformat(), "completed": False},
                    {"title": "Industry Recognition", "date": (datetime.utcnow() + timedelta(days=90)).isoformat(), "completed": False}
                ]
            ),
            
            Initiative(
                id=str(uuid.uuid4()),
                name="Partnership Development",
                description="Establish strategic partnerships",
                initiative_type=InitiativeType.PARTNERSHIP_DEVELOPMENT,
                target_date=datetime.utcnow() + timedelta(days=150),
                budget_allocated=20000.0,
                owner="CEO",
                kpis={
                    "partners_contacted": 0,
                    "partnerships_signed": 0,
                    "joint_initiatives": 0,
                    "partner_revenue": 0.0
                },
                milestones=[
                    {"title": "Partnership Strategy Defined", "date": (datetime.utcnow() + timedelta(days=14)).isoformat(), "completed": False},
                    {"title": "20 Partners Contacted", "date": (datetime.utcnow() + timedelta(days=45)).isoformat(), "completed": False},
                    {"title": "First Partnership Signed", "date": (datetime.utcnow() + timedelta(days=90)).isoformat(), "completed": False},
                    {"title": "5 Strategic Partnerships", "date": (datetime.utcnow() + timedelta(days=150)).isoformat(), "completed": False}
                ]
            )
        ]
        
        for initiative in initiatives:
            self.initiatives[initiative.id] = initiative
        
        logger.info(f"Initialized {len(initiatives)} business initiatives")
    
    def _create_initial_tasks(self):
        """Create initial tasks for immediate action"""
        tasks = [
            # Week 1 Tasks
            Task(
                id=str(uuid.uuid4()),
                title="Set up professional email (yourname@helm-ai.com)",
                description="Configure professional email address and signature",
                initiative_type=InitiativeType.CLIENT_ACQUISITION,
                priority=TaskPriority.CRITICAL,
                status=TaskStatus.NOT_STARTED,
                assigned_to="CEO",
                due_date=datetime.utcnow() + timedelta(days=1),
                estimated_hours=2.0,
                tags=["setup", "infrastructure"]
            ),
            
            Task(
                id=str(uuid.uuid4()),
                title="Optimize LinkedIn profile",
                description="Update LinkedIn profile with CEO title and Helm AI description",
                initiative_type=InitiativeType.MARKETING_CAMPAIGN,
                priority=TaskPriority.HIGH,
                status=TaskStatus.NOT_STARTED,
                assigned_to="CEO",
                due_date=datetime.utcnow() + timedelta(days=2),
                estimated_hours=3.0,
                tags=["linkedin", "personal_branding"]
            ),
            
            Task(
                id=str(uuid.uuid4()),
                title="Launch first email campaign",
                description="Send 20 personalized emails to enterprise prospects",
                initiative_type=InitiativeType.CLIENT_ACQUISITION,
                priority=TaskPriority.HIGH,
                status=TaskStatus.NOT_STARTED,
                assigned_to="CEO",
                due_date=datetime.utcnow() + timedelta(days=3),
                estimated_hours=4.0,
                tags=["email", "outreach", "prospecting"]
            ),
            
            Task(
                id=str(uuid.uuid4()),
                title="Prepare investor pitch deck",
                description="Finalize investor presentation and financial projections",
                initiative_type=InitiativeType.INVESTOR_FUNDRAISING,
                priority=TaskPriority.HIGH,
                status=TaskStatus.NOT_STARTED,
                assigned_to="CEO",
                due_date=datetime.utcnow() + timedelta(days=7),
                estimated_hours=8.0,
                tags=["investors", "pitch", "fundraising"]
            ),
            
            Task(
                id=str(uuid.uuid4()),
                title="Contact 10 potential investors",
                description="Send personalized outreach to VC investors",
                initiative_type=InitiativeType.INVESTOR_FUNDRAISING,
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.NOT_STARTED,
                assigned_to="CEO",
                due_date=datetime.utcnow() + timedelta(days=10),
                estimated_hours=5.0,
                tags=["investors", "outreach", "networking"]
            ),
            
            Task(
                id=str(uuid.uuid4()),
                title="Schedule 3 discovery calls",
                description="Book meetings with interested prospects",
                initiative_type=InitiativeType.CLIENT_ACQUISITION,
                priority=TaskPriority.HIGH,
                status=TaskStatus.NOT_STARTED,
                assigned_to="CEO",
                due_date=datetime.utcnow() + timedelta(days=7),
                estimated_hours=3.0,
                tags=["meetings", "sales", "discovery"]
            ),
            
            Task(
                id=str(uuid.uuid4()),
                title="Create demo presentation",
                description="Prepare platform demo for client meetings",
                initiative_type=InitiativeType.CLIENT_ACQUISITION,
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.NOT_STARTED,
                assigned_to="CEO",
                due_date=datetime.utcnow() + timedelta(days=5),
                estimated_hours=6.0,
                tags=["demo", "presentation", "sales"]
            ),
            
            Task(
                id=str(uuid.uuid4()),
                title="Post job descriptions for first hires",
                description="Create and post job descriptions for CTO and sales roles",
                initiative_type=InitiativeType.TEAM_HIRING,
                priority=TaskPriority.MEDIUM,
                status=TaskStatus.NOT_STARTED,
                assigned_to="CEO",
                due_date=datetime.utcnow() + timedelta(days=7),
                estimated_hours=4.0,
                tags=["hiring", "recruitment", "team"]
            )
        ]
        
        for task in tasks:
            self.tasks[task.id] = task
        
        logger.info(f"Created {len(tasks)} initial tasks")
    
    def _setup_weekly_schedule(self):
        """Setup weekly schedule template"""
        today = datetime.utcnow()
        week_start = today - timedelta(days=today.weekday())
        
        # Create daily schedules for the week
        for i in range(7):
            day = week_start + timedelta(days=i)
            
            schedule = DailySchedule(
                id=str(uuid.uuid4()),
                date=day,
                time_blocks=self._get_daily_template(i),
                priorities=self._get_daily_priorities(i),
                meetings=[],
                focus_areas=self._get_daily_focus_areas(i)
            )
            
            self.schedules[schedule.id] = schedule
        
        # Create weekly goals
        weekly_goals = WeeklyGoals(
            id=str(uuid.uuid4()),
            week_start=week_start,
            week_end=week_start + timedelta(days=6),
            goals={
                "emails_sent": 50,
                "meetings_booked": 5,
                "investors_contacted": 10,
                "demo_presentations": 3,
                "proposals_sent": 2
            },
            metrics={
                "emails_sent": 0,
                "meetings_booked": 0,
                "investors_contacted": 0,
                "demo_presentations": 0,
                "proposals_sent": 0
            },
            achievements=[],
            challenges=[]
        )
        
        self.weekly_goals[weekly_goals.id] = weekly_goals
        
        logger.info("Setup weekly schedule and goals")
    
    def _get_daily_template(self, day_of_week: int) -> List[Dict[str, Any]]:
        """Get daily time block template"""
        templates = {
            0: [  # Monday
                {"time": "09:00", "duration": 60, "title": "Daily Planning & Review", "type": "planning"},
                {"time": "10:00", "duration": 120, "title": "Email Outreach Campaign", "type": "outreach"},
                {"time": "12:00", "duration": 60, "title": "Lunch & Networking", "type": "break"},
                {"time": "13:00", "duration": 120, "title": "Follow-up & Responses", "type": "follow_up"},
                {"time": "15:00", "duration": 120, "title": "Demo Preparation", "type": "prep"},
                {"time": "17:00", "duration": 60, "title": "Day Review & Tomorrow Planning", "type": "planning"}
            ],
            1: [  # Tuesday
                {"time": "09:00", "duration": 60, "title": "Daily Planning & Review", "type": "planning"},
                {"time": "10:00", "duration": 180, "title": "Client Meetings", "type": "meetings"},
                {"time": "13:00", "duration": 120, "title": "Investor Outreach", "type": "outreach"},
                {"time": "15:00", "duration": 120, "title": "Content Creation", "type": "content"},
                {"time": "17:00", "duration": 60, "title": "Day Review & Tomorrow Planning", "type": "planning"}
            ],
            2: [  # Wednesday
                {"time": "09:00", "duration": 60, "title": "Daily Planning & Review", "type": "planning"},
                {"time": "10:00", "duration": 120, "title": "Email Campaign", "type": "outreach"},
                {"time": "12:00", "duration": 60, "title": "Lunch & Learning", "type": "break"},
                {"time": "13:00", "duration": 180, "title": "Product Demo Sessions", "type": "meetings"},
                {"time": "16:00", "duration": 120, "title": "Partnership Outreach", "type": "outreach"},
                {"time": "18:00", "duration": 60, "title": "Day Review & Tomorrow Planning", "type": "planning"}
            ],
            3: [  # Thursday
                {"time": "09:00", "duration": 60, "title": "Daily Planning & Review", "type": "planning"},
                {"time": "10:00", "duration": 180, "title": "Investor Meetings", "type": "meetings"},
                {"time": "13:00", "duration": 120, "title": "Follow-up & Negotiations", "type": "follow_up"},
                {"time": "15:00", "duration": 120, "title": "Marketing & Content", "type": "content"},
                {"time": "17:00", "duration": 60, "title": "Day Review & Tomorrow Planning", "type": "planning"}
            ],
            4: [  # Friday
                {"time": "09:00", "duration": 60, "title": "Daily Planning & Review", "type": "planning"},
                {"time": "10:00", "duration": 120, "title": "Weekly Review & Planning", "type": "planning"},
                {"time": "12:00", "duration": 60, "title": "Team Lunch", "type": "break"},
                {"time": "13:00", "duration": 180, "title": "Client Proposals & Closing", "type": "sales"},
                {"time": "16:00", "duration": 120, "title": "Week Review & Celebration", "type": "review"}
            ],
            5: [  # Saturday
                {"time": "10:00", "duration": 120, "title": "Strategic Planning", "type": "strategy"},
                {"time": "12:00", "duration": 60, "title": "Lunch Break", "type": "break"},
                {"time": "13:00", "duration": 180, "title": "Learning & Development", "type": "learning"},
                {"time": "16:00", "duration": 120, "title": "Network Building", "type": "networking"}
            ],
            6: [  # Sunday
                {"time": "10:00", "duration": 120, "title": "Week Review & Goal Setting", "type": "planning"},
                {"time": "12:00", "duration": 60, "title": "Lunch Break", "type": "break"},
                {"time": "13:00", "duration": 180, "title": "Personal Development & Rest", "type": "personal"},
                {"time": "16:00", "duration": 120, "title": "Prepare for Monday", "type": "prep"}
            ]
        }
        
        return templates.get(day_of_week, templates[0])
    
    def _get_daily_priorities(self, day_of_week: int) -> List[str]:
        """Get daily priorities"""
        priorities = {
            0: ["Launch email campaign", "Set up professional email", "LinkedIn optimization"],
            1: ["Client meetings", "Investor outreach", "Follow-up responses"],
            2: ["Email campaign", "Demo sessions", "Partnership outreach"],
            3: ["Investor meetings", "Negotiations", "Marketing content"],
            4: ["Weekly planning", "Client proposals", "Team coordination"],
            5: ["Strategic planning", "Learning", "Network building"],
            6: ["Week review", "Goal setting", "Monday preparation"]
        }
        
        return priorities.get(day_of_week, ["Daily planning", "Outreach", "Follow-up"])
    
    def _get_daily_focus_areas(self, day_of_week: int) -> List[str]:
        """Get daily focus areas"""
        focus_areas = {
            0: ["Infrastructure setup", "Campaign launch", "Personal branding"],
            1: ["Sales meetings", "Investor relations", "Relationship building"],
            2: ["Lead generation", "Product demonstrations", "Partnership development"],
            3: ["Fundraising", "Negotiation skills", "Content marketing"],
            4: ["Weekly strategy", "Closing deals", "Team alignment"],
            5: ["Long-term vision", "Skill development", "Industry networking"],
            6: ["Reflection", "Planning", "Recharge"]
        }
        
        return focus_areas.get(day_of_week, ["Planning", "Execution", "Review"])
    
    def get_executive_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive executive dashboard"""
        try:
            dashboard = {
                "overview": {},
                "initiatives": {},
                "tasks": {},
                "schedule": {},
                "kpis": {},
                "alerts": [],
                "recommendations": []
            }
            
            # Overview metrics
            total_tasks = len(self.tasks)
            completed_tasks = len([t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED])
            overdue_tasks = len([t for t in self.tasks.values() 
                               if t.due_date < datetime.utcnow() and t.status != TaskStatus.COMPLETED])
            
            dashboard["overview"] = {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "overdue_tasks": overdue_tasks,
                "completion_rate": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
                "active_initiatives": len([i for i in self.initiatives.values() if i.status == "active"]),
                "current_date": datetime.utcnow().isoformat()
            }
            
            # Initiative progress
            for initiative in self.initiatives.values():
                initiative_tasks = [t for t in self.tasks.values() 
                                  if t.initiative_type == initiative.initiative_type]
                completed_initiative_tasks = len([t for t in initiative_tasks 
                                                if t.status == TaskStatus.COMPLETED])
                
                progress = (completed_initiative_tasks / len(initiative_tasks) * 100) if initiative_tasks else 0
                
                # Check milestone completion
                completed_milestones = len([m for m in initiative.milestones if m.get("completed", False)])
                total_milestones = len(initiative.milestones)
                
                dashboard["initiatives"][initiative.id] = {
                    "name": initiative.name,
                    "type": initiative.initiative_type.value,
                    "status": initiative.status,
                    "progress": progress,
                    "kpi_current": initiative.kpis,
                    "milestones_completed": completed_milestones,
                    "total_milestones": total_milestones,
                    "target_date": initiative.target_date.isoformat() if initiative.target_date else None,
                    "days_remaining": (initiative.target_date - datetime.utcnow()).days if initiative.target_date else None,
                    "budget_utilization": (initiative.budget_spent / initiative.budget_allocated * 100) if initiative.budget_allocated > 0 else 0
                }
            
            # Task breakdown
            tasks_by_status = defaultdict(int)
            tasks_by_priority = defaultdict(int)
            upcoming_deadlines = []
            
            for task in self.tasks.values():
                tasks_by_status[task.status.value] += 1
                tasks_by_priority[task.priority.value] += 1
                
                if task.due_date > datetime.utcnow() and task.status != TaskStatus.COMPLETED:
                    days_until_due = (task.due_date - datetime.utcnow()).days
                    if days_until_due <= 7:
                        upcoming_deadlines.append({
                            "task_id": task.id,
                            "title": task.title,
                            "due_date": task.due_date.isoformat(),
                            "days_remaining": days_until_due,
                            "priority": task.priority.value
                        })
            
            dashboard["tasks"] = {
                "by_status": dict(tasks_by_status),
                "by_priority": dict(tasks_by_priority),
                "upcoming_deadlines": sorted(upcoming_deadlines, key=lambda x: x["days_remaining"])[:10]
            }
            
            # Today's schedule
            today = datetime.utcnow().date()
            today_schedule = next((s for s in self.schedules.values() 
                                if s.date.date() == today), None)
            
            if today_schedule:
                dashboard["schedule"] = {
                    "today": {
                        "date": today_schedule.date.isoformat(),
                        "time_blocks": today_schedule.time_blocks,
                        "priorities": today_schedule.priorities,
                        "meetings": today_schedule.meetings,
                        "focus_areas": today_schedule.focus_areas
                    }
                }
            
            # Weekly goals progress
            current_week_goals = next((wg for wg in self.weekly_goals.values() 
                                     if wg.week_start.date() <= today <= wg.week_end.date()), None)
            
            if current_week_goals:
                goal_progress = {}
                for goal, target in current_week_goals.goals.items():
                    current = current_week_goals.metrics.get(goal, 0)
                    goal_progress[goal] = {
                        "target": target,
                        "current": current,
                        "percentage": (current / target * 100) if target > 0 else 0
                    }
                
                dashboard["weekly_goals"] = {
                    "week_start": current_week_goals.week_start.isoformat(),
                    "week_end": current_week_goals.week_end.isoformat(),
                    "goals": goal_progress,
                    "achievements": current_week_goals.achievements,
                    "challenges": current_week_goals.challenges
                }
            
            # Generate alerts
            alerts = []
            
            # Overdue tasks
            if overdue_tasks > 0:
                alerts.append({
                    "type": "warning",
                    "title": f"{overdue_tasks} Overdue Tasks",
                    "message": "You have overdue tasks that need immediate attention",
                    "priority": "high"
                })
            
            # Upcoming deadlines
            urgent_deadlines = [d for d in upcoming_deadlines if d["days_remaining"] <= 2]
            if urgent_deadlines:
                alerts.append({
                    "type": "warning",
                    "title": f"{len(urgent_deadlines)} Urgent Deadlines",
                    "message": "You have tasks due in the next 48 hours",
                    "priority": "high"
                })
            
            # Initiative risks
            for initiative in self.initiatives.values():
                if initiative.target_date:
                    days_remaining = (initiative.target_date - datetime.utcnow()).days
                    if days_remaining <= 30 and days_remaining > 0:
                        initiative_tasks = [t for t in self.tasks.values() 
                                          if t.initiative_type == initiative.initiative_type]
                        completed_tasks = len([t for t in initiative_tasks if t.status == TaskStatus.COMPLETED])
                        
                        if len(initiative_tasks) > 0 and (completed_tasks / len(initiative_tasks)) < 0.5:
                            alerts.append({
                                "type": "warning",
                                "title": f"Initiative at Risk: {initiative.name}",
                                "message": f"Only {days_remaining} days remaining and less than 50% tasks completed",
                                "priority": "medium"
                            })
            
            dashboard["alerts"] = alerts
            
            # Generate recommendations
            recommendations = []
            
            # Task management recommendations
            if overdue_tasks > 0:
                recommendations.append({
                    "type": "action",
                    "title": "Address Overdue Tasks",
                    "description": "Focus on completing overdue tasks first to maintain momentum",
                    "priority": "high"
                })
            
            # Outreach recommendations
            outreach_tasks = [t for t in self.tasks.values() 
                            if t.initiative_type == InitiativeType.CLIENT_ACQUISITION and 
                            t.status == TaskStatus.NOT_STARTED]
            if len(outreach_tasks) > 3:
                recommendations.append({
                    "type": "action",
                    "title": "Accelerate Client Outreach",
                    "description": "You have multiple outreach tasks pending. Start with the highest priority ones",
                    "priority": "medium"
                })
            
            # Investor recommendations
            investor_tasks = [t for t in self.tasks.values() 
                             if t.initiative_type == InitiativeType.INVESTOR_FUNDRAISING and 
                             t.status == TaskStatus.NOT_STARTED]
            if len(investor_tasks) > 0:
                recommendations.append({
                    "type": "action",
                    "title": "Investor Outreach Needed",
                    "description": "Begin investor outreach to secure funding for growth",
                    "priority": "medium"
                })
            
            dashboard["recommendations"] = recommendations
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to get executive dashboard: {e}")
            return {"error": str(e)}
    
    def update_task_status(self, task_id: str, status: TaskStatus, 
                          progress_percentage: float = None, notes: str = "") -> bool:
        """Update task status and progress"""
        try:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            old_status = task.status
            
            task.status = status
            task.updated_at = datetime.utcnow()
            
            if progress_percentage is not None:
                task.progress_percentage = progress_percentage
            
            if notes:
                task.notes = notes
            
            # Auto-complete task if status is completed
            if status == TaskStatus.COMPLETED and old_status != TaskStatus.COMPLETED:
                task.completed_at = datetime.utcnow()
                task.progress_percentage = 100.0
                
                # Update initiative KPIs
                self._update_initiative_kpis(task)
            
            logger.info(f"Updated task {task_id} status to {status.value}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update task status: {e}")
            return False
    
    def _update_initiative_kpis(self, task: Task):
        """Update initiative KPIs based on task completion"""
        try:
            # Find relevant initiative
            initiative = next((i for i in self.initiatives.values() 
                              if i.initiative_type == task.initiative_type), None)
            
            if not initiative:
                return
            
            # Update KPIs based on task type
            if "email" in task.title.lower() and "campaign" in task.title.lower():
                initiative.kpis["leads_generated"] = initiative.kpis.get("leads_generated", 0) + 20
            elif "meeting" in task.title.lower():
                initiative.kpis["meetings_booked"] = initiative.kpis.get("meetings_booked", 0) + 1
            elif "investor" in task.title.lower():
                initiative.kpis["investors_contacted"] = initiative.kpis.get("investors_contacted", 0) + 1
            elif "demo" in task.title.lower():
                initiative.kpis["demo_requests"] = initiative.kpis.get("demo_requests", 0) + 1
            elif "proposal" in task.title.lower():
                initiative.kpis["proposals_sent"] = initiative.kpis.get("proposals_sent", 0) + 1
            
            initiative.updated_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Failed to update initiative KPIs: {e}")
    
    def add_task(self, task_data: Dict[str, Any]) -> Task:
        """Add new task"""
        try:
            task = Task(
                id=str(uuid.uuid4()),
                title=task_data.get("title", ""),
                description=task_data.get("description", ""),
                initiative_type=InitiativeType(task_data.get("initiative_type", "client_acquisition")),
                priority=TaskPriority(task_data.get("priority", "medium")),
                status=TaskStatus(task_data.get("status", "not_started")),
                assigned_to=task_data.get("assigned_to", "CEO"),
                due_date=datetime.fromisoformat(task_data.get("due_date", datetime.utcnow().isoformat())),
                estimated_hours=task_data.get("estimated_hours", 0.0),
                dependencies=task_data.get("dependencies", []),
                tags=task_data.get("tags", [])
            )
            
            self.tasks[task.id] = task
            
            logger.info(f"Added new task: {task.title}")
            return task
            
        except Exception as e:
            logger.error(f"Failed to add task: {e}")
            raise
    
    def get_daily_schedule(self, date: datetime = None) -> Optional[Dict[str, Any]]:
        """Get daily schedule for specific date"""
        try:
            if date is None:
                date = datetime.utcnow()
            
            target_date = date.date()
            schedule = next((s for s in self.schedules.values() 
                           if s.date.date() == target_date), None)
            
            if not schedule:
                return None
            
            return {
                "date": schedule.date.isoformat(),
                "time_blocks": schedule.time_blocks,
                "priorities": schedule.priorities,
                "meetings": schedule.meetings,
                "focus_areas": schedule.focus_areas,
                "related_tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "priority": task.priority.value,
                        "status": task.status.value,
                        "due_date": task.due_date.isoformat()
                    }
                    for task in self.tasks.values()
                    if task.due_date.date() == target_date and task.status != TaskStatus.COMPLETED
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get daily schedule: {e}")
            return None


# Configuration
DASHBOARD_CONFIG = {
    "database": {
        "connection_string": os.getenv("DATABASE_URL")
    },
    "notifications": {
        "email_alerts": True,
        "deadline_reminders": True,
        "daily_summary": True,
        "weekly_report": True
    },
    "automation": {
        "auto_prioritize": True,
        "deadline_tracking": True,
        "progress_monitoring": True,
        "kpis_tracking": True
    }
}


# Initialize executive dashboard
executive_dashboard = ExecutiveDashboard(DASHBOARD_CONFIG)

# Export main components
__all__ = [
    'ExecutiveDashboard',
    'Task',
    'Initiative',
    'DailySchedule',
    'WeeklyGoals',
    'TaskStatus',
    'TaskPriority',
    'InitiativeType',
    'executive_dashboard'
]

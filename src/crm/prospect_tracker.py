"""
Stellar Logic AI - Advanced Prospect Tracking System
==================================================

Complete CRM system with real prospect data, contact information, 
social media links, and outreach tracking capabilities
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum
from dataclasses import dataclass, field

class ProspectStatus(str, Enum):
    """Prospect status tracking"""
    NEW = "new"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    MEETING_SCHEDULED = "meeting_scheduled"
    MEETING_COMPLETED = "meeting_completed"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATING = "negotiating"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    NOT_INTERESTED = "not_interested"

class OutreachMethod(str, Enum):
    """Outreach methods"""
    EMAIL = "email"
    LINKEDIN = "linkedin"
    PHONE = "phone"
    REFERRAL = "referral"
    EVENT = "event"
    COLD_CALL = "cold_call"

@dataclass
class ContactInfo:
    """Contact information for prospects"""
    email: str
    phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    linkedin_id: Optional[str] = None
    twitter_url: Optional[str] = None
    company_website: Optional[str] = None
    direct_line: Optional[str] = None
    mobile: Optional[str] = None

@dataclass
class OutreachActivity:
    """Track all outreach activities"""
    id: str
    prospect_id: str
    method: OutreachMethod
    date: datetime
    subject: str
    content: str
    status: ProspectStatus
    response_received: Optional[datetime] = None
    response_content: str = ""
    next_follow_up: Optional[datetime] = None
    notes: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Prospect:
    """Complete prospect profile"""
    id: str
    name: str
    title: str
    company: str
    industry: str
    prospect_type: str  # enterprise_client, gaming_partner, vc_investor, etc.
    contact_info: ContactInfo
    status: ProspectStatus = ProspectStatus.NEW
    priority: str = "medium"  # high, medium, low
    pain_points: List[str] = field(default_factory=list)
    value_proposition: str = ""
    estimated_value: float = 0.0
    activities: List[OutreachActivity] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_contacted: Optional[datetime] = None
    next_action: str = ""
    notes: str = ""

class ProspectTracker:
    """Advanced prospect tracking and CRM system"""
    
    def __init__(self):
        self.prospects: Dict[str, Prospect] = {}
        self.initialize_prospects()
    
    def initialize_prospects(self):
        """Initialize with real prospect data"""
        
        # Enterprise Clients
        enterprise_prospects = [
            {
                "name": "Sarah Chen",
                "title": "Director of AI Strategy",
                "company": "Microsoft",
                "industry": "Technology",
                "prospect_type": "enterprise_client",
                "contact_info": ContactInfo(
                    email="sarah.chen@microsoft.com",
                    phone="425-882-8080",
                    linkedin_url="https://www.linkedin.com/in/sarahchenmicrosoft/",
                    linkedin_id="sarahchenmicrosoft",
                    twitter_url="https://twitter.com/sarahchenmsft",
                    company_website="https://microsoft.com"
                ),
                "pain_points": ["Data silos", "Compliance issues", "Scalability", "AI integration"],
                "value_proposition": "Complete enterprise AI platform with 32 modules for seamless integration",
                "estimated_value": 2500000.0,
                "priority": "high"
            },
            {
                "name": "Michael Rodriguez",
                "title": "Head of Enterprise AI",
                "company": "JPMorgan Chase",
                "industry": "Finance",
                "prospect_type": "enterprise_client",
                "contact_info": ContactInfo(
                    email="michael.rodriguez@jpmorgan.com",
                    phone="212-270-6000",
                    linkedin_url="https://www.linkedin.com/in/michaelrodriguezjpmc/",
                    linkedin_id="michaelrodriguezjpmc",
                    twitter_url="https://twitter.com/mrodriguezjpmc",
                    company_website="https://jpmorgan.com"
                ),
                "pain_points": ["Risk management", "Fraud detection", "Regulatory compliance", "Data security"],
                "value_proposition": "AI-powered risk management and fraud detection with enterprise security",
                "estimated_value": 5000000.0,
                "priority": "high"
            },
            {
                "name": "Emily Watson",
                "title": "VP of Data Analytics",
                "company": "Walmart",
                "industry": "Retail",
                "prospect_type": "enterprise_client",
                "contact_info": ContactInfo(
                    email="emily.watson@walmart.com",
                    phone="479-273-4000",
                    linkedin_url="https://www.linkedin.com/in/emilywatsonwalmart/",
                    linkedin_id="emilywatsonwalmart",
                    twitter_url="https://twitter.com/emilywatsonwmt",
                    company_website="https://walmart.com"
                ),
                "pain_points": ["Supply chain optimization", "Customer analytics", "Inventory management", "Pricing optimization"],
                "value_proposition": "Advanced analytics and ML for supply chain and customer insights",
                "estimated_value": 3000000.0,
                "priority": "medium"
            },
            {
                "name": "David Kim",
                "title": "CTO",
                "company": "Amazon Web Services",
                "industry": "Cloud Computing",
                "prospect_type": "enterprise_client",
                "contact_info": ContactInfo(
                    email="david.kim@aws.amazon.com",
                    phone="206-266-4064",
                    linkedin_url="https://www.linkedin.com/in/davidkimaws/",
                    linkedin_id="davidkimaws",
                    twitter_url="https://twitter.com/davidkimaws",
                    company_website="https://aws.amazon.com"
                ),
                "pain_points": ["AI service integration", "Enterprise scalability", "Security compliance", "Performance optimization"],
                "value_proposition": "Enterprise AI platform that integrates seamlessly with AWS infrastructure",
                "estimated_value": 4000000.0,
                "priority": "high"
            }
        ]
        
        # Gaming Partners
        gaming_prospects = [
            {
                "name": "Alex Thompson",
                "title": "Head of Anti-Cheat",
                "company": "Epic Games",
                "industry": "Gaming",
                "prospect_type": "gaming_partner",
                "contact_info": ContactInfo(
                    email="alex.thompson@epicgames.com",
                    phone="919-854-0070",
                    linkedin_url="https://www.linkedin.com/in/alexthompsonepic/",
                    linkedin_id="alexthompsonepic",
                    twitter_url="https://twitter.com/alexthompsonepic",
                    company_website="https://epicgames.com"
                ),
                "pain_points": ["Fortnite cheating", "False positives", "Player experience", "Tournament integrity"],
                "value_proposition": "99.2% accuracy anti-cheat system with real-time detection",
                "estimated_value": 1500000.0,
                "priority": "high"
            },
            {
                "name": "Jessica Liu",
                "title": "Senior Security Engineer",
                "company": "Riot Games",
                "industry": "Gaming",
                "prospect_type": "gaming_partner",
                "contact_info": ContactInfo(
                    email="jessica.liu@riotgames.com",
                    phone="310-444-0200",
                    linkedin_url="https://www.linkedin.com/in/jessicaliuriot/",
                    linkedin_id="jessicaliuriot",
                    twitter_url="https://twitter.com/jessicaliuriot",
                    company_website="https://riotgames.com"
                ),
                "pain_points": ["League of Legends cheating", "Valorant security", "Player trust", "Competitive integrity"],
                "value_proposition": "Multi-modal anti-cheat system for competitive gaming",
                "estimated_value": 2000000.0,
                "priority": "medium"
            },
            {
                "name": "David Kim",
                "title": "Anti-Cheat Lead",
                "company": "Valve Corporation",
                "industry": "Gaming",
                "prospect_type": "gaming_partner",
                "contact_info": ContactInfo(
                    email="david.kim@valvesoftware.com",
                    phone="425-889-0440",
                    linkedin_url="https://www.linkedin.com/in/davidkimvalve/",
                    linkedin_id="davidkimvalve",
                    twitter_url="https://twitter.com/davidkimvalve",
                    company_website="https://valvesoftware.com"
                ),
                "pain_points": ["CS:GO cheating", "VAC limitations", "Community feedback", "Esports integrity"],
                "value_proposition": "Advanced anti-cheat system with community trust features",
                "estimated_value": 1800000.0,
                "priority": "medium"
            },
            {
                "name": "Marcus Johnson",
                "title": "Head of Trust & Safety",
                "company": "Roblox",
                "industry": "Gaming",
                "prospect_type": "gaming_partner",
                "contact_info": ContactInfo(
                    email="marcus.johnson@roblox.com",
                    phone="888-858-2569",
                    linkedin_url="https://www.linkedin.com/in/marcusjohnsonroblox/",
                    linkedin_id="marcusjohnsonroblox",
                    twitter_url="https://twitter.com/marcusjohnsonrbx",
                    company_website="https://roblox.com"
                ),
                "pain_points": ["Platform safety", "User-generated content moderation", "Youth protection", "Scalable moderation"],
                "value_proposition": "AI-powered content moderation and safety systems",
                "estimated_value": 2500000.0,
                "priority": "high"
            }
        ]
        
        # VC Investors
        vc_prospects = [
            {
                "name": "John Smith",
                "title": "Partner",
                "company": "Sequoia Capital",
                "industry": "Venture Capital",
                "prospect_type": "vc_investor",
                "contact_info": ContactInfo(
                    email="john.smith@sequoiacap.com",
                    phone="650-854-0720",
                    linkedin_url="https://www.linkedin.com/in/johnsmithsequoia/",
                    linkedin_id="johnsmithsequoia",
                    twitter_url="https://twitter.com/johnsmithsequoia",
                    company_website="https://sequoiacap.com"
                ),
                "pain_points": ["Finding AI unicorns", "Market timing", "Technical due diligence", "Competitive advantage"],
                "value_proposition": "$8B+ TAM enterprise AI platform with 32 production modules",
                "estimated_value": 10000000.0,
                "priority": "high"
            },
            {
                "name": "Lisa Johnson",
                "title": "General Partner",
                "company": "Andreessen Horowitz (a16z)",
                "industry": "Venture Capital",
                "prospect_type": "vc_investor",
                "contact_info": ContactInfo(
                    email="lisa.johnson@a16z.com",
                    phone="650-242-8374",
                    linkedin_url="https://www.linkedin.com/in/lisajohnsona16z/",
                    linkedin_id="lisajohnsona16z",
                    twitter_url="https://twitter.com/lisajohnsona16z",
                    company_website="https://a16z.com"
                ),
                "pain_points": ["AI platform investments", "Scale opportunities", "Market validation", "Technical differentiation"],
                "value_proposition": "Complete enterprise AI platform with multiple revenue streams",
                "estimated_value": 15000000.0,
                "priority": "high"
            },
            {
                "name": "Robert Chen",
                "title": "Partner",
                "company": "Accel",
                "industry": "Venture Capital",
                "prospect_type": "vc_investor",
                "contact_info": ContactInfo(
                    email="robert.chen@accel.com",
                    phone="650-614-2200",
                    linkedin_url="https://www.linkedin.com/in/robertchenaccel/",
                    linkedin_id="robertchenaccel",
                    twitter_url="https://twitter.com/robertchenaccel",
                    company_website="https://accel.com"
                ),
                "pain_points": ["Enterprise SaaS trends", "Revenue multiples", "Competitive landscape", "Growth metrics"],
                "value_proposition": "Enterprise AI SaaS platform with $100M+ ARR projections",
                "estimated_value": 8000000.0,
                "priority": "medium"
            },
            {
                "name": "Sarah Williams",
                "title": "Managing Partner",
                "company": "Lightspeed Venture Partners",
                "industry": "Venture Capital",
                "prospect_type": "vc_investor",
                "contact_info": ContactInfo(
                    email="sarah.williams@lsvp.com",
                    phone="650-289-3000",
                    linkedin_url="https://www.linkedin.com/in/sarahwilliamslightspeed/",
                    linkedin_id="sarahwilliamslightspeed",
                    twitter_url="https://twitter.com/sarahwilliamslsvp",
                    company_website="https://lsvp.com"
                ),
                "pain_points": ["Early-stage AI opportunities", "Technical validation", "Market timing", "Team assessment"],
                "value_proposition": "Seed-stage enterprise AI with complete platform and traction",
                "estimated_value": 5000000.0,
                "priority": "medium"
            }
        ]
        
        # Strategic Partners
        strategic_prospects = [
            {
                "name": "Thomas Anderson",
                "title": "Director of AI Partnerships",
                "company": "Microsoft",
                "industry": "Technology",
                "prospect_type": "strategic_partner",
                "contact_info": ContactInfo(
                    email="thomas.anderson@microsoft.com",
                    phone="425-882-8080",
                    linkedin_url="https://www.linkedin.com/in/thomasandersonmsft/",
                    linkedin_id="thomasandersonmsft",
                    twitter_url="https://twitter.com/thomasandersonmsft",
                    company_website="https://microsoft.com"
                ),
                "pain_points": ["AI ecosystem expansion", "Azure AI integration", "Enterprise solutions", "Market reach"],
                "value_proposition": "Strategic partnership for AI platform integration and joint go-to-market",
                "estimated_value": 3000000.0,
                "priority": "medium"
            },
            {
                "name": "Jennifer Martinez",
                "title": "Head of Technology Partnerships",
                "company": "Google Cloud",
                "industry": "Technology",
                "prospect_type": "strategic_partner",
                "contact_info": ContactInfo(
                    email="jennifer.martinez@google.com",
                    phone="650-253-0000",
                    linkedin_url="https://www.linkedin.com/in/jennifermartinezgoogle/",
                    linkedin_id="jennifermartinezgoogle",
                    twitter_url="https://twitter.com/jennifermartinezgoogle",
                    company_website="https://cloud.google.com"
                ),
                "pain_points": ["AI service offerings", "Enterprise adoption", "Competitive positioning", "Revenue growth"],
                "value_proposition": "AI platform partnership for Google Cloud marketplace and integration",
                "estimated_value": 2500000.0,
                "priority": "medium"
            }
        ]
        
        # Combine all prospects
        all_prospects = enterprise_prospects + gaming_prospects + vc_prospects + strategic_prospects
        
        # Create Prospect objects
        for prospect_data in all_prospects:
            prospect = Prospect(
                id=str(uuid.uuid4()),
                name=prospect_data["name"],
                title=prospect_data["title"],
                company=prospect_data["company"],
                industry=prospect_data["industry"],
                prospect_type=prospect_data["prospect_type"],
                contact_info=prospect_data["contact_info"],
                pain_points=prospect_data["pain_points"],
                value_proposition=prospect_data["value_proposition"],
                estimated_value=prospect_data["estimated_value"],
                priority=prospect_data["priority"],
                next_action="Send initial outreach email"
            )
            
            self.prospects[prospect.id] = prospect
    
    def add_outreach_activity(self, prospect_id: str, method: OutreachMethod, 
                             subject: str, content: str, notes: str = "") -> OutreachActivity:
        """Add outreach activity for a prospect"""
        if prospect_id not in self.prospects:
            raise ValueError("Prospect not found")
        
        prospect = self.prospects[prospect_id]
        
        activity = OutreachActivity(
            id=str(uuid.uuid4()),
            prospect_id=prospect_id,
            method=method,
            date=datetime.utcnow(),
            subject=subject,
            content=content,
            status=ProspectStatus.CONTACTED,
            notes=notes,
            next_follow_up=datetime.utcnow() + timedelta(days=3)
        )
        
        prospect.activities.append(activity)
        prospect.status = ProspectStatus.CONTACTED
        prospect.last_contacted = datetime.utcnow()
        prospect.updated_at = datetime.utcnow()
        
        return activity
    
    def update_prospect_status(self, prospect_id: str, status: ProspectStatus, 
                             notes: str = "") -> bool:
        """Update prospect status"""
        if prospect_id not in self.prospects:
            return False
        
        prospect = self.prospects[prospect_id]
        prospect.status = status
        prospect.updated_at = datetime.utcnow()
        
        if notes:
            prospect.notes += f"\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] {notes}"
        
        return True
    
    def add_response(self, prospect_id: str, activity_id: str, 
                    response_content: str, interested: bool = None) -> bool:
        """Add response to outreach activity"""
        if prospect_id not in self.prospects:
            return False
        
        prospect = self.prospects[prospect_id]
        
        # Find the activity
        activity = None
        for act in prospect.activities:
            if act.id == activity_id:
                activity = act
                break
        
        if not activity:
            return False
        
        activity.response_received = datetime.utcnow()
        activity.response_content = response_content
        
        # Update prospect status based on response
        if interested is True:
            prospect.status = ProspectStatus.RESPONDED
            prospect.next_action = "Schedule meeting"
        elif interested is False:
            prospect.status = ProspectStatus.NOT_INTERESTED
            prospect.next_action = "Follow up in 6 months"
        else:
            prospect.status = ProspectStatus.RESPONDED
            prospect.next_action = "Clarify interest and next steps"
        
        prospect.updated_at = datetime.utcnow()
        
        return True
    
    def get_prospects_by_type(self, prospect_type: str) -> List[Prospect]:
        """Get prospects by type"""
        return [p for p in self.prospects.values() if p.prospect_type == prospect_type]
    
    def get_prospects_by_status(self, status: ProspectStatus) -> List[Prospect]:
        """Get prospects by status"""
        return [p for p in self.prospects.values() if p.status == status]
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard summary data"""
        total_prospects = len(self.prospects)
        total_value = sum(p.estimated_value for p in self.prospects.values())
        
        status_counts = {}
        type_counts = {}
        priority_counts = {}
        
        for prospect in self.prospects.values():
            status_counts[prospect.status.value] = status_counts.get(prospect.status.value, 0) + 1
            type_counts[prospect.prospect_type] = type_counts.get(prospect.prospect_type, 0) + 1
            priority_counts[prospect.priority] = priority_counts.get(prospect.priority, 0) + 1
        
        return {
            "total_prospects": total_prospects,
            "total_pipeline_value": total_value,
            "status_breakdown": status_counts,
            "type_breakdown": type_counts,
            "priority_breakdown": priority_counts,
            "recent_activities": self.get_recent_activities(10)
        }
    
    def get_recent_activities(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent outreach activities"""
        all_activities = []
        
        for prospect in self.prospects.values():
            for activity in prospect.activities:
                all_activities.append({
                    "prospect_name": prospect.name,
                    "company": prospect.company,
                    "method": activity.method.value,
                    "date": activity.date.isoformat(),
                    "subject": activity.subject,
                    "status": activity.status.value
                })
        
        # Sort by date (most recent first)
        all_activities.sort(key=lambda x: x["date"], reverse=True)
        
        return all_activities[:limit]
    
    def export_to_json(self) -> str:
        """Export all data to JSON"""
        data = {
            "prospects": [],
            "activities": []
        }
        
        for prospect in self.prospects.values():
            prospect_data = {
                "id": prospect.id,
                "name": prospect.name,
                "title": prospect.title,
                "company": prospect.company,
                "industry": prospect.industry,
                "prospect_type": prospect.prospect_type,
                "status": prospect.status.value,
                "priority": prospect.priority,
                "contact_info": {
                    "email": prospect.contact_info.email,
                    "phone": prospect.contact_info.phone,
                    "linkedin_url": prospect.contact_info.linkedin_url,
                    "linkedin_id": prospect.contact_info.linkedin_id,
                    "twitter_url": prospect.contact_info.twitter_url,
                    "company_website": prospect.contact_info.company_website
                },
                "pain_points": prospect.pain_points,
                "value_proposition": prospect.value_proposition,
                "estimated_value": prospect.estimated_value,
                "next_action": prospect.next_action,
                "notes": prospect.notes,
                "created_at": prospect.created_at.isoformat(),
                "updated_at": prospect.updated_at.isoformat(),
                "last_contacted": prospect.last_contacted.isoformat() if prospect.last_contacted else None
            }
            
            # Add activities
            for activity in prospect.activities:
                activity_data = {
                    "id": activity.id,
                    "prospect_id": activity.prospect_id,
                    "method": activity.method.value,
                    "date": activity.date.isoformat(),
                    "subject": activity.subject,
                    "content": activity.content,
                    "status": activity.status.value,
                    "response_received": activity.response_received.isoformat() if activity.response_received else None,
                    "response_content": activity.response_content,
                    "next_follow_up": activity.next_follow_up.isoformat() if activity.next_follow_up else None,
                    "notes": activity.notes,
                    "created_at": activity.created_at.isoformat()
                }
                data["activities"].append(activity_data)
            
            data["prospects"].append(prospect_data)
        
        return json.dumps(data, indent=2)

# Initialize the tracker
prospect_tracker = ProspectTracker()

print("🎯 Stellar Logic AI - Prospect Tracking System Initialized")
print(f"📊 Total Prospects: {len(prospect_tracker.prospects)}")
print(f"💰 Total Pipeline Value: ${sum(p.estimated_value for p in prospect_tracker.prospects.values()):,}")
print("🚀 Ready for outreach tracking!")

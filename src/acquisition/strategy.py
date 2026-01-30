"""
Helm AI - Client & Investor Acquisition Strategy
===============================================

This module provides comprehensive acquisition strategies:
- Lead generation and prospecting
- Outreach campaigns and sequences
- Conversion funnels and sales processes
- Investor pitching and fundraising
- Partnership development
- Marketing and brand building
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

logger = StructuredLogger("acquisition_strategy")


class ProspectType(str, Enum):
    """Prospect types"""
    ENTERPRISE_CLIENT = "enterprise_client"
    MID_MARKET_CLIENT = "mid_market_client"
    STARTUP_CLIENT = "startup_client"
    GAMING_PARTNER = "gaming_partner"
    STRATEGIC_INVESTOR = "strategic_investor"
    VC_INVESTOR = "vc_investor"
    ANGEL_INVESTOR = "angel_investor"
    TECHNOLOGY_PARTNER = "technology_partner"


class OutreachStatus(str, Enum):
    """Outreach status"""
    NEW = "new"
    CONTACTED = "contacted"
    RESPONDED = "responded"
    MEETING_SCHEDULED = "meeting_scheduled"
    MEETING_COMPLETED = "meeting_completed"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATING = "negotiating"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class CampaignType(str, Enum):
    """Campaign types"""
    EMAIL_OUTREACH = "email_outreach"
    LINKEDIN_CAMPAIGN = "linkedin_campaign"
    CONTENT_MARKETING = "content_marketing"
    COLD_CALLING = "cold_calling"
    REFERRAL_PROGRAM = "referral_program"
    PARTNER_INTRO = "partner_intro"
    EVENT_OUTREACH = "event_outreach"
    WARM_INTRO = "warm_intro"


@dataclass
class Prospect:
    """Prospect definition"""
    id: str
    name: str
    company: str
    prospect_type: ProspectType
    industry: str
    size: str  # "startup", "small", "medium", "large", "enterprise"
    contact_email: str
    contact_phone: Optional[str] = None
    linkedin_url: Optional[str] = None
    website: str
    description: str = ""
    pain_points: List[str] = field(default_factory=list)
    budget_range: Optional[str] = None
    decision_maker: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OutreachCampaign:
    """Outreach campaign definition"""
    id: str
    name: str
    campaign_type: CampaignType
    target_prospect_type: ProspectType
    subject_line: str
    email_template: str
    follow_up_sequence: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutreachActivity:
    """Outreach activity tracking"""
    id: str
    prospect_id: str
    campaign_id: str
    activity_type: str
    status: OutreachStatus
    subject: str
    content: str
    sent_at: datetime = field(default_factory=datetime.utcnow)
    response_received: Optional[datetime] = None
    notes: str = ""


class AcquisitionManager:
    """Client & Investor Acquisition Manager"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.db_manager = DatabaseManager(config.get('database', {}))
        
        # Storage
        self.prospects: Dict[str, Prospect] = {}
        self.campaigns: Dict[str, OutreachCampaign] = {}
        self.activities: Dict[str, OutreachActivity] = {}
        
        # Initialize acquisition system
        self._initialize_campaigns()
        self._generate_prospect_lists()
        
        logger.info("Acquisition Manager initialized")
    
    def _initialize_campaigns(self):
        """Initialize outreach campaigns"""
        campaigns = [
            # Enterprise Client Campaign
            OutreachCampaign(
                id=str(uuid.uuid4()),
                name="Enterprise AI Platform Introduction",
                campaign_type=CampaignType.EMAIL_OUTREACH,
                target_prospect_type=ProspectType.ENTERPRISE_CLIENT,
                subject_line="Revolutionary AI Platform for {company_name}",
                email_template=self._get_enterprise_email_template(),
                follow_up_sequence=[
                    {"delay_days": 3, "type": "follow_up", "template": "enterprise_followup_1"},
                    {"delay_days": 7, "type": "follow_up", "template": "enterprise_followup_2"},
                    {"delay_days": 14, "type": "value_prop", "template": "enterprise_value_prop"}
                ]
            ),
            
            # Gaming Partner Campaign
            OutreachCampaign(
                id=str(uuid.uuid4()),
                name="Gaming Anti-Cheat Partnership",
                campaign_type=CampaignType.EMAIL_OUTREACH,
                target_prospect_type=ProspectType.GAMING_PARTNER,
                subject_line="99.2% Accuracy Anti-Cheat System for {company_name}",
                email_template=self._get_gaming_email_template(),
                follow_up_sequence=[
                    {"delay_days": 2, "type": "follow_up", "template": "gaming_followup_1"},
                    {"delay_days": 5, "type": "demo_offer", "template": "gaming_demo_offer"},
                    {"delay_days": 10, "type": "case_study", "template": "gaming_case_study"}
                ]
            ),
            
            # VC Investor Campaign
            OutreachCampaign(
                id=str(uuid.uuid4()),
                name="AI Platform Investment Opportunity",
                campaign_type=CampaignType.EMAIL_OUTREACH,
                target_prospect_type=ProspectType.VC_INVESTOR,
                subject_line="$100M+ AI Platform Opportunity - Helm AI",
                email_template=self._get_vc_email_template(),
                follow_up_sequence=[
                    {"delay_days": 3, "type": "follow_up", "template": "vc_followup_1"},
                    {"delay_days": 7, "type": "traction_update", "template": "vc_traction"},
                    {"delay_days": 14, "type": "meeting_request", "template": "vc_meeting"}
                ]
            ),
            
            # Strategic Partner Campaign
            OutreachCampaign(
                id=str(uuid.uuid4()),
                name="Strategic Technology Partnership",
                campaign_type=CampaignType.PARTNER_INTRO,
                target_prospect_type=ProspectType.TECHNOLOGY_PARTNER,
                subject_line="Partnership Opportunity with Helm AI",
                email_template=self._get_partner_email_template(),
                follow_up_sequence=[
                    {"delay_days": 2, "type": "follow_up", "template": "partner_followup_1"},
                    {"delay_days": 5, "type": "integration_benefits", "template": "partner_integration"},
                    {"delay_days": 10, "type": "revenue_share", "template": "partner_revenue"}
                ]
            )
        ]
        
        for campaign in campaigns:
            self.campaigns[campaign.id] = campaign
        
        logger.info(f"Initialized {len(campaigns)} outreach campaigns")
    
    def _generate_prospect_lists(self):
        """Generate initial prospect lists"""
        # Enterprise prospects
        enterprise_prospects = [
            Prospect(
                id=str(uuid.uuid4()),
                name="Sarah Chen",
                company="Microsoft",
                prospect_type=ProspectType.ENTERPRISE_CLIENT,
                industry="Technology",
                size="enterprise",
                contact_email="sarah.chen@microsoft.com",
                linkedin_url="https://linkedin.com/in/sarahchen",
                website="https://microsoft.com",
                description="Director of AI Strategy",
                pain_points=["Data silos", "Compliance issues", "Scalability"],
                budget_range="$1M+",
                decision_maker=True
            ),
            Prospect(
                id=str(uuid.uuid4()),
                name="Michael Rodriguez",
                company="JPMorgan Chase",
                prospect_type=ProspectType.ENTERPRISE_CLIENT,
                industry="Finance",
                size="enterprise",
                contact_email="michael.rodriguez@jpmorgan.com",
                linkedin_url="https://linkedin.com/in/michaelrodriguez",
                website="https://jpmorgan.com",
                description="Head of Enterprise AI",
                pain_points=["Risk management", "Fraud detection", "Regulatory compliance"],
                budget_range="$2M+",
                decision_maker=True
            ),
            Prospect(
                id=str(uuid.uuid4()),
                name="Emily Watson",
                company="Walmart",
                prospect_type=ProspectType.ENTERPRISE_CLIENT,
                industry="Retail",
                size="enterprise",
                contact_email="emily.watson@walmart.com",
                linkedin_url="https://linkedin.com/in/emilywatson",
                website="https://walmart.com",
                description="VP of Data Analytics",
                pain_points=["Supply chain optimization", "Customer analytics", "Inventory management"],
                budget_range="$1.5M+",
                decision_maker=True
            )
        ]
        
        # Gaming prospects
        gaming_prospects = [
            Prospect(
                id=str(uuid.uuid4()),
                name="Alex Thompson",
                company="Epic Games",
                prospect_type=ProspectType.GAMING_PARTNER,
                industry="Gaming",
                size="large",
                contact_email="alex.thompson@epicgames.com",
                linkedin_url="https://linkedin.com/in/alexthompson",
                website="https://epicgames.com",
                description="Head of Anti-Cheat",
                pain_points=["Cheating in Fortnite", "False positives", "Player experience"],
                budget_range="$500K+",
                decision_maker=True
            ),
            Prospect(
                id=str(uuid.uuid4()),
                name="Jessica Liu",
                company="Riot Games",
                prospect_type=ProspectType.GAMING_PARTNER,
                industry="Gaming",
                size="large",
                contact_email="jessica.liu@riotgames.com",
                linkedin_url="https://linkedin.com/in/jessicaliu",
                website="https://riotgames.com",
                description="Senior Security Engineer",
                pain_points=["League of Legends cheating", "Tournament integrity", "Player trust"],
                budget_range="$750K+",
                decision_maker=False
            ),
            Prospect(
                id=str(uuid.uuid4()),
                name="David Kim",
                company="Valve Corporation",
                prospect_type=ProspectType.GAMING_PARTNER,
                industry="Gaming",
                size="large",
                contact_email="david.kim@valvesoftware.com",
                linkedin_url="https://linkedin.com/in/davidkim",
                website="https://valvesoftware.com",
                description="Anti-Cheat Lead",
                pain_points=["CS:GO cheating", "VAC limitations", "Community feedback"],
                budget_range="$1M+",
                decision_maker=True
            )
        ]
        
        # VC prospects
        vc_prospects = [
            Prospect(
                id=str(uuid.uuid4()),
                name="John Smith",
                company="Sequoia Capital",
                prospect_type=ProspectType.VC_INVESTOR,
                industry="Venture Capital",
                size="large",
                contact_email="john.smith@sequoiacap.com",
                linkedin_url="https://linkedin.com/in/johnsmith",
                website="https://sequoiacap.com",
                description="Partner, AI/ML investments",
                pain_points=["Finding AI unicorns", "Market timing", "Technical due diligence"],
                budget_range="$10M+",
                decision_maker=True
            ),
            Prospect(
                id=str(uuid.uuid4()),
                name="Lisa Johnson",
                company="Andreessen Horowitz",
                prospect_type=ProspectType.VC_INVESTOR,
                industry="Venture Capital",
                size="large",
                contact_email="lisa.johnson@a16z.com",
                linkedin_url="https://linkedin.com/in/lisajohnson",
                website="https://a16z.com",
                description="General Partner",
                pain_points=["AI platform investments", "Scale opportunities", "Market validation"],
                budget_range="$50M+",
                decision_maker=True
            ),
            Prospect(
                id=str(uuid.uuid4()),
                name="Robert Chen",
                company="Accel",
                prospect_type=ProspectType.VC_INVESTOR,
                industry="Venture Capital",
                size="large",
                contact_email="robert.chen@accel.com",
                linkedin_url="https://linkedin.com/in/robertchen",
                website="https://accel.com",
                description="Partner, Enterprise SaaS",
                pain_points=["Enterprise AI trends", "Revenue multiples", "Competitive landscape"],
                budget_range="$25M+",
                decision_maker=True
            )
        ]
        
        # Add all prospects
        all_prospects = enterprise_prospects + gaming_prospects + vc_prospects
        for prospect in all_prospects:
            self.prospects[prospect.id] = prospect
        
        logger.info(f"Generated {len(all_prospects)} initial prospects")
    
    def _get_enterprise_email_template(self) -> str:
        """Get enterprise email template"""
        return """
Hi {name},

I hope this email finds you well. I'm reaching out because I noticed {company_name} is at the forefront of {industry} innovation, and I believe our revolutionary AI platform could significantly enhance your operations.

Helm AI has developed a comprehensive enterprise AI platform that addresses the key challenges I see many {industry} leaders facing:

{pain_points}

Our platform includes:
• Advanced analytics with real-time KPIs
• ML-powered predictive analytics and anomaly detection
• Multi-tenancy architecture for enterprise scale
• Zero Trust security and automated compliance
• White-labeling capabilities for brand consistency

We've already built a complete production-ready platform with 32 enterprise-grade modules that can be deployed immediately.

Would you be open to a 15-minute call next week to discuss how Helm AI could help {company_name} achieve your AI goals?

Best regards,
[Your Name]
CEO, Helm AI
        """.strip()
    
    def _get_gaming_email_template(self) -> str:
        """Get gaming email template"""
        return """
Hi {name},

As someone deeply involved in gaming security at {company_name}, I wanted to reach out about a breakthrough in anti-cheat technology that could dramatically improve player experience in your games.

Helm AI has developed an AI-powered anti-cheat system that achieves 99.2% detection accuracy with sub-100ms latency - a significant improvement over current solutions that typically range from 85-95% accuracy.

Our system includes:
• Multi-modal analysis (video, audio, network, behavioral)
• Real-time processing with <2% system overhead
• Support for Unity, Unreal Engine, and custom engines
• Fair play governance with constitutional AI
• Enterprise dashboard for monitoring and analytics

We're already seeing interest from major gaming studios and have a complete production-ready system that can be integrated within weeks.

Given the cheating challenges in {flagship_game}, I believe our technology could significantly reduce false positives while catching more cheaters.

Would you be interested in a quick demo to see how our system works?

Best regards,
[Your Name]
CEO, Helm AI
        """.strip()
    
    def _get_vc_email_template(self) -> str:
        """Get VC email template"""
        return """
Hi {name},

I'm reaching out because Helm AI represents a significant opportunity in the enterprise AI market that aligns perfectly with {firm_name}'s investment thesis.

We've built a comprehensive enterprise AI platform with 32 production-ready modules addressing a $8B+ TAM growing at 20% YoY. What makes us unique:

✅ **Complete Platform**: Everything from analytics to security to marketplace
✅ **Anti-Cheat Technology**: Revolutionary gaming security with 99.2% accuracy
✅ **Production Ready**: Full platform built and ready for deployment
✅ **Multiple Revenue Streams**: SaaS, marketplace, licensing, consulting
✅ **Enterprise-Grade**: Multi-tenancy, compliance, white-labeling

Our projections show $100M+ ARR by Year 3, and we're already seeing strong interest from both enterprise clients and gaming partners.

We have:
• Complete technical architecture and documentation
• 50+ business documents (NDAs, contracts, guides)
• Professional web presence and marketing materials
• Clear go-to-market strategy and hiring plans

We're seeking seed funding to accelerate our go-to-market and scale our team.

Would you be open to learning more about our opportunity?

Best regards,
[Your Name]
CEO, Helm AI
        """.strip()
    
    def _get_partner_email_template(self) -> str:
        """Get partner email template"""
        return """
Hi {name},

I hope this email finds you well. I'm reaching out from Helm AI to explore a potential strategic partnership between our companies.

Helm AI has developed a comprehensive enterprise AI platform that could complement {company_name}'s offerings and create significant value for both our customer bases.

Partnership opportunities include:
• Technology integration with our AI platform
• Marketplace distribution for your tools
• Joint go-to-market initiatives
• Revenue sharing arrangements
• Co-marketing and lead generation

Our platform includes:
• Advanced analytics and ML capabilities
• Multi-tenancy and white-labeling
• Complete security and compliance framework
• Marketplace ecosystem for third-party tools

Given {company_name}'s leadership in {specialty}, I believe a partnership could create a powerful combined solution for the market.

Would you be open to a discussion to explore how we could work together?

Best regards,
[Your Name]
CEO, Helm AI
        """.strip()
    
    def launch_outreach_campaign(self, campaign_id: str, prospect_ids: List[str] = None) -> Dict[str, Any]:
        """Launch outreach campaign"""
        try:
            if campaign_id not in self.campaigns:
                return {"error": "Campaign not found"}
            
            campaign = self.campaigns[campaign_id]
            
            # Get target prospects
            if prospect_ids:
                target_prospects = [self.prospects[pid] for pid in prospect_ids if pid in self.prospects]
            else:
                target_prospects = [p for p in self.prospects.values() 
                                  if p.prospect_type == campaign.target_prospect_type]
            
            # Send initial emails
            sent_count = 0
            for prospect in target_prospects:
                # Personalize email
                personalized_email = self._personalize_email(campaign.email_template, prospect)
                
                # Create activity record
                activity = OutreachActivity(
                    id=str(uuid.uuid4()),
                    prospect_id=prospect.id,
                    campaign_id=campaign_id,
                    activity_type="initial_email",
                    status=OutreachStatus.CONTACTED,
                    subject=campaign.subject_line.format(company_name=prospect.company),
                    content=personalized_email
                )
                
                self.activities[activity.id] = activity
                sent_count += 1
            
            # Update campaign metrics
            campaign.metrics = {
                "prospects_contacted": sent_count,
                "campaign_launched": datetime.utcnow().isoformat(),
                "status": "active"
            }
            
            logger.info(f"Launched campaign {campaign.name} to {sent_count} prospects")
            return {
                "success": True,
                "campaign_id": campaign_id,
                "prospects_contacted": sent_count,
                "next_follow_up": self._get_next_follow_up_dates(campaign)
            }
            
        except Exception as e:
            logger.error(f"Failed to launch campaign: {e}")
            return {"error": str(e)}
    
    def _personalize_email(self, template: str, prospect: Prospect) -> str:
        """Personalize email template for prospect"""
        personalized = template.replace("{name}", prospect.name)
        personalized = personalized.replace("{company_name}", prospect.company)
        personalized = personalized.replace("{industry}", prospect.industry)
        
        if prospect.pain_points:
            pain_points_text = "\n".join([f"• {point}" for point in prospect.pain_points])
            personalized = personalized.replace("{pain_points}", pain_points_text)
        
        # Add gaming-specific personalization
        if prospect.prospect_type == ProspectType.GAMING_PARTNER:
            flagship_games = {
                "Epic Games": "Fortnite",
                "Riot Games": "League of Legends and Valorant", 
                "Valve Corporation": "CS:GO and Dota 2"
            }
            flagship_game = flagship_games.get(prospect.company, "your flagship games")
            personalized = personalized.replace("{flagship_game}", flagship_game)
        
        # Add VC-specific personalization
        if prospect.prospect_type == ProspectType.VC_INVESTOR:
            firm_names = {
                "Sequoia Capital": "Sequoia Capital",
                "Andreessen Horowitz": "a16z",
                "Accel": "Accel"
            }
            firm_name = firm_names.get(prospect.company, prospect.company)
            personalized = personalized.replace("{firm_name}", firm_name)
        
        # Add partner-specific personalization
        if prospect.prospect_type == ProspectType.TECHNOLOGY_PARTNER:
            specialties = {
                "Microsoft": "cloud computing and enterprise software",
                "Amazon": "cloud infrastructure and AI services",
                "Google": "AI research and cloud platforms"
            }
            specialty = specialties.get(prospect.company, "your core offerings")
            personalized = personalized.replace("{specialty}", specialty)
        
        return personalized
    
    def _get_next_follow_up_dates(self, campaign: OutreachCampaign) -> List[Dict[str, Any]]:
        """Get next follow-up dates for campaign"""
        follow_ups = []
        for i, follow_up in enumerate(campaign.follow_up_sequence):
            follow_up_date = datetime.utcnow() + timedelta(days=follow_up["delay_days"])
            follow_ups.append({
                "sequence": i + 1,
                "date": follow_up_date.isoformat(),
                "type": follow_up["type"],
                "template": follow_up["template"]
            })
        return follow_ups
    
    def get_acquisition_dashboard(self) -> Dict[str, Any]:
        """Get acquisition dashboard data"""
        try:
            dashboard = {
                "overview": {},
                "campaign_performance": {},
                "prospect_pipeline": {},
                "conversion_metrics": {},
                "next_actions": []
            }
            
            # Overview stats
            total_prospects = len(self.prospects)
            total_campaigns = len(self.campaigns)
            total_activities = len(self.activities)
            
            # Pipeline breakdown
            pipeline_by_type = defaultdict(int)
            pipeline_by_status = defaultdict(int)
            
            for prospect in self.prospects.values():
                pipeline_by_type[prospect.prospect_type.value] += 1
            
            for activity in self.activities.values():
                pipeline_by_status[activity.status.value] += 1
            
            dashboard["overview"] = {
                "total_prospects": total_prospects,
                "total_campaigns": total_campaigns,
                "total_activities": total_activities,
                "active_campaigns": len([c for c in self.campaigns.values() if c.metrics.get("status") == "active"])
            }
            
            dashboard["prospect_pipeline"] = {
                "by_type": dict(pipeline_by_type),
                "by_status": dict(pipeline_by_status)
            }
            
            # Campaign performance
            for campaign in self.campaigns.values():
                campaign_activities = [a for a in self.activities.values() if a.campaign_id == campaign.id]
                responses = len([a for a in campaign_activities if a.response_received])
                
                dashboard["campaign_performance"][campaign.id] = {
                    "name": campaign.name,
                    "type": campaign.campaign_type.value,
                    "target": campaign.target_prospect_type.value,
                    "sent": len(campaign_activities),
                    "responses": responses,
                    "response_rate": (responses / len(campaign_activities) * 100) if campaign_activities else 0
                }
            
            # Next actions
            next_actions = []
            
            # Campaign follow-ups
            for campaign in self.campaigns.values():
                if campaign.metrics.get("status") == "active":
                    follow_ups = self._get_next_follow_up_dates(campaign)
                    for follow_up in follow_ups:
                        follow_up_date = datetime.fromisoformat(follow_up["date"])
                        if follow_up_date <= datetime.utcnow() + timedelta(days=1):
                            next_actions.append({
                                "type": "campaign_follow_up",
                                "campaign": campaign.name,
                                "action": follow_up["type"],
                                "due_date": follow_up["date"],
                                "priority": "high"
                            })
            
            dashboard["next_actions"] = sorted(next_actions, key=lambda x: x["due_date"])[:10]
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Failed to get acquisition dashboard: {e}")
            return {"error": str(e)}
    
    def get_prospect_details(self, prospect_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed prospect information"""
        try:
            if prospect_id not in self.prospects:
                return None
            
            prospect = self.prospects[prospect_id]
            
            # Get prospect activities
            activities = [a for a in self.activities.values() if a.prospect_id == prospect_id]
            activities.sort(key=lambda x: x.sent_at, reverse=True)
            
            return {
                "prospect": {
                    "id": prospect.id,
                    "name": prospect.name,
                    "company": prospect.company,
                    "type": prospect.prospect_type.value,
                    "industry": prospect.industry,
                    "size": prospect.size,
                    "contact_email": prospect.contact_email,
                    "contact_phone": prospect.contact_phone,
                    "linkedin_url": prospect.linkedin_url,
                    "website": prospect.website,
                    "description": prospect.description,
                    "pain_points": prospect.pain_points,
                    "budget_range": prospect.budget_range,
                    "decision_maker": prospect.decision_maker,
                    "created_at": prospect.created_at.isoformat(),
                    "updated_at": prospect.updated_at.isoformat()
                },
                "activities": [
                    {
                        "id": activity.id,
                        "type": activity.activity_type,
                        "status": activity.status.value,
                        "subject": activity.subject,
                        "sent_at": activity.sent_at.isoformat(),
                        "response_received": activity.response_received.isoformat() if activity.response_received else None,
                        "notes": activity.notes
                    }
                    for activity in activities
                ],
                "next_steps": self._get_prospect_next_steps(prospect, activities)
            }
            
        except Exception as e:
            logger.error(f"Failed to get prospect details: {e}")
            return None
    
    def _get_prospect_next_steps(self, prospect: Prospect, activities: List[OutreachActivity]) -> List[str]:
        """Get next steps for prospect"""
        next_steps = []
        
        if not activities:
            next_steps.append("Send initial outreach email")
        else:
            last_activity = activities[0]
            
            if last_activity.status == OutreachStatus.CONTACTED and not last_activity.response_received:
                next_steps.append("Follow up if no response in 3-5 days")
            elif last_activity.status == OutreachStatus.RESPONDED:
                next_steps.append("Schedule meeting/call")
            elif last_activity.status == OutreachStatus.MEETING_SCHEDULED:
                next_steps.append("Prepare for meeting")
            elif last_activity.status == OutreachStatus.MEETING_COMPLETED:
                next_steps.append("Send proposal/next steps")
            elif last_activity.status == OutreachStatus.PROPOSAL_SENT:
                next_steps.append("Follow up on proposal")
        
        return next_steps
    
    def add_prospect(self, prospect_data: Dict[str, Any]) -> Prospect:
        """Add new prospect"""
        try:
            prospect = Prospect(
                id=str(uuid.uuid4()),
                name=prospect_data.get("name", ""),
                company=prospect_data.get("company", ""),
                prospect_type=ProspectType(prospect_data.get("prospect_type", "enterprise_client")),
                industry=prospect_data.get("industry", ""),
                size=prospect_data.get("size", "medium"),
                contact_email=prospect_data.get("contact_email", ""),
                contact_phone=prospect_data.get("contact_phone"),
                linkedin_url=prospect_data.get("linkedin_url"),
                website=prospect_data.get("website", ""),
                description=prospect_data.get("description", ""),
                pain_points=prospect_data.get("pain_points", []),
                budget_range=prospect_data.get("budget_range"),
                decision_maker=prospect_data.get("decision_maker", False)
            )
            
            self.prospects[prospect.id] = prospect
            
            logger.info(f"Added new prospect: {prospect.name} at {prospect.company}")
            return prospect
            
        except Exception as e:
            logger.error(f"Failed to add prospect: {e}")
            raise


# Configuration
ACQUISITION_CONFIG = {
    "database": {
        "connection_string": os.getenv("DATABASE_URL")
    },
    "outreach": {
        "email_provider": "sendgrid",
        "daily_limit": 100,
        "follow_up_intervals": [3, 7, 14],
        "personalization_enabled": True
    },
    "crm": {
        "track_all_activities": True,
        "auto_score_leads": True,
        "sync_with_salesforce": True
    }
}


# Initialize acquisition manager
acquisition_manager = AcquisitionManager(ACQUISITION_CONFIG)

# Export main components
__all__ = [
    'AcquisitionManager',
    'Prospect',
    'OutreachCampaign',
    'OutreachActivity',
    'ProspectType',
    'OutreachStatus',
    'CampaignType',
    'acquisition_manager'
]

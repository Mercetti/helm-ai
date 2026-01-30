"""
Helm AI Game Session Model
SQLAlchemy model for game session tracking and analysis
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, Enum as SQLEnum, ForeignKey, Float
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
import enum

from . import Base

class GameSessionStatus(enum.Enum):
    """Game session status enumeration"""
    ACTIVE = "active"
    COMPLETED = "completed"
    ABORTED = "aborted"
    DISCONNECTED = "disconnected"
    SUSPENDED = "suspended"
    BANNED = "banned"

class GameType(enum.Enum):
    """Game type enumeration"""
    POKER = "poker"
    BLACKJACK = "blackjack"
    ROULETTE = "roulette"
    SLOTS = "slots"
    SPORTS_BETTING = "sports_betting"
    ESPORTS = "esports"
    CUSTOM = "custom"

class CheatDetectionStatus(enum.Enum):
    """Cheat detection status enumeration"""
    CLEAN = "clean"
    SUSPICIOUS = "suspicious"
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"

class GameSession(Base):
    """Game session model for tracking gameplay and cheat detection"""
    
    __tablename__ = "game_sessions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User relationship
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Session information
    session_id = Column(String(128), unique=True, nullable=False, index=True)
    game_type = Column(SQLEnum(GameType), nullable=False, index=True)
    game_variant = Column(String(100), nullable=True)  # Texas Hold'em, Omaha, etc.
    
    # Status and timing
    status = Column(SQLEnum(GameSessionStatus), default=GameSessionStatus.ACTIVE, index=True)
    started_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    ended_at = Column(DateTime, nullable=True, index=True)
    duration_seconds = Column(Integer, nullable=True)
    
    # Game configuration
    table_id = Column(String(100), nullable=True, index=True)
    tournament_id = Column(String(100), nullable=True, index=True)
    stake_level = Column(String(50), nullable=True)  # Low, Medium, High, etc.
    buy_in_amount = Column(Float, nullable=True)
    currency = Column(String(10), default="USD")
    
    # Player information
    player_name = Column(String(100), nullable=True)
    player_avatar = Column(String(255), nullable=True)
    player_level = Column(Integer, nullable=True)
    player_rank = Column(String(50), nullable=True)
    
    # Connection information
    client_ip = Column(String(45), nullable=True, index=True)
    client_country = Column(String(2), nullable=True, index=True)
    client_user_agent = Column(Text, nullable=True)
    client_version = Column(String(50), nullable=True)
    platform = Column(String(50), nullable=True)  # Windows, Mac, Mobile, etc.
    
    # Performance metrics
    total_actions = Column(Integer, default=0)
    total_hands = Column(Integer, default=0)
    total_winnings = Column(Float, default=0.0)
    total_losses = Column(Float, default=0.0)
    net_profit = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    
    # Behavioral metrics
    avg_decision_time_ms = Column(Float, nullable=True)
    avg_bet_size = Column(Float, nullable=True)
    max_bet_size = Column(Float, nullable=True)
    variance_score = Column(Float, nullable=True)
    aggression_score = Column(Float, nullable=True)
    
    # Cheat detection
    cheat_detection_status = Column(SQLEnum(CheatDetectionStatus), default=CheatDetectionStatus.CLEAN, index=True)
    cheat_confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    cheat_types_detected = Column(JSON, default=list)  # List of detected cheat types
    risk_score = Column(Float, default=0.0)  # 0.0 to 100.0
    flagged_at = Column(DateTime, nullable=True)
    investigated_at = Column(DateTime, nullable=True)
    
    # AI analysis results
    ai_analysis = Column(JSON, default=dict)  # Detailed AI analysis results
    vision_analysis = Column(JSON, default=dict)  # Computer vision analysis
    audio_analysis = Column(JSON, default=dict)  # Audio analysis
    network_analysis = Column(JSON, default=dict)  # Network traffic analysis
    
    # Manual review
    manual_review_required = Column(Boolean, default=False)
    manual_review_by = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    manual_review_notes = Column(Text, nullable=True)
    manual_review_at = Column(DateTime, nullable=True)
    
    # Actions taken
    actions_taken = Column(JSON, default=list)  # List of actions taken (warning, ban, etc.)
    ban_reason = Column(Text, nullable=True)
    ban_expires_at = Column(DateTime, nullable=True)
    
    # Session events
    events = Column(JSON, default=list)  # Timeline of session events
    
    # Metadata
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="game_sessions")
    reviewer = relationship("User", foreign_keys=[manual_review_by])
    
    def __repr__(self):
        return f"<GameSession(id={self.id}, user_id={self.user_id}, game_type={self.game_type})>"
    
    @property
    def is_active(self) -> bool:
        """Check if session is currently active"""
        return self.status == GameSessionStatus.ACTIVE
    
    @property
    def is_completed(self) -> bool:
        """Check if session is completed"""
        return self.status == GameSessionStatus.COMPLETED
    
    @property
    def is_suspicious(self) -> bool:
        """Check if session is flagged as suspicious"""
        return (
            self.cheat_detection_status in [CheatDetectionStatus.SUSPICIOUS, CheatDetectionStatus.DETECTED, CheatDetectionStatus.CONFIRMED] or
            (self.risk_score and self.risk_score >= 70)
        )
    
    @property
    def requires_review(self) -> bool:
        """Check if session requires manual review"""
        return (
            self.manual_review_required or
            self.is_suspicious or
            (self.cheat_confidence_score and self.cheat_confidence_score >= 0.7)
        )
    
    @property
    def duration_minutes(self) -> Optional[float]:
        """Get session duration in minutes"""
        if self.duration_seconds:
            return self.duration_seconds / 60
        return None
    
    @property
    def profit_loss(self) -> float:
        """Get profit/loss amount"""
        return self.net_profit
    
    @property
    def roi_percentage(self) -> Optional[float]:
        """Get return on investment percentage"""
        if self.buy_in_amount and self.buy_in_amount > 0:
            return (self.net_profit / self.buy_in_amount) * 100
        return None
    
    @property
    def session_age_hours(self) -> float:
        """Get session age in hours"""
        return (datetime.now() - self.started_at).total_seconds() / 3600
    
    def end_session(self, status: GameSessionStatus = GameSessionStatus.COMPLETED):
        """End the session"""
        if self.is_active:
            self.status = status
            self.ended_at = datetime.now()
            if self.started_at:
                self.duration_seconds = int((self.ended_at - self.started_at).total_seconds())
            self.updated_at = datetime.now()
    
    def add_event(self, event_type: str, description: str, timestamp: datetime = None, **kwargs):
        """Add event to session timeline"""
        event = {
            "type": event_type,
            "description": description,
            "timestamp": (timestamp or datetime.now()).isoformat(),
            **kwargs
        }
        self.events.append(event)
        self.updated_at = datetime.now()
    
    def update_performance_metrics(self, **kwargs):
        """Update performance metrics"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def add_cheat_detection(self, cheat_type: str, confidence: float, **kwargs):
        """Add cheat detection result"""
        if cheat_type not in self.cheat_types_detected:
            self.cheat_types_detected.append(cheat_type)
        
        # Update confidence score (keep highest)
        if self.cheat_confidence_score is None or confidence > self.cheat_confidence_score:
            self.cheat_confidence_score = confidence
        
        # Update status based on confidence
        if confidence >= 0.8:
            self.cheat_detection_status = CheatDetectionStatus.DETECTED
        elif confidence >= 0.5:
            self.cheat_detection_status = CheatDetectionStatus.SUSPICIOUS
        
        self.flagged_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Add event
        self.add_event("cheat_detected", f"Cheat type {cheat_type} detected with confidence {confidence}", **kwargs)
    
    def calculate_risk_score(self) -> float:
        """Calculate comprehensive risk score"""
        score = 0.0
        
        # Base score from cheat detection
        if self.cheat_confidence_score:
            score += self.cheat_confidence_score * 50  # Max 50 points
        
        # Add points for multiple cheat types
        score += len(self.cheat_types_detected) * 10  # 10 points per cheat type
        
        # Add points for suspicious behavior patterns
        if self.variance_score and self.variance_score > 0.8:
            score += 15
        
        if self.aggression_score and self.aggression_score > 0.9:
            score += 10
        
        # Add points for unusual performance metrics
        if self.avg_decision_time_ms and self.avg_decision_time_ms < 100:  # Too fast
            score += 10
        
        if self.win_rate and self.win_rate > 0.8:  # Too high win rate
            score += 15
        
        # Cap at 100
        return min(100.0, score)
    
    def update_risk_score(self):
        """Update risk score"""
        self.risk_score = self.calculate_risk_score()
        self.updated_at = datetime.now()
    
    def flag_for_review(self, reason: str = None):
        """Flag session for manual review"""
        self.manual_review_required = True
        self.add_event("flagged_for_review", reason or "Session flagged for manual review")
        self.updated_at = datetime.now()
    
    def assign_reviewer(self, reviewer_id: int):
        """Assign reviewer for manual review"""
        self.manual_review_by = reviewer_id
        self.updated_at = datetime.now()
    
    def complete_review(self, reviewer_id: int, notes: str, action: str = None):
        """Complete manual review"""
        self.manual_review_by = reviewer_id
        self.manual_review_notes = notes
        self.manual_review_at = datetime.now()
        self.manual_review_required = False
        
        if action:
            self.actions_taken.append(action)
            self.add_event("review_completed", f"Manual review completed with action: {action}")
        
        self.updated_at = datetime.now()
    
    def ban_player(self, reason: str, duration_days: int = None):
        """Ban player"""
        self.status = GameSessionStatus.BANNED
        self.ban_reason = reason
        if duration_days:
            self.ban_expires_at = datetime.now() + timedelta(days=duration_days)
        
        self.actions_taken.append(f"banned: {reason}")
        self.add_event("player_banned", f"Player banned: {reason}")
        self.end_session(GameSessionStatus.BANNED)
    
    def to_dict(self, include_sensitive: bool = True) -> Dict[str, Any]:
        """Convert game session to dictionary"""
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "game_type": self.game_type.value,
            "game_variant": self.game_variant,
            "status": self.status.value,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": self.duration_seconds,
            "duration_minutes": self.duration_minutes,
            "table_id": self.table_id,
            "tournament_id": self.tournament_id,
            "stake_level": self.stake_level,
            "buy_in_amount": self.buy_in_amount,
            "currency": self.currency,
            "player_name": self.player_name,
            "player_level": self.player_level,
            "player_rank": self.player_rank,
            "client_ip": self.client_ip,
            "client_country": self.client_country,
            "client_version": self.client_version,
            "platform": self.platform,
            "total_actions": self.total_actions,
            "total_hands": self.total_hands,
            "total_winnings": self.total_winnings,
            "total_losses": self.total_losses,
            "net_profit": self.net_profit,
            "profit_loss": self.profit_loss,
            "win_rate": self.win_rate,
            "roi_percentage": self.roi_percentage,
            "avg_decision_time_ms": self.avg_decision_time_ms,
            "avg_bet_size": self.avg_bet_size,
            "max_bet_size": self.max_bet_size,
            "variance_score": self.variance_score,
            "aggression_score": self.aggression_score,
            "cheat_detection_status": self.cheat_detection_status.value,
            "cheat_confidence_score": self.cheat_confidence_score,
            "cheat_types_detected": self.cheat_types_detected,
            "risk_score": self.risk_score,
            "flagged_at": self.flagged_at.isoformat() if self.flagged_at else None,
            "investigated_at": self.investigated_at.isoformat() if self.investigated_at else None,
            "manual_review_required": self.manual_review_required,
            "manual_review_by": self.manual_review_by,
            "manual_review_at": self.manual_review_at.isoformat() if self.manual_review_at else None,
            "actions_taken": self.actions_taken,
            "ban_reason": self.ban_reason,
            "ban_expires_at": self.ban_expires_at.isoformat() if self.ban_expires_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "is_completed": self.is_completed,
            "is_suspicious": self.is_suspicious,
            "requires_review": self.requires_review,
            "session_age_hours": self.session_age_hours
        }
        
        if include_sensitive:
            data.update({
                "details": self.details if hasattr(self, 'details') else {},
                "ai_analysis": self.ai_analysis,
                "vision_analysis": self.vision_analysis,
                "audio_analysis": self.audio_analysis,
                "network_analysis": self.network_analysis,
                "manual_review_notes": self.manual_review_notes,
                "events": self.events
            })
        
        return data
    
    @classmethod
    def create_session(cls, user_id: int, game_type: GameType, session_id: str, **kwargs) -> "GameSession":
        """Create new game session"""
        defaults = {
            "status": GameSessionStatus.ACTIVE,
            "events": [],
            "actions_taken": [],
            "cheat_types_detected": [],
            "ai_analysis": {},
            "vision_analysis": {},
            "audio_analysis": {},
            "network_analysis": {}
        }
        
        # Override defaults with provided kwargs
        defaults.update(kwargs)
        
        session = cls(
            user_id=user_id,
            game_type=game_type,
            session_id=session_id,
            **defaults
        )
        
        # Add start event
        session.add_event("session_started", f"Game session started: {game_type.value}")
        
        return session

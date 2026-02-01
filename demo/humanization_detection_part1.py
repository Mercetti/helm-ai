#!/usr/bin/env python3
"""
Stellar Logic AI - Advanced Humanization Detection System (Part 1)
Enhanced humanization detection for fatigue, emotion, skill progression
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import random
import math
from collections import defaultdict, deque

class HumanizationType(Enum):
    """Types of humanization techniques"""
    FATIGUE_SIMULATION = "fatigue_simulation"
    EMOTIONAL_VARIATION = "emotional_variation"
    SKILL_PROGRESSION = "skill_progression"
    STRESS_RESPONSE = "stress_response"
    MOTIVATION_FLUCTUATION = "motivation_fluctuation"

class HumanizationSeverity(Enum):
    """Severity levels for humanization detection"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class HumanizationEvent:
    """Humanization event data point"""
    timestamp: datetime
    player_id: str
    humanization_type: HumanizationType
    intensity: float
    context: Dict[str, Any]
    metrics: Dict[str, float]

@dataclass
class HumanizationDetection:
    """Humanization detection result"""
    detection_id: str
    humanization_type: HumanizationType
    severity: HumanizationSeverity
    confidence: float
    timestamp: datetime
    player_id: str
    event_data: HumanizationEvent
    analysis_metrics: Dict[str, float]
    risk_factors: List[str]

@dataclass
class HumanizationProfile:
    """Humanization profile for player"""
    player_id: str
    session_count: int
    total_playtime: float
    humanization_events: deque
    baseline_patterns: Dict[str, Dict[str, float]]
    last_updated: datetime

class AdvancedHumanizationDetection:
    """Advanced humanization detection system"""
    
    def __init__(self):
        self.profiles = {}
        self.humanization_thresholds = {
            'fatigue_threshold': 0.7,
            'emotion_threshold': 0.6,
            'skill_progression_threshold': 0.5,
            'stress_threshold': 0.8,
            'motivation_threshold': 0.6
        }
        
        # Humanization analysis methods
        self.methods = {
            'fatigue_simulation': self._analyze_fatigue,
            'emotional_variation': self._analyze_emotion,
            'skill_progression': self._analyze_skill_progression,
            'stress_response': self._analyze_stress_response,
            'motivation_fluctuation': self._analyze_motivation
        }
        
        # Performance metrics
        self.humanization_events_detected = 0
        self.false_positives = 0
        self.true_positives = 0
        
        # Data window configuration
        self.window_size = 1000
        self.min_events_for_analysis = 50
        
    def create_profile(self, player_id: str) -> HumanizationProfile:
        """Create humanization profile for player"""
        profile = HumanizationProfile(
            player_id=player_id,
            session_count=0,
            total_playtime=0.0,
            humanization_events=deque(maxlen=self.window_size),
            baseline_patterns={},
            last_updated=datetime.now()
        )
        
        self.profiles[player_id] = profile
        return profile
    
    def add_humanization_event(self, player_id: str, event: HumanizationEvent) -> List[HumanizationDetection]:
        """Add humanization event and detect patterns"""
        profile = self.profiles.get(player_id)
        if not profile:
            profile = self.create_profile(player_id)
        
        # Add event to history
        profile.humanization_events.append(event)
        profile.last_updated = datetime.now()
        
        # Update session and playtime
        if event.context.get('session_duration'):
            profile.session_count += 1
            profile.total_playtime += event.context['session_duration']
        
        # Detect humanization patterns
        detections = []
        
        if len(profile.humanization_events) >= self.min_events_for_analysis:
            # Update baseline patterns
            self._update_baseline_patterns(profile)
            
            # Analyze specific humanization type
            method_result = self.methods[event.humanization_type.value](profile, event)
            
            if method_result['is_humanization']:
                # Create detection result
                detection = self._create_detection_result(method_result, player_id, event)
                detections.append(detection)
                profile.humanization_events.append(event)
                self.humanization_events_detected += 1
        
        return detections
    
    def _update_baseline_patterns(self, profile: HumanizationProfile):
        """Update baseline patterns for humanization analysis"""
        recent_events = list(profile.humanization_events)[-100:]
        
        # Group events by type
        events_by_type = defaultdict(list)
        for event in recent_events:
            events_by_type[event.humanization_type].append(event)
        
        # Calculate baseline statistics for each type
        for humanization_type, events in events_by_type.items():
            if len(events) >= 10:
                intensities = [event.intensity for event in events]
                profile.baseline_patterns[humanization_type.value] = {
                    'mean_intensity': sum(intensities) / len(intensities),
                    'std_intensity': self._std(intensities),
                    'min_intensity': min(intensities),
                    'max_intensity': max(intensities),
                    'frequency': len(events) / len(recent_events),
                    'pattern_stability': self._calculate_pattern_stability(intensities)
                }
    
    def _analyze_fatigue(self, profile: HumanizationProfile, event: HumanizationEvent) -> Dict[str, Any]:
        """Analyze fatigue patterns"""
        recent_events = list(profile.humanization_events)[-50:]
        fatigue_events = [e for e in recent_events if e.humanization_type == HumanizationType.FATIGUE_SIMULATION]
        
        if len(fatigue_events) < 5:
            return {'is_humanization': False, 'confidence': 0.0, 'method': 'fatigue_analysis'}
        
        # Calculate fatigue metrics
        intensities = [e.intensity for e in fatigue_events]
        current_intensity = event.intensity
        
        # Check for increasing fatigue pattern
        fatigue_trend = self._calculate_trend(intensities)
        
        # Check if current session shows fatigue indicators
        session_duration = event.context.get('session_duration', 0)
        hours_played = event.context.get('hours_played_today', 0)
        
        fatigue_indicators = []
        if hours_played > 4:
            fatigue_indicators.append("extended_playtime")
        
        if session_duration > 120:
            fatigue_indicators.append("long_session")
        
        if current_intensity > self.humanization_thresholds['fatigue_threshold']:
            fatigue_indicators.append("high_fatigue_level")
        
        if fatigue_trend > 0.3:
            fatigue_indicators.append("fatigue_trend_upward")
        
        # Calculate confidence
        confidence = 0.0
        if fatigue_indicators:
            confidence = min(1.0, len(fatigue_indicators) * 0.25)
        
        is_humanization = confidence > 0.5
        
        return {
            'is_humanization': is_humanization,
            'confidence': confidence,
            'method': 'fatigue_analysis',
            'fatigue_trend': fatigue_trend,
            'fatigue_indicators': fatigue_indicators,
            'hours_played': hours_played,
            'session_duration': session_duration
        }
    
    def _analyze_emotion(self, profile: HumanizationProfile, event: HumanizationEvent) -> Dict[str, Any]:
        """Analyze emotional variation patterns"""
        recent_events = list(profile.humanization_events)[-50:]
        emotion_events = [e for e in recent_events if e.humanization_type == HumanizationType.EMOTIONAL_VARIATION]
        
        if len(emotion_events) < 5:
            return {'is_humanization': False, 'confidence': 0.0, 'method': 'emotion_analysis'}
        
        # Calculate emotional volatility
        intensities = [e.intensity for e in emotion_events]
        emotional_volatility = self._std(intensities)
        
        # Check for emotional triggers
        triggers = event.context.get('emotional_triggers', [])
        
        # Check for emotional patterns
        emotional_patterns = []
        if emotional_volatility > 0.3:
            emotional_patterns.append("high_volatility")
        
        if len(triggers) > 0:
            emotional_patterns.append("triggered_responses")
        
        # Check for emotional stability over time
        stability = self._calculate_pattern_stability(intensities)
        if stability < 0.5:
            emotional_patterns.append("unstable_emotions")
        
        # Calculate confidence
        confidence = min(1.0, emotional_volatility * 2)
        
        is_humanization = confidence > self.humanization_thresholds['emotion_threshold']
        
        return {
            'is_humanization': is_humanization,
            'confidence': confidence,
            'method': 'emotion_analysis',
            'emotional_volatility': emotional_volatility,
            'emotional_patterns': emotional_patterns,
            'emotional_triggers': triggers,
            'stability': stability
        }
    
    def _analyze_skill_progression(self, profile: HumanizationProfile, event: HumanizationEvent) -> Dict[str, Any]:
        """Analyze skill progression patterns"""
        recent_events = list(profile.humanization_events)[-100:]
        skill_events = [e for e in recent_events if e.humanization_type == HumanizationType.SKILL_PROGRESSION]
        
        if len(skill_events) < 10:
            return {'is_humanization': False, 'confidence': 0.0, 'method': 'skill_progression_analysis'}
        
        # Calculate skill progression metrics
        performance_scores = [event.metrics.get('performance_score', 0.5) for event in skill_events]
        
        # Calculate progression rate
        if len(performance_scores) >= 2:
            progression_rate = (performance_scores[-1] - performance_scores[0]) / len(performance_scores)
        else:
            progression_rate = 0.0
        
        # Check for natural learning patterns
        learning_patterns = []
        
        # Check for gradual improvement
        if 0.05 < progression_rate < 0.15:
            learning_patterns.append("gradual_improvement")
        elif progression_rate > 0.2:
            learning_patterns.append("rapid_improvement")
        elif progression_rate < -0.1:
            learning_patterns.append("performance_decline")
        
        # Check for plateau periods
        if abs(progression_rate) < 0.02:
            learning_patterns.append("plateau_period")
        
        # Calculate confidence
        confidence = min(1.0, abs(progression_rate) * 5)
        
        is_humanization = confidence > self.humanization_thresholds['skill_progression_threshold']
        
        return {
            'is_humanization': is_humanization,
            'confidence': confidence,
            'method': 'skill_progression_analysis',
            'progression_rate': progression_rate,
            'learning_patterns': learning_patterns,
            'performance_scores': performance_scores[-5:] if len(performance_scores) >= 5 else performance_scores
        }
    
    def _analyze_stress_response(self, profile: HumanizationProfile, event: HumanizationEvent) -> Dict[str, Any]:
        """Analyze stress response patterns"""
        recent_events = list(profile.humanization_events)[-50:]
        stress_events = [e for e in recent_events if e.humanization_type == HumanizationType.STRESS_RESPONSE]
        
        if len(stress_events) < 5:
            return {'is_humanization': False, 'confidence': 0.0, 'method': 'stress_response_analysis'}
        
        # Calculate stress metrics
        intensities = [e.intensity for e in stress_events]
        current_stress = event.intensity
        
        # Check for stress triggers
        stress_triggers = event.context.get('stress_triggers', [])
        
        # Check for stress patterns
        stress_patterns = []
        
        if current_stress > self.humanization_thresholds['stress_threshold']:
            stress_patterns.append("high_stress_level")
        
        if len(stress_triggers) > 0:
            stress_patterns.append("triggered_stress")
        
        # Calculate confidence
        confidence = min(1.0, current_stress * 1.2)
        
        is_humanization = confidence > self.humanization_thresholds['stress_threshold']
        
        return {
            'is_humanization': is_humanization,
            'confidence': confidence,
            'method': 'stress_response_analysis',
            'current_stress': current_stress,
            'stress_patterns': stress_patterns,
            'stress_triggers': stress_triggers
        }
    
    def _analyze_motivation(self, profile: HumanizationProfile, event: HumanizationEvent) -> Dict[str, Any]:
        """Analyze motivation fluctuation patterns"""
        recent_events = list(profile.humanization_events)[-50:]
        motivation_events = [e for e in recent_events if e.humanization_type == HumanizationType.MOTIVATION_FLUCTUATION]
        
        if len(motivation_events) < 5:
            return {'is_humanization': False, 'confidence': 0.0, 'method': 'motivation_analysis'}
        
        # Calculate motivation metrics
        intensities = [e.intensity for e in motivation_events]
        current_motivation = event.intensity
        
        # Check for motivation patterns
        motivation_patterns = []
        
        if current_motivation < 0.3:
            motivation_patterns.append("low_motivation")
        elif current_motivation > 0.8:
            motivation_patterns.append("high_motivation")
        
        # Check for motivation stability
        motivation_stability = self._calculate_pattern_stability(intensities)
        if motivation_stability < 0.4:
            motivation_patterns.append("unstable_motivation")
        
        # Calculate confidence
        confidence = min(1.0, (1 - motivation_stability) * 2)
        
        is_humanization = confidence > self.humanization_thresholds['motivation_threshold']
        
        return {
            'is_humanization': is_humanization,
            'confidence': confidence,
            'method': 'motivation_analysis',
            'current_motivation': current_motivation,
            'motivation_patterns': motivation_patterns,
            'motivation_stability': motivation_stability
        }
    
    def _create_detection_result(self, method_result: Dict, player_id: str, event: HumanizationEvent) -> HumanizationDetection:
        """Create humanization detection result"""
        # Determine severity based on confidence and intensity
        confidence = method_result['confidence']
        intensity = event.intensity
        
        if confidence >= 0.9:
            severity = HumanizationSeverity.CRITICAL
        elif confidence >= 0.7:
            severity = HumanizationSeverity.HIGH
        elif confidence >= 0.5:
            severity = HumanizationSeverity.MEDIUM
        else:
            severity = HumanizationSeverity.LOW
        
        # Collect risk factors
        risk_factors = []
        for key, value in method_result.items():
            if key.endswith('_indicators') or key.endswith('_patterns'):
                if isinstance(value, list):
                    risk_factors.extend(value)
                elif isinstance(value, str):
                    risk_factors.append(value)
        
        return HumanizationDetection(
            detection_id=f"humanization_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            humanization_type=event.humanization_type,
            severity=severity,
            confidence=confidence,
            timestamp=datetime.now(),
            player_id=player_id,
            event_data=event,
            analysis_metrics={
                'method_confidence': confidence,
                'intensity': intensity,
                'detection_method': method_result['method']
            },
            risk_factors=risk_factors
        )
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend in values"""
        if len(values) < 2:
            return 0.0
        
        n = len(values)
        x = list(range(n))
        
        # Simple linear trend calculation
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(x[i] ** 2 for i in range(n))
        
        if n * sum_x2 - sum_x ** 2 == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        return slope
    
    def _calculate_pattern_stability(self, values: List[float]) -> float:
        """Calculate pattern stability"""
        if len(values) < 2:
            return 1.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        if mean == 0:
            return 1.0
        
        return 1.0 - (math.sqrt(variance) / abs(mean))
    
    def _std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)
    
    def get_profile_summary(self, player_id: str) -> Dict[str, Any]:
        """Get humanization profile summary"""
        profile = self.profiles.get(player_id)
        if not profile:
            return {'error': 'Profile not found'}
        
        # Calculate detection statistics
        detection_stats = self._calculate_detection_statistics(profile)
        
        return {
            'player_id': player_id,
            'session_count': profile.session_count,
            'total_playtime': profile.total_playtime,
            'total_events': len(profile.humanization_events),
            'baseline_established': len(profile.baseline_patterns) > 0,
            'detection_statistics': detection_stats,
            'last_updated': profile.last_updated.isoformat()
        }
    
    def _calculate_detection_statistics(self, profile: HumanizationProfile) -> Dict[str, Any]:
        """Calculate detection statistics"""
        if not profile.humanization_events:
            return {
                'total_detections': 0,
                'type_distribution': {},
                'severity_distribution': {},
                'avg_confidence': 0.0,
                'trend': 'stable'
            }
        
        # Calculate statistics from recent events
        recent_events = list(profile.humanization_events)[-100:]
        
        type_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        confidences = []
        
        for event in recent_events:
            type_counts[event.humanization_type.value] += 1
            if event.intensity > 0.7:
                severity_counts['high'] += 1
            elif event.intensity > 0.4:
                severity_counts['medium'] += 1
            else:
                severity_counts['low'] += 1
            confidences.append(event.intensity)
        
        # Analyze trend
        if len(confidences) >= 10:
            recent_confidences = confidences[-10:]
            older_confidences = confidences[-20:-10] if len(confidences) > 10 else []
            
            recent_avg = sum(recent_confidences) / len(recent_confidences)
            older_avg = sum(older_confidences) / len(older_confidences) if older_confidences else recent_avg
            
            if recent_avg > older_avg * 1.2:
                trend = 'increasing'
            elif recent_avg < older_avg * 0.8:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'total_detections': len(recent_events),
            'type_distribution': dict(type_counts),
            'severity_distribution': dict(severity_counts),
            'avg_confidence': sum(confidences) / len(confidences),
            'trend': trend
        }
    
    def get_system_performance(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return {
            'humanization_events_detected': self.humanization_events_detected,
            'true_positives': self.true_positives,
            'false_positives': self.false_positives,
            'accuracy_rate': self.true_positives / max(1, self.humanization_events_detected),
            'active_profiles': len(self.profiles),
            'humanization_methods': len(self.methods),
            'humanization_thresholds': self.humanization_thresholds
        }

# Test the advanced humanization detection system
def test_advanced_humanization_detection():
    """Test the advanced humanization detection system"""
    print("🧠 Testing Advanced Humanization Detection System")
    print("=" * 50)
    
    system = AdvancedHumanizationDetection()
    
    # Create test profiles
    print("\n🎮 Creating Test Profiles...")
    
    # Normal player
    normal_player_id = "player_normal_001"
    normal_profile = system.create_profile(normal_player_id)
    
    # Humanized cheater
    humanized_player_id = "player_humanized_001"
    humanized_profile = system.create_profile(humanized_player_id)
    
    # AI vs AI cheater
    ai_player_id = "player_ai_001"
    ai_profile = system.create_profile(ai_player_id)
    
    # Simulate normal player behavior
    print("\n👤 Simulating Normal Player Behavior...")
    for session in range(20):
        session_start = datetime.now() - timedelta(hours=session*2)
        session_duration = random.uniform(30, 120)
        
        # Normal fatigue pattern
        if session > 10:
            fatigue_intensity = 0.3 + (session - 10) * 0.05
        else:
            fatigue_intensity = 0.1
        
        fatigue_event = HumanizationEvent(
            timestamp=session_start,
            player_id=normal_player_id,
            humanization_type=HumanizationType.FATIGUE_SIMULATION,
            intensity=fatigue_intensity,
            context={
                'session_duration': session_duration,
                'hours_played_today': session * 2,
                'performance_degradation': fatigue_intensity * 0.2
            },
            metrics={'performance_score': 0.8 - fatigue_intensity * 0.1}
        )
        system.add_humanization_event(normal_player_id, fatigue_event)
        
        # Normal emotional variation
        for _ in range(5):
            emotion_intensity = random.uniform(0.2, 0.6)
            emotion_event = HumanizationEvent(
                timestamp=session_start + timedelta(minutes=random.randint(1, 60)),
                player_id=normal_player_id,
                humanization_type=HumanizationType.EMOTIONAL_VARIATION,
                intensity=emotion_intensity,
                context={
                    'emotional_triggers': ['win', 'loss', 'team_conflict'],
                    'emotional_state': random.choice(['happy', 'frustrated', 'neutral', 'excited'])
                },
                metrics={'performance_score': 0.75 + emotion_intensity * 0.1}
            )
            system.add_humanization_event(normal_player_id, emotion_event)
        
        # Normal skill progression
        skill_improvement = 0.02 + session * 0.01
        skill_event = HumanizationEvent(
            timestamp=session_start + timedelta(minutes=30),
            player_id=normal_player_id,
            humanization_type=HumanizationType.SKILL_PROGRESSION,
            intensity=skill_improvement,
            context={'learning_session': True},
            metrics={'performance_score': 0.6 + skill_improvement}
        )
        system.add_humanization_event(normal_player_id, skill_event)
    
    # Simulate humanized cheater behavior
    print("\n🎭 Simulating Humanized Cheater Behavior...")
    for session in range(15):
        session_start = datetime.now() - timedelta(hours=session*3)
        session_duration = random.uniform(60, 180)
        
        # Exaggerated fatigue simulation
        fatigue_intensity = 0.6 + random.uniform(0, 0.3)
        fatigue_event = HumanizationEvent(
            timestamp=session_start,
            player_id=humanized_player_id,
            humanization_type=HumanizationType.FATIGUE_SIMULATION,
            intensity=fatigue_intensity,
            context={
                'session_duration': session_duration,
                'hours_played_today': session * 3,
                'performance_degradation': fatigue_intensity * 0.4
            },
            metrics={'performance_score': 0.9 - fatigue_intensity * 0.2}
        )
        system.add_humanization_event(humanized_player_id, fatigue_event)
        
        # Overly emotional responses
        for _ in range(8):
            emotion_intensity = random.uniform(0.5, 0.9)
            emotion_event = HumanizationEvent(
                timestamp=session_start + timedelta(minutes=random.randint(1, 60)),
                player_id=humanized_player_id,
                humanization_type=HumanizationType.EMOTIONAL_VARIATION,
                intensity=emotion_intensity,
                context={
                    'emotional_triggers': ['win', 'loss', 'team_conflict', 'cheat_detected'],
                    'emotional_state': random.choice(['angry', 'frustrated', 'nervous', 'overconfident'])
                },
                metrics={'performance_score': 0.8 + emotion_intensity * 0.15}
            )
            system.add_humanization_event(humanized_player_id, emotion_event)
        
        # Unrealistic skill progression
        skill_improvement = 0.15 + session * 0.02
        skill_event = HumanizationEvent(
            timestamp=session_start + timedelta(minutes=30),
            player_id=humanized_player_id,
            humanization_type=HumanizationType.SKILL_PROGRESSION,
            intensity=skill_improvement,
            context={'learning_session': True, 'rapid_improvement': True},
            metrics={'performance_score': 0.7 + skill_improvement}
        )
        system.add_humanization_event(humanized_player_id, skill_event)
    
    # Simulate AI vs AI cheater behavior
    print("\n🤖 Simulating AI vs AI Cheater Behavior...")
    for session in range(10):
        session_start = datetime.now() - timedelta(hours=session*4)
        session_duration = random.uniform(90, 240)
        
        # No fatigue simulation (AI doesn't get tired)
        fatigue_event = HumanizationEvent(
            timestamp=session_start,
            player_id=ai_player_id,
            humanization_type=HumanizationType.FATIGUE_SIMULATION,
            intensity=0.05,  # Very low fatigue
            context={
                'session_duration': session_duration,
                'hours_played_today': session * 4,
                'performance_degradation': 0.01
            },
            metrics={'performance_score': 0.95}
        )
        system.add_humanization_event(ai_player_id, fatigue_event)
        
        # No emotional variation (AI doesn't have emotions)
        for _ in range(3):
            emotion_intensity = 0.1  # Very low emotion
            emotion_event = HumanizationEvent(
                timestamp=session_start + timedelta(minutes=random.randint(1, 60)),
                player_id=ai_player_id,
                humanization_type=HumanizationType.EMOTIONAL_VARIATION,
                intensity=emotion_intensity,
                context={
                    'emotional_triggers': [],
                    'emotional_state': 'neutral'
                },
                metrics={'performance_score': 0.95}
            )
            system.add_humanization_event(ai_player_id, emotion_event)
        
        # Perfect skill progression (AI learns instantly)
        skill_improvement = 0.3 + session * 0.05
        skill_event = HumanizationEvent(
            timestamp=session_start + timedelta(minutes=30),
            player_id=ai_player_id,
            humanization_type=HumanizationType.SKILL_PROGRESSION,
            intensity=skill_improvement,
            context={'learning_session': True, 'instant_learning': True},
            metrics={'performance_score': 0.95 + skill_improvement}
        )
        system.add_humanization_event(ai_player_id, skill_event)
    
    # Generate reports
    print("\n📋 Generating Humanization Detection Reports...")
    
    print("\n📄 NORMAL PLAYER REPORT:")
    normal_summary = system.get_profile_summary(normal_player_id)
    print(f"   Sessions: {normal_summary['session_count']}")
    print(f"   Total Playtime: {normal_summary['total_playtime']:.1f} hours")
    print(f"   Total Events: {normal_summary['total_events']}")
    print(f"   Baseline Established: {normal_summary['baseline_established']}")
    print(f"   Total Detections: {normal_summary['detection_statistics']['total_detections']}")
    print(f"   Average Confidence: {normal_summary['detection_statistics']['avg_confidence']:.1%}")
    
    print("\n📄 HUMANIZED CHEATER REPORT:")
    humanized_summary = system.get_profile_summary(humanized_player_id)
    print(f"   Sessions: {humanized_summary['session_count']}")
    print(f"   Total Playtime: {humanized_summary['total_playtime']:.1f} hours")
    print(f"   Total Events: {humanized_summary['total_events']}")
    print(f"   Baseline Established: {humanized_summary['baseline_established']}")
    print(f"   Total Detections: {humanized_summary['detection_statistics']['total_detections']}")
    print(f"   Average Confidence: {humanized_summary['detection_statistics']['avg_confidence']:.1%}")
    
    print("\n📄 AI CHEATER REPORT:")
    ai_summary = system.get_profile_summary(ai_player_id)
    print(f"   Sessions: {ai_summary['session_count']}")
    print(f"   Total Playtime: {ai_summary['total_playtime']:.1f} hours")
    print(f"   Total Events: {ai_summary['total_events']}")
    print(f"   Baseline Established: {ai_summary['baseline_established']}")
    print(f"   Total Detections: {ai_summary['detection_statistics']['total_detections']}")
    print(f"   Average Confidence: {ai_summary['detection_statistics']['avg_confidence']:.1%}")
    
    # System performance
    print("\n📊 SYSTEM PERFORMANCE:")
    performance = system.get_system_performance()
    print(f"   Humanization Events Detected: {performance['humanization_events_detected']}")
    print(f"   Active Profiles: {performance['active_profiles']}")
    print(f"   Humanization Methods: {performance['humanization_methods']}")
    
    return system

if __name__ == "__main__":
    test_advanced_humanization_detection()

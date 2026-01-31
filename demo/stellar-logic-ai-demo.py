#!/usr/bin/env python3
"""
Stellar Logic AI - Free Real-World Implementation
Browser-based Anti-Cheat Detection Demo
"""

import json
import time
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class PlayerStats:
    player_id: str
    aim_accuracy: float
    reaction_time: int
    movement_speed: float
    kills_per_minute: float
    headshot_ratio: float
    timestamp: datetime

@dataclass
class DetectionResult:
    player_id: str
    risk_score: float
    anomalies: List[str]
    confidence: float
    timestamp: datetime

class StellarLogicAIDemo:
    """Free anti-cheat detection system for demo purposes"""
    
    def __init__(self):
        self.detection_thresholds = {
            'aim_accuracy': 85.0,      # Above 85% suspicious
            'reaction_time': 150,        # Below 150ms suspicious
            'movement_speed': 250.0,    # Above 250 units/s suspicious
            'kills_per_minute': 3.0,    # Above 3 kills/min suspicious
            'headshot_ratio': 0.7       # Above 70% suspicious
        }
        
        self.risk_weights = {
            'aim_accuracy': 0.3,
            'reaction_time': 0.25,
            'movement_speed': 0.2,
            'kills_per_minute': 0.15,
            'headshot_ratio': 0.1
        }
        
        self.detection_history = []
    
    def analyze_player(self, stats: PlayerStats) -> DetectionResult:
        """Analyze player statistics for cheating patterns"""
        anomalies = []
        risk_score = 0.0
        
        # Check aim accuracy
        if stats.aim_accuracy > self.detection_thresholds['aim_accuracy']:
            anomalies.append(f"Suspicious aim accuracy: {stats.aim_accuracy:.1f}%")
            risk_score += self.risk_weights['aim_accuracy']
        
        # Check reaction time
        if stats.reaction_time < self.detection_thresholds['reaction_time']:
            anomalies.append(f"Superhuman reaction time: {stats.reaction_time}ms")
            risk_score += self.risk_weights['reaction_time']
        
        # Check movement speed
        if stats.movement_speed > self.detection_thresholds['movement_speed']:
            anomalies.append(f"Abnormal movement speed: {stats.movement_speed:.1f} units/s")
            risk_score += self.risk_weights['movement_speed']
        
        # Check kills per minute
        if stats.kills_per_minute > self.detection_thresholds['kills_per_minute']:
            anomalies.append(f"High kill rate: {stats.kills_per_minute:.1f} kills/min")
            risk_score += self.risk_weights['kills_per_minute']
        
        # Check headshot ratio
        if stats.headshot_ratio > self.detection_thresholds['headshot_ratio']:
            anomalies.append(f"Suspicious headshot ratio: {stats.headshot_ratio:.1%}")
            risk_score += self.risk_weights['headshot_ratio']
        
        # Calculate confidence based on number of anomalies
        confidence = min(len(anomalies) * 0.2, 1.0)
        
        result = DetectionResult(
            player_id=stats.player_id,
            risk_score=risk_score,
            anomalies=anomalies,
            confidence=confidence,
            timestamp=datetime.now()
        )
        
        self.detection_history.append(result)
        return result
    
    def generate_report(self, player_id: str) -> Dict:
        """Generate comprehensive report for a player"""
        player_detections = [
            d for d in self.detection_history 
            if d.player_id == player_id
        ]
        
        if not player_detections:
            return {"error": "No detection history found for player"}
        
        latest = player_detections[-1]
        avg_risk = sum(d.risk_score for d in player_detections) / len(player_detections)
        
        return {
            "player_id": player_id,
            "latest_detection": {
                "risk_score": latest.risk_score,
                "anomalies": latest.anomalies,
                "confidence": latest.confidence,
                "timestamp": latest.timestamp.isoformat()
            },
            "statistics": {
                "total_scans": len(player_detections),
                "average_risk_score": avg_risk,
                "highest_risk_score": max(d.risk_score for d in player_detections),
                "first_scan": player_detections[0].timestamp.isoformat(),
                "last_scan": player_detections[-1].timestamp.isoformat()
            },
            "recommendation": self._get_recommendation(latest.risk_score)
        }
    
    def _get_recommendation(self, risk_score: float) -> str:
        """Get recommendation based on risk score"""
        if risk_score >= 0.8:
            return "IMMEDIATE ACTION REQUIRED - High probability of cheating"
        elif risk_score >= 0.5:
            return "MONITOR CLOSELY - Suspicious activity detected"
        elif risk_score >= 0.2:
            return "OBSERVE - Minor anomalies detected"
        else:
            return "NORMAL - No suspicious activity detected"
    
    def get_dashboard_data(self) -> Dict:
        """Get data for dashboard display"""
        if not self.detection_history:
            return {"message": "No detection data available"}
        
        total_scans = len(self.detection_history)
        high_risk_players = len([
            d for d in self.detection_history 
            if d.risk_score >= 0.5
        ])
        
        recent_detections = [
            d for d in self.detection_history 
            if (datetime.now() - d.timestamp).seconds < 3600
        ]
        
        return {
            "total_scans": total_scans,
            "high_risk_players": high_risk_players,
            "recent_detections": len(recent_detections),
            "detection_rate": (high_risk_players / total_scans * 100) if total_scans > 0 else 0,
            "latest_detections": [
                {
                    "player_id": d.player_id,
                    "risk_score": d.risk_score,
                    "anomalies_count": len(d.anomalies),
                    "timestamp": d.timestamp.isoformat()
                }
                for d in self.detection_history[-10:]
            ]
        }

# Demo usage
if __name__ == "__main__":
    # Initialize the system
    stellar_ai = StellarLogicAIDemo()
    
    # Simulate player data
    test_players = [
        PlayerStats("player_001", 92.5, 120, 280.0, 4.2, 0.85, datetime.now()),
        PlayerStats("player_002", 65.3, 250, 180.0, 1.8, 0.45, datetime.now()),
        PlayerStats("player_003", 88.7, 95, 320.0, 5.1, 0.92, datetime.now()),
        PlayerStats("player_004", 72.1, 180, 200.0, 2.3, 0.55, datetime.now()),
    ]
    
    # Analyze players
    print("🚀 Stellar Logic AI - Anti-Cheat Detection Demo")
    print("=" * 50)
    
    for player in test_players:
        result = stellar_ai.analyze_player(player)
        print(f"\n🎮 Player: {player.player_id}")
        print(f"⚠️  Risk Score: {result.risk_score:.2f}")
        print(f"🔍 Anomalies: {len(result.anomalies)}")
        
        if result.anomalies:
            for anomaly in result.anomalies:
                print(f"   • {anomaly}")
        
        print(f"💡 Recommendation: {stellar_ai._get_recommendation(result.risk_score)}")
    
    # Generate dashboard
    print("\n📊 Dashboard Summary:")
    dashboard = stellar_ai.get_dashboard_data()
    print(f"   Total Scans: {dashboard['total_scans']}")
    print(f"   High Risk Players: {dashboard['high_risk_players']}")
    print(f"   Detection Rate: {dashboard['detection_rate']:.1f}%")
    
    # Generate detailed report
    print(f"\n📋 Detailed Report for player_001:")
    report = stellar_ai.generate_report("player_001")
    print(json.dumps(report, indent=2))

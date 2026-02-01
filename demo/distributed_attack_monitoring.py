#!/usr/bin/env python3
"""
Stellar Logic AI - Distributed Attack Monitoring and Botnet Detection System
Advanced distributed attack monitoring with botnet detection capabilities
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random
import math
import json
import hashlib
from collections import defaultdict, deque

class AttackType(Enum):
    """Types of distributed attacks"""
    DDOS = "ddos"
    BOTNET = "botnet"
    DISTRIBUTED_BRUTE_FORCE = "distributed_brute_force"
    COORDINATED_ATTACK = "coordinated_attack"
    P2P_ATTACK = "p2p_attack"
    CLOUD_BASED_ATTACK = "cloud_based_attack"
    MOBILE_BOTNET = "mobile_botnet"
    IOT_BOTNET = "iot_botnet"

class ThreatLevel(Enum):
    """Threat levels for attacks"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class NetworkNode:
    """Network node information"""
    node_id: str
    ip_address: str
    geolocation: Dict[str, float]
    reputation_score: float
    activity_level: float
    last_seen: datetime
    node_type: str
    metadata: Dict[str, Any]

@dataclass
class AttackEvent:
    """Attack event information"""
    event_id: str
    attack_type: AttackType
    source_nodes: List[str]
    target_nodes: List[str]
    timestamp: datetime
    severity: ThreatLevel
    attack_vectors: List[str]
    traffic_volume: float
    attack_patterns: Dict[str, Any]

@dataclass
class BotnetDetection:
    """Botnet detection result"""
    detection_id: str
    botnet_type: AttackType
    confidence: float
    severity: ThreatLevel
    timestamp: datetime
    infected_nodes: List[str]
    command_servers: List[str]
    attack_patterns: List[str]
    communication_protocols: List[str]
    detection_metrics: Dict[str, float]

@dataclass
class DistributedProfile:
    """Distributed attack monitoring profile"""
    network_id: str
    nodes: Dict[str, NetworkNode]
    attack_events: deque
    botnet_detections: deque
    threat_assessment: Dict[str, float]
    network_topology: Dict[str, List[str]]
    attack_correlations: Dict[str, List[str]]
    last_updated: datetime
    total_nodes: int
    total_attacks: int

class DistributedAttackMonitoring:
    """Distributed attack monitoring and botnet detection system"""
    
    def __init__(self):
        self.profiles = {}
        self.nodes = {}
        self.attack_events = {}
        self.detection_methods = {}
        
        # Monitoring configuration
        self.monitoring_config = {
            'traffic_threshold': 1000.0,  # MB/s
            'node_activity_threshold': 0.8,
            'correlation_threshold': 0.7,
            'reputation_threshold': 0.3,
            'attack_pattern_threshold': 0.6,
            'communication_frequency_threshold': 10,
            'topology_anomaly_threshold': 0.5,
            'ml_confidence_threshold': 0.8
        }
        
        # Botnet detection configuration
        self.botnet_config = {
            'min_infected_nodes': 5,
            'max_command_servers': 10,
            'communication_protocols': ['HTTP', 'HTTPS', 'DNS', 'P2P', 'IRC'],
            'attack_vectors': ['DDoS', 'Brute Force', 'Data Exfiltration', 'Crypto Mining'],
            'botnet_types': ['Traditional', 'P2P', 'Cloud-based', 'Mobile', 'IoT']
        }
        
        # Performance metrics
        self.total_nodes = 0
        self.total_attacks = 0
        self.botnets_detected = 0
        self.false_positives = 0
        self.true_positives = 0
        
        # Data window configuration
        self.window_size = 10000
        self.min_events_for_analysis = 100
        
        # Initialize network models
        self._initialize_network_models()
        
    def _initialize_network_models(self):
        """Initialize network analysis models"""
        self.network_models = {
            'traffic_analyzer': {
                'baseline_traffic': defaultdict(float),
                'traffic_patterns': defaultdict(list),
                'anomaly_threshold': self.monitoring_config['traffic_threshold']
            },
            'behavior_analyzer': {
                'normal_behaviors': defaultdict(list),
                'behavior_patterns': defaultdict(float),
                'anomaly_threshold': self.monitoring_config['node_activity_threshold']
            },
            'topology_analyzer': {
                'normal_topologies': defaultdict(list),
                'topology_patterns': defaultdict(float),
                'anomaly_threshold': self.monitoring_config['topology_anomaly_threshold']
            }
        }
    
    def create_profile(self, network_id: str) -> DistributedProfile:
        """Create distributed attack monitoring profile"""
        profile = DistributedProfile(
            network_id=network_id,
            nodes={},
            attack_events=deque(maxlen=self.window_size),
            botnet_detections=deque(maxlen=self.window_size),
            threat_assessment={
                'overall_threat': 0.0,
                'ddos_risk': 0.0,
                'botnet_risk': 0.0,
                'coordinated_attack_risk': 0.0
            },
            network_topology={},
            attack_correlations={},
            last_updated=datetime.now(),
            total_nodes=0,
            total_attacks=0
        )
        
        self.profiles[network_id] = profile
        return profile
    
    def add_network_node(self, network_id: str, node: NetworkNode) -> None:
        """Add network node to monitoring"""
        profile = self.profiles.get(network_id)
        if not profile:
            profile = self.create_profile(network_id)
        
        # Add node to profile
        profile.nodes[node.node_id] = node
        profile.total_nodes = len(profile.nodes)
        profile.last_updated = datetime.now()
        
        # Update global nodes
        self.nodes[node.node_id] = node
        self.total_nodes = len(self.nodes)
        
        # Update network topology
        self._update_network_topology(profile, node)
    
    def add_attack_event(self, network_id: str, event: AttackEvent) -> List[BotnetDetection]:
        """Add attack event and detect botnets"""
        profile = self.profiles.get(network_id)
        if not profile:
            profile = self.create_profile(network_id)
        
        # Add event to profile
        profile.attack_events.append(event)
        profile.total_attacks = len(profile.attack_events)
        profile.last_updated = datetime.now()
        
        # Update global events
        self.attack_events[event.event_id] = event
        self.total_attacks = len(self.attack_events)
        
        # Detect botnets and distributed attacks
        detections = []
        
        if profile.total_attacks >= self.min_events_for_analysis:
            # Check for botnet patterns
            botnet_detections = self._detect_botnet_patterns(profile, event)
            detections.extend(botnet_detections)
            
            # Store detections
            for detection in botnet_detections:
                profile.botnet_detections.append(detection)
                self.botnets_detected += 1
                
                # Update threat assessment
                self._update_threat_assessment(profile, detection)
        
        return detections
    
    def _update_network_topology(self, profile: DistributedProfile, node: NetworkNode) -> None:
        """Update network topology"""
        # Simulate network connections based on geolocation
        for other_node_id, other_node in profile.nodes.items():
            if other_node_id != node.node_id:
                # Calculate distance
                distance = self._calculate_distance(
                    node.geolocation['lat'], node.geolocation['lon'],
                    other_node.geolocation['lat'], other_node.geolocation['lon']
                )
                
                # Create connection if within reasonable distance
                if distance < 1000:  # 1000km threshold
                    if node.node_id not in profile.network_topology:
                        profile.network_topology[node.node_id] = []
                    if other_node_id not in profile.network_topology[node.node_id]:
                        profile.network_topology[node.node_id].append(other_node_id)
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two geographic points"""
        # Simplified distance calculation
        lat_diff = abs(lat1 - lat2) * 111  # 1 degree latitude ≈ 111 km
        lon_diff = abs(lon1 - lon2) * 111 * math.cos(math.radians((lat1 + lat2) / 2))
        return math.sqrt(lat_diff ** 2 + lon_diff ** 2)
    
    def _detect_botnet_patterns(self, profile: DistributedProfile, event: AttackEvent) -> List[BotnetDetection]:
        """Detect botnet patterns in attack events"""
        detections = []
        
        # Check for distributed attack patterns
        distributed_detection = self._detect_distributed_attack(profile, event)
        if distributed_detection:
            detections.append(distributed_detection)
        
        # Check for botnet communication patterns
        communication_detection = self._detect_botnet_communication(profile, event)
        if communication_detection:
            detections.append(communication_detection)
        
        # Check for coordinated attack patterns
        coordination_detection = self._detect_coordinated_attack(profile, event)
        if coordination_detection:
            detections.append(coordination_detection)
        
        # Check for P2P botnet patterns
        p2p_detection = self._detect_p2p_botnet(profile, event)
        if p2p_detection:
            detections.append(p2p_detection)
        
        return detections
    
    def _detect_distributed_attack(self, profile: DistributedProfile, event: AttackEvent) -> Optional[BotnetDetection]:
        """Detect distributed attack patterns"""
        recent_events = list(profile.attack_events)[-50:]
        
        # Check for multiple source nodes
        if len(event.source_nodes) >= self.botnet_config['min_infected_nodes']:
            # Calculate attack correlation
            correlated_events = self._find_correlated_events(recent_events, event)
            
            if len(correlated_events) >= 3:  # Minimum correlated events
                confidence = min(1.0, len(correlated_events) / 10)
                severity = self._calculate_attack_severity(event, correlated_events)
                
                return BotnetDetection(
                    detection_id=f"distributed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    botnet_type=AttackType.DISTRIBUTED_BRUTE_FORCE,
                    confidence=confidence,
                    severity=severity,
                    timestamp=datetime.now(),
                    infected_nodes=event.source_nodes,
                    command_servers=self._identify_command_servers(profile, event.source_nodes),
                    attack_patterns=event.attack_vectors,
                    communication_protocols=['HTTP', 'HTTPS'],
                    detection_metrics={
                        'correlated_events': len(correlated_events),
                        'source_nodes': len(event.source_nodes),
                        'attack_volume': event.traffic_volume
                    }
                )
        
        return None
    
    def _detect_botnet_communication(self, profile: DistributedProfile, event: AttackEvent) -> Optional[BotnetDetection]:
        """Detect botnet communication patterns"""
        # Analyze communication patterns between nodes
        communication_frequency = self._calculate_communication_frequency(profile, event.source_nodes)
        
        if communication_frequency > self.monitoring_config['communication_frequency_threshold']:
            # Check for C2 server patterns
            c2_servers = self._identify_command_servers(profile, event.source_nodes)
            
            if len(c2_servers) > 0:
                confidence = min(1.0, communication_frequency / 20)
                severity = ThreatLevel.HIGH if confidence > 0.7 else ThreatLevel.MEDIUM
                
                return BotnetDetection(
                    detection_id=f"communication_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    botnet_type=AttackType.BOTNET,
                    confidence=confidence,
                    severity=severity,
                    timestamp=datetime.now(),
                    infected_nodes=event.source_nodes,
                    command_servers=c2_servers,
                    attack_patterns=['C2 Communication', 'Data Exfiltration'],
                    communication_protocols=self.botnet_config['communication_protocols'],
                    detection_metrics={
                        'communication_frequency': communication_frequency,
                        'c2_servers': len(c2_servers),
                        'infected_nodes': len(event.source_nodes)
                    }
                )
        
        return None
    
    def _detect_coordinated_attack(self, profile: DistributedProfile, event: AttackEvent) -> Optional[BotnetDetection]:
        """Detect coordinated attack patterns"""
        recent_events = list(profile.attack_events)[-100:]
        
        # Check for temporal correlation
        temporal_correlation = self._calculate_temporal_correlation(recent_events, event)
        
        if temporal_correlation > self.monitoring_config['correlation_threshold']:
            # Check for attack pattern similarity
            pattern_similarity = self._calculate_pattern_similarity(recent_events, event)
            
            if pattern_similarity > 0.6:
                confidence = (temporal_correlation + pattern_similarity) / 2
                severity = ThreatLevel.CRITICAL if confidence > 0.8 else ThreatLevel.HIGH
                
                return BotnetDetection(
                    detection_id=f"coordinated_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    botnet_type=AttackType.COORDINATED_ATTACK,
                    confidence=confidence,
                    severity=severity,
                    timestamp=datetime.now(),
                    infected_nodes=event.source_nodes,
                    command_servers=self._identify_command_servers(profile, event.source_nodes),
                    attack_patterns=event.attack_vectors,
                    communication_protocols=['P2P', 'IRC'],
                    detection_metrics={
                        'temporal_correlation': temporal_correlation,
                        'pattern_similarity': pattern_similarity,
                        'coordinated_nodes': len(event.source_nodes)
                    }
                )
        
        return None
    
    def _detect_p2p_botnet(self, profile: DistributedProfile, event: AttackEvent) -> Optional[BotnetDetection]:
        """Detect P2P botnet patterns"""
        # Analyze P2P communication patterns
        p2p_connections = self._analyze_p2p_connections(profile, event.source_nodes)
        
        if len(p2p_connections) >= 5:  # Minimum P2P connections
            # Check for decentralized command structure
            decentralization_score = self._calculate_decentralization_score(p2p_connections)
            
            if decentralization_score > 0.7:
                confidence = min(1.0, decentralization_score)
                severity = ThreatLevel.HIGH if confidence > 0.6 else ThreatLevel.MEDIUM
                
                return BotnetDetection(
                    detection_id=f"p2p_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    botnet_type=AttackType.P2P_ATTACK,
                    confidence=confidence,
                    severity=severity,
                    timestamp=datetime.now(),
                    infected_nodes=event.source_nodes,
                    command_servers=[],  # P2P botnets have no central C2
                    attack_patterns=['P2P Communication', 'Distributed Command'],
                    communication_protocols=['P2P', 'DHT'],
                    detection_metrics={
                        'p2p_connections': len(p2p_connections),
                        'decentralization_score': decentralization_score,
                        'infected_nodes': len(event.source_nodes)
                    }
                )
        
        return None
    
    def _find_correlated_events(self, events: List[AttackEvent], target_event: AttackEvent) -> List[AttackEvent]:
        """Find events correlated with target event"""
        correlated = []
        
        for event in events:
            if event.event_id != target_event.event_id:
                # Check for source node overlap
                source_overlap = len(set(event.source_nodes) & set(target_event.source_nodes))
                
                # Check for attack vector similarity
                vector_similarity = len(set(event.attack_vectors) & set(target_event.attack_vectors))
                
                # Check for temporal proximity
                time_diff = abs((event.timestamp - target_event.timestamp).total_seconds())
                
                # Correlation criteria
                if (source_overlap >= 2 or 
                    vector_similarity >= 2 or 
                    time_diff <= 300):  # 5 minutes
                    correlated.append(event)
        
        return correlated
    
    def _calculate_communication_frequency(self, profile: DistributedProfile, nodes: List[str]) -> float:
        """Calculate communication frequency between nodes"""
        # Simulate communication frequency based on node activity
        total_activity = 0.0
        
        for node_id in nodes:
            if node_id in profile.nodes:
                node = profile.nodes[node_id]
                total_activity += node.activity_level
        
        return total_activity / len(nodes) if nodes else 0.0
    
    def _identify_command_servers(self, profile: DistributedProfile, infected_nodes: List[str]) -> List[str]:
        """Identify potential command servers"""
        # Simulate C2 server identification based on reputation and activity
        potential_c2 = []
        
        for node_id in infected_nodes:
            if node_id in profile.nodes:
                node = profile.nodes[node_id]
                
                # Check if node could be C2 server
                if (node.reputation_score < self.monitoring_config['reputation_threshold'] and
                    node.activity_level > self.monitoring_config['node_activity_threshold']):
                    potential_c2.append(node_id)
        
        return potential_c2[:self.botnet_config['max_command_servers']]
    
    def _calculate_temporal_correlation(self, events: List[AttackEvent], target_event: AttackEvent) -> float:
        """Calculate temporal correlation between events"""
        if len(events) < 2:
            return 0.0
        
        # Find events within time window
        time_window = 3600  # 1 hour
        correlated_events = []
        
        for event in events:
            time_diff = abs((event.timestamp - target_event.timestamp).total_seconds())
            if time_diff <= time_window:
                correlated_events.append(event)
        
        # Calculate correlation score
        correlation_score = len(correlated_events) / len(events)
        return correlation_score
    
    def _calculate_pattern_similarity(self, events: List[AttackEvent], target_event: AttackEvent) -> float:
        """Calculate pattern similarity between events"""
        if len(events) < 2:
            return 0.0
        
        similarities = []
        
        for event in events:
            if event.event_id != target_event.event_id:
                # Calculate attack vector similarity
                vector_similarity = len(set(event.attack_vectors) & set(target_event.attack_vectors))
                max_vectors = max(len(event.attack_vectors), len(target_event.attack_vectors))
                similarity = vector_similarity / max_vectors if max_vectors > 0 else 0.0
                
                similarities.append(similarity)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def _analyze_p2p_connections(self, profile: DistributedProfile, nodes: List[str]) -> List[Tuple[str, str]]:
        """Analyze P2P connections between nodes"""
        connections = []
        
        # Check network topology for P2P connections
        for node_id in nodes:
            if node_id in profile.network_topology:
                for connected_node in profile.network_topology[node_id]:
                    if connected_node in nodes:
                        connections.append((node_id, connected_node))
        
        return connections
    
    def _calculate_decentralization_score(self, connections: List[Tuple[str, str]]) -> float:
        """Calculate decentralization score for P2P network"""
        if not connections:
            return 0.0
        
        # Calculate node degrees
        node_degrees = defaultdict(int)
        for node1, node2 in connections:
            node_degrees[node1] += 1
            node_degrees[node2] += 1
        
        # Calculate degree distribution
        degrees = list(node_degrees.values())
        if not degrees:
            return 0.0
        
        # Calculate decentralization (inverse of degree variance)
        mean_degree = sum(degrees) / len(degrees)
        variance = sum((d - mean_degree) ** 2 for d in degrees) / len(degrees)
        
        # Higher decentralization = lower variance
        decentralization = 1.0 / (1.0 + variance)
        return decentralization
    
    def _calculate_attack_severity(self, event: AttackEvent, correlated_events: List[AttackEvent]) -> ThreatLevel:
        """Calculate attack severity"""
        # Calculate total impact
        total_nodes = len(set(event.source_nodes + [node for e in correlated_events for node in e.source_nodes]))
        total_volume = event.traffic_volume + sum(e.traffic_volume for e in correlated_events)
        
        # Determine severity based on impact
        if total_nodes >= 100 or total_volume >= 10000:
            return ThreatLevel.CRITICAL
        elif total_nodes >= 50 or total_volume >= 5000:
            return ThreatLevel.HIGH
        elif total_nodes >= 20 or total_volume >= 1000:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    def _update_threat_assessment(self, profile: DistributedProfile, detection: BotnetDetection) -> None:
        """Update threat assessment based on detection"""
        # Update overall threat
        profile.threat_assessment['overall_threat'] = max(
            profile.threat_assessment['overall_threat'],
            detection.confidence
        )
        
        # Update specific threat categories
        if detection.botnet_type == AttackType.DDOS:
            profile.threat_assessment['ddos_risk'] = max(
                profile.threat_assessment['ddos_risk'],
                detection.confidence
            )
        elif detection.botnet_type == AttackType.BOTNET:
            profile.threat_assessment['botnet_risk'] = max(
                profile.threat_assessment['botnet_risk'],
                detection.confidence
            )
        elif detection.botnet_type == AttackType.COORDINATED_ATTACK:
            profile.threat_assessment['coordinated_attack_risk'] = max(
                profile.threat_assessment['coordinated_attack_risk'],
                detection.confidence
            )
    
    def get_profile_summary(self, network_id: str) -> Dict[str, Any]:
        """Get distributed attack monitoring profile summary"""
        profile = self.profiles.get(network_id)
        if not profile:
            return {'error': 'Profile not found'}
        
        # Calculate detection statistics
        detection_stats = self._calculate_detection_statistics(profile)
        
        return {
            'network_id': network_id,
            'total_nodes': profile.total_nodes,
            'total_attacks': profile.total_attacks,
            'botnet_detections': len(profile.botnet_detections),
            'threat_assessment': profile.threat_assessment,
            'network_topology_size': len(profile.network_topology),
            'detection_statistics': detection_stats,
            'last_updated': profile.last_updated.isoformat()
        }
    
    def _calculate_detection_statistics(self, profile: DistributedProfile) -> Dict[str, Any]:
        """Calculate detection statistics"""
        if not profile.botnet_detections:
            return {
                'total_detections': 0,
                'type_distribution': {},
                'severity_distribution': {},
                'avg_confidence': 0.0,
                'success_rate': 0.0,
                'detection_frequency': 0.0,
                'recent_trend': 'stable'
            }
        
        recent_detections = list(profile.botnet_detections)[-100:]
        
        # Calculate statistics
        type_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        confidences = []
        
        for detection in recent_detections:
            type_counts[detection.botnet_type.value] += 1
            severity_counts[detection.severity.value] += 1
            confidences.append(detection.confidence)
        
        # Calculate detection frequency
        if len(recent_detections) >= 2:
            time_span = (recent_detections[-1].timestamp - recent_detections[0].timestamp).total_seconds()
            detection_frequency = len(recent_detections) / (time_span / 3600) if time_span > 0 else 0
        else:
            detection_frequency = 0.0
        
        # Analyze trend
        if len(recent_detections) >= 10:
            recent_confidences = confidences[-10:]
            older_confidences = confidences[-20:-10] if len(confidences) > 10 else []
            
            recent_avg = sum(recent_confidences) / len(recent_confidences)
            older_avg = sum(older_confidences) / len(older_confidences) if older_confidences else recent_avg
            
            if recent_avg > older_avg * 1.1:
                trend = 'increasing'
            elif recent_avg < older_avg * 0.9:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'total_detections': len(recent_detections),
            'type_distribution': dict(type_counts),
            'severity_distribution': dict(severity_counts),
            'avg_confidence': sum(confidences) / len(confidences),
            'success_rate': sum(1 for d in recent_detections if d.confidence > 0.7) / len(recent_detections),
            'detection_frequency': detection_frequency,
            'recent_trend': trend
        }
    
    def get_system_performance(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return {
            'total_nodes': self.total_nodes,
            'total_attacks': self.total_attacks,
            'botnets_detected': self.botnets_detected,
            'true_positives': self.true_positives,
            'false_positives': self.false_positives,
            'success_rate': self.true_positives / max(1, self.botnets_detected),
            'active_profiles': len(self.profiles),
            'detection_methods': len(self.detection_methods),
            'monitoring_config': self.monitoring_config,
            'botnet_config': self.botnet_config
        }

# Test the distributed attack monitoring system
def test_distributed_attack_monitoring():
    """Test the distributed attack monitoring system"""
    print("🌐 Testing Distributed Attack Monitoring System")
    print("=" * 50)
    
    monitor = DistributedAttackMonitoring()
    
    # Create test network profiles
    print("\n🏢 Creating Test Network Profiles...")
    
    # Enterprise network
    enterprise_network_id = "enterprise_network_001"
    enterprise_profile = monitor.create_profile(enterprise_network_id)
    
    # Cloud network
    cloud_network_id = "cloud_network_001"
    cloud_profile = monitor.create_profile(cloud_network_id)
    
    # IoT network
    iot_network_id = "iot_network_001"
    iot_profile = monitor.create_profile(iot_network_id)
    
    # Simulate network nodes for enterprise network
    print("\n🖥️ Simulating Enterprise Network Nodes...")
    for i in range(200):
        node = NetworkNode(
            node_id=f"enterprise_node_{i}",
            ip_address=f"192.168.{i//256}.{i%256}",
            geolocation={'lat': 40.7128 + random.uniform(-0.1, 0.1), 'lon': -74.0060 + random.uniform(-0.1, 0.1)},
            reputation_score=random.uniform(0.2, 0.9),
            activity_level=random.uniform(0.1, 0.8),
            last_seen=datetime.now() - timedelta(minutes=random.randint(0, 60)),
            node_type='server',
            metadata={'department': random.choice(['IT', 'Finance', 'HR', 'Operations'])}
        )
        monitor.add_network_node(enterprise_network_id, node)
    
    # Simulate network nodes for cloud network
    print("\n☁️ Simulating Cloud Network Nodes...")
    for i in range(150):
        node = NetworkNode(
            node_id=f"cloud_node_{i}",
            ip_address=f"10.0.{i//256}.{i%256}",
            geolocation={'lat': 37.7749 + random.uniform(-0.2, 0.2), 'lon': -122.4194 + random.uniform(-0.2, 0.2)},
            reputation_score=random.uniform(0.3, 0.8),
            activity_level=random.uniform(0.2, 0.9),
            last_seen=datetime.now() - timedelta(minutes=random.randint(0, 30)),
            node_type='cloud_instance',
            metadata={'provider': random.choice(['AWS', 'Azure', 'GCP']), 'region': random.choice(['us-east', 'us-west', 'eu-west'])}
        )
        monitor.add_network_node(cloud_network_id, node)
    
    # Simulate network nodes for IoT network
    print("\n🔌 Simulating IoT Network Nodes...")
    for i in range(300):
        node = NetworkNode(
            node_id=f"iot_node_{i}",
            ip_address=f"172.16.{i//256}.{i%256}",
            geolocation={'lat': random.uniform(25, 50), 'lon': random.uniform(-125, -65)},
            reputation_score=random.uniform(0.1, 0.7),
            activity_level=random.uniform(0.05, 0.6),
            last_seen=datetime.now() - timedelta(minutes=random.randint(0, 120)),
            node_type='iot_device',
            metadata={'device_type': random.choice(['camera', 'sensor', 'smart_home', 'industrial'])}
        )
        monitor.add_network_node(iot_network_id, node)
    
    # Simulate normal attack events for enterprise network
    print("\n🔒 Simulating Normal Attack Events (Enterprise)...")
    for i in range(80):
        timestamp = datetime.now() - timedelta(hours=i*2)
        
        # Normal distributed attack
        event = AttackEvent(
            event_id=f"enterprise_attack_{i}",
            attack_type=random.choice([AttackType.DDOS, AttackType.DISTRIBUTED_BRUTE_FORCE]),
            source_nodes=random.sample([f"enterprise_node_{j}" for j in range(200)], random.randint(3, 8)),
            target_nodes=[f"enterprise_node_{random.randint(0, 199)}"],
            timestamp=timestamp,
            severity=random.choice([ThreatLevel.LOW, ThreatLevel.MEDIUM]),
            attack_vectors=['HTTP Flood', 'SYN Flood'],
            traffic_volume=random.uniform(100, 500),
            attack_patterns={'timing': 'random', 'source_distribution': 'geographic'}
        )
        
        detections = monitor.add_attack_event(enterprise_network_id, event)
        
        if detections:
            print(f"   Event {i}: {len(detections)} botnet detections")
    
    # Simulate botnet attack events for cloud network
    print("\n🤖 Simulating Botnet Attack Events (Cloud)...")
    for i in range(60):
        timestamp = datetime.now() - timedelta(hours=i*1.5)
        
        # Botnet attack with coordinated patterns
        event = AttackEvent(
            event_id=f"cloud_attack_{i}",
            attack_type=AttackType.BOTNET,
            source_nodes=random.sample([f"cloud_node_{j}" for j in range(150)], random.randint(10, 20)),
            target_nodes=[f"cloud_node_{random.randint(0, 149)}"],
            timestamp=timestamp,
            severity=random.choice([ThreatLevel.HIGH, ThreatLevel.CRITICAL]),
            attack_vectors=['HTTP Flood', 'DNS Amplification', 'Data Exfiltration'],
            traffic_volume=random.uniform(1000, 5000),
            attack_patterns={'timing': 'coordinated', 'source_distribution': 'global', 'command_structure': 'centralized'}
        )
        
        detections = monitor.add_attack_event(cloud_network_id, event)
        
        if detections:
            print(f"   Event {i}: {len(detections)} botnet detections")
    
    # Simulate P2P botnet events for IoT network
    print("\n🔗 Simulating P2P Botnet Events (IoT)...")
    for i in range(40):
        timestamp = datetime.now() - timedelta(hours=i*1)
        
        # P2P botnet attack
        event = AttackEvent(
            event_id=f"iot_attack_{i}",
            attack_type=AttackType.P2P_ATTACK,
            source_nodes=random.sample([f"iot_node_{j}" for j in range(300)], random.randint(15, 30)),
            target_nodes=[f"iot_node_{random.randint(0, 299)}"],
            timestamp=timestamp,
            severity=random.choice([ThreatLevel.MEDIUM, ThreatLevel.HIGH]),
            attack_vectors=['P2P Communication', 'Distributed Command', 'Traffic Amplification'],
            traffic_volume=random.uniform(500, 2000),
            attack_patterns={'timing': 'synchronized', 'source_distribution': 'decentralized', 'command_structure': 'p2p'}
        )
        
        detections = monitor.add_attack_event(iot_network_id, event)
        
        if detections:
            print(f"   Event {i}: {len(detections)} botnet detections")
    
    # Generate reports
    print("\n📋 Generating Distributed Attack Monitoring Reports...")
    
    print("\n📄 ENTERPRISE NETWORK REPORT:")
    enterprise_summary = monitor.get_profile_summary(enterprise_network_id)
    print(f"   Total Nodes: {enterprise_summary['total_nodes']}")
    print(f"   Total Attacks: {enterprise_summary['total_attacks']}")
    print(f"   Botnet Detections: {enterprise_summary['botnet_detections']}")
    print(f"   Overall Threat: {enterprise_summary['threat_assessment']['overall_threat']:.3f}")
    print(f"   DDoS Risk: {enterprise_summary['threat_assessment']['ddos_risk']:.3f}")
    print(f"   Success Rate: {enterprise_summary['detection_statistics']['success_rate']:.2%}")
    
    print("\n📄 CLOUD NETWORK REPORT:")
    cloud_summary = monitor.get_profile_summary(cloud_network_id)
    print(f"   Total Nodes: {cloud_summary['total_nodes']}")
    print(f"   Total Attacks: {cloud_summary['total_attacks']}")
    print(f"   Botnet Detections: {cloud_summary['botnet_detections']}")
    print(f"   Overall Threat: {cloud_summary['threat_assessment']['overall_threat']:.3f}")
    print(f"   Botnet Risk: {cloud_summary['threat_assessment']['botnet_risk']:.3f}")
    print(f"   Success Rate: {cloud_summary['detection_statistics']['success_rate']:.2%}")
    
    print("\n📄 IOT NETWORK REPORT:")
    iot_summary = monitor.get_profile_summary(iot_network_id)
    print(f"   Total Nodes: {iot_summary['total_nodes']}")
    print(f"   Total Attacks: {iot_summary['total_attacks']}")
    print(f"   Botnet Detections: {iot_summary['botnet_detections']}")
    print(f"   Overall Threat: {iot_summary['threat_assessment']['overall_threat']:.3f}")
    print(f"   Coordinated Attack Risk: {iot_summary['threat_assessment']['coordinated_attack_risk']:.3f}")
    print(f"   Success Rate: {iot_summary['detection_statistics']['success_rate']:.2%}")
    
    # System performance
    print("\n📊 SYSTEM PERFORMANCE:")
    performance = monitor.get_system_performance()
    print(f"   Total Nodes: {performance['total_nodes']}")
    print(f"   Total Attacks: {performance['total_attacks']}")
    print(f"   Botnets Detected: {performance['botnets_detected']}")
    print(f"   Success Rate: {performance['success_rate']:.2%}")
    print(f"   Active Profiles: {performance['active_profiles']}")
    print(f"   Detection Methods: {performance['detection_methods']}")
    
    return monitor

if __name__ == "__main__":
    test_distributed_attack_monitoring()

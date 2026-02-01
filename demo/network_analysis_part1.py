#!/usr/bin/env python3
"""
Stellar Logic AI - Network Analysis System (Part 1)
Enhanced network analysis for detecting network-based cheating patterns
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import random
import math
from collections import defaultdict, deque

class NetworkAnomalyType(Enum):
    """Types of network anomalies"""
    PACKET_TIMING_ANOMALY = "packet_timing_anomaly"
    TRAFFIC_VOLUME_ANOMALY = "traffic_volume_anomaly"
    CONNECTION_PATTERN_ANOMALY = "connection_pattern_anomaly"
    PROTOCOL_ANOMALY = "protocol_anomaly"
    GEOGRAPHIC_ANOMALY = "geographic_anomaly"
    BANDWIDTH_ANOMALY = "bandwidth_anomaly"
    LATENCY_SPIKE = "latency_spike"
    PACKET_SIZE_ANOMALY = "packet_size_anomaly"
    DNS_ANOMALY = "dns_anomaly"
    PORT_SCAN_ANOMALY = "port_scan_anomaly"

class NetworkSeverity(Enum):
    """Severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class NetworkEvent:
    """Network event data point"""
    timestamp: datetime
    source_ip: str
    dest_ip: str
    protocol: str
    port: int
    packet_size: int
    latency: float
    jitter: float
    metadata: Dict[str, Any]

@dataclass
class NetworkDetection:
    """Network anomaly detection result"""
    detection_id: str
    anomaly_type: NetworkAnomalyType
    severity: NetworkSeverity
    confidence: float
    timestamp: datetime
    player_id: str
    network_data: NetworkEvent
    anomaly_metrics: Dict[str, float]
    risk_factors: List[str]

@dataclass
class NetworkProfile:
    """Network profile for player"""
    player_id: str
    connection_history: deque
    packet_history: deque
    timing_history: deque
    bandwidth_usage: deque
    anomaly_history: List[NetworkDetection]
    last_updated: datetime
    total_packets: int
    total_bytes: int
    connection_rate: float
    packet_rate: float
    avg_latency: float
    avg_bandwidth: float

class AdvancedNetworkAnalysis:
    """Advanced network analysis system"""
    
    def __init__(self):
        self.profiles = {}
        self.network_thresholds = {
            'packet_rate_threshold': 100,
            'bandwidth_threshold': 1000000,
            'latency_threshold': 50.0,
            'jitter_threshold': 10.0,
            'connection_rate_threshold': 50,
            'port_scan_threshold': 10,
            'dns_query_threshold': 20
        }
        
        self.methods = {
            'packet_timing_analysis': self._packet_timing_analysis,
            'traffic_volume_analysis': self._traffic_volume_analysis,
            'connection_pattern_analysis': self._connection_pattern_analysis,
            'geographic_analysis': self._geographic_analysis,
            'protocol_analysis': self._protocol_analysis,
            'dns_analysis': self._dns_analysis,
            'port_scan_detection': self._port_scan_detection,
            'bandwidth_anomaly': self._bandwidth_anomaly,
            'latency_spike_detection': self._latency_spike_detection
        }
        
        self.network_events_detected = 0
        self.false_positives = 0
        self.true_positives = 0
        self.window_size = 1000
        self.min_packets_for_analysis = 100
        
        self.suspicious_ips = [
            '192.168.1.0', '10.0.0.0', '172.16.0.0', '203.0.113.0'
        ]
        self.suspicious_ports = [22, 80, 443, 3389, 8080, 8443]
        self.suspicious_protocols = ['udp', 'icmp', 'arp']
        
    def create_profile(self, player_id: str) -> NetworkProfile:
        """Create network profile"""
        profile = NetworkProfile(
            player_id=player_id,
            connection_history=deque(maxlen=self.window_size),
            packet_history=deque(maxlen=self.window_size),
            timing_history=deque(maxlen=self.window_size),
            bandwidth_usage=deque(maxlen=self.window_size),
            anomaly_history=[],
            last_updated=datetime.now(),
            total_packets=0,
            total_bytes=0,
            connection_rate=0.0,
            packet_rate=0.0,
            avg_latency=0.0,
            avg_bandwidth=0.0
        )
        self.profiles[player_id] = profile
        return profile
    
    def add_network_event(self, player_id: str, event: NetworkEvent) -> List[NetworkDetection]:
        """Add network event and detect anomalies"""
        profile = self.profiles.get(player_id)
        if not profile:
            profile = self.create_profile(player_id)
        
        profile.connection_history.append(event)
        profile.packet_history.append(event)
        profile.timing_history.append(event.latency)
        profile.bandwidth_usage.append(event.packet_size)
        profile.total_packets += 1
        profile.total_bytes += event.packet_size
        profile.last_updated = datetime.now()
        
        anomalies = []
        
        if profile.total_packets >= self.min_packets_for_analysis:
            self._update_network_stats(profile)
            
            method_results = []
            for method_name, method_func in self.methods.items():
                try:
                    result = method_func(profile)
                    if result['is_anomaly']:
                        method_results.append(result)
                except Exception:
                    continue
            
            if method_results:
                combined_anomaly = self._combine_network_results(
                    method_results, player_id, event
                )
                anomalies.append(combined_anomaly)
        
        for anomaly in anomalies:
            profile.anomaly_history.append(anomaly)
            self.network_events_detected += 1
        
        return anomalies
    
    def _update_network_stats(self, profile: NetworkProfile):
        """Update network statistics"""
        if profile.connection_history:
            recent_connections = list(profile.connection_history)[-50:]
            connection_rate = len(recent_connections) / 50.0 * 60
            profile.connection_rate = min(connection_rate, 1000)
            
            recent_packets = list(profile.packet_history)[-100:]
            packet_rate = len(recent_packets) / 100.0
            profile.packet_rate = min(packet_rate, 1000)
            
            recent_latencies = list(profile.timing_history)[-100:]
            avg_latency = sum(recent_latencies) / len(recent_latencies)
            profile.avg_latency = avg_latency
            
            recent_bandwidth = list(profile.bandwidth_usage)[-100:]
            avg_bandwidth = sum(recent_bandwidth) / len(recent_bandwidth)
            profile.avg_bandwidth = avg_bandwidth
    
    def _combine_network_results(self, method_results: List[Dict], player_id: str, event: NetworkEvent) -> NetworkDetection:
        """Combine results from multiple network analysis methods"""
        total_confidence = sum(result['confidence'] for result in method_results)
        avg_confidence = total_confidence / len(method_results)
        
        if avg_confidence >= 0.9:
            severity = NetworkSeverity.CRITICAL
        elif avg_confidence >= 0.8:
            severity = NetworkSeverity.HIGH
        elif avg_confidence >= 0.7:
            severity = NetworkSeverity.MEDIUM
        else:
            severity = NetworkSeverity.LOW
        
        anomaly_type = NetworkAnomalyType.PACKET_TIMING_ANOMALY
        
        risk_factors = []
        for result in method_results:
            risk_factors.extend(result.get('risk_factors', []))
        risk_factors = list(set(risk_factors))
        
        return NetworkDetection(
            detection_id=f"net_anomaly_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            anomaly_type=anomaly_type,
            severity=severity,
            confidence=avg_confidence,
            timestamp=datetime.now(),
            player_id=player_id,
            network_data=event,
            anomaly_metrics={
                'combined_confidence': avg_confidence,
                'method_count': len(method_results),
                'max_confidence': max(result['confidence'] for result in method_results),
                'all_confidences': [result['confidence'] for result in method_results]
            },
            risk_factors=risk_factors
        )
    
    def _packet_timing_analysis(self, profile: NetworkProfile) -> Dict[str, Any]:
        """Analyze packet timing patterns"""
        if len(profile.packet_history) < 10:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'packet_timing_analysis'}
        
        recent_packets = list(profile.packet_history)[-50:]
        
        intervals = []
        for i in range(1, len(recent_packets)):
            interval = (recent_packets[i].timestamp - recent_packets[i-1].timestamp).total_seconds()
            intervals.append(interval)
        
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
            std_deviation = math.sqrt(variance)
            
            if std_deviation < 5:
                is_anomaly = True
                confidence = 1.0
                risk_factors = ["robotic_timing", "extremely_consistent"]
            elif std_deviation < 10:
                is_anomaly = True
                confidence = 0.8
                risk_factors = ["consistent_timing"]
            elif std_deviation < 20:
                is_anomaly = True
                confidence = 0.6
                risk_factors = ["low_variance"]
            else:
                is_anomaly = False
                confidence = 0.3
                risk_factors = []
            
            return {
                'is_anomaly': is_anomaly,
                'confidence': confidence,
                'method': 'packet_timing_analysis',
                'avg_interval': avg_interval,
                'std_deviation': std_deviation,
                'risk_factors': risk_factors
            }
        
        return {'is_anomaly': False, 'confidence': 0.0, 'method': 'packet_timing_analysis'}
    
    def _traffic_volume_analysis(self, profile: NetworkProfile) -> Dict[str, Any]:
        """Analyze traffic volume patterns"""
        if len(profile.bandwidth_usage) < 10:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'traffic_volume_analysis'}
        
        recent_bandwidth = list(profile.bandwidth_usage)[-50:]
        avg_bandwidth = sum(recent_bandwidth) / len(recent_bandwidth)
        max_bandwidth = max(recent_bandwidth)
        min_bandwidth = min(recent_bandwidth)
        
        spike_threshold = self.network_thresholds['bandwidth_threshold']
        is_anomaly = max_bandwidth > spike_threshold
        confidence = min(1.0, max_bandwidth / spike_threshold)
        
        risk_factors = []
        if max_bandwidth > 5000000:
            risk_factors.append("massive_bandwidth_spike")
        elif max_bandwidth > 1000000:
            risk_factors.append("high_bandwidth_usage")
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': confidence,
            'method': 'traffic_volume_analysis',
            'avg_bandwidth': avg_bandwidth,
            'max_bandwidth': max_bandwidth,
            'min_bandwidth': min_bandwidth,
            'risk_factors': risk_factors
        }
    
    def _connection_pattern_analysis(self, profile: NetworkProfile) -> Dict[str, Any]:
        """Analyze connection patterns"""
        if len(profile.connection_history) < 10:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'connection_pattern_analysis'}
        
        recent_connections = list(profile.connection_history)[-50:]
        connection_rate = len(recent_connections) / 50.0 * 60
        connection_rate = min(connection_rate, 1000)
        
        connection_intervals = []
        for i in range(1, len(recent_connections)):
            interval = (recent_connections[i].timestamp - recent_connections[i-1].timestamp).total_seconds()
            connection_intervals.append(interval)
        
        burst_count = 0
        for interval in connection_intervals:
            if interval < 0.1:
                burst_count += 1
            elif interval < 0.5:
                burst_count += 0.5
            else:
                break
        
        burst_ratio = burst_count / len(connection_intervals) if connection_intervals else 0
        
        is_anomaly = burst_ratio > 0.3
        confidence = min(1.0, burst_ratio / 0.3)
        
        risk_factors = []
        if connection_rate > 500:
            risk_factors.append("high_connection_rate")
        if burst_ratio > 0.5:
            risk_factors.append("connection_burst_pattern")
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': confidence,
            'method': 'connection_pattern_analysis',
            'connection_rate': connection_rate,
            'burst_ratio': burst_ratio,
            'risk_factors': risk_factors
        }
    
    def _geographic_analysis(self, profile: NetworkProfile) -> Dict[str, Any]:
        """Analyze geographic patterns"""
        if not profile.geographic_data:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'geographic_analysis'}
        
        geographic_data = profile.geographic_data
        
        is_anomaly = False
        confidence = 0.0
        risk_factors = []
        
        if geographic_data.get('unique_source_ips', 0) > 5:
            is_anomaly = True
            risk_factors.append("multi_country_access")
            confidence += 0.4
        
        if len(geographic_data.get('countries', [])) > 1:
            is_anomaly = True
            risk_factors.append("rapid_geo_change")
            confidence += 0.3
        
        if geographic_data.get('primary_country') == 'Unknown':
            is_anomaly = True
            risk_factors.append("unknown_location")
            confidence += 0.2
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': confidence,
            'method': 'geographic_analysis',
            'geographic_data': geographic_data,
            'risk_factors': risk_factors
        }
    
    def _protocol_analysis(self, profile: NetworkProfile) -> Dict[str, Any]:
        """Analyze protocol usage patterns"""
        if not profile.connection_history:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'protocol_analysis'}
        
        recent_connections = list(profile.connection_history)[-50:]
        protocol_counts = defaultdict(int)
        for event in recent_connections:
            protocol_counts[event.protocol] += 1
        
        suspicious_protocols = ['arp', 'icmp', 'raw']
        suspicious_count = sum(count for protocol in suspicious_protocols if protocol_counts.get(protocol, 0) > 10)
        
        is_anomaly = suspicious_count > 2
        confidence = min(1.0, suspicious_count / 10)
        
        risk_factors = []
        if suspicious_count > 5:
            risk_factors.append("suspicious_protocol_usage")
        elif suspicious_count > 3:
            risk_factors.append("unusual_protocol_distribution")
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': confidence,
            'method': 'protocol_analysis',
            'protocol_counts': dict(protocol_counts),
            'suspicious_protocols': suspicious_count,
            'risk_factors': risk_factors
        }
    
    def _dns_analysis(self, profile: NetworkProfile) -> Dict[str, Any]:
        """Analyze DNS query patterns"""
        dns_queries = []
        
        for event in profile.connection_history:
            if 'dns_query' in event.metadata:
                dns_queries.append(event.metadata['dns_query'])
        
        if len(dns_queries) < 5:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'dns_analysis'}
        
        query_frequency = len(dns_queries) / len(profile.connection_history)
        is_anomaly = query_frequency > self.network_thresholds['dns_query_threshold']
        confidence = min(1.0, query_frequency / self.network_thresholds['dns_query_threshold'])
        
        risk_factors = []
        if query_frequency > 0.5:
            risk_factors.append("high_dns_query_frequency")
        elif query_frequency > 0.3:
            risk_factors.append("moderate_dns_query_frequency")
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': confidence,
            'method': 'dns_analysis',
            'query_frequency': query_frequency,
            'risk_factors': risk_factors
        }
    
    def _port_scan_detection(self, profile: NetworkProfile) -> Dict[str, Any]:
        """Detect port scanning attempts"""
        recent_ports = []
        
        for event in profile.connection_history:
            if 'port_scan' in event.metadata:
                recent_ports.append(event.port)
        
        if len(recent_ports) < 5:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'port_scan_detection'}
        
        port_scan_frequency = len(recent_ports) / len(profile.connection_history)
        unique_ports = len(set(recent_ports))
        
        is_anomaly = unique_ports > 10 or port_scan_frequency > 0.1
        confidence = min(1.0, port_scan_frequency * 10)
        
        risk_factors = []
        if unique_ports > 20:
            risk_factors.append("extensive_port_scanning")
        elif unique_ports > 10:
            risk_factors.append("multiple_unique_ports")
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': confidence,
            'method': 'port_scan_detection',
            'unique_ports': unique_ports,
            'scan_frequency': port_scan_frequency,
            'risk_factors': risk_factors
        }
    
    def _bandwidth_anomaly(self, profile: NetworkProfile) -> Dict[str, Any]:
        """Detect bandwidth anomalies"""
        if len(profile.bandwidth_usage) < 10:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'bandwidth_anomaly'}
        
        recent_bandwidth = list(profile.bandwidth_usage)[-50:]
        avg_bandwidth = sum(recent_bandwidth) / len(recent_bandwidth)
        max_bandwidth = max(recent_bandwidth)
        min_bandwidth = min(recent_bandwidth)
        
        spike_threshold = self.network_thresholds['bandwidth_threshold']
        is_anomaly = max_bandwidth > spike_threshold
        confidence = min(1.0, max_bandwidth / spike_threshold)
        
        risk_factors = []
        if max_bandwidth > 5000000:
            risk_factors.append("massive_bandwidth_spike")
        elif max_bandwidth > 1000000:
            risk_factors.append("high_bandwidth_usage")
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': confidence,
            'method': 'bandwidth_anomaly',
            'avg_bandwidth': avg_bandwidth,
            'max_bandwidth': max_bandwidth,
            'min_bandwidth': min_bandwidth,
            'risk_factors': risk_factors
        }
    
    def _latency_spike_detection(self, profile: NetworkProfile) -> Dict[str, Any]:
        """Detect latency spikes"""
        if len(profile.timing_history) < 10:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'latency_spike_detection'}
        
        recent_latencies = list(profile.timing_history)[-50:]
        current_latency = recent_latencies[-1]
        
        avg_latency = sum(recent_latencies) / len(recent_latencies)
        std_latency = self._std(recent_latencies)
        
        spike_threshold = self.network_thresholds['latency_threshold']
        is_anomaly = current_latency < (avg_latency - spike_threshold)
        confidence = min(1.0, (avg_latency - spike_threshold) / spike_threshold)
        
        risk_factors = []
        if current_latency < 50:
            risk_factors.append("superhuman_latency")
        elif current_latency < 100:
            risk_factors.append("extremely_low_latency")
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': confidence,
            'method': 'latency_spike_detection',
            'avg_latency': avg_latency,
            'current_latency': current_latency,
            'risk_factors': risk_factors
        }
    
    def get_profile_summary(self, player_id: str) -> Dict[str, Any]:
        """Get network profile summary"""
        profile = self.profiles.get(player_id)
        if not profile:
            return {'error': 'Profile not found'}
        
        anomaly_summary = self._analyze_network_anomaly_history(profile.anomaly_history)
        
        return {
            'player_id': player_id,
            'total_packets': profile.total_packets,
            'total_bytes': profile.total_bytes,
            'connection_rate': profile.connection_rate,
            'avg_latency': profile.avg_latency,
            'avg_bandwidth': profile.avg_bandwidth,
            'total_anomalies': len(profile.anomaly_history),
            'anomaly_summary': anomaly_summary,
            'last_updated': profile.last_updated.isoformat()
        }
    
    def _analyze_network_anomaly_history(self, anomalies: List[NetworkDetection]) -> Dict[str, Any]:
        """Analyze network anomaly history"""
        if not anomalies:
            return {
                'total_anomalies': 0,
                'severity_distribution': {},
                'type_distribution': {},
                'avg_confidence': 0.0,
                'trend': 'stable'
            }
        
        severity_counts = defaultdict(int)
        type_counts = defaultdict(int)
        total_confidence = sum(a.confidence for a in anomalies)
        
        for anomaly in anomalies:
            severity_counts[anomaly.severity.value] += 1
            type_counts[anomaly.anomaly_type.value] += 1
        
        if len(anomalies) >= 10:
            recent_anomalies = anomalies[-10:]
            older_anomalies = anomalies[-20:-10] if len(anomalies) > 10 else []
            
            recent_count = len(recent_anomalies)
            older_count = len(older_anomalies)
            
            if recent_count > older_count * 1.5:
                trend = 'increasing'
            elif recent_count < older_count * 0.5:
                trend = 'decreasing'
            else:
                trend = 'stable'
        else:
            trend = 'insufficient_data'
        
        return {
            'total_anomalies': len(anomalies),
            'severity_distribution': dict(severity_counts),
            'type_distribution': dict(type_counts),
            'avg_confidence': total_confidence / len(anomalies),
            'trend': trend
        }
    
    def generate_network_report(self, player_id: str) -> str:
        """Generate detailed network analysis report"""
        summary = self.get_profile_summary(player_id)
        
        lines = []
        lines.append("# 🌐 NETWORK ANALYSIS REPORT")
        lines.append("=" * 50)
        lines.append("")
        lines.append(f"Player ID: {summary['player_id']}")
        lines.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        lines.append("## 📡 NETWORK PROFILE")
        lines.append("")
        lines.append(f"- **Total Packets**: {summary['total_packets']}")
        lines.append(f"- **Total Bytes**: {summary['total_bytes']}")
        lines.append(f"- **Connection Rate**: {summary.get('connection_rate', 0):.1f}/s")
        lines.append(f"- **Avg Latency**: {summary.get('avg_latency', 0):.1f}ms")
        lines.append(f"- **Avg Bandwidth**: {summary.get('avg_bandwidth', 0):.0f} bytes/s")
        lines.append("")
        
        lines.append("## 🔍 NETWORK STATISTICS")
        lines.append("")
        lines.append(f"- **Total Anomalies**: {summary['anomaly_summary']['total_anomalies']}")
        lines.append(f"- **Average Confidence**: {summary['anomaly_summary']['avg_confidence']:.1%}")
        lines.append(f"- **Trend**: {summary['anomaly_summary']['trend']}")
        lines.append("")
        
        if summary['anomaly_summary']['severity_distribution']:
            lines.append("## 🎯 SEVERITY DISTRIBUTION")
            lines.append("")
            for severity, count in summary['anomaly_summary']['severity_distribution'].items():
                lines.append(f"- **{severity.title()}**: {count}")
            lines.append("")
        
        if summary['anomaly_summary']['type_distribution']:
            lines.append("## 🔍 ANOMALY TYPES")
            lines.append("")
            for anomaly_type, count in summary['anomaly_summary']['type_distribution'].items():
                lines.append(f"**{anomaly_type.replace('_', ' ').title()}**: {count}")
            lines.append("")
        
        lines.append("## ⚠️ NETWORK RISK ASSESSMENT")
        lines.append("")
        if summary['anomaly_summary']['total_anomalies'] > 20:
            lines.append("🚨 **CRITICAL NETWORK ANOMALY RATE**")
            lines.append("Immediate investigation required")
        elif summary['anomaly_summary']['total_anomalies'] > 10:
            lines.append("⚠️ **HIGH NETWORK ANOMALY RATE**")
            lines.append("Enhanced monitoring recommended")
        elif summary['anomaly_summary']['total_anomalies'] > 5:
            lines.append("⚠️ **MEDIUM NETWORK ANOMALY RATE**")
            lines.append("Increased monitoring recommended")
        elif summary['anomaly_summary']['total_anomalies'] > 0:
            lines.append("⚠️ **LOW NETWORK ANOMALY RATE**")
            lines.append("Normal network variation")
        else:
            lines.append("✅ **NO NETWORK ANOMALIES**")
            lines.append("Normal network behavior")
        
        lines.append("")
        lines.append("---")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("Stellar Logic AI - Network Analysis")
        
        return "\n".join(lines)
    
    def get_system_performance(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return {
            'network_events_detected': self.network_events_detected,
            'true_positives': self.true_positives,
            'false_positives': self.false_positives,
            'accuracy_rate': self.true_positives / max(1, self.network_events_detected),
            'active_profiles': len(self.profiles),
            'network_methods': len(self.methods),
            'network_thresholds': self.network_thresholds
        }
    
    def _std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)

# Test the enhanced network analysis system
def test_advanced_network_analysis():
    """Test the advanced network analysis system"""
    print("🌐 Testing Advanced Network Analysis System")
    print("=" * 50)
    
    detector = AdvancedNetworkAnalysis()
    
    # Test with normal player
    print("\n👤 Testing Normal Player Network Behavior...")
    normal_player_id = "player_normal_001"
    
    for i in range(100):
        event = NetworkEvent(
            timestamp=datetime.now() - timedelta(seconds=i*10),
            source_ip="192.168.1.100",
            dest_ip="192.168.1.50",
            protocol="tcp",
            port=80,
            packet_size=random.randint(64, 1500),
            latency=random.uniform(50, 150),
            jitter=random.uniform(0, 15),
            metadata={
                'session_id': f"session_{random.randint(1, 100)}",
                'game_session': True
            }
        )
        detector.add_network_event(normal_player_id, event)
    
    normal_summary = detector.get_profile_summary(normal_player_id)
    print(f"   Total Packets: {normal_summary['total_packets']}")
    print(f"   Total Bytes: {normal_summary['total_bytes']}")
    print(f"   Connection Rate: {normal_summary.get('connection_rate', 0):.1f}/s")
    print(f"   Avg Latency: {normal_summary.get('avg_latency', 0):.1f}ms")
    
    # Test with suspicious player (high traffic)
    print("\n🤖 Testing Suspicious Player Network Behavior...")
    suspicious_player_id = "player_suspicious_001"
    
    for i in range(100):
        if i % 5 == 0:
            for j in range(10):
                event = NetworkEvent(
                    timestamp=datetime.now() - timedelta(seconds=i*10 + j*0.1),
                    source_ip="10.0.0.0",
                    dest_ip="10.0.0.1",
                    protocol="tcp",
                    port=80,
                    packet_size=random.randint(5000, 20000),
                    latency=random.uniform(5, 30),
                    jitter=random.uniform(0, 5),
                    metadata={
                        'session_id': f"session_{random.randint(1, 100)}",
                        'game_session': True,
                        'bot_detected': True
                    }
                )
                detector.add_network_event(suspicious_player_id, event)
        else:
            event = NetworkEvent(
                timestamp=datetime.now() - timedelta(seconds=i*10),
                source_ip="10.0.0.0",
                dest_ip="10.0.0.1",
                protocol="tcp",
                port=80,
                packet_size=random.randint(64, 1500),
                latency=random.uniform(5, 30),
                jitter=random.uniform(0, 5),
                metadata={
                    'session_id': f"session_{random.randint(1, 100)}",
                    'game_session': True
                }
            )
            detector.add_network_event(suspicious_player_id, event)
    
    suspicious_summary = detector.get_profile_summary(suspicious_player_id)
    print(f"   Total Packets: {suspicious_summary['total_packets']}")
    print(f"   Total Bytes: {suspicious_summary['total_bytes']}")
    print(f"   Connection Rate: {suspicious_summary.get('connection_rate', 0):.1f}/s")
    print(f"   Avg Latency: {suspicious_summary.get('avg_latency', 0):.1f}ms")
    
    # Test with port scanner
    print("\n🔍 Testing Port Scanner Network Behavior...")
    scanner_player_id = "player_scanner_001"
    
    for i in range(50):
        for port in [22, 80, 443, 3389, 8080, 8443, 21, 23, 25, 53]:
            event = NetworkEvent(
                timestamp=datetime.now() - timedelta(seconds=i*5 + port*0.1),
                source_ip="203.0.113.0",
                dest_ip="10.0.0.1",
                protocol="tcp",
                port=port,
                packet_size=random.randint(64, 100),
                latency=random.uniform(100, 200),
                jitter=random.uniform(0, 10),
                metadata={
                    'port_scan': True,
                    'scan_type': 'port_scan'
                }
            )
            detector.add_network_event(scanner_player_id, event)
    
    scanner_summary = detector.get_profile_summary(scanner_player_id)
    print(f"   Total Packets: {scanner_summary['total_packets']}")
    print(f"   Total Bytes: {scanner_summary['total_bytes']}")
    print(f"   Connection Rate: {scanner_summary.get('connection_rate', 0):.1f}/s")
    print(f"   Avg Latency: {scanner_summary.get('avg_latency', 0):.1f}ms")
    
    # Generate reports
    print("\n📋 Generating Network Analysis Reports...")
    
    print("\n📄 NORMAL PLAYER REPORT:")
    print(detector.generate_network_report(normal_player_id))
    
    print("\n📄 SUSPICIOUS PLAYER REPORT:")
    print(detector.generate_network_report(suspicious_player_id))
    
    print("\n📄 SCANNER PLAYER REPORT:")
    print(detector.generate_network_report(scanner_player_id))
    
    # System performance
    print("\n📊 SYSTEM PERFORMANCE:")
    performance = detector.get_system_performance()
    print(f"   Network Events Detected: {performance['network_events_detected']}")
    print(f"   Active Profiles: {performance['active_profiles']}")
    print(f"   Network Methods: {performance['network_methods']}")
    
    return detector

if __name__ == "__main__":
    test_advanced_network_analysis()

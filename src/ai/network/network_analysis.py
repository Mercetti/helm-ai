"""
Helm AI Network Analysis Module
This module provides network traffic analysis for cheat detection
"""

import os
import logging
import json
import socket
import struct
import time
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict, deque
import asyncio
from concurrent.futures import ThreadPoolExecutor
import ipaddress
import hashlib
import base64
from pathlib import Path
import numpy as np
import pandas as pd
from scapy.all import IP, TCP, UDP, ICMP, ARP, DNS, HTTP, get_raw_packet
from scapy.utils import PcapWriter
import psutil
import netaddr

logger = logging.getLogger(__name__)

@dataclass
class NetworkEvent:
    """Network event data class"""
    timestamp: datetime
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    packet_size: int
    flags: List[str] = field(default_factory=list)
    payload_hash: str = ""
    is_suspicious: bool = False
    threat_level: str = "low"
    analysis: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NetworkAnalysisResult:
    """Network analysis result"""
    is_suspicious: bool
    confidence: float
    threat_types: List[str]
    events: List[NetworkEvent]
    statistics: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    processing_time: float

class ThreatType:
    """Network threat types"""
    PACKET_INJECTION = "packet_injection"
    TIMING_ANOMALIES = "timing_anomalies"
    UNUSUAL_PORTS = "unusual_ports"
    DATA_EXFILTRATION = "data_exfiltration"
    COMMAND_CONTROL = "command_control"
    DDOS_PARTICIPATION = "ddos_participation"
    PROTOCOL_VIOLATIONS = "protocol_violations"
    ENCRYPTED_TRAFFIC = "encrypted_traffic"
    BROADCAST_STORM = "broadcast_storm"
    PORT_SCANNING = "port_scanning"

class NetworkAnalyzer:
    """Network traffic analysis system for cheat detection"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize network analyzer
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or os.getenv('NETWORK_CONFIG_PATH', 'config/network_config.json')
        
        # Analysis settings
        self.analysis_window = int(os.getenv('NETWORK_ANALYSIS_WINDOW', '300'))  # 5 minutes
        self.packet_buffer_size = int(os.getenv('NETWORK_BUFFER_SIZE', '10000'))
        self.threat_threshold = float(os.getenv('NETWORK_THREAT_THRESHOLD', '0.7'))
        
        # Network monitoring
        self.interface = os.getenv('NETWORK_INTERFACE', 'any')
        self.capture_filter = os.getenv('NETWORK_CAPTURE_FILTER', '')
        
        # Data storage
        self.packet_buffer = deque(maxlen=self.packet_buffer_size)
        self.event_history = deque(maxlen=1000)
        self.statistics = defaultdict(int)
        
        # Suspicious patterns
        self.suspicious_ports = set(os.getenv('SUSPICIOUS_PORTS', '6667,6668,6669,8080,8443,1337').split(','))
        self.suspicious_ips = set()
        self.known_game_servers = set()
        
        # Thread pool for processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Load configuration
        self._load_configuration()
        
        # Initialize monitoring
        self._initialize_monitoring()
    
    def _load_configuration(self):
        """Load network analysis configuration"""
        try:
            config_path = Path(self.config_path)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Load suspicious ports
                if 'suspicious_ports' in config:
                    self.suspicious_ports.update(config['suspicious_ports'])
                
                # Load known game servers
                if 'game_servers' in config:
                    self.known_game_servers.update(config['game_servers'])
                
                # Load suspicious IPs
                if 'suspicious_ips' in config:
                    self.suspicious_ips.update(config['suspicious_ips'])
                
                logger.info(f"Network configuration loaded from {config_path}")
            else:
                logger.warning(f"Network config file not found: {config_path}")
                self._create_default_config()
        
        except Exception as e:
            logger.error(f"Failed to load network configuration: {e}")
    
    def _create_default_config(self):
        """Create default network configuration"""
        default_config = {
            "suspicious_ports": ["6667", "6668", "6669", "8080", "8443", "1337", "31337"],
            "game_servers": [
                "192.168.1.100",  # Example game server
                "10.0.0.50"       # Example game server
            ],
            "suspicious_ips": [],
            "protocols": ["tcp", "udp", "icmp"],
            "analysis_settings": {
                "timing_threshold": 0.1,
                "packet_size_anomaly": 1500,
                "connection_threshold": 100
            }
        }
        
        try:
            config_path = Path(self.config_path)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            
            logger.info(f"Created default network configuration: {config_path}")
        
        except Exception as e:
            logger.error(f"Failed to create default config: {e}")
    
    def _initialize_monitoring(self):
        """Initialize network monitoring"""
        try:
            # Get network interfaces
            self.interfaces = psutil.net_if_addrs().keys()
            logger.info(f"Available network interfaces: {self.interfaces}")
            
            # Initialize statistics
            self.reset_statistics()
            
        except Exception as e:
            logger.error(f"Failed to initialize network monitoring: {e}")
    
    def reset_statistics(self):
        """Reset network statistics"""
        self.statistics = {
            'total_packets': 0,
            'tcp_packets': 0,
            'udp_packets': 0,
            'icmp_packets': 0,
            'suspicious_packets': 0,
            'unique_sources': set(),
            'unique_destinations': set(),
            'start_time': datetime.now()
        }
    
    async def analyze_network_traffic(self, packet_data: Optional[bytes] = None, 
                                      pcap_file: Optional[str] = None) -> NetworkAnalysisResult:
        """
        Analyze network traffic for suspicious activities
        
        Args:
            packet_data: Raw packet data
            pcap_file: Path to PCAP file for analysis
            
        Returns:
            NetworkAnalysisResult with analysis results
        """
        start_time = datetime.now()
        
        try:
            # Load packets
            packets = []
            
            if packet_data:
                # Analyze single packet
                packet = get_raw_packet(packet_data)
                if packet:
                    packets.append(packet)
            
            elif pcap_file:
                # Analyze PCAP file
                packets = self._load_pcap_file(pcap_file)
            
            else:
                # Analyze recent buffer
                packets = list(self.packet_buffer)
            
            if not packets:
                return NetworkAnalysisResult(
                    is_suspicious=False,
                    confidence=0.0,
                    threat_types=[],
                    events=[],
                    statistics=dict(self.statistics),
                    metadata={"error": "No packets to analyze"},
                    timestamp=start_time,
                    processing_time=0.0
                )
            
            # Process packets
            events = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._process_packets, packets
            )
            
            # Analyze patterns
            analysis_results = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._analyze_patterns, events
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update statistics
            self._update_statistics(events)
            
            return NetworkAnalysisResult(
                is_suspicious=analysis_results['is_suspicious'],
                confidence=analysis_results['confidence'],
                threat_types=analysis_results['threat_types'],
                events=events,
                statistics=dict(self.statistics),
                metadata={
                    'packets_analyzed': len(packets),
                    'analysis_window': self.analysis_window,
                    'threshold': self.threat_threshold
                },
                timestamp=start_time,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Network traffic analysis failed: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return NetworkAnalysisResult(
                is_suspicious=False,
                confidence=0.0,
                threat_types=[],
                events=[],
                statistics=dict(self.statistics),
                metadata={"error": str(e)},
                timestamp=start_time,
                processing_time=processing_time
            )
    
    def _load_pcap_file(self, pcap_file: str) -> List:
        """Load packets from PCAP file"""
        packets = []
        
        try:
            from scapy.all import PcapReader
            
            pcap_reader = PcapReader(pcap_file)
            for packet in pcap_reader:
                packets.append(packet)
                
                # Limit number of packets for performance
                if len(packets) >= 10000:
                    break
            
            logger.info(f"Loaded {len(packets)} packets from {pcap_file}")
        
        except Exception as e:
            logger.error(f"Failed to load PCAP file {pcap_file}: {e}")
        
        return packets
    
    def _process_packets(self, packets: List) -> List[NetworkEvent]:
        """Process raw packets into events"""
        events = []
        
        for packet in packets:
            try:
                event = self._extract_packet_info(packet)
                if event:
                    events.append(event)
            except Exception as e:
                logger.warning(f"Failed to process packet: {e}")
        
        return events
    
    def _extract_packet_info(self, packet) -> Optional[NetworkEvent]:
        """Extract information from packet"""
        try:
            if IP not in packet:
                return None
            
            ip_layer = packet[IP]
            
            # Basic packet info
            src_ip = ip_layer.src
            dst_ip = ip_layer.dst
            protocol = ip_layer.proto
            
            # Extract ports for TCP/UDP
            src_port = 0
            dst_port = 0
            
            if TCP in packet:
                tcp_layer = packet[TCP]
                src_port = tcp_layer.sport
                dst_port = tcp_layer.dport
                protocol_name = "TCP"
                flags = [flag for flag in ['SYN', 'ACK', 'FIN', 'RST', 'URG', 'PSH'] if getattr(tcp_layer, flag, False)]
            
            elif UDP in packet:
                udp_layer = packet[UDP]
                src_port = udp_layer.sport
                dst_port = udp_layer.dport
                protocol_name = "UDP"
                flags = []
            
            elif ICMP in packet:
                protocol_name = "ICMP"
                flags = []
            
            else:
                protocol_name = "OTHER"
                flags = []
            
            # Calculate payload hash
            payload_hash = ""
            if packet.payload:
                payload_bytes = bytes(packet.payload)
                payload_hash = hashlib.md5(payload_bytes).hexdigest()
            
            # Create event
            event = NetworkEvent(
                timestamp=datetime.now(),
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=src_port,
                dst_port=dst_port,
                protocol=protocol_name,
                packet_size=len(packet),
                flags=flags,
                payload_hash=payload_hash
            )
            
            # Initial threat assessment
            event.is_suspicious = self._initial_threat_assessment(event)
            event.threat_level = self._calculate_threat_level(event)
            
            return event
        
        except Exception as e:
            logger.error(f"Failed to extract packet info: {e}")
            return None
    
    def _initial_threat_assessment(self, event: NetworkEvent) -> bool:
        """Initial threat assessment based on packet characteristics"""
        # Check suspicious ports
        if str(event.src_port) in self.suspicious_ports or str(event.dst_port) in self.suspicious_ports:
            return True
        
        # Check suspicious IPs
        if event.src_ip in self.suspicious_ips or event.dst_ip in self.suspicious_ips:
            return True
        
        # Check for unusual packet sizes
        if event.packet_size > 1500:  # Larger than typical MTU
            return True
        
        # Check for private IP communication with external IPs
        if self._is_private_ip(event.src_ip) and not self._is_private_ip(event.dst_ip):
            if event.dst_port not in [80, 443, 53]:  # Not standard web/DNS ports
                return True
        
        return False
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return ip_obj.is_private
        except:
            return False
    
    def _calculate_threat_level(self, event: NetworkEvent) -> str:
        """Calculate threat level for event"""
        threat_score = 0
        
        # Suspicious ports
        if str(event.src_port) in self.suspicious_ports or str(event.dst_port) in self.suspicious_ports:
            threat_score += 3
        
        # Suspicious IPs
        if event.src_ip in self.suspicious_ips or event.dst_ip in self.suspicious_ips:
            threat_score += 4
        
        # Unusual packet size
        if event.packet_size > 1500:
            threat_score += 2
        
        # Protocol anomalies
        if event.protocol == "ICMP" and event.packet_size > 100:
            threat_score += 2
        
        # Convert score to threat level
        if threat_score >= 5:
            return "high"
        elif threat_score >= 3:
            return "medium"
        elif threat_score >= 1:
            return "low"
        else:
            return "none"
    
    def _analyze_patterns(self, events: List[NetworkEvent]) -> Dict[str, Any]:
        """Analyze patterns in network events"""
        results = {
            'is_suspicious': False,
            'confidence': 0.0,
            'threat_types': [],
            'patterns': {}
        }
        
        try:
            # Analyze timing patterns
            timing_analysis = self._analyze_timing_patterns(events)
            results['patterns']['timing'] = timing_analysis
            
            # Analyze port usage
            port_analysis = self._analyze_port_usage(events)
            results['patterns']['ports'] = port_analysis
            
            # Analyze traffic volume
            volume_analysis = self._analyze_traffic_volume(events)
            results['patterns']['volume'] = volume_analysis
            
            # Analyze communication patterns
            comm_analysis = self._analyze_communication_patterns(events)
            results['patterns']['communication'] = comm_analysis
            
            # Analyze protocol violations
            protocol_analysis = self._analyze_protocol_violations(events)
            results['patterns']['protocols'] = protocol_analysis
            
            # Aggregate threat assessment
            threat_types = []
            confidence = 0.0
            
            for pattern_type, analysis in results['patterns'].items():
                if analysis.get('is_suspicious', False):
                    threat_types.extend(analysis.get('threat_types', []))
                    confidence = max(confidence, analysis.get('confidence', 0.0))
            
            results['is_suspicious'] = len(threat_types) > 0 and confidence >= self.threat_threshold
            results['confidence'] = confidence
            results['threat_types'] = list(set(threat_types))
        
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")
        
        return results
    
    def _analyze_timing_patterns(self, events: List[NetworkEvent]) -> Dict[str, Any]:
        """Analyze timing patterns in network traffic"""
        analysis = {
            'is_suspicious': False,
            'confidence': 0.0,
            'threat_types': []
        }
        
        try:
            if len(events) < 2:
                return analysis
            
            # Calculate inter-packet timings
            timestamps = [event.timestamp for event in events]
            timestamps.sort()
            
            inter_packet_times = []
            for i in range(1, len(timestamps)):
                delta = (timestamps[i] - timestamps[i-1]).total_seconds()
                inter_packet_times.append(delta)
            
            if not inter_packet_times:
                return analysis
            
            # Statistical analysis
            mean_time = np.mean(inter_packet_times)
            std_time = np.std(inter_packet_times)
            
            # Look for suspicious patterns
            suspicious_patterns = []
            
            # Very regular timing (possible bot)
            if std_time < 0.01 and mean_time < 1.0:
                suspicious_patterns.append(ThreatType.TIMING_ANOMALIES)
                analysis['confidence'] = 0.8
            
            # Burst patterns (possible DDoS)
            burst_count = sum(1 for t in inter_packet_times if t < 0.1)
            if burst_count > len(inter_packet_times) * 0.5:
                suspicious_patterns.append(ThreatType.DDOS_PARTICIPATION)
                analysis['confidence'] = max(analysis['confidence'], 0.7)
            
            # Very slow timing (possible command and control)
            if mean_time > 10.0 and std_time < 1.0:
                suspicious_patterns.append(ThreatType.COMMAND_CONTROL)
                analysis['confidence'] = max(analysis['confidence'], 0.6)
            
            analysis['is_suspicious'] = len(suspicious_patterns) > 0
            analysis['threat_types'] = suspicious_patterns
            analysis['statistics'] = {
                'mean_inter_packet_time': mean_time,
                'std_inter_packet_time': std_time,
                'total_events': len(events)
            }
        
        except Exception as e:
            logger.error(f"Timing pattern analysis failed: {e}")
        
        return analysis
    
    def _analyze_port_usage(self, events: List[NetworkEvent]) -> Dict[str, Any]:
        """Analyze port usage patterns"""
        analysis = {
            'is_suspicious': False,
            'confidence': 0.0,
            'threat_types': []
        }
        
        try:
            # Count port usage
            port_counts = defaultdict(int)
            suspicious_port_usage = 0
            
            for event in events:
                port_counts[event.src_port] += 1
                port_counts[event.dst_port] += 1
                
                # Check for suspicious ports
                if (str(event.src_port) in self.suspicious_ports or 
                    str(event.dst_port) in self.suspicious_ports):
                    suspicious_port_usage += 1
            
            # Analyze port distribution
            total_ports = len(port_counts)
            if total_ports == 0:
                return analysis
            
            # Look for suspicious patterns
            suspicious_patterns = []
            
            # High usage of suspicious ports
            if suspicious_port_usage > len(events) * 0.1:
                suspicious_patterns.append(ThreatType.UNUSUAL_PORTS)
                analysis['confidence'] = 0.7
            
            # Port scanning pattern (many different ports)
            if total_ports > 50:
                suspicious_patterns.append(ThreatType.PORT_SCANNING)
                analysis['confidence'] = max(analysis['confidence'], 0.8)
            
            # High-numbered ports (possible backdoors)
            high_port_usage = sum(1 for port in port_counts if port > 10000)
            if high_port_usage > total_ports * 0.3:
                suspicious_patterns.append(ThreatType.DATA_EXFILTRATION)
                analysis['confidence'] = max(analysis['confidence'], 0.6)
            
            analysis['is_suspicious'] = len(suspicious_patterns) > 0
            analysis['threat_types'] = suspicious_patterns
            analysis['statistics'] = {
                'unique_ports': total_ports,
                'suspicious_port_usage': suspicious_port_usage,
                'high_port_usage': high_port_usage
            }
        
        except Exception as e:
            logger.error(f"Port usage analysis failed: {e}")
        
        return analysis
    
    def _analyze_traffic_volume(self, events: List[NetworkEvent]) -> Dict[str, Any]:
        """Analyze traffic volume patterns"""
        analysis = {
            'is_suspicious': False,
            'confidence': 0.0,
            'threat_types': []
        }
        
        try:
            # Calculate traffic statistics
            total_bytes = sum(event.packet_size for event in events)
            total_packets = len(events)
            
            if total_packets == 0:
                return analysis
            
            avg_packet_size = total_bytes / total_packets
            
            # Group by time windows
            time_windows = defaultdict(list)
            for event in events:
                window = event.timestamp.replace(second=0, microsecond=0)
                time_windows[window].append(event)
            
            # Analyze volume patterns
            suspicious_patterns = []
            
            # Very large packets (possible data exfiltration)
            large_packets = sum(1 for event in events if event.packet_size > 8000)
            if large_packets > total_packets * 0.1:
                suspicious_patterns.append(ThreatType.DATA_EXFILTRATION)
                analysis['confidence'] = 0.6
            
            # High volume in short time (possible DDoS)
            if len(time_windows) > 0:
                max_window_packets = max(len(window) for window in time_windows.values())
                if max_window_packets > 1000:
                    suspicious_patterns.append(ThreatType.DDOS_PARTICIPATION)
                    analysis['confidence'] = max(analysis['confidence'], 0.8)
            
            # Broadcast storm
            broadcast_packets = sum(1 for event in events 
                                 if event.dst_ip.endswith('.255') or event.dst_ip == '255.255.255.255')
            if broadcast_packets > total_packets * 0.2:
                suspicious_patterns.append(ThreatType.BROADCAST_STORM)
                analysis['confidence'] = max(analysis['confidence'], 0.7)
            
            analysis['is_suspicious'] = len(suspicious_patterns) > 0
            analysis['threat_types'] = suspicious_patterns
            analysis['statistics'] = {
                'total_bytes': total_bytes,
                'total_packets': total_packets,
                'avg_packet_size': avg_packet_size,
                'large_packets': large_packets,
                'broadcast_packets': broadcast_packets
            }
        
        except Exception as e:
            logger.error(f"Traffic volume analysis failed: {e}")
        
        return analysis
    
    def _analyze_communication_patterns(self, events: List[NetworkEvent]) -> Dict[str, Any]:
        """Analyze communication patterns"""
        analysis = {
            'is_suspicious': False,
            'confidence': 0.0,
            'threat_types': []
        }
        
        try:
            # Build communication graph
            connections = defaultdict(int)
            unique_sources = set()
            unique_destinations = set()
            
            for event in events:
                connection = (event.src_ip, event.dst_ip, event.dst_port)
                connections[connection] += 1
                unique_sources.add(event.src_ip)
                unique_destinations.add(event.dst_ip)
            
            # Analyze communication patterns
            suspicious_patterns = []
            
            # Many connections to single destination (possible C&C)
            dst_counts = defaultdict(int)
            for event in events:
                dst_counts[event.dst_ip] += 1
            
            max_dst_connections = max(dst_counts.values()) if dst_counts else 0
            if max_dst_connections > len(events) * 0.5:
                suspicious_patterns.append(ThreatType.COMMAND_CONTROL)
                analysis['confidence'] = 0.7
            
            # P2P communication pattern
            if len(unique_sources) > 1 and len(unique_destinations) > 1:
                p2p_ratio = min(len(unique_sources), len(unique_destinations)) / max(len(unique_sources), len(unique_destinations))
                if p2p_ratio > 0.8:
                    suspicious_patterns.append(ThreatType.DATA_EXFILTRATION)
                    analysis['confidence'] = max(analysis['confidence'], 0.6)
            
            analysis['is_suspicious'] = len(suspicious_patterns) > 0
            analysis['threat_types'] = suspicious_patterns
            analysis['statistics'] = {
                'unique_sources': len(unique_sources),
                'unique_destinations': len(unique_destinations),
                'total_connections': len(connections),
                'max_dst_connections': max_dst_connections
            }
        
        except Exception as e:
            logger.error(f"Communication pattern analysis failed: {e}")
        
        return analysis
    
    def _analyze_protocol_violations(self, events: List[NetworkEvent]) -> Dict[str, Any]:
        """Analyze protocol violations"""
        analysis = {
            'is_suspicious': False,
            'confidence': 0.0,
            'threat_types': []
        }
        
        try:
            violations = []
            
            for event in events:
                # Check for protocol violations
                if event.protocol == "TCP":
                    # TCP without proper flags
                    if not event.flags:
                        violations.append("TCP without flags")
                
                elif event.protocol == "UDP":
                    # UDP with large packets (possible tunneling)
                    if event.packet_size > 1400:
                        violations.append("Large UDP packet")
                
                # Check for unusual protocol combinations
                if event.protocol == "ICMP" and event.packet_size > 100:
                    violations.append("Large ICMP packet")
            
            # Assess violations
            if len(violations) > len(events) * 0.1:
                analysis['is_suspicious'] = True
                analysis['confidence'] = 0.6
                analysis['threat_types'] = [ThreatType.PROTOCOL_VIOLATIONS]
            
            analysis['statistics'] = {
                'total_violations': len(violations),
                'violation_rate': len(violations) / len(events) if events else 0
            }
        
        except Exception as e:
            logger.error(f"Protocol violation analysis failed: {e}")
        
        return analysis
    
    def _update_statistics(self, events: List[NetworkEvent]):
        """Update network statistics"""
        self.statistics['total_packets'] += len(events)
        
        for event in events:
            self.statistics[f"{event.protocol.lower()}_packets"] += 1
            
            if event.is_suspicious:
                self.statistics['suspicious_packets'] += 1
            
            self.statistics['unique_sources'].add(event.src_ip)
            self.statistics['unique_destinations'].add(event.dst_ip)
        
        # Convert sets to counts for serialization
        self.statistics['unique_sources'] = len(self.statistics['unique_sources'])
        self.statistics['unique_destinations'] = len(self.statistics['unique_destinations'])
    
    def add_packet(self, packet_data: bytes):
        """Add packet to analysis buffer"""
        try:
            packet = get_raw_packet(packet_data)
            if packet:
                self.packet_buffer.append(packet)
                
                # Maintain buffer size
                if len(self.packet_buffer) > self.packet_buffer_size:
                    self.packet_buffer.popleft()
        
        except Exception as e:
            logger.error(f"Failed to add packet to buffer: {e}")
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get analysis statistics"""
        return {
            "config_path": self.config_path,
            "analysis_window": self.analysis_window,
            "packet_buffer_size": self.packet_buffer_size,
            "threat_threshold": self.threat_threshold,
            "suspicious_ports": list(self.suspicious_ports),
            "known_game_servers": list(self.known_game_servers),
            "suspicious_ips": list(self.suspicious_ips),
            "buffer_size": len(self.packet_buffer),
            "statistics": dict(self.statistics)
        }
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update analysis settings"""
        if 'threat_threshold' in settings:
            self.threat_threshold = float(settings['threat_threshold'])
        
        if 'analysis_window' in settings:
            self.analysis_window = int(settings['analysis_window'])
        
        if 'suspicious_ports' in settings:
            self.suspicious_ports.update(settings['suspicious_ports'])
        
        logger.info(f"Network analysis settings updated: {settings}")

# Global instance
network_analyzer = NetworkAnalyzer()

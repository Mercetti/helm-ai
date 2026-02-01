#!/usr/bin/env python3
"""
Stellar Logic AI - Advanced Statistical Anomaly Detection System
Enhanced statistical anomaly detection for detecting sophisticated cheating patterns
Target: 70%+ detection rate
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random
import math
import json
from collections import defaultdict, deque

class AnomalyType(Enum):
    """Types of statistical anomalies to detect"""
    OUTLIER_DETECTION = "outlier_detection"
    DISTRIBUTION_SHIFT = "distribution_shift"
    VARIANCE_ANOMALY = "variance_anomaly"
    CORRELATION_ANOMALY = "correlation_anomaly"
    TREND_ANOMALY = "trend_anomaly"
    SEASONAL_ANOMALY = "seasonal_anomaly"
    MULTIVARIATE_ANOMALY = "multivariate_anomaly"
    TEMPORAL_ANOMALY = "temporal_anomaly"

class AnomalySeverity(Enum):
    """Severity levels for detected anomalies"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class AnomalyDetection:
    """Anomaly detection result"""
    anomaly_id: str
    anomaly_type: AnomalyType
    severity: AnomalySeverity
    confidence: float
    timestamp: datetime
    player_id: str
    anomaly_data: Dict[str, Any]
    statistical_metrics: Dict[str, float]
    risk_factors: List[str]

@dataclass
class StatisticalProfile:
    """Statistical profile for player behavior"""
    player_id: str
    metrics_history: Dict[str, deque]
    baseline_stats: Dict[str, Dict[str, float]]
    anomaly_history: List[AnomalyDetection]
    last_updated: datetime
    data_points: int

class AdvancedStatisticalAnomalyDetection:
    """Advanced statistical anomaly detection system"""
    
    def __init__(self):
        self.profiles = {}
        self.anomaly_thresholds = {
            'z_score_threshold': 3.0,
            'iqr_multiplier': 1.5,
            'correlation_threshold': 0.8,
            'trend_deviation_threshold': 2.0,
            'seasonal_deviation_threshold': 2.5
        }
        
        # Statistical methods configuration
        self.methods = {
            'z_score': self._z_score_detection,
            'iqr': self._iqr_detection,
            'isolation_forest': self._isolation_forest_detection,
            'local_outlier_factor': self._local_outlier_factor_detection,
            'one_class_svm': self._one_class_svm_detection,
            'autoencoder': self._autoencoder_detection
        }
        
        # Performance metrics
        self.anomalies_detected = 0
        self.false_positives = 0
        self.true_positives = 0
        
        # Data window configuration
        self.window_size = 100
        self.min_data_points = 30
        
    def create_profile(self, player_id: str) -> StatisticalProfile:
        """Create statistical profile for player"""
        profile = StatisticalProfile(
            player_id=player_id,
            metrics_history=defaultdict(lambda: deque(maxlen=self.window_size)),
            baseline_stats={},
            anomaly_history=[],
            last_updated=datetime.now(),
            data_points=0
        )
        
        self.profiles[player_id] = profile
        return profile
    
    def add_data_point(self, player_id: str, metrics: Dict[str, float]) -> List[AnomalyDetection]:
        """Add data point and detect anomalies"""
        profile = self.profiles.get(player_id)
        if not profile:
            profile = self.create_profile(player_id)
        
        # Add metrics to history
        for metric_name, value in metrics.items():
            profile.metrics_history[metric_name].append(value)
        
        profile.last_updated = datetime.now()
        profile.data_points += 1
        
        # Detect anomalies
        anomalies = []
        
        if profile.data_points >= self.min_data_points:
            # Update baseline statistics
            self._update_baseline_stats(profile)
            
            # Detect anomalies using multiple methods
            for metric_name, values in profile.metrics_history.items():
                if len(values) >= self.min_data_points:
                    # Apply all statistical methods
                    method_results = []
                    
                    for method_name, method_func in self.methods.items():
                        try:
                            result = method_func(values, profile.baseline_stats.get(metric_name, {}))
                            if result['is_anomaly']:
                                method_results.append(result)
                        except Exception as e:
                            # Log error and continue
                            continue
                    
                    # Combine results from multiple methods
                    if method_results:
                        combined_anomaly = self._combine_anomaly_results(
                            method_results, player_id, metric_name, values[-1]
                        )
                        anomalies.append(combined_anomaly)
        
        # Store anomalies
        for anomaly in anomalies:
            profile.anomaly_history.append(anomaly)
            self.anomalies_detected += 1
        
        return anomalies
    
    def _update_baseline_stats(self, profile: StatisticalProfile):
        """Update baseline statistics"""
        for metric_name, values in profile.metrics_history.items():
            if len(values) >= self.min_data_points:
                values_list = list(values)
                profile.baseline_stats[metric_name] = {
                    'mean': self._mean(values_list),
                    'std': self._std(values_list),
                    'min': min(values_list),
                    'max': max(values_list),
                    'median': self._median(values_list),
                    'q1': self._percentile(values_list, 25),
                    'q3': self._percentile(values_list, 75),
                    'iqr': self._iqr(values_list),
                    'skewness': self._skewness(values_list),
                    'kurtosis': self._kurtosis(values_list)
                }
    
    def _combine_anomaly_results(self, method_results: List[Dict], player_id: str, 
                              metric_name: str, current_value: float) -> AnomalyDetection:
        """Combine results from multiple anomaly detection methods"""
        
        # Calculate combined confidence
        total_confidence = sum(result['confidence'] for result in method_results)
        avg_confidence = total_confidence / len(method_results)
        
        # Determine anomaly type based on most confident result
        best_result = max(method_results, key=lambda x: x['confidence'])
        
        # Determine severity based on confidence and deviation
        if avg_confidence >= 0.9:
            severity = AnomalySeverity.CRITICAL
        elif avg_confidence >= 0.8:
            severity = AnomalySeverity.HIGH
        elif avg_confidence >= 0.7:
            severity = AnomalySeverity.MEDIUM
        else:
            severity = AnomalySeverity.LOW
        
        # Determine anomaly type (default to outlier detection)
        anomaly_type = AnomalyType.OUTLIER_DETECTION
        
        # Collect all risk factors
        risk_factors = []
        for result in method_results:
            risk_factors.extend(result.get('risk_factors', []))
        
        # Remove duplicates
        risk_factors = list(set(risk_factors))
        
        return AnomalyDetection(
            anomaly_id=f"stat_anomaly_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            anomaly_type=anomaly_type,
            severity=severity,
            confidence=avg_confidence,
            timestamp=datetime.now(),
            player_id=player_id,
            anomaly_data={
                'metric_name': metric_name,
                'current_value': current_value,
                'methods_detected': [result['method'] for result in method_results]
            },
            statistical_metrics={
                'combined_confidence': avg_confidence,
                'method_count': len(method_results),
                'max_confidence': best_result['confidence'],
                'all_confidences': [result['confidence'] for result in method_results]
            },
            risk_factors=risk_factors
        )
    
    def _z_score_detection(self, values: List[float], baseline: Dict[str, float]) -> Dict[str, Any]:
        """Z-score based anomaly detection"""
        if not baseline or 'mean' not in baseline or 'std' not in baseline:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'z_score'}
        
        current_value = values[-1]
        mean = baseline['mean']
        std = baseline['std']
        
        if std == 0:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'z_score'}
        
        z_score = abs(current_value - mean) / std
        
        is_anomaly = z_score > self.anomaly_thresholds['z_score_threshold']
        confidence = min(1.0, z_score / self.anomaly_thresholds['z_score_threshold'])
        
        risk_factors = []
        if z_score > 4:
            risk_factors.append("extreme_outlier")
        elif z_score > 3:
            risk_factors.append("significant_outlier")
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': confidence,
            'method': 'z_score',
            'z_score': z_score,
            'risk_factors': risk_factors
        }
    
    def _iqr_detection(self, values: List[float], baseline: Dict[str, float]) -> Dict[str, Any]:
        """Interquartile Range (IQR) based anomaly detection"""
        if not baseline or 'q1' not in baseline or 'q3' not in baseline or 'iqr' not in baseline:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'iqr'}
        
        current_value = values[-1]
        q1 = baseline['q1']
        q3 = baseline['q3']
        iqr = baseline['iqr']
        
        if iqr == 0:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'iqr'}
        
        lower_bound = q1 - self.anomaly_thresholds['iqr_multiplier'] * iqr
        upper_bound = q3 + self.anomaly_thresholds['iqr_multiplier'] * iqr
        
        is_anomaly = current_value < lower_bound or current_value > upper_bound
        
        if current_value < lower_bound:
            deviation = (lower_bound - current_value) / iqr
        else:
            deviation = (current_value - upper_bound) / iqr
        
        confidence = min(1.0, abs(deviation) / self.anomaly_thresholds['iqr_multiplier'])
        
        risk_factors = []
        if deviation > 3:
            risk_factors.append("extreme_iqr_outlier")
        elif deviation > 2:
            risk_factors.append("significant_iqr_outlier")
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': confidence,
            'method': 'iqr',
            'deviation': deviation,
            'bounds': (lower_bound, upper_bound),
            'risk_factors': risk_factors
        }
    
    def _isolation_forest_detection(self, values: List[float], baseline: Dict[str, float]) -> Dict[str, Any]:
        """Isolation Forest based anomaly detection (simplified)"""
        # Simplified isolation forest simulation
        if len(values) < 20:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'isolation_forest'}
        
        current_value = values[-1]
        recent_values = values[-20:]
        
        # Calculate isolation score (simplified)
        mean_recent = self._mean(recent_values)
        std_recent = self._std(recent_values)
        
        if std_recent == 0:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'isolation_forest'}
        
        isolation_score = abs(current_value - mean_recent) / std_recent
        
        # Isolation forest typically uses a threshold around 0.5
        is_anomaly = isolation_score > 0.5
        confidence = min(1.0, isolation_score)
        
        risk_factors = []
        if isolation_score > 1.0:
            risk_factors.append("extreme_isolation")
        elif isolation_score > 0.7:
            risk_factors.append("significant_isolation")
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': confidence,
            'method': 'isolation_forest',
            'isolation_score': isolation_score,
            'risk_factors': risk_factors
        }
    
    def _local_outlier_factor_detection(self, values: List[float], baseline: Dict[str, float]) -> Dict[str, Any]:
        """Local Outlier Factor (LOF) based anomaly detection (simplified)"""
        if len(values) < 10:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'local_outlier_factor'}
        
        current_value = values[-1]
        k = min(10, len(values) // 2)  # k neighbors
        
        # Calculate distances to k nearest neighbors
        sorted_values = sorted(values)
        current_idx = sorted_values.index(current_value)
        
        # Get k nearest neighbors
        start_idx = max(0, current_idx - k)
        end_idx = min(len(sorted_values), current_idx + k + 1)
        neighbors = sorted_values[start_idx:end_idx]
        neighbors = [n for n in neighbors if n != current_value]
        
        if not neighbors:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'local_outlier_factor'}
        
        # Calculate LOF score
        avg_distance = sum(abs(current_value - n) for n in neighbors) / len(neighbors)
        
        # Calculate average distance of neighbors to their neighbors
        neighbor_distances = []
        for i, neighbor in enumerate(neighbors):
            neighbor_idx = sorted_values.index(neighbor)
            neighbor_start = max(0, neighbor_idx - k)
            neighbor_end = min(len(sorted_values), neighbor_idx + k + 1)
            neighbor_neighbors = sorted_values[neighbor_start:neighbor_end]
            neighbor_neighbors = [n for n in neighbor_neighbors if n != neighbor]
            
            if neighbor_neighbors:
                neighbor_avg_dist = sum(abs(neighbor - n) for n in neighbor_neighbors) / len(neighbor_neighbors)
                neighbor_distances.append(neighbor_avg_dist)
        
        if not neighbor_distances:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'local_outlier_factor'}
        
        avg_neighbor_distance = sum(neighbor_distances) / len(neighbor_distances)
        
        if avg_neighbor_distance == 0:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'local_outlier_factor'}
        
        lof_score = avg_distance / avg_neighbor_distance
        
        # LOF > 1.5 is typically considered anomalous
        is_anomaly = lof_score > 1.5
        confidence = min(1.0, (lof_score - 1.0) / 1.0)
        
        risk_factors = []
        if lof_score > 3.0:
            risk_factors.append("extreme_lof_outlier")
        elif lof_score > 2.0:
            risk_factors.append("significant_lof_outlier")
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': confidence,
            'method': 'local_outlier_factor',
            'lof_score': lof_score,
            'risk_factors': risk_factors
        }
    
    def _one_class_svm_detection(self, values: List[float], baseline: Dict[str, float]) -> Dict[str, Any]:
        """One-Class SVM based anomaly detection (simplified)"""
        # Simplified one-class SVM simulation
        if len(values) < 20:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'one_class_svm'}
        
        current_value = values[-1]
        training_values = values[:-1]
        
        # Calculate decision boundary (simplified)
        mean_train = self._mean(training_values)
        std_train = self._std(training_values)
        
        if std_train == 0:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'one_class_svm'}
        
        # Simplified decision boundary
        decision_boundary = mean_train + 2 * std_train
        
        is_anomaly = current_value > decision_boundary
        distance = abs(current_value - decision_boundary) / std_train
        confidence = min(1.0, distance / 2.0)
        
        risk_factors = []
        if distance > 4:
            risk_factors.append("extreme_svm_outlier")
        elif distance > 2:
            risk_factors.append("significant_svm_outlier")
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': confidence,
            'method': 'one_class_svm',
            'decision_boundary': decision_boundary,
            'distance': distance,
            'risk_factors': risk_factors
        }
    
    def _autoencoder_detection(self, values: List[float], baseline: Dict[str, float]) -> Dict[str, Any]:
        """Autoencoder based anomaly detection (simplified)"""
        # Simplified autoencoder simulation
        if len(values) < 20:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'autoencoder'}
        
        current_value = values[-1]
        training_values = values[:-1]
        
        # Simplified reconstruction error calculation
        mean_train = self._mean(training_values)
        std_train = self._std(training_values)
        
        if std_train == 0:
            return {'is_anomaly': False, 'confidence': 0.0, 'method': 'autoencoder'}
        
        # Simplified reconstruction error
        reconstruction_error = abs(current_value - mean_train) / std_train
        
        # Reconstruction error threshold
        error_threshold = 2.0
        is_anomaly = reconstruction_error > error_threshold
        confidence = min(1.0, reconstruction_error / error_threshold)
        
        risk_factors = []
        if reconstruction_error > 4:
            risk_factors.append("extreme_reconstruction_error")
        elif reconstruction_error > 2:
            risk_factors.append("significant_reconstruction_error")
        
        return {
            'is_anomaly': is_anomaly,
            'confidence': confidence,
            'method': 'autoencoder',
            'reconstruction_error': reconstruction_error,
            'risk_factors': risk_factors
        }
    
    def detect_multivariate_anomalies(self, player_id: str, metrics: Dict[str, List[float]]) -> List[AnomalyDetection]:
        """Detect multivariate anomalies across multiple metrics"""
        profile = self.profiles.get(player_id)
        if not profile:
            return []
        
        anomalies = []
        
        # Check if we have enough data for multivariate analysis
        metric_names = list(metrics.keys())
        if len(metric_names) < 2:
            return anomalies
        
        # Calculate correlation matrix
        correlation_matrix = self._calculate_correlation_matrix(metrics)
        
        # Detect correlation anomalies
        for i in range(len(metric_names)):
            for j in range(i + 1, len(metric_names)):
                correlation = correlation_matrix[i][j]
                if abs(correlation) > self.anomaly_thresholds['correlation_threshold']:
                    # This is a strong correlation, check if it's anomalous
                    metric1_history = list(profile.metrics_history.get(metric_names[i], []))
                    metric2_history = list(profile.metrics_history.get(metric_names[j], []))
                    
                    if len(metric1_history) >= self.min_data_points and len(metric2_history) >= self.min_data_points:
                        recent_correlation = self._calculate_correlation(metric1_history, metric2_history)
                        
                        # Check if correlation has changed significantly
                        baseline_correlation = 0.0  # Would normally come from baseline
                        correlation_change = abs(recent_correlation - baseline_correlation)
                        
                        if correlation_change > 0.5:  # Significant change in correlation
                            confidence = min(1.0, correlation_change)
                            severity = AnomalySeverity.MEDIUM if correlation_change < 0.8 else AnomalySeverity.HIGH
                            
                            anomalies.append(AnomalyDetection(
                                anomaly_id=f"multivariate_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                                anomaly_type=AnomalyType.MULTIVARIATE_ANOMALY,
                                severity=severity,
                                confidence=confidence,
                                timestamp=datetime.now(),
                                player_id=player_id,
                                anomaly_data={
                                    'metric1': metric_names[i],
                                    'metric2': metric_names[j],
                                    'correlation': recent_correlation,
                                    'correlation_change': correlation_change
                                },
                                statistical_metrics={
                                    'correlation': recent_correlation,
                                    'correlation_change': correlation_change,
                                    'metric_count': len(metric_names)
                                },
                                risk_factors=[f"correlation_anomaly_{metric_names[i]}_{metric_names[j]}"]
                            ))
        
        return anomalies
    
    def _calculate_correlation_matrix(self, metrics: Dict[str, List[float]]) -> List[List[float]]:
        """Calculate correlation matrix for multiple metrics"""
        metric_names = list(metrics.keys())
        n = len(metric_names)
        correlation_matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        # Calculate correlations
        for i in range(n):
            for j in range(n):
                if i == j:
                    correlation_matrix[i][j] = 1.0
                else:
                    metric1_data = metrics[metric_names[i]]
                    metric2_data = metrics[metric_names[j]]
                    
                    min_len = min(len(metric1_data), len(metric2_data))
                    if min_len > 1:
                        correlation_matrix[i][j] = self._calculate_correlation(metric1_data[:min_len], metric2_data[:min_len])
        
        return correlation_matrix
    
    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate correlation coefficient between two lists"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        mean_x = self._mean(x)
        mean_y = self._mean(y)
        
        if self._std(x) == 0 or self._std(y) == 0:
            return 0.0
        
        covariance = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        
        return covariance / (n * self._std(x) * self._std(y))
    
    def get_profile_summary(self, player_id: str) -> Dict[str, Any]:
        """Get statistical profile summary"""
        profile = self.profiles.get(player_id)
        if not profile:
            return {'error': 'Profile not found'}
        
        anomaly_summary = self._analyze_anomaly_history(profile.anomaly_history)
        
        return {
            'player_id': player_id,
            'data_points': profile.data_points,
            'metrics_tracked': list(profile.metrics_history.keys()),
            'baseline_established': len(profile.baseline_stats) > 0,
            'total_anomalies': len(profile.anomaly_history),
            'anomaly_summary': anomaly_summary,
            'last_updated': profile.last_updated.isoformat()
        }
    
    def _analyze_anomaly_history(self, anomalies: List[AnomalyDetection]) -> Dict[str, Any]:
        """Analyze anomaly history"""
        if not anomalies:
            return {
                'total_anomalies': 0,
                'severity_distribution': {},
                'type_distribution': {},
                'avg_confidence': 0.0,
                'trend': 'stable'
            }
        
        # Calculate statistics
        severity_counts = defaultdict(int)
        type_counts = defaultdict(int)
        total_confidence = sum(a.confidence for a in anomalies)
        
        for anomaly in anomalies:
            severity_counts[anomaly.severity.value] += 1
            type_counts[anomaly.anomaly_type.value] += 1
        
        # Analyze trend (simplified)
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
    
    def generate_statistical_report(self, player_id: str) -> str:
        """Generate detailed statistical anomaly detection report"""
        summary = self.get_profile_summary(player_id)
        
        lines = []
        lines.append("# 📊 STATISTICAL ANOMALY DETECTION REPORT")
        lines.append("=" * 50)
        lines.append("")
        lines.append(f"Player ID: {summary['player_id']}")
        lines.append(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        lines.append("## 📈 STATISTICAL PROFILE")
        lines.append("")
        lines.append(f"- **Data Points Analyzed**: {summary['data_points']}")
        lines.append(f"- **Metrics Tracked**: {', '.join(summary['metrics_tracked'])}")
        lines.append(f"- **Baseline Established**: {summary['baseline_established']}")
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
                lines.append(f"- **{anomaly_type.replace('_', ' ').title()}**: {count}")
            lines.append("")
        
        lines.append("## ⚠️ STATISTICAL RISK ASSESSMENT")
        lines.append("")
        if summary['anomaly_summary']['total_anomalies'] > 10:
            lines.append("🚨 **HIGH STATISTICAL ANOMALY RATE**")
            lines.append("Comprehensive investigation required")
        elif summary['anomaly_summary']['total_anomalies'] > 5:
            lines.append("⚠️ **MEDIUM STATISTICAL ANOMALY RATE**")
            lines.append("Enhanced monitoring recommended")
        elif summary['anomaly_summary']['total_anomalies'] > 0:
            lines.append("⚠️ **LOW STATISTICAL ANOMALY RATE**")
            lines.append("Normal statistical variation")
        else:
            lines.append("✅ **NO STATISTICAL ANOMALIES**")
            lines.append("Normal statistical behavior")
        
        lines.append("")
        lines.append("---")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("Stellar Logic AI - Statistical Anomaly Detection")
        
        return "\n".join(lines)
    
    def get_system_performance(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return {
            'anomalies_detected': self.anomalies_detected,
            'true_positives': self.true_positives,
            'false_positives': self.false_positives,
            'accuracy_rate': self.true_positives / max(1, self.anomalies_detected),
            'active_profiles': len(self.profiles),
            'statistical_methods': len(self.methods),
            'anomaly_thresholds': self.anomaly_thresholds
        }
    
    # Statistical utility functions
    def _mean(self, values: List[float]) -> float:
        """Calculate mean"""
        return sum(values) / len(values) if values else 0.0
    
    def _std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        mean = self._mean(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)
    
    def _median(self, values: List[float]) -> float:
        """Calculate median"""
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n == 0:
            return 0.0
        elif n % 2 == 1:
            return sorted_values[n // 2]
        else:
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """Calculate percentile"""
        sorted_values = sorted(values)
        index = int(len(sorted_values) * percentile / 100)
        return sorted_values[min(index, len(sorted_values) - 1)]
    
    def _iqr(self, values: List[float]) -> float:
        """Calculate interquartile range"""
        q1 = self._percentile(values, 25)
        q3 = self._percentile(values, 75)
        return q3 - q1
    
    def _skewness(self, values: List[float]) -> float:
        """Calculate skewness"""
        if len(values) < 3:
            return 0.0
        
        n = len(values)
        mean = self._mean(values)
        std = self._std(values)
        
        if std == 0:
            return 0.0
        
        skewness = sum(((x - mean) / std) ** 3 for x in values) / n
        return skewness
    
    def _kurtosis(self, values: List[float]) -> float:
        """Calculate kurtosis"""
        if len(values) < 4:
            return 0.0
        
        n = len(values)
        mean = self._mean(values)
        std = self._std(values)
        
        if std == 0:
            return 0.0
        
        kurtosis = sum(((x - mean) / std) ** 4 for x in values) / n - 3
        return kurtosis

# Test the enhanced statistical anomaly detection system
def test_advanced_statistical_anomaly_detection():
    """Test the advanced statistical anomaly detection system"""
    print("📊 Testing Advanced Statistical Anomaly Detection System")
    print("=" * 50)
    
    detector = AdvancedStatisticalAnomalyDetection()
    
    # Test with normal player
    print("\n👤 Testing Normal Player Statistical Behavior...")
    normal_player_id = "player_normal_001"
    
    # Generate normal statistical data
    normal_metrics = {}
    for _ in range(50):
        normal_metrics['accuracy'] = random.gauss(0.75, 0.1)
        normal_metrics['reaction_time'] = random.gauss(200, 30)
        normal_metrics['movement_speed'] = random.gauss(250, 50)
        normal_metrics['kill_rate'] = random.gauss(1.2, 0.3)
        
        anomalies = detector.add_data_point(normal_player_id, normal_metrics)
    
    normal_summary = detector.get_profile_summary(normal_player_id)
    print(f"   Data Points: {normal_summary['data_points']}")
    print(f"   Total Anomalies: {normal_summary['anomaly_summary']['total_anomalies']}")
    print(f"   Risk Score: {normal_summary['anomaly_summary']['avg_confidence']:.2f}")
    
    # Test with cheating player (outliers)
    print("\n🤖 Testing Cheating Player Statistical Behavior (Outliers)...")
    cheating_player_id = "player_cheating_001"
    
    # Generate data with outliers
    cheating_metrics = {}
    for i in range(50):
        if i % 10 == 0:  # Occasional outlier
            cheating_metrics['accuracy'] = 0.99  # Outlier
        else:
            cheating_metrics['accuracy'] = random.gauss(0.85, 0.05)
        
        if i % 8 == 0:  # Occasional outlier
            cheating_metrics['reaction_time'] = 80  # Superhuman
        else:
            cheating_metrics['reaction_time'] = random.gauss(180, 20)
        
        cheating_metrics['movement_speed'] = random.gauss(300, 40)
        cheating_metrics['kill_rate'] = random.gauss(2.5, 0.4)
        
        anomalies = detector.add_data_point(cheating_player_id, cheating_metrics)
    
    cheating_summary = detector.get_profile_summary(cheating_player_id)
    print(f"   Data Points: {cheating_summary['data_points']}")
    print(f"   Total Anomalies: {cheating_summary['anomaly_summary']['total_anomalies']}")
    print(f"   Risk Score: {cheating_summary['anomaly_summary']['avg_confidence']:.2f}")
    
    # Test with subtle cheater (distribution shift)
    print("\n🎭 Testing Subtle Cheater Statistical Behavior (Distribution Shift)...")
    subtle_player_id = "player_subtle_001"
    
    # Generate data with distribution shift
    subtle_metrics = {}
    for i in range(50):
        if i < 25:  # First half - normal
            subtle_metrics['accuracy'] = random.gauss(0.70, 0.08)
            subtle_metrics['reaction_time'] = random.gauss(220, 25)
        else:  # Second half - shifted
            subtle_metrics['accuracy'] = random.gauss(0.90, 0.05)  # Shifted up
            subtle_metrics['reaction_time'] = random.gauss(160, 15)  # Shifted down
        
        subtle_metrics['movement_speed'] = random.gauss(250, 50)
        subtle_metrics['kill_rate'] = random.gauss(1.8, 0.3)
        
        anomalies = detector.add_data_point(subtle_player_id, subtle_metrics)
    
    subtle_summary = detector.get_profile_summary(subtle_player_id)
    print(f"   Data Points: {subtle_summary['data_points']}")
    print(f"   Total Anomalies: {subtle_summary['anomaly_summary']['total_anomalies']}")
    print(f"   Risk Score: {subtle_summary['anomaly_summary']['avg_confidence']:.2f}")
    
    # Test multivariate anomalies
    print("\n🔗 Testing Multivariate Anomalies...")
    multivariate_player_id = "player_multivariate_001"
    
    # Generate correlated metrics (normal correlation)
    multivariate_metrics = {
        'accuracy': [],
        'headshot_ratio': [],
        'kill_rate': []
    }
    
    for i in range(100):
        base_accuracy = random.gauss(0.75, 0.1)
        # Create correlated metrics
        headshot_ratio = base_accuracy * 0.8 + random.gauss(0, 0.05)
        kill_rate = base_accuracy * 2.0 + random.gauss(0, 0.3)
        
        multivariate_metrics['accuracy'].append(base_accuracy)
        multivariate_metrics['headshot_ratio'].append(headshot_ratio)
        multivariate_metrics['kill_rate'].append(kill_rate)
    
    # Add multivariate anomalies
    multivariate_anomalies = detector.detect_multivariate_anomalies(
        multivariate_player_id, multivariate_metrics
    )
    
    multivariate_summary = detector.get_profile_summary(multivariate_player_id)
    print(f"   Multivariate Anomalies: {len(multivariate_anomalies)}")
    
    # Generate reports
    print("\n📋 Generating Statistical Anomaly Detection Reports...")
    
    print("\n📄 NORMAL PLAYER REPORT:")
    print(detector.generate_statistical_report(normal_player_id))
    
    print("\n📄 CHEATING PLAYER REPORT:")
    print(detector.generate_statistical_report(cheating_player_id))
    
    print("\n📄 SUBTLE PLAYER REPORT:")
    print(detector.generate_statistical_report(subtle_player_id))
    
    # System performance
    print("\n📊 SYSTEM PERFORMANCE:")
    performance = detector.get_system_performance()
    print(f"   Anomalies Detected: {performance['anomalies_detected']}")
    print(f"   Statistical Methods: {performance['statistical_methods']}")
    
    return detector

if __name__ == "__main__":
    test_advanced_statistical_anomaly_detection()

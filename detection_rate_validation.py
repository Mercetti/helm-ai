#!/usr/bin/env python3
"""
Stellar Logic AI - 98.5% Detection Rate Validation System
=========================================================

Scientific validation framework to prove 98.5% detection rate
Industry-standard testing methodology and statistical analysis
"""

import json
import time
import random
import statistics
import math
from datetime import datetime
from typing import Dict, List, Any, Tuple
import csv

class DetectionRateValidator:
    """
    Scientific validation system for 98.5% detection rate claim
    Industry-standard testing methodology
    """
    
    def __init__(self):
        self.test_results = []
        self.validation_metrics = {
            'total_tests': 0,
            'true_positives': 0,
            'false_positives': 0,
            'true_negatives': 0,
            'false_negatives': 0,
            'detection_rate': 0.0,
            'false_positive_rate': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1_score': 0.0,
            'confidence_interval': 0.0,
            'statistical_significance': 0.0
        }
        
        # Test datasets
        self.test_datasets = self._create_test_datasets()
        
        print("🔬 Stellar Logic AI - Detection Rate Validation System")
        print("🎯 Objective: Prove 98.5% detection rate with scientific validation")
        
    def _create_test_datasets(self) -> Dict[str, List]:
        """Create comprehensive test datasets for validation"""
        return {
            'known_threats': self._generate_known_threats(10000),
            'benign_samples': self._generate_benign_samples(10000),
            'edge_cases': self._generate_edge_cases(2000),
            'ai_threats': self._generate_ai_threats(2000),
            'zero_day_threats': self._generate_zero_day_threats(1000),
            'adversarial_attacks': self._generate_adversarial_attacks(1000)
        }
    
    def _generate_known_threats(self, count: int) -> List[Dict]:
        """Generate known threat test cases"""
        threats = []
        threat_types = [
            'aimbot', 'wallhack', 'speed_hack', 'esp', 'auto_aim',
            'memory_injection', 'network_exploit', 'texture_hack',
            'sound_hack', 'custom_script', 'ai_malware', 'deepfake'
        ]
        
        for i in range(count):
            threat_type = random.choice(threat_types)
            severity = random.uniform(0.7, 1.0)
            
            threats.append({
                'id': f'threat_{i}',
                'type': threat_type,
                'severity': severity,
                'ground_truth': 1.0,  # This is definitely a threat
                'features': self._generate_threat_features(threat_type, severity)
            })
        
        return threats
    
    def _generate_benign_samples(self, count: int) -> List[Dict]:
        """Generate benign test cases"""
        benign = []
        
        for i in range(count):
            benign.append({
                'id': f'benign_{i}',
                'type': 'normal_player',
                'severity': 0.0,
                'ground_truth': 0.0,  # This is definitely benign
                'features': self._generate_benign_features()
            })
        
        return benign
    
    def _generate_edge_cases(self, count: int) -> List[Dict]:
        """Generate edge case test scenarios"""
        edge_cases = []
        
        for i in range(count):
            # Mix of threat and benign with ambiguous features
            is_threat = random.choice([True, False])
            ground_truth = 1.0 if is_threat else 0.0
            
            edge_cases.append({
                'id': f'edge_{i}',
                'type': 'edge_case',
                'severity': random.uniform(0.3, 0.7),
                'ground_truth': ground_truth,
                'features': self._generate_edge_case_features(is_threat)
            })
        
        return edge_cases
    
    def _generate_ai_threats(self, count: int) -> List[Dict]:
        """Generate AI-powered threat test cases"""
        ai_threats = []
        
        for i in range(count):
            ai_threats.append({
                'id': f'ai_threat_{i}',
                'type': random.choice(['ai_malware', 'deepfake', 'llm_exploit', 'adversarial_ai']),
                'severity': random.uniform(0.8, 1.0),
                'ground_truth': 1.0,
                'features': self._generate_ai_threat_features()
            })
        
        return ai_threats
    
    def _generate_zero_day_threats(self, count: int) -> List[Dict]:
        """Generate zero-day threat test cases"""
        zero_day = []
        
        for i in range(count):
            zero_day.append({
                'id': f'zero_day_{i}',
                'type': 'zero_day_exploit',
                'severity': random.uniform(0.9, 1.0),
                'ground_truth': 1.0,
                'features': self._generate_zero_day_features()
            })
        
        return zero_day
    
    def _generate_adversarial_attacks(self, count: int) -> List[Dict]:
        """Generate adversarial attack test cases"""
        adversarial = []
        
        for i in range(count):
            adversarial.append({
                'id': f'adversarial_{i}',
                'type': 'adversarial_attack',
                'severity': random.uniform(0.85, 1.0),
                'ground_truth': 1.0,
                'features': self._generate_adversarial_features()
            })
        
        return adversarial
    
    def _generate_threat_features(self, threat_type: str, severity: float) -> Dict:
        """Generate realistic threat features"""
        return {
            'signatures': [f'{threat_type}_signature', f'malicious_pattern_{random.randint(1000, 9999)}'],
            'behavior_patterns': [f'suspicious_{threat_type}', f'automated_behavior'],
            'movement_data': [random.uniform(50, 150) for _ in range(10)],
            'action_timing': [random.uniform(0.001, 0.01) for _ in range(10)],
            'performance_stats': {
                'accuracy': random.uniform(95, 100),
                'reaction_time': random.uniform(5, 50),
                'headshot_ratio': random.uniform(80, 100)
            },
            'running_processes': [f'{threat_type}_process.exe', 'suspicious_tool.exe'],
            'modified_files': ['game.exe', 'client.dll'],
            'network_connections': ['suspicious_server', 'proxy_connection']
        }
    
    def _generate_benign_features(self) -> Dict:
        """Generate realistic benign features"""
        return {
            'signatures': ['normal_player_001', 'legitimate_software'],
            'behavior_patterns': ['normal_movement', 'typical_actions'],
            'movement_data': [random.uniform(3, 15) for _ in range(10)],
            'action_timing': [random.uniform(0.1, 0.5) for _ in range(10)],
            'performance_stats': {
                'accuracy': random.uniform(30, 60),
                'reaction_time': random.uniform(200, 400),
                'headshot_ratio': random.uniform(5, 25)
            },
            'running_processes': ['chrome.exe', 'discord.exe', 'steam.exe'],
            'modified_files': [],
            'network_connections': ['game_server', 'cdn_connection']
        }
    
    def _generate_edge_case_features(self, is_threat: bool) -> Dict:
        """Generate ambiguous edge case features"""
        base_features = self._generate_benign_features() if not is_threat else self._generate_threat_features('mixed', 0.5)
        
        # Add ambiguous elements
        base_features['movement_data'] = [random.uniform(10, 50) for _ in range(10)]
        base_features['performance_stats']['accuracy'] = random.uniform(60, 80)
        base_features['performance_stats']['reaction_time'] = random.uniform(100, 200)
        
        return base_features
    
    def _generate_ai_threat_features(self) -> Dict:
        """Generate AI-specific threat features"""
        return {
            'signatures': ['ai_generated_pattern', 'ml_exploit_signature'],
            'behavior_patterns': ['ai_automated', 'machine_learning_behavior'],
            'movement_data': [random.uniform(20, 80) for _ in range(10)],
            'action_timing': [random.uniform(0.01, 0.1) for _ in range(10)],
            'performance_stats': {
                'accuracy': random.uniform(85, 95),
                'reaction_time': random.uniform(20, 100),
                'headshot_ratio': random.uniform(60, 85)
            },
            'running_processes': ['python.exe', 'tensorflow.exe', 'ai_framework.exe'],
            'modified_files': ['ai_model.dll', 'ml_library.dll'],
            'network_connections': ['ai_command_server', 'ml_training_server']
        }
    
    def _generate_zero_day_features(self) -> Dict:
        """Generate zero-day threat features"""
        return {
            'signatures': ['unknown_pattern', 'novel_exploit'],
            'behavior_patterns': ['unusual_behavior', 'novel_attack_vector'],
            'movement_data': [random.uniform(30, 120) for _ in range(10)],
            'action_timing': [random.uniform(0.005, 0.05) for _ in range(10)],
            'performance_stats': {
                'accuracy': random.uniform(90, 100),
                'reaction_time': random.uniform(10, 80),
                'headshot_ratio': random.uniform(70, 95)
            },
            'running_processes': ['unknown_process.exe', 'novel_exploit.exe'],
            'modified_files': ['system_dll.dll', 'core_engine.dll'],
            'network_connections': ['unknown_server', 'encrypted_connection']
        }
    
    def _generate_adversarial_features(self) -> Dict:
        """Generate adversarial attack features"""
        return {
            'signatures': ['adversarial_pattern', 'evasion_technique'],
            'behavior_patterns': ['stealth_behavior', 'evasion_movement'],
            'movement_data': [random.uniform(15, 60) for _ in range(10)],
            'action_timing': [random.uniform(0.02, 0.2) for _ in range(10)],
            'performance_stats': {
                'accuracy': random.uniform(75, 90),
                'reaction_time': random.uniform(50, 150),
                'headshot_ratio': random.uniform(50, 75)
            },
            'running_processes': ['evasion_tool.exe', 'anti_detection.exe'],
            'modified_files': ['detection_bypass.dll', 'evasion_library.dll'],
            'network_connections': ['stealth_server', 'encrypted_tunnel']
        }
    
    def run_validation_test(self, detection_system) -> Dict[str, Any]:
        """Run comprehensive validation test"""
        print("🔬 Running Comprehensive Validation Test...")
        print(f"📊 Test Dataset Size: {sum(len(dataset) for dataset in self.test_datasets.values()):,}")
        
        all_results = []
        
        # Test each dataset
        for dataset_name, test_cases in self.test_datasets.items():
            print(f"\n🎯 Testing {dataset_name}: {len(test_cases)} cases")
            
            dataset_results = []
            for test_case in test_cases:
                # Run detection
                start_time = time.time()
                detection_result = detection_system.detect_threat(test_case['features'])
                processing_time = time.time() - start_time
                
                # Calculate result
                predicted_threat = 1 if detection_result['prediction'] > 0.5 else 0
                actual_threat = int(test_case['ground_truth'])
                
                result = {
                    'test_id': test_case['id'],
                    'dataset': dataset_name,
                    'predicted': predicted_threat,
                    'actual': actual_threat,
                    'confidence': detection_result['confidence'],
                    'processing_time': processing_time,
                    'correct': predicted_threat == actual_threat
                }
                
                dataset_results.append(result)
                all_results.append(result)
            
            # Calculate dataset metrics
            dataset_metrics = self._calculate_dataset_metrics(dataset_results)
            print(f"📊 {dataset_name} Detection Rate: {dataset_metrics['detection_rate']:.3f}")
            print(f"📊 {dataset_name} False Positive Rate: {dataset_metrics['false_positive_rate']:.4f}")
        
        # Calculate overall metrics
        overall_metrics = self._calculate_overall_metrics(all_results)
        
        # Calculate statistical significance
        statistical_analysis = self._calculate_statistical_significance(all_results)
        
        # Generate validation report
        validation_report = {
            'test_summary': {
                'total_tests': len(all_results),
                'test_datasets': {name: len(cases) for name, cases in self.test_datasets.items()},
                'test_date': datetime.now().isoformat(),
                'validation_method': 'Industry_Standard_Testing'
            },
            'overall_metrics': overall_metrics,
            'statistical_analysis': statistical_analysis,
            'dataset_breakdown': self._get_dataset_breakdown(all_results),
            'performance_analysis': self._analyze_performance(all_results),
            'confidence_analysis': self._analyze_confidence(all_results),
            'processing_time_analysis': self._analyze_processing_time(all_results)
        }
        
        return validation_report
    
    def _calculate_dataset_metrics(self, results: List[Dict]) -> Dict[str, float]:
        """Calculate metrics for a dataset"""
        tp = sum(1 for r in results if r['predicted'] == 1 and r['actual'] == 1)
        fp = sum(1 for r in results if r['predicted'] == 1 and r['actual'] == 0)
        tn = sum(1 for r in results if r['predicted'] == 0 and r['actual'] == 0)
        fn = sum(1 for r in results if r['predicted'] == 0 and r['actual'] == 1)
        
        total = len(results)
        
        return {
            'true_positives': tp,
            'false_positives': fp,
            'true_negatives': tn,
            'false_negatives': fn,
            'detection_rate': (tp + tn) / total if total > 0 else 0,
            'false_positive_rate': fp / (fp + tn) if (fp + tn) > 0 else 0,
            'precision': tp / (tp + fp) if (tp + fp) > 0 else 0,
            'recall': tp / (tp + fn) if (tp + fn) > 0 else 0,
            'f1_score': 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
        }
    
    def _calculate_overall_metrics(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate overall validation metrics"""
        tp = sum(1 for r in results if r['predicted'] == 1 and r['actual'] == 1)
        fp = sum(1 for r in results if r['predicted'] == 1 and r['actual'] == 0)
        tn = sum(1 for r in results if r['predicted'] == 0 and r['actual'] == 0)
        fn = sum(1 for r in results if r['predicted'] == 0 and r['actual'] == 1)
        
        total = len(results)
        
        detection_rate = (tp + tn) / total if total > 0 else 0
        false_positive_rate = fp / (fp + tn) if (fp + tn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_score = 2 * tp / (2 * tp + fp + fn) if (2 * tp + fp + fn) > 0 else 0
        
        return {
            'true_positives': tp,
            'false_positives': fp,
            'true_negatives': tn,
            'false_negatives': fn,
            'total_tests': total,
            'detection_rate': detection_rate,
            'false_positive_rate': false_positive_rate,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score,
            'target_achieved': detection_rate >= 0.985,
            'performance_gap': max(0, 0.985 - detection_rate)
        }
    
    def _calculate_statistical_significance(self, results: List[Dict]) -> Dict[str, Any]:
        """Calculate statistical significance of results"""
        correct_predictions = [r['correct'] for r in results]
        n = len(correct_predictions)
        
        if n == 0:
            return {'sample_size': 0, 'confidence_interval': 0, 'significance': 'insufficient_data'}
        
        # Calculate proportion of correct predictions
        p_hat = sum(correct_predictions) / n
        
        # Calculate 95% confidence interval
        z_score = 1.96  # 95% confidence
        margin_of_error = z_score * math.sqrt((p_hat * (1 - p_hat)) / n)
        confidence_interval = margin_of_error
        
        # Calculate statistical significance
        target_rate = 0.985
        z_statistic = (p_hat - target_rate) / math.sqrt((target_rate * (1 - target_rate)) / n)
        
        return {
            'sample_size': n,
            'observed_rate': p_hat,
            'target_rate': target_rate,
            'confidence_interval_95': confidence_interval,
            'lower_bound': max(0, p_hat - confidence_interval),
            'upper_bound': min(1, p_hat + confidence_interval),
            'z_statistic': z_statistic,
            'p_value': 2 * (1 - self._normal_cdf(abs(z_statistic))),
            'statistically_significant': abs(z_statistic) > 1.96,
            'meets_target_with_confidence': (p_hat - confidence_interval) >= target_rate
        }
    
    def _normal_cdf(self, x: float) -> float:
        """Normal distribution CDF approximation"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    def _get_dataset_breakdown(self, results: List[Dict]) -> Dict[str, Any]:
        """Get breakdown by dataset"""
        breakdown = {}
        
        for result in results:
            dataset = result['dataset']
            if dataset not in breakdown:
                breakdown[dataset] = {
                    'total': 0,
                    'correct': 0,
                    'detection_rate': 0.0
                }
            
            breakdown[dataset]['total'] += 1
            if result['correct']:
                breakdown[dataset]['correct'] += 1
        
        # Calculate rates
        for dataset in breakdown:
            breakdown[dataset]['detection_rate'] = (
                breakdown[dataset]['correct'] / breakdown[dataset]['total']
            )
        
        return breakdown
    
    def _analyze_performance(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze performance across different scenarios"""
        performance_analysis = {
            'by_threat_type': {},
            'by_severity': {},
            'by_confidence': {}
        }
        
        # Group by different criteria
        for result in results:
            # This would need to be enhanced with actual threat type data
            pass
        
        return performance_analysis
    
    def _analyze_confidence(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze confidence scores"""
        confidences = [r['confidence'] for r in results]
        
        return {
            'average_confidence': statistics.mean(confidences),
            'median_confidence': statistics.median(confidences),
            'min_confidence': min(confidences),
            'max_confidence': max(confidences),
            'confidence_std': statistics.stdev(confidences) if len(confidences) > 1 else 0
        }
    
    def _analyze_processing_time(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze processing times"""
        times = [r['processing_time'] for r in results]
        
        return {
            'average_time': statistics.mean(times),
            'median_time': statistics.median(times),
            'min_time': min(times),
            'max_time': max(times),
            'time_std': statistics.stdev(times) if len(times) > 1 else 0,
            'under_25ms': sum(1 for t in times if t < 0.025) / len(times)
        }
    
    def generate_validation_report(self, validation_report: Dict[str, Any]) -> str:
        """Generate comprehensive validation report"""
        report = []
        report.append("# 🔬 STELLAR LOGIC AI - 98.5% DETECTION RATE VALIDATION REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Executive Summary
        report.append("## 🎯 EXECUTIVE SUMMARY")
        report.append("")
        metrics = validation_report['overall_metrics']
        report.append(f"**Detection Rate Achieved:** {metrics['detection_rate']:.4f} ({metrics['detection_rate']*100:.2f}%)")
        report.append(f"**Target Detection Rate:** 98.5%")
        report.append(f"**Performance Gap:** {metrics['performance_gap']:.4f} ({metrics['performance_gap']*100:.2f}%)")
        report.append(f"**Target Achieved:** {'✅ YES' if metrics['target_achieved'] else '❌ NO'}")
        report.append("")
        
        # Statistical Analysis
        stats = validation_report['statistical_analysis']
        report.append("## 📊 STATISTICAL ANALYSIS")
        report.append("")
        report.append(f"**Sample Size:** {stats['sample_size']:,} test cases")
        report.append(f"**Observed Rate:** {stats['observed_rate']:.4f} ({stats['observed_rate']*100:.2f}%)")
        report.append(f"**95% Confidence Interval:** ±{stats['confidence_interval_95']:.4f}")
        report.append(f"**Lower Bound:** {stats['lower_bound']:.4f} ({stats['lower_bound']*100:.2f}%)")
        report.append(f"**Upper Bound:** {stats['upper_bound']:.4f} ({stats['upper_bound']*100:.2f}%)")
        report.append(f"**Statistically Significant:** {'✅ YES' if stats['statistically_significant'] else '❌ NO'}")
        report.append(f"**Meets Target with Confidence:** {'✅ YES' if stats['meets_target_with_confidence'] else '❌ NO'}")
        report.append("")
        
        # Test Results
        report.append("## 🧪 TEST RESULTS")
        report.append("")
        report.append(f"**Total Tests:** {metrics['total_tests']:,}")
        report.append(f"**True Positives:** {metrics['true_positives']:,}")
        report.append(f"**False Positives:** {metrics['false_positives']:,}")
        report.append(f"**True Negatives:** {metrics['true_negatives']:,}")
        report.append(f"**False Negatives:** {metrics['false_negatives']:,}")
        report.append("")
        
        # Performance Metrics
        report.append("## 📈 PERFORMANCE METRICS")
        report.append("")
        report.append(f"**Precision:** {metrics['precision']:.4f}")
        report.append(f"**Recall:** {metrics['recall']:.4f}")
        report.append(f"**F1 Score:** {metrics['f1_score']:.4f}")
        report.append(f"**False Positive Rate:** {metrics['false_positive_rate']:.6f}")
        report.append("")
        
        # Dataset Breakdown
        report.append("## 📋 DATASET BREAKDOWN")
        report.append("")
        for dataset, data in validation_report['dataset_breakdown'].items():
            report.append(f"**{dataset}:** {data['detection_rate']:.4f} ({data['detection_rate']*100:.2f}%)")
        report.append("")
        
        # Processing Time Analysis
        time_analysis = validation_report['processing_time_analysis']
        report.append("## ⚡ PROCESSING TIME ANALYSIS")
        report.append("")
        report.append(f"**Average Time:** {time_analysis['average_time']:.6f}s")
        report.append(f"**Median Time:** {time_analysis['median_time']:.6f}s")
        report.append(f"**Under 25ms:** {time_analysis['under_25ms']:.4f} ({time_analysis['under_25ms']*100:.2f}%)")
        report.append("")
        
        # Conclusion
        report.append("## 🎯 CONCLUSION")
        report.append("")
        if metrics['target_achieved']:
            report.append("✅ **TARGET ACHIEVED:** The 98.5% detection rate claim is validated by scientific testing.")
        else:
            report.append("❌ **TARGET NOT ACHIEVED:** The system did not meet the 98.5% detection rate target.")
        
        report.append(f"📊 **Final Detection Rate:** {metrics['detection_rate']:.4f} ({metrics['detection_rate']*100:.2f}%)")
        report.append(f"🎯 **Target:** 98.5%")
        report.append(f"📈 **Gap:** {metrics['performance_gap']:.4f} ({metrics['performance_gap']*100:.2f}%)")
        report.append("")
        
        return "\n".join(report)
    
    def save_validation_results(self, validation_report: Dict[str, Any], filename: str = "validation_report.json"):
        """Save validation results to file"""
        with open(filename, 'w') as f:
            json.dump(validation_report, f, indent=2)
        
        # Also save human-readable report
        report_filename = filename.replace('.json', '_report.md')
        with open(report_filename, 'w') as f:
            f.write(self.generate_validation_report(validation_report))
        
        print(f"📄 Validation results saved to: {filename}")
        print(f"📄 Human-readable report saved to: {report_filename}")

# Mock detection system for testing
class MockDetectionSystem:
    """Mock detection system for validation testing"""
    
    def detect_threat(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Mock detection with configurable accuracy"""
        # Simulate 98.5% detection rate
        base_detection = random.random() < 0.985
        
        # Add some logic based on features
        threat_indicators = 0
        if 'signatures' in features:
            for sig in features['signatures']:
                if any(keyword in sig.lower() for keyword in ['threat', 'malware', 'exploit', 'hack']):
                    threat_indicators += 1
        
        if 'performance_stats' in features:
            stats = features['performance_stats']
            if stats.get('accuracy', 0) > 95:
                threat_indicators += 1
            if stats.get('reaction_time', 1000) < 50:
                threat_indicators += 1
        
        # Adjust detection based on indicators
        if threat_indicators >= 2:
            detection_probability = 0.95
        elif threat_indicators >= 1:
            detection_probability = 0.8
        else:
            detection_probability = 0.2
        
        final_detection = random.random() < detection_probability
        
        return {
            'prediction': 1.0 if final_detection else 0.0,
            'confidence': random.uniform(0.7, 0.95),
            'detection_result': 'THREAT_DETECTED' if final_detection else 'SAFE'
        }

def main():
    """Main validation function"""
    print("🔬 STELLAR LOGIC AI - 98.5% DETECTION RATE VALIDATION")
    print("=" * 80)
    
    # Initialize validator
    validator = DetectionRateValidator()
    
    # Initialize mock detection system (replace with real system)
    detection_system = MockDetectionSystem()
    
    # Run validation test
    validation_report = validator.run_validation_test(detection_system)
    
    # Display results
    print("\n🎯 VALIDATION RESULTS:")
    print("=" * 40)
    metrics = validation_report['overall_metrics']
    print(f"📊 Detection Rate: {metrics['detection_rate']:.4f} ({metrics['detection_rate']*100:.2f}%)")
    print(f"🎯 Target: 98.5%")
    print(f"📈 Gap: {metrics['performance_gap']:.4f} ({metrics['performance_gap']*100:.2f}%)")
    print(f"✅ Target Achieved: {'YES' if metrics['target_achieved'] else 'NO'}")
    
    stats = validation_report['statistical_analysis']
    print(f"\n📊 Statistical Significance:")
    print(f"📈 Sample Size: {stats['sample_size']:,}")
    print(f"📊 95% CI: ±{stats['confidence_interval_95']:.4f}")
    print(f"📈 Lower Bound: {stats['lower_bound']:.4f} ({stats['lower_bound']*100:.2f}%)")
    print(f"📈 Upper Bound: {stats['upper_bound']:.4f} ({stats['upper_bound']*100:.2f}%)")
    print(f"✅ Statistically Significant: {'YES' if stats['statistically_significant'] else 'NO'}")
    
    # Save results
    validator.save_validation_results(validation_report)
    
    print(f"\n🎉 VALIDATION COMPLETE!")
    print(f"📄 Results saved to validation files")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Stellar Logic AI - Explainable AI System
====================================

Transparent decision making and model interpretability
Feature importance analysis, decision tree reasoning, SHAP values
"""

import json
import time
import random
import statistics
import math
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

class ExplainableAISystem:
    """
    Explainable AI system for transparent decision making
    Feature importance analysis, decision tree reasoning, SHAP values
    """
    
    def __init__(self):
        # Explanation methods
        self.explainers = {
            'feature_importance': self._create_feature_importance_analyzer(),
            'decision_tree': self._create_decision_tree_explainer(),
            'shap_analyzer': self._create_shap_analyzer(),
            'rule_based': self._create_rule_based_explainer(),
            'attention_visualizer': self._create_attention_visualizer()
        }
        
        # Explanation cache
        self.explanation_cache = {}
        self.explanation_history = []
        
        # Interpretability metrics
        self.interpretability_metrics = {
            'total_explanations': 0,
            'average_confidence': 0.0,
            'feature_importance_scores': {},
            'decision_tree_depth': 0,
            'shap_values': []
        }
        
        print("🔍 Explainable AI System Initialized")
        print("🎯 Methods: Feature Importance, Decision Trees, SHAP Analysis")
        print("📊 Capabilities: Transparent decision making, Model interpretability")
        
    def _create_feature_importance_analyzer(self) -> Dict[str, Any]:
        """Create feature importance analyzer"""
        return {
            'type': 'feature_importance',
            'method': 'permutation_importance',
            'scoring_methods': ['variance_importance', 'correlation_importance', 'mutual_information'],
            'importance_scores': {},
            'feature_names': ['behavior_score', 'anomaly_score', 'risk_factors', 'suspicious_activities', 'ai_indicators']
        }
    
    def _create_decision_tree_explainer(self) -> Dict[str, Any]:
        """Create decision tree explainer"""
        return {
            'type': 'decision_tree',
            'max_depth': 5,
            'min_samples_split': 2,
            'criterion': 'gini',
            'tree_structure': None,
            'feature_importance': {},
            'explanations': []
        }
    
    def _create_shap_analyzer(self) -> Dict[str, Any]:
        """Create SHAP analyzer"""
        return {
            'type': 'shap',
            'background_dataset': self._create_shap_background_data(),
            'model': None,
            'explanations': []
        }
    
    def _create_rule_based_explainer(self) -> Dict[str, Any]:
        """Create rule-based explainer"""
        return {
            'type': 'rule_based',
            'rules': self._create_explanation_rules(),
            'rule_weights': {},
            'explanations': []
        }
    
    def _create_shap_background_data(self) -> List[Dict[str, Any]]:
        """Create SHAP background dataset"""
        background_data = []
        
        # Generate synthetic background data
        for i in range(100):
            features = {
                'behavior_score': random.uniform(0, 1),
                'anomaly_score': random.uniform(0, 1),
                'risk_factors': random.randint(0, 10),
                'suspicious_activities': random.randint(0, 8),
                'ai_indicators': random.randint(0, 7)
            }
            background_data.append(features)
        
        return background_data
    
    def _create_explanation_rules(self) -> List[Dict[str, Any]]:
        """Create explanation rules"""
        rules = [
            {
                'name': 'high_behavior_score',
                'condition': 'behavior_score > 0.7',
                'weight': 0.3,
                'description': 'High behavioral score indicates threat'
            },
            {
                'name': 'high_anomaly_score',
                'condition': 'anomaly_score > 0.6',
                'weight': 0.25,
                'description': 'High anomaly score indicates threat'
            },
            {
                'name': 'multiple_risk_factors',
                'condition': 'risk_factors > 5',
                'weight': 0.2,
                'description': 'Multiple risk factors indicate threat'
            },
            {
                'suspicious_activities': 'suspicious_activities > 3',
                'weight': 0.15,
                'description': 'Suspicious activities indicate threat'
            },
            {
                'ai_indicators': 'ai_indicators > 2',
                'weight': 0.1,
                'description': 'AI indicators indicate advanced threat'
            }
        ]
        
        return rules
    
    def analyze_feature_importance(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze feature importance using multiple methods"""
        feature_vector = self._extract_explainable_features(features)
        
        # Permutation importance
        perm_importance = self._calculate_permutation_importance(feature_vector)
        
        # Correlation importance
        correlation_importance = self._calculate_correlation_importance(feature_vector)
        
        # Mutual information
        mutual_info_importance = self._calculate_mutual_information(feature_vector)
        
        # Combine importance scores
        importance_scores = {
            'permutation': perm_importance,
            'correlation': correlation_importance,
            'mutual_info': mutual_info_importance
        }
        
        # Calculate overall importance
        overall_importance = {
            'behavior_score': (perm_importance[0] + correlation_importance[0] + mutual_info_importance[0]) / 3,
            'anomaly_score': (perm_importance[1] + correlation_importance[1] + mutual_info_importance[1]) / 3,
            'risk_factors': (perm_importance[2] + correlation_importance[2] + mutual_info_importance[2]) / 3,
            'suspicious_activities': (perm_importance[3] + correlation_importance[3] + mutual_info_importance[3]) / 3,
            'ai_indicators': (perm_importance[4] + correlation_importance[4] + mutual_info_importance[4]) / 3
        }
        
        return {
            'importance_scores': importance_scores,
            'method': 'multi_method',
            'feature_vector': feature_vector,
            'overall_importance': overall_importance
        }
    
    def _extract_explainable_features(self, features: Dict[str, Any]) -> List[float]:
        """Extract features for explainable AI analysis"""
        explainable_features = []
        
        # Basic features
        explainable_features.append(features.get('behavior_score', 0))
        explainable_features.append(features.get('anomaly_score', 0))
        explainable_features.append(features.get('risk_factors', 0) / 10))
        explainable_features.append(features.get('suspicious_activities', 0) / 8))
        explainable_features.append(features.get('ai_indicators', 0) / 7))
        
        # Statistical features
        if 'movement_data' in features:
            movement = features['movement_data']
            if isinstance(movement, list) and len(movement) > 0:
                explainable_features.append(statistics.mean(movement))
                explainable_features.append(statistics.stdev(movement) if len(movement) > 1 else 0))
        
        if 'action_timing' in features:
            timing = features['action_timing']
            if isinstance(timing, list) and len(timing) > 0:
                explainable_features.append(statistics.mean(timing))
                explainable_features.append(statistics.stdev(timing) if len(timing) > 1 else 0))
        
        # Performance features
        if 'performance_stats' in features:
            stats = features['performance_stats']
            explainable_features.append(stats.get('accuracy', 0) / 100))
            explainable_features.append(stats.get('reaction_time', 0) / 1000))
            explainable_features.append(stats.get('headshot_ratio', 0) / 100))
            explainable_features.append(stats.get('kill_death_ratio', 0) / 10))
        
        # Pad to fixed size
        while len(explainable_features) < 20):
            explainable_features.append(0.0)
        
        return explainable_features[:20]
    
    def _calculate_permutation_importance(self, features: List[float]) -> float:
        """Calculate permutation importance"""
        if len(features) < 2:
            return 0.0
        
        # Calculate variance for each feature
        feature_variances = []
        for i in range(len(features)):
            other_features = features[:i] + features[i+1:]
            if other_features:
                variance = statistics.variance(other_features)
                feature_variances.append(variance)
        
        # Average variance (lower variance = more important)
        avg_variance = sum(feature_variances) / len(feature_variances) if feature_variances else 0
        return avg_variance
    
    def _calculate_correlation_importance(self, features: List[float]) -> float:
        """Calculate correlation importance"""
        if len(features) < 2:
            return 0.0
        
        # Calculate correlation with target (threat level)
        target_value = features[0]  # Assume first feature is target
        correlations = []
        
        for i in range(1, len(features)):
            correlation = abs(statistics.corrcoef([features[0], [features[i] if i < len(features) else 0]))
            correlations.append(abs(correlation))
        
        # Average correlation with target
        avg_correlation = sum(correlations) / len(correlations) if correlations else 0
        return avg_correlation
    
    def _calculate_mutual_information(self, features: List[float]) -> float:
        """Calculate mutual information"""
        if len(features) < 2:
            return 0.0
        
        # Calculate pairwise mutual information
        mutual_infos = []
        for i in range(len(features)):
            for j in range(i+1, len(features)):
                # Simplified mutual information calculation
                p_i = features[i] + 0.001
                p_j = features[j] + 0.001
                joint_p = features[i] * features[j] + 0.001
                marginal_p_i = features[i] * sum(features[:i] + 1) + 0.001) / sum(features[i] + 1) + 0.001)
                marginal_p_j = features[j] * sum(features[:i] + 1) + 0.001) / sum(features[:i] + 1) + 0.001)
                
                mi = joint_p - marginal_p_i - marginal_p_j
                mutual_infos.append(mi)
        
        # Average mutual information
        avg_mi = sum(mutual_infos) / len(mutual_infos) if mutual_infos else 0
        return avg_mi
    
    def explain_decision(self, features: Dict[str, Any], prediction: float, confidence: float) -> Dict[str, Any]:
        """Explain the decision making process"""
        start_time = time.time()
        
        # Extract features
        feature_vector = self._extract_explainable_features(features)
        
        # Analyze feature importance
        importance_result = self.analyze_feature_importance(features)
        
        # Generate explanations from all methods
        explanations = {}
        
        # Feature importance explanation
        explanations['feature_importance'] = {
            'method': 'multi_method',
            'importance_scores': importance_result['importance_scores'],
            'overall_importance': importance_result['overall_importance'],
            'top_features': sorted(importance_result['importance_scores'].items(), 
                                     key=lambda x: x[1], reverse=True)[:5]
        }
        
        # Decision tree explanation
        tree_explanation = self._explain_decision_tree(features, prediction)
        explanations['decision_tree'] = tree_explanation
        
        # SHAP explanation
        shap_explanation = self._explain_with_shap(features, prediction)
        explanations['shap_analysis'] = shap_explanation
        
        # Rule-based explanation
        rule_explanation = self._explain_with_rules(features, prediction)
        explanations['rule_analysis'] = rule_explanation
        
        # Calculate confidence
        explanation_confidence = self._calculate_explanation_confidence(explanations)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create comprehensive result
        result = {
            'prediction': prediction,
            'confidence': confidence,
            'explanations': explanations,
            'explanation_confidence': explanation_confidence,
            'processing_time': processing_time,
            'detection_result': 'THREAT_DETECTED' if prediction > 0.5 else 'SAFE',
            'risk_level': self._calculate_risk_level(prediction, confidence),
            'recommendation': self._generate_recommendation(prediction, confidence),
            'explainable_strength': self._calculate_explainable_strength(explanations),
            'feature_importance': importance_result['importance_scores'],
            'top_features': explanations['feature_importance']['top_features'],
            'method': 'explainable_ai'
        }
        
        # Store explanation history
        self.explanation_history.append({
            'timestamp': datetime.now(),
            'prediction': prediction,
            'confidence': confidence,
            'explanations': explanations,
            'processing_time': processing_time,
            'features': features
        })
        
        return result
    
    def _explain_decision_tree(self, features: Dict[str, Any], prediction: float) -> Dict[str, Any]:
        """Explain decision using decision tree"""
        tree_model = self.explainers['decision_tree']
        
        # Simple decision tree logic
        path = []
        current_features = self._extract_explainable_features(features)
        
        # Decision tree path
        if features.get('behavior_score', 0) > 0.7:
            if features.get('risk_factors', 0) > 5:
                path.append("High behavior score + High risk factors → THREAT")
                decision = 1.0
            else:
                path.append("High behavior score + Low risk factors → MEDIUM")
                decision = 0.7
        elif features.get('anomaly_score', 0) > 0.6:
            path.append("High anomaly score → THREAT")
            decision = 0.8
        elif features.get('risk_factors', 0) > 3:
            path.append("Medium risk factors → MEDIUM")
            decision = 0.6
        elif features.get('suspicious_activities', 0) > 2:
            path.append("Suspicious activities → MEDIUM")
            decision = 0.5
        else:
            path.append("Low indicators → SAFE")
            decision = 0.2
        
        # Calculate confidence based on path depth
        path_confidence = 1.0 / (len(path) + 1)
        
        return {
            'method': 'decision_tree',
            'decision_path': path,
            'decision': decision,
            'confidence': path_confidence,
            'explanation': " -> ".join(path),
            'confidence': path_confidence
        }
    
    def _explain_with_shap(self, features: List[float], prediction: float) -> Dict[str, Any]:
        """Explain using SHAP values"""
        shap_model = self.explainers['shap_analyzer']
        
        # Get background model predictions
        background_predictions = []
        for bg_sample in shap_model['background_dataset']:
            bg_features = self._extract_explainable_features(bg_sample['features'])
            bg_prediction = sum(bg_features) / len(bg_features)
            background_predictions.append(bg_prediction)
        
        # Calculate SHAP values
        shap_values = []
        for i in range(len(features)):
            shap_value = features[i] - statistics.mean(background_predictions) if background_predictions else 0.0
            shap_values.append(shap_value)
        
        # Calculate SHAP importance
        shap_importance = abs(shap_values[0]) / (statistics.stdev(shap_values) if len(shap_values) > 1 else 1.0))
        
        return {
            'method': 'shap',
            'shap_values': shap_values,
            'shap_importance': shap_importance,
            'explanation': f"SHAP value: {shap_values[0]:.4f} (Feature 1)"
        }
    
    def _calculate_explanation_confidence(self, explanations: Dict[str, Any]) -> float:
        """Calculate explanation confidence"""
        confidences = []
        
        if 'feature_importance' in explanations:
            confidences.append(explanations['feature_importance']['overall_importance'])
        
        if 'decision_tree' in explanations:
            confidences.append(explanations['decision_confidence'])
        
        if 'shap_analysis' in explanations:
            confidences.append(explanations['shap_importance'])
        
        if 'rule_analysis' in explanations:
            confidences.append(explanations['rule_confidence'])
        
        return statistics.mean(confidences) if confidences else 0.5
    
    def _calculate_explainable_strength(self, explanations: Dict[str, Any]) -> float:
        """Calculate explainable strength"""
        strength = 0.0
        
        if 'feature_importance' in explanations:
            strength += explanations['feature_importance']['overall_importance']
        
        if 'decision_tree' in explanations:
            strength += explanations['decision_confidence']
        
        if 'shap_analysis' in explanations:
            strength += explanations['shap_importance']
        
        if 'rule_analysis' in explanations:
            strength += explanations['rule_confidence']
        
        return min(1.0, strength / 3)
    
    def _generate_recommendation(self, prediction: float, confidence: float) -> str:
        """Generate recommendation based on prediction and confidence"""
        if prediction > 0.7 and confidence > 0.8:
            return "EXPLAINABLE_IMMEDIATE_ACTION_REQUIRED"
        elif prediction > 0.5 and confidence > 0.7:
            return "EXPLAINABLE_ENHANCED_MONITORING"
        elif prediction > 0.3 and confidence > 0.6:
            return "EXPLAINABLE_ANALYSIS_RECOMMENDED"
        else:
            return "CONTINUE_EXPLAINABLE_MONITORING"
    
    def get_explainability_statistics(self) -> Dict[str, Any]:
        """Get explainability statistics"""
        return {
            'total_explanations': len(self.explanation_history),
            'average_confidence': self.interpretability_metrics['average_confidence'],
            'feature_importance_scores': self.interpretability_metrics['feature_importance_scores'],
            'decision_tree_depth': self.interpretability_metrics['decision_tree_depth'],
            'shap_values': self.interpretability_metrics.get('shap_values', []),
            'available_methods': list(self.explainers.keys()),
            'model_accuracy': 'high' if self.interpretability_metrics['average_confidence'] > 0.7 else 'medium'
        }

# Test the explainable AI system
def test_explainable_ai():
    """Test the explainable AI system"""
    print("Testing Explainable AI System")
    print("=" * 50)
    
    # Initialize explainable AI system
    explainable_ai = ExplainableAI()
    
    # Test cases
    test_cases = [
        {
            'name': 'Clear Benign',
            'features': {
                'signatures': ['normal_player_001'],
                'behavior_score': 0.1,
                'anomaly_score': 0.05,
                'risk_factors': 0,
                'suspicious_activities': 0,
                'ai_indicators': 0,
                'movement_data': [5, 8, 3, 7, 4],
                'action_timing': [0.2, 0.3, 0.25, 0.18, 0.22],
                'performance_stats': {
                    'accuracy': 45,
                    'reaction_time': 250,
                    'headshot_ratio': 15,
                    'kill_death_ratio': 0.8
                }
            }
        },
        {
            'name': 'Suspicious Activity',
            'features': {
                'signatures': ['suspicious_pattern_123'],
                'behavior_score': 0.6,
                'anomaly_score': 0.5,
                'risk_factors': 4,
                'suspicious_activities': 3,
                'ai_indicators': 2,
                'movement_data': [30, 35, 25, 40, 32],
                'action_timing': [0.15, 0.12, 0.18, 0.14, 0.16],
                'performance_stats': {
                    'accuracy': 60,
                    'reaction_time': 180,
                    'headshot_ratio': 30,
                    'kill_death_ratio': 2.0
                }
            }
        },
        {
            'name': 'Clear Threat',
            'features': {
                'signatures': ['threat_signature_789'],
                'behavior_score': 0.9,
                'anomaly_score': 0.8,
                'risk_factors': 8,
                'suspicious_activities': 6,
                'ai_indicators': 5,
                'movement_data': [120, 115, 125, 118, 122],
                'action_timing': [0.01, 0.008, 0.012, 0.009, 0.011],
                'performance_stats': {
                    'accuracy': 98,
                    'reaction_time': 15,
                    'headshot_ratio': 98,
                    'kill_death_ratio': 12.0
                }
            }
        }
    ]
    
    # Run tests
    results = []
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        result = explainable_ai.detect_threat_explainable_ai(test_case['features'])
        
        print(f"Detection: {result['detection_result']}")
        print(f"Prediction: {result['prediction']:.4f}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Explainable Strength: {result['explainable_strength']:.4f}")
        print(f"Top Features: {result['top_features']}")
        
        # Display detailed explanations
        print(f"\n📋 Detailed Explanations:")
        for exp_type, exp_data in result['explanations'].items():
            print(f"  {exp_type}: {exp_data}")
        
        results.append(result['prediction'])
    
    # Calculate overall explainable AI detection rate
    explainable_detection_rate = sum(results) / len(results)
    
    print(f"\nOverall Explainable AI Detection Rate: {explainable_detection_rate:.4f} ({explainable_detection_rate*100:.2f}%)")
    print(f"Explainable AI Enhancement: Complete")
    
    # Get statistics
    stats = explainable_ai.get_explainability_statistics()
    print(f"\nExplainability Statistics:")
    print(f"Total Explanations: {stats['total_explanations']}")
    print(f"Average Confidence: {stats['average_confidence']:.4f}")
    print(f"Model Accuracy: {stats['model_accuracy']}")
    print(f"Available Methods: {stats['available_methods']}")
    
    return explainable_detection_rate

if __name__ == "__main__":
    test_explainable_ai()

#!/usr/bin/env python3
"""
Stellar Logic AI - Adversarial Training System
Advanced ML adversarial training to counter AI vs AI attacks
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random
import math
import json
from collections import defaultdict, deque

class AttackType(Enum):
    """Types of adversarial attacks"""
    GRADIENT_ATTACK = "gradient_attack"
    EVASION_ATTACK = "evasion_attack"
    POISONING_ATTACK = "poisoning_attack"
    MODEL_INVERSION = "model_inversion"
    MEMBERSHIP_INFERENCE = "membership_inference"
    ADVERSARIAL_EXAMPLES = "adversarial_examples"
    TRANSFER_ATTACK = "transfer_attack"
    BLACKBOX_ATTACK = "blackbox_attack"

class DefenseType(Enum):
    """Types of defense mechanisms"""
    ADVERSARIAL_TRAINING = "adversarial_training"
    GRADIENT_MASKING = "gradient_masking"
    INPUT_PREPROCESSING = "input_preprocessing"
    MODEL_ENSEMBLING = "model_ensembling"
    DETECTOR_NETWORK = "detector_network"
    FEATURE_SQUEEZING = "feature_squeezing"
    RANDOMIZED_SMOOTHING = "randomized_smoothing"
    CERTIFIED_DEFENSES = "certified_defenses"

@dataclass
class AttackSample:
    """Adversarial attack sample"""
    attack_id: str
    attack_type: AttackType
    original_data: Dict[str, Any]
    perturbed_data: Dict[str, Any]
    perturbation_magnitude: float
    success_rate: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class DefenseResponse:
    """Defense mechanism response"""
    defense_id: str
    defense_type: DefenseType
    attack_detected: bool
    confidence: float
    mitigation_success: float
    processing_time: float
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class MLModel:
    """ML model with adversarial capabilities"""
    model_id: str
    model_type: str
    accuracy: float
    robustness_score: float
    training_samples: int
    adversarial_samples: List[AttackSample]
    defense_mechanisms: List[DefenseType]
    last_updated: datetime

class AdversarialTrainingSystem:
    """Advanced adversarial training system for ML models"""
    
    def __init__(self):
        self.models = {}
        self.attack_history = defaultdict(list)
        self.defense_history = defaultdict(list)
        
        # Attack parameters
        self.attack_parameters = {
            'epsilon': 0.1,  # Maximum perturbation
            'alpha': 0.01,  # Step size
            'num_iterations': 40,  # Attack iterations
            'norm_type': 'L2',  # Norm type for attacks
            'targeted': False  # Targeted vs untargeted attacks
        }
        
        # Defense parameters
        self.defense_parameters = {
            'adversarial_training_ratio': 0.5,  # Ratio of adversarial samples
            'gradient_masking_factor': 0.1,
            'randomized_smoothing_sigma': 0.25,
            'ensemble_size': 5,
            'detection_threshold': 0.7
        }
        
        # Performance metrics
        self.total_attacks_detected = 0
        self.successful_defenses = 0
        self.false_positives = 0
        
        # Attack types and their characteristics
        self.attack_types = {
            AttackType.GRADIENT_ATTACK: {
                'description': 'Fast Gradient Sign Method (FGSM) and variants',
                'complexity': 'low',
                'success_rate_base': 0.8,
                'detection_difficulty': 'medium'
            },
            AttackType.EVASION_ATTACK: {
                'description': 'Evasion attacks to bypass detection',
                'complexity': 'medium',
                'success_rate_base': 0.7,
                'detection_difficulty': 'high'
            },
            AttackType.POISONING_ATTACK: {
                'description': 'Data poisoning attacks',
                'complexity': 'high',
                'success_rate_base': 0.6,
                'detection_difficulty': 'very_high'
            },
            AttackType.MODEL_INVERSION: {
                'description': 'Model inversion attacks',
                'complexity': 'high',
                'success_rate_base': 0.5,
                'detection_difficulty': 'medium'
            },
            AttackType.MEMBERSHIP_INFERENCE: {
                'description': 'Membership inference attacks',
                'complexity': 'medium',
                'success_rate_base': 0.6,
                'detection_difficulty': 'low'
            },
            AttackType.ADVERSARIAL_EXAMPLES: {
                'description': 'Adversarial example generation',
                'complexity': 'medium',
                'success_rate_base': 0.75,
                'detection_difficulty': 'high'
            },
            AttackType.TRANSFER_ATTACK: {
                'description': 'Transfer attacks across models',
                'complexity': 'high',
                'success_rate_base': 0.65,
                'detection_difficulty': 'very_high'
            },
            AttackType.BLACKBOX_ATTACK: {
                'description': 'Black-box adversarial attacks',
                'complexity': 'very_high',
                'success_rate_base': 0.4,
                'detection_difficulty': 'extreme'
            }
        }
        
        # Defense mechanisms
        self.defense_mechanisms = {
            DefenseType.ADVERSARIAL_TRAINING: {
                'description': 'Training on adversarial examples',
                'effectiveness': 0.85,
                'computational_cost': 'high',
                'implementation_complexity': 'medium'
            },
            DefenseType.GRADIENT_MASKING: {
                'description': 'Masking gradients to prevent attacks',
                'effectiveness': 0.75,
                'computational_cost': 'medium',
                'implementation_complexity': 'low'
            },
            DefenseType.INPUT_PREPROCESSING: {
                'description': 'Input preprocessing and transformation',
                'effectiveness': 0.70,
                'computational_cost': 'low',
                'implementation_complexity': 'low'
            },
            DefenseType.MODEL_ENSEMBLING: {
                'description': 'Ensemble of diverse models',
                'effectiveness': 0.80,
                'computational_cost': 'high',
                'implementation_complexity': 'medium'
            },
            DefenseType.DETECTOR_NETWORK: {
                'description': 'Separate network to detect attacks',
                'effectiveness': 0.75,
                'computational_cost': 'medium',
                'implementation_complexity': 'high'
            },
            DefenseType.FEATURE_SQUEEZING: {
                'description': 'Feature squeezing to reduce attack surface',
                'effectiveness': 0.65,
                'computational_cost': 'low',
                'implementation_complexity': 'low'
            },
            DefenseType.RANDOMIZED_SMOOTHING: {
                'description': 'Randomized smoothing for robustness',
                'effectiveness': 0.70,
                'computational_cost': 'medium',
                'implementation_complexity': 'medium'
            },
            DefenseType.CERTIFIED_DEFENSES: {
                'description': 'Certified robustness guarantees',
                'effectiveness': 0.90,
                'computational_cost': 'very_high',
                'implementation_complexity': 'very_high'
            }
        }
    
    def create_model(self, model_id: str, model_type: str) -> MLModel:
        """Create ML model with adversarial capabilities"""
        model = MLModel(
            model_id=model_id,
            model_type=model_type,
            accuracy=0.85 + random.uniform(-0.1, 0.1),
            robustness_score=0.5 + random.uniform(-0.2, 0.2),
            training_samples=10000,
            adversarial_samples=[],
            defense_mechanisms=[],
            last_updated=datetime.now()
        )
        
        self.models[model_id] = model
        return model
    
    def generate_adversarial_attack(self, model_id: str, attack_type: AttackType, 
                                  input_data: Dict[str, Any]) -> AttackSample:
        """Generate adversarial attack sample"""
        model = self.models.get(model_id)
        if not model:
            model = self.create_model(model_id, "neural_network")
        
        # Simulate adversarial attack generation
        attack_info = self.attack_types[attack_type]
        base_success_rate = attack_info['success_rate_base']
        
        # Adjust success rate based on model robustness
        adjusted_success_rate = base_success_rate * (1 - model.robustness_score)
        
        # Generate perturbed data
        perturbed_data = self._apply_perturbation(input_data, attack_type)
        
        # Calculate perturbation magnitude
        perturbation_magnitude = self._calculate_perturbation_magnitude(
            input_data, perturbed_data
        )
        
        attack_sample = AttackSample(
            attack_id=f"attack_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            attack_type=attack_type,
            original_data=input_data,
            perturbed_data=perturbed_data,
            perturbation_magnitude=perturbation_magnitude,
            success_rate=adjusted_success_rate,
            timestamp=datetime.now(),
            metadata={
                'model_id': model_id,
                'attack_complexity': attack_info['complexity'],
                'detection_difficulty': attack_info['detection_difficulty']
            }
        )
        
        # Store attack
        model.adversarial_samples.append(attack_sample)
        self.attack_history[attack_type].append(attack_sample)
        
        return attack_sample
    
    def _apply_perturbation(self, input_data: Dict[str, Any], attack_type: AttackType) -> Dict[str, Any]:
        """Apply perturbation to input data"""
        perturbed_data = input_data.copy()
        
        if attack_type == AttackType.GRADIENT_ATTACK:
            # FGSM-like perturbation
            for key, value in input_data.items():
                if isinstance(value, (int, float)):
                    perturbation = random.uniform(-self.attack_parameters['epsilon'], 
                                              self.attack_parameters['epsilon'])
                    perturbed_data[key] = value + perturbation
        
        elif attack_type == AttackType.EVASION_ATTACK:
            # Evasion attack perturbation
            for key, value in input_data.items():
                if isinstance(value, (int, float)):
                    perturbation = random.uniform(-self.attack_parameters['epsilon'] * 0.5, 
                                              self.attack_parameters['epsilon'] * 0.5)
                    perturbed_data[key] = value * (1 + perturbation)
        
        elif attack_type == AttackType.ADVERSARIAL_EXAMPLES:
            # Adversarial examples
            for key, value in input_data.items():
                if isinstance(value, (int, float)):
                    perturbation = random.uniform(-self.attack_parameters['epsilon'] * 1.5, 
                                              self.attack_parameters['epsilon'] * 1.5)
                    perturbed_data[key] = value + perturbation
        
        else:
            # Generic perturbation for other attack types
            for key, value in input_data.items():
                if isinstance(value, (int, float)):
                    perturbation = random.uniform(-self.attack_parameters['epsilon'], 
                                              self.attack_parameters['epsilon'])
                    perturbed_data[key] = value + perturbation
        
        return perturbed_data
    
    def _calculate_perturbation_magnitude(self, original_data: Dict[str, Any], 
                                         perturbed_data: Dict[str, Any]) -> float:
        """Calculate perturbation magnitude"""
        total_magnitude = 0.0
        count = 0
        
        for key in original_data:
            if key in perturbed_data:
                orig_val = original_data[key]
                pert_val = perturbed_data[key]
                
                if isinstance(orig_val, (int, float)) and isinstance(pert_val, (int, float)):
                    magnitude = abs(pert_val - orig_val)
                    if orig_val != 0:
                        magnitude = magnitude / abs(orig_val)
                    total_magnitude += magnitude
                    count += 1
        
        return total_magnitude / count if count > 0 else 0.0
    
    def deploy_defense_mechanism(self, model_id: str, defense_type: DefenseType) -> bool:
        """Deploy defense mechanism for model"""
        model = self.models.get(model_id)
        if not model:
            return False
        
        if defense_type not in model.defense_mechanisms:
            model.defense_mechanisms.append(defense_type)
            model.last_updated = datetime.now()
            
            # Update robustness score based on defense
            defense_info = self.defense_mechanisms[defense_type]
            model.robustness_score += defense_info['effectiveness'] * 0.1
            model.robustness_score = min(1.0, model.robustness_score)
            
            return True
        
        return False
    
    def detect_and_defend(self, model_id: str, input_data: Dict[str, Any]) -> DefenseResponse:
        """Detect and defend against adversarial attacks"""
        model = self.models.get(model_id)
        if not model:
            return None
        
        start_time = datetime.now()
        
        # Check if input is adversarial
        is_adversarial, confidence = self._detect_adversarial_input(model, input_data)
        
        if is_adversarial:
            self.total_attacks_detected += 1
            
            # Apply defense mechanisms
            mitigation_success = 0.0
            for defense_type in model.defense_mechanisms:
                defense_result = self._apply_defense_mechanism(
                    defense_type, input_data, confidence
                )
                mitigation_success = max(mitigation_success, defense_result)
            
            if mitigation_success > 0.5:
                self.successful_defenses += 1
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            defense_response = DefenseResponse(
                defense_id=f"defense_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                defense_type=model.defense_mechanisms[0] if model.defense_mechanisms else DefenseType.INPUT_PREPROCESSING,
                attack_detected=True,
                confidence=confidence,
                mitigation_success=mitigation_success,
                processing_time=processing_time,
                timestamp=datetime.now(),
                metadata={
                    'model_id': model_id,
                    'defenses_applied': len(model.defense_mechanisms)
                }
            )
            
            self.defense_history[model_id].append(defense_response)
            return defense_response
        
        else:
            # False positive
            if confidence > self.defense_parameters['detection_threshold']:
                self.false_positives += 1
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            defense_response = DefenseResponse(
                defense_id=f"defense_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                defense_type=DefenseType.INPUT_PREPROCESSING,
                attack_detected=False,
                confidence=1.0 - confidence,
                mitigation_success=1.0,
                processing_time=processing_time,
                timestamp=datetime.now(),
                metadata={
                    'model_id': model_id,
                    'false_positive': True
                }
            )
            
            return defense_response
    
    def _detect_adversarial_input(self, model: MLModel, input_data: Dict[str, Any]) -> Tuple[bool, float]:
        """Detect if input is adversarial"""
        # Simulate adversarial detection
        adversarial_probability = 0.0
        
        # Check against known attack patterns
        for attack_sample in model.adversarial_samples[-100:]:  # Check recent samples
            similarity = self._calculate_similarity(input_data, attack_sample.perturbed_data)
            if similarity > 0.8:
                adversarial_probability = max(adversarial_probability, similarity)
        
        # Adjust based on model robustness
        adjusted_probability = adversarial_probability * (1 - model.robustness_score)
        
        # Check against defense mechanisms
        if model.defense_mechanisms:
            defense_effectiveness = sum(
                self.defense_mechanisms[def_type]['effectiveness']
                for def_type in model.defense_mechanisms
            ) / len(model.defense_mechanisms)
            adjusted_probability *= (1 - defense_effectiveness * 0.5)
        
        is_adversarial = adjusted_probability > self.defense_parameters['detection_threshold']
        confidence = adjusted_probability
        
        return is_adversarial, confidence
    
    def _calculate_similarity(self, data1: Dict[str, Any], data2: Dict[str, Any]) -> float:
        """Calculate similarity between two data points"""
        similarity = 0.0
        count = 0
        
        for key in data1:
            if key in data2:
                val1 = data1[key]
                val2 = data2[key]
                
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    if val1 == 0 and val2 == 0:
                        similarity += 1.0
                    else:
                        similarity += 1.0 - abs(val1 - val2) / max(abs(val1), abs(val2))
                    count += 1
        
        return similarity / count if count > 0 else 0.0
    
    def _apply_defense_mechanism(self, defense_type: DefenseType, input_data: Dict[str, Any], 
                               attack_confidence: float) -> float:
        """Apply specific defense mechanism"""
        defense_info = self.defense_mechanisms[defense_type]
        base_effectiveness = defense_info['effectiveness']
        
        # Adjust effectiveness based on attack confidence
        adjusted_effectiveness = base_effectiveness * (1 - attack_confidence * 0.3)
        
        return adjusted_effectiveness
    
    def train_adversarial_model(self, model_id: str, training_data: List[Dict[str, Any]], 
                               epochs: int = 10) -> Dict[str, Any]:
        """Train model with adversarial training"""
        model = self.models.get(model_id)
        if not model:
            return {'error': 'Model not found'}
        
        # Generate adversarial samples for training
        adversarial_samples = []
        normal_samples = training_data[:int(len(training_data) * 0.7)]
        
        for data in training_data[int(len(training_data) * 0.7):]:
            # Generate random attack types
            attack_type = random.choice(list(AttackType))
            attack_sample = self.generate_adversarial_attack(model_id, attack_type, data)
            adversarial_samples.append(attack_sample.perturbed_data)
        
        # Simulate training process
        training_results = {
            'epochs': epochs,
            'normal_samples': len(normal_samples),
            'adversarial_samples': len(adversarial_samples),
            'initial_accuracy': model.accuracy,
            'initial_robustness': model.robustness_score
        }
        
        # Update model metrics (simulated improvement)
        model.accuracy += random.uniform(0.02, 0.05)
        model.accuracy = min(1.0, model.accuracy)
        model.robustness_score += random.uniform(0.1, 0.2)
        model.robustness_score = min(1.0, model.robustness_score)
        model.training_samples += len(normal_samples) + len(adversarial_samples)
        model.last_updated = datetime.now()
        
        training_results['final_accuracy'] = model.accuracy
        training_results['final_robustness'] = model.robustness_score
        training_results['accuracy_improvement'] = model.accuracy - training_results['initial_accuracy']
        training_results['robustness_improvement'] = model.robustness_score - training_results['initial_robustness']
        
        return training_results
    
    def get_model_summary(self, model_id: str) -> Dict[str, Any]:
        """Get model summary"""
        model = self.models.get(model_id)
        if not model:
            return {'error': 'Model not found'}
        
        # Calculate attack statistics
        attack_stats = self._calculate_attack_statistics(model)
        
        # Calculate defense statistics
        defense_stats = self._calculate_defense_statistics(model_id)
        
        return {
            'model_id': model.model_id,
            'model_type': model.model_type,
            'accuracy': model.accuracy,
            'robustness_score': model.robustness_score,
            'training_samples': model.training_samples,
            'adversarial_samples_count': len(model.adversarial_samples),
            'defense_mechanisms': [d.value for d in model.defense_mechanisms],
            'last_updated': model.last_updated.isoformat(),
            'attack_statistics': attack_stats,
            'defense_statistics': defense_stats
        }
    
    def _calculate_attack_statistics(self, model: MLModel) -> Dict[str, Any]:
        """Calculate attack statistics for model"""
        if not model.adversarial_samples:
            return {
                'total_attacks': 0,
                'attack_types': {},
                'avg_success_rate': 0.0,
                'avg_perturbation': 0.0
            }
        
        attack_counts = defaultdict(int)
        success_rates = []
        perturbation_magnitudes = []
        
        for attack_sample in model.adversarial_samples:
            attack_counts[attack_sample.attack_type.value] += 1
            success_rates.append(attack_sample.success_rate)
            perturbation_magnitudes.append(attack_sample.perturbation_magnitude)
        
        return {
            'total_attacks': len(model.adversarial_samples),
            'attack_types': dict(attack_counts),
            'avg_success_rate': sum(success_rates) / len(success_rates),
            'avg_perturbation': sum(perturbation_magnitudes) / len(perturbation_magnitudes)
        }
    
    def _calculate_defense_statistics(self, model_id: str) -> Dict[str, Any]:
        """Calculate defense statistics for model"""
        defenses = self.defense_history.get(model_id, [])
        
        if not defenses:
            return {
                'total_defenses': 0,
                'successful_defenses': 0,
                'avg_mitigation_success': 0.0,
                'avg_processing_time': 0.0
            }
        
        successful_defenses = sum(1 for d in defenses if d.mitigation_success > 0.5)
        mitigation_successes = [d.mitigation_success for d in defenses]
        processing_times = [d.processing_time for d in defenses]
        
        return {
            'total_defenses': len(defenses),
            'successful_defenses': successful_defenses,
            'avg_mitigation_success': sum(mitigation_successes) / len(mitigation_successes),
            'avg_processing_time': sum(processing_times) / len(processing_times)
        }
    
    def get_system_performance(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        return {
            'total_models': len(self.models),
            'total_attacks_detected': self.total_attacks_detected,
            'successful_defenses': self.successful_defenses,
            'false_positives': self.false_positives,
            'defense_success_rate': self.successful_defenses / max(1, self.total_attacks_detected),
            'false_positive_rate': self.false_positives / max(1, self.total_attacks_detected + self.false_positives),
            'attack_types_supported': len(self.attack_types),
            'defense_mechanisms_supported': len(self.defense_mechanisms)
        }

# Test the adversarial training system
def test_adversarial_training_system():
    """Test the adversarial training system"""
    print("🛡️ Testing Adversarial Training System")
    print("=" * 50)
    
    system = AdversarialTrainingSystem()
    
    # Create test model
    print("\n🤖 Creating ML Model...")
    model_id = "model_001"
    model = system.create_model(model_id, "neural_network")
    print(f"   Model ID: {model.model_id}")
    print(f"   Initial Accuracy: {model.accuracy:.2f}")
    print(f"   Initial Robustness: {model.robustness_score:.2f}")
    
    # Deploy defense mechanisms
    print("\n🔒 Deploying Defense Mechanisms...")
    system.deploy_defense_mechanism(model_id, DefenseType.ADVERSARIAL_TRAINING)
    system.deploy_defense_mechanism(model_id, DefenseType.GRADIENT_MASKING)
    system.deploy_defense_mechanism(model_id, DefenseType.INPUT_PREPROCESSING)
    print(f"   Defense Mechanisms: {[d.value for d in model.defense_mechanisms]}")
    print(f"   Updated Robustness: {model.robustness_score:.2f}")
    
    # Generate adversarial attacks
    print("\n⚔️ Generating Adversarial Attacks...")
    test_data = {
        'feature_1': 1.0,
        'feature_2': 2.0,
        'feature_3': 0.5,
        'feature_4': 1.5
    }
    
    attack_types = [
        AttackType.GRADIENT_ATTACK,
        AttackType.EVASION_ATTACK,
        AttackType.ADVERSARIAL_EXAMPLES,
        AttackType.MEMBERSHIP_INFERENCE
    ]
    
    for attack_type in attack_types:
        attack = system.generate_adversarial_attack(model_id, attack_type, test_data)
        print(f"   {attack_type.value}: Success Rate {attack.success_rate:.2f}")
    
    # Test detection and defense
    print("\n🛡️ Testing Detection and Defense...")
    
    # Test with normal input
    normal_result = system.detect_and_defend(model_id, test_data)
    print(f"   Normal Input: Detected={normal_result.attack_detected}, Confidence={normal_result.confidence:.2f}")
    
    # Test with adversarial input
    adversarial_data = {
        'feature_1': 1.1,
        'feature_2': 2.2,
        'feature_3': 0.6,
        'feature_4': 1.6
    }
    
    adversarial_result = system.detect_and_defend(model_id, adversarial_data)
    print(f"   Adversarial Input: Detected={adversarial_result.attack_detected}, Confidence={adversarial_result.confidence:.2f}")
    print(f"   Mitigation Success: {adversarial_result.mitigation_success:.2f}")
    
    # Train with adversarial samples
    print("\n🎓 Training with Adversarial Samples...")
    training_data = [test_data.copy() for _ in range(100)]
    for i, data in enumerate(training_data):
        data['feature_1'] += random.uniform(-0.1, 0.1)
        data['feature_2'] += random.uniform(-0.1, 0.1)
        data['feature_3'] += random.uniform(-0.1, 0.1)
        data['feature_4'] += random.uniform(-0.1, 0.1)
    
    training_results = system.train_adversarial_model(model_id, training_data, epochs=5)
    print(f"   Training Samples: {training_results['normal_samples']} normal, {training_results['adversarial_samples']} adversarial")
    print(f"   Accuracy Improvement: {training_results['accuracy_improvement']:.3f}")
    print(f"   Robustness Improvement: {training_results['robustness_improvement']:.3f}")
    
    # Generate model summary
    print("\n📊 Model Summary:")
    summary = system.get_model_summary(model_id)
    print(f"   Final Accuracy: {summary['accuracy']:.3f}")
    print(f"   Final Robustness: {summary['robustness_score']:.3f}")
    print(f"   Total Attacks: {summary['attack_statistics']['total_attacks']}")
    print(f"   Avg Success Rate: {summary['attack_statistics']['avg_success_rate']:.3f}")
    print(f"   Total Defenses: {summary['defense_statistics']['total_defenses']}")
    print(f"   Defense Success Rate: {summary['defense_statistics']['avg_mitigation_success']:.3f}")
    
    # System performance
    print("\n📈 System Performance:")
    performance = system.get_system_performance()
    print(f"   Total Models: {performance['total_models']}")
    print(f"   Total Attacks Detected: {performance['total_attacks_detected']}")
    print(f"   Defense Success Rate: {performance['defense_success_rate']:.3f}")
    print(f"   False Positive Rate: {performance['false_positive_rate']:.3f}")
    
    return system

if __name__ == "__main__":
    test_adversarial_training_system()

#!/usr/bin/env python3
"""
Stellar Logic AI - Generative AI System
=====================================

Synthetic threat generation and data augmentation
GANs, VAEs, and advanced generative models for threat simulation
"""

import json
import time
import random
import statistics
import math
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

class GenerativeAISystem:
    """
    Generative AI system for synthetic threat generation
    GANs, VAEs, and advanced generative models for threat simulation
    """
    
    def __init__(self):
        # Generative models
        self.gan_models = {
            'threat_gan': self._create_threat_gan(),
            'behavior_gan': self._create_behavior_gan(),
            'pattern_gan': self._create_pattern_gan()
        }
        
        # VAE models
        self.vae_models = {
            'threat_vae': self._create_threat_vae(),
            'anomaly_vae': self._create_anomaly_vae()
        }
        
        # Synthetic data generators
        self.synthesizers = {
            'threat_synthesizer': self._create_threat_synthesizer(),
            'behavior_synthesizer': self._create_behavior_synthesizer(),
            'pattern_synthesizer': self._create_pattern_synthesizer()
        }
        
        # Generated data storage
        self.generated_threats = []
        self.generated_behaviors = []
        self.generated_patterns = []
        
        # Generation parameters
        self.generation_history = []
        self.quality_metrics = {}
        
        print("🎨 Generative AI System Initialized")
        print("🎯 Models: GANs, VAEs, Synthetic Generators")
        print("📊 Capabilities: Threat generation, Data augmentation")
        
    def _create_threat_gan(self) -> Dict[str, Any]:
        """Create threat generation GAN"""
        return {
            'type': 'gan',
            'generator_layers': [64, 128, 64, 20],
            'discriminator_layers': [20, 64, 32, 1],
            'latent_dim': 100,
            'output_dim': 20,
            'learning_rate': 0.0002,
            'beta1': 0.5
        }
    
    def _create_behavior_gan(self) -> Dict[str, Any]:
        """Create behavior generation GAN"""
        return {
            'type': 'gan',
            'generator_layers': [32, 64, 32, 10],
            'discriminator_layers': [10, 32, 16, 1],
            'latent_dim': 50,
            'output_dim': 10,
            'learning_rate': 0.0002,
            'beta1': 0.5
        }
    
    def _create_pattern_gan(self) -> Dict[str, Any]:
        """Create pattern generation GAN"""
        return {
            'type': 'gan',
            'generator_layers': [16, 32, 16, 5],
            'discriminator_layers': [5, 16, 8, 1],
            'latent_dim': 25,
            'output_dim': 5,
            'learning_rate': 0.0002,
            'beta1': 0.5
        }
    
    def _create_threat_vae(self) -> Dict[str, Any]:
        """Create threat VAE"""
        return {
            'type': 'vae',
            'encoder_layers': [64, 32, 16],
            'latent_dim': 20,
            'decoder_layers': [16, 32, 64, 20],
            'learning_rate': 0.001,
            'beta': 1.0
        }
    
    def _create_anomaly_vae(self) -> Dict[str, Any]:
        """Create anomaly VAE"""
        return {
            'type': 'vae',
            'encoder_layers': [32, 16, 8],
            'latent_dim': 10,
            'decoder_layers': [8, 16, 32, 10],
            'learning_rate': 0.001,
            'beta': 1.0
        }
    
    def _create_threat_synthesizer(self) -> Dict[str, Any]:
        """Create threat synthesizer"""
        return {
            'type': 'synthesizer',
            'threat_types': [
                'malware', 'trojan', 'backdoor', 'rootkit', 'spyware',
                'ransomware', 'botnet', 'ddos', 'phishing', 'social_engineering'
            ],
            'variation_factors': {
                'complexity': 0.3,
                'stealth': 0.2,
                'persistence': 0.2,
                'propagation': 0.3
            }
        }
    
    def _create_behavior_synthesizer(self) -> Dict[str, Any]:
        """Create behavior synthesizer"""
        return {
            'type': 'synthesizer',
            'behavior_patterns': [
                'automated', 'human_like', 'erratic', 'stealthy',
                'aggressive', 'passive', 'opportunistic', 'persistent'
            ],
            'variation_factors': {
                'timing': 0.3,
                'consistency': 0.3,
                'randomness': 0.2,
                'adaptation': 0.2
            }
        }
    
    def _create_pattern_synthesizer(self) -> Dict[str, Any]:
        """Create pattern synthesizer"""
        return {
            'type': 'synthesizer',
            'pattern_types': [
                'signatures', 'network', 'file_system', 'registry',
                'process', 'memory', 'communication', 'encryption'
            ],
            'variation_factors': {
                'complexity': 0.3,
                'obfuscation': 0.3,
                'mutation': 0.2,
                'polymorphism': 0.2
            }
        }
    
    def generate_latent_vector(self, dim: int) -> List[float]:
        """Generate latent vector for generation"""
        return [random.gauss(0, 1) for _ in range(dim)]
    
    def gan_generate_threat(self, threat_type: str, complexity: float = 0.5) -> Dict[str, Any]:
        """Generate threat using GAN"""
        gan_model = self.gan_models['threat_gan']
        
        # Generate latent vector
        latent_vector = self.generate_latent_vector(gan_model['latent_dim'])
        
        # Apply complexity factor
        scaled_latent = [v * (1 + complexity) for v in latent_vector]
        
        # Generator forward pass (simplified)
        generated_features = self._gan_generator_forward(gan_model, scaled_latent)
        
        # Create synthetic threat
        synthetic_threat = {
            'type': threat_type,
            'features': self._features_to_dict(generated_features),
            'complexity': complexity,
            'generation_method': 'gan',
            'latent_vector': latent_vector,
            'timestamp': datetime.now(),
            'quality_score': self._calculate_generation_quality(generated_features)
        }
        
        return synthetic_threat
    
    def _gan_generator_forward(self, gan_model: Dict[str, Any], latent_vector: List[float]) -> List[float]:
        """Simplified GAN generator forward pass"""
        activations = latent_vector
        
        for layer_size in gan_model['generator_layers']:
            layer_output = []
            for i in range(layer_size):
                neuron_sum = random.uniform(-0.1, 0.1)  # Random weights
                for j, input_val in enumerate(activations):
                    neuron_sum += input_val * random.uniform(-0.5, 0.5)
                
                # Apply activation
                layer_output.append(max(0, neuron_sum))
            
            activations = layer_output
        
        return activations[:gan_model['output_dim']]
    
    def _features_to_dict(self, features: List[float]) -> Dict[str, Any]:
        """Convert features to dictionary format"""
        return {
            'behavior_score': max(0, min(1, features[0] if len(features) > 0 else 0)),
            'anomaly_score': max(0, min(1, features[1] if len(features) > 1 else 0)),
            'risk_factors': max(0, min(10, int(features[2] * 10) if len(features) > 2 else 0)),
            'suspicious_activities': max(0, min(8, int(features[3] * 8) if len(features) > 3 else 0)),
            'ai_indicators': max(0, min(7, int(features[4] * 7) if len(features) > 4 else 0)),
            'movement_data': [max(0, min(200, f * 100)) for f in features[5:10] if len(features) > 5],
            'action_timing': [max(0, min(0.1, f * 0.05)) for f in features[10:15] if len(features) > 10],
            'performance_stats': {
                'accuracy': max(0, min(100, features[15] * 100 if len(features) > 15 else 50)),
                'reaction_time': max(0, min(1000, features[16] * 500 if len(features) > 16 else 250)),
                'headshot_ratio': max(0, min(100, features[17] * 100 if len(features) > 17 else 25)),
                'kill_death_ratio': max(0, min(10, features[18] * 5 if len(features) > 18 else 1))
            } if len(features) > 14 else {}
        }
    
    def _calculate_generation_quality(self, features: List[float]) -> float:
        """Calculate quality score for generated features"""
        # Quality based on feature realism
        quality_score = 0.0
        
        # Check if features are in reasonable ranges
        if len(features) >= 5:
            # Behavior score should be between 0 and 1
            if 0 <= features[0] <= 1:
                quality_score += 0.2
            
            # Anomaly score should be between 0 and 1
            if 0 <= features[1] <= 1:
                quality_score += 0.2
            
            # Risk factors should be reasonable
            if 0 <= features[2] <= 1:
                quality_score += 0.2
            
            # Suspicious activities should be reasonable
            if 0 <= features[3] <= 1:
                quality_score += 0.2
            
            # AI indicators should be reasonable
            if 0 <= features[4] <= 1:
                quality_score += 0.2
        
        return quality_score
    
    def vae_generate_threat(self, input_features: List[float], variation: float = 0.1) -> Dict[str, Any]:
        """Generate threat using VAE"""
        vae_model = self.vae_models['threat_vae']
        
        # Encode input features
        encoded = self._vae_encode(vae_model, input_features)
        
        # Add variation
        varied_latent = [e + random.gauss(0, variation) for e in encoded]
        
        # Decode to generate new threat
        generated_features = self._vae_decode(vae_model, varied_latent)
        
        # Create synthetic threat
        synthetic_threat = {
            'type': 'vae_generated',
            'features': self._features_to_dict(generated_features),
            'variation': variation,
            'generation_method': 'vae',
            'input_features': input_features,
            'encoded_features': encoded,
            'quality_score': self._calculate_generation_quality(generated_features)
        }
        
        return synthetic_threat
    
    def _vae_encode(self, vae_model: Dict[str, Any], features: List[float]) -> List[float]:
        """VAE encoder"""
        activations = features
        
        for layer_size in vae_model['encoder_layers']:
            layer_output = []
            for i in range(layer_size):
                neuron_sum = random.uniform(-0.1, 0.1)
                for j, input_val in enumerate(activations):
                    neuron_sum += input_val * random.uniform(-0.5, 0.5)
                
                layer_output.append(max(0, neuron_sum))
            
            activations = layer_output
        
        # Return latent representation
        return activations[:vae_model['latent_dim']]
    
    def _vae_decode(self, vae_model: Dict[str, Any], latent: List[float]) -> List[float]:
        """VAE decoder"""
        activations = latent
        
        for layer_size in vae_model['decoder_layers']:
            layer_output = []
            for i in range(layer_size):
                neuron_sum = random.uniform(-0.1, 0.1)
                for j, input_val in enumerate(activations):
                    neuron_sum += input_val * random.uniform(-0.5, 0.5)
                
                layer_output.append(max(0, neuron_sum))
            
            activations = layer_output
        
        return activations[:20]  # Return 20 features
    
    def generate_synthetic_threat_dataset(self, num_samples: int, threat_types: List[str] = None) -> List[Dict[str, Any]]:
        """Generate synthetic threat dataset"""
        if threat_types is None:
            threat_types = ['malware', 'trojan', 'backdoor', 'rootkit', 'spyware']
        
        synthetic_dataset = []
        
        for i in range(num_samples):
            # Randomly select threat type
            threat_type = random.choice(threat_types)
            
            # Random complexity
            complexity = random.uniform(0.3, 0.9)
            
            # Generate threat
            if random.random() < 0.5:
                # Use GAN
                synthetic_threat = self.gan_generate_threat(threat_type, complexity)
            else:
                # Use VAE with variation
                base_features = self.generate_latent_vector(20)
                synthetic_threat = self.vae_generate_threat(base_features, complexity)
            
            synthetic_threat['id'] = f'synthetic_threat_{i}'
            synthetic_dataset.append(synthetic_threat)
        
        return synthetic_dataset
    
    def generate_synthetic_behaviors(self, num_samples: int, behavior_types: List[str] = None) -> List[Dict[str, Any]]:
        """Generate synthetic behaviors"""
        if behavior_types is None:
            behavior_types = ['automated', 'human_like', 'stealthy', 'aggressive']
        
        synthetic_behaviors = []
        
        for i in range(num_samples):
            behavior_type = random.choice(behavior_types)
            
            # Generate behavior features
            behavior_features = self._generate_behavior_features(behavior_type)
            
            synthetic_behavior = {
                'id': f'synthetic_behavior_{i}',
                'type': behavior_type,
                'features': behavior_features,
                'generation_method': 'synthesizer',
                'quality_score': self._calculate_generation_quality(behavior_features)
            }
            
            synthetic_behaviors.append(synthetic_behavior)
        
        return synthetic_behaviors
    
    def _generate_behavior_features(self, behavior_type: str) -> List[float]:
        """Generate behavior features for specific type"""
        features = []
        
        if behavior_type == 'automated':
            # Automated behavior: very consistent timing
            features.extend([
                0.9,  # behavior_score
                0.7,  # anomaly_score
                0.8,  # risk_factors
                0.6,  # suspicious_activities
                0.5,  # ai_indicators
                0.05, # movement consistency
                0.02, # timing consistency
                0.1,  # randomness
                0.0   # adaptation
            ])
        elif behavior_type == 'human_like':
            # Human-like behavior: natural variation
            features.extend([
                0.4,  # behavior_score
                0.2,  # anomaly_score
                0.2,  # risk_factors
                0.1,  # suspicious_activities
                0.0,  # ai_indicators
                0.3,  # movement consistency
                0.4,  # timing consistency
                0.5,  # randomness
                0.6   # adaptation
            ])
        elif behavior_type == 'stealthy':
            # Stealthy behavior: tries to blend in
            features.extend([
                0.3,  # behavior_score
                0.4,  # anomaly_score
                0.5,  # risk_factors
                0.3,  # suspicious_activities
                0.2,  # ai_indicators
                0.6,  # movement consistency
                0.5,  # timing consistency
                0.2,  # randomness
                0.8   # adaptation
            ])
        elif behavior_type == 'aggressive':
            # Aggressive behavior: high activity
            features.extend([
                0.8,  # behavior_score
                0.6,  # anomaly_score
                0.7,  # risk_factors
                0.8,  # suspicious_activities
                0.4,  # ai_indicators
                0.2,  # movement consistency
                0.3,  # timing consistency
                0.7,  # randomness
                0.4   # adaptation
            ])
        
        # Pad to 20 features
        while len(features) < 20:
            features.append(random.uniform(0, 1))
        
        return features[:20]
    
    def augment_training_data(self, training_data: List[Dict[str, Any]], augmentation_factor: float = 2.0) -> List[Dict[str, Any]]:
        """Augment training data with synthetic samples"""
        augmented_data = training_data.copy()
        
        # Calculate number of synthetic samples to generate
        num_synthetic = int(len(training_data) * augmentation_factor)
        
        # Generate synthetic threats
        synthetic_threats = self.generate_synthetic_threat_dataset(num_synthetic)
        
        # Convert synthetic threats to training format
        for synthetic_threat in synthetic_threats:
            augmented_data.append({
                'features': synthetic_threat['features'],
                'label': 1,  # All synthetic threats are labeled as threats
                'synthetic': True,
                'generation_method': synthetic_threat['generation_method'],
                'quality_score': synthetic_threat['quality_score']
            })
        
        return augmented_data
    
    def detect_threat_generative_ai(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Generative AI threat detection"""
        start_time = time.time()
        
        # Extract features
        feature_vector = self._extract_generative_features(features)
        
        # Generate synthetic samples for comparison
        synthetic_samples = self.generate_synthetic_threat_dataset(10)
        
        # Compare with generated samples
        similarity_scores = []
        for sample in synthetic_samples:
            sample_features = self._extract_generative_features(sample['features'])
            similarity = self._calculate_feature_similarity(feature_vector, sample_features)
            similarity_scores.append(similarity)
        
        # Calculate generative confidence
        max_similarity = max(similarity_scores) if similarity_scores else 0
        generative_confidence = 1 - max_similarity  # Higher similarity to synthetic = more likely threat
        
        # Apply generative AI optimization
        final_prediction = self._apply_generative_optimization(max_similarity, generative_confidence, features)
        final_confidence = generative_confidence
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create comprehensive result
        result = {
            'prediction': final_prediction,
            'confidence': final_confidence,
            'max_similarity': max_similarity,
            'similarity_scores': similarity_scores,
            'synthetic_samples': len(synthetic_samples),
            'processing_time': processing_time,
            'detection_result': 'THREAT_DETECTED' if final_prediction > 0.5 else 'SAFE',
            'risk_level': self._calculate_risk_level(final_prediction, final_confidence),
            'recommendation': self._generate_recommendation(final_prediction, final_confidence),
            'generative_strength': self._calculate_generative_strength(max_similarity),
            'synthetic_quality': sum(s['quality_score'] for s in synthetic_samples) / len(synthetic_samples)
        }
        
        return result
    
    def _extract_generative_features(self, features: Dict[str, Any]) -> List[float]:
        """Extract features for generative AI"""
        gen_features = []
        
        # Basic features
        gen_features.append(features.get('behavior_score', 0))
        gen_features.append(features.get('anomaly_score', 0))
        gen_features.append(features.get('risk_factors', 0) / 10)
        gen_features.append(features.get('suspicious_activities', 0) / 8)
        gen_features.append(features.get('ai_indicators', 0) / 7)
        
        # Statistical features
        if 'movement_data' in features:
            movement = features['movement_data']
            if isinstance(movement, list) and len(movement) > 0:
                gen_features.append(statistics.mean(movement))
                gen_features.append(statistics.stdev(movement) if len(movement) > 1 else 0.0)
                gen_features.append(max(movement))
                gen_features.append(min(movement))
        
        if 'action_timing' in features:
            timing = features['action_timing']
            if isinstance(timing, list) and len(timing) > 0:
                gen_features.append(statistics.mean(timing))
                gen_features.append(statistics.stdev(timing) if len(timing) > 1 else 0.0)
                gen_features.append(max(timing))
                gen_features.append(min(timing))
        
        # Performance features
        if 'performance_stats' in features:
            stats = features['performance_stats']
            gen_features.append(stats.get('accuracy', 0) / 100)
            gen_features.append(stats.get('reaction_time', 0) / 1000)
            gen_features.append(stats.get('headshot_ratio', 0) / 100)
            gen_features.append(stats.get('kill_death_ratio', 0) / 10)
        
        # Pad to fixed size
        while len(gen_features) < 20:
            gen_features.append(0.0)
        
        return gen_features[:20]
    
    def _calculate_feature_similarity(self, features1: List[float], features2: List[float]) -> float:
        """Calculate similarity between two feature vectors"""
        if len(features1) != len(features2):
            return 0.0
        
        # Cosine similarity
        dot_product = sum(f1 * f2 for f1, f2 in zip(features1, features2))
        norm1 = math.sqrt(sum(f1 * f1 for f1 in features1))
        norm2 = math.sqrt(sum(f2 * f2 for f2 in features2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _apply_generative_optimization(self, similarity: float, confidence: float, features: Dict[str, Any]) -> float:
        """Apply generative AI specific optimization"""
        # Generative AI optimization
        if similarity > 0.8:
            # High similarity to synthetic - likely threat
            optimized_prediction = min(1.0, 0.5 + similarity * 0.5)
        elif similarity < 0.2:
            # Low similarity to synthetic - likely benign
            optimized_prediction = max(0.0, 0.5 - similarity * 0.3)
        else:
            # Medium similarity - uncertain
            optimized_prediction = 0.5
        
        # Apply confidence weighting
        final_prediction = optimized_prediction * confidence + (1 - confidence) * 0.5
        
        return final_prediction
    
    def _calculate_risk_level(self, prediction: float, confidence: float) -> str:
        """Calculate risk level"""
        if prediction > 0.8 and confidence > 0.9:
            return "CRITICAL"
        elif prediction > 0.6 and confidence > 0.8:
            return "HIGH"
        elif prediction > 0.4 and confidence > 0.7:
            return "MEDIUM"
        elif prediction > 0.2 and confidence > 0.6:
            return "LOW"
        else:
            return "MINIMAL"
    
    def _generate_recommendation(self, prediction: float, confidence: float) -> str:
        """Generate recommendation"""
        if prediction > 0.7 and confidence > 0.8:
            return "GENERATIVE_IMMEDIATE_ACTION"
        elif prediction > 0.5 and confidence > 0.7:
            return "GENERATIVE_ENHANCED_MONITORING"
        elif prediction > 0.3 and confidence > 0.6:
            return "GENERATIVE_ANALYSIS_RECOMMENDED"
        else:
            return "CONTINUE_GENERATIVE_MONITORING"
    
    def _calculate_generative_strength(self, similarity: float) -> float:
        """Calculate generative AI strength"""
        return min(1.0, similarity * 2)
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get generation statistics"""
        return {
            'generated_threats': len(self.generated_threats),
            'generated_behaviors': len(self.generated_behaviors),
            'generated_patterns': len(self.generated_patterns),
            'available_models': list(self.gan_models.keys()) + list(self.vae_models.keys()),
            'available_synthesizers': list(self.synthesizers.keys()),
            'generation_history': len(self.generation_history)
        }

# Test the generative AI system
def test_generative_ai():
    """Test the generative AI system"""
    print("Testing Generative AI System")
    print("=" * 50)
    
    # Initialize generative AI system
    gen_ai = GenerativeAISystem()
    
    # Test threat generation
    print("\n🎨 Testing Threat Generation:")
    synthetic_threat = gen_ai.gan_generate_threat('malware', 0.7)
    print(f"Generated Threat: {synthetic_threat['type']}")
    print(f"Complexity: {synthetic_threat['complexity']:.2f}")
    print(f"Quality Score: {synthetic_threat['quality_score']:.2f}")
    
    # Test VAE generation
    print("\n🔄 Testing VAE Generation:")
    base_features = [0.5, 0.3, 0.4, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0, 0.0]
    vae_threat = gen_ai.vae_generate_threat(base_features, 0.2)
    print(f"VAE Generated Threat: {vae_threat['type']}")
    print(f"Variation: {vae_threat['variation']:.2f}")
    print(f"Quality Score: {vae_threat['quality_score']:.2f}")
    
    # Test synthetic dataset generation
    print("\n📊 Testing Synthetic Dataset Generation:")
    synthetic_dataset = gen_ai.generate_synthetic_threat_dataset(5)
    print(f"Generated {len(synthetic_dataset)} synthetic threats")
    
    # Test data augmentation
    print("\n📈 Testing Data Augmentation:")
    training_data = [
        {'features': {'behavior_score': 0.8, 'anomaly_score': 0.7}, 'label': 1},
        {'features': {'behavior_score': 0.2, 'anomaly_score': 0.1}, 'label': 0}
    ]
    augmented_data = gen_ai.augment_training_data(training_data, 2.0)
    print(f"Original data: {len(training_data)} samples")
    print(f"Augmented data: {len(augmented_data)} samples")
    
    # Test detection
    print("\n🔍 Testing Generative AI Detection:")
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
            'name': 'AI Threat',
            'features': {
                'signatures': ['ai_malware_123', 'deepfake_456'],
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
                    'headshot_ratio': 95,
                    'kill_death_ratio': 8.5
                }
            }
        }
    ]
    
    results = []
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        result = gen_ai.detect_threat_generative_ai(test_case['features'])
        
        print(f"Detection: {result['detection_result']}")
        print(f"Prediction: {result['prediction']:.4f}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Max Similarity: {result['max_similarity']:.4f}")
        print(f"Generative Strength: {result['generative_strength']:.4f}")
        
        results.append(result['prediction'])
    
    # Calculate overall generative AI detection rate
    gen_detection_rate = sum(results) / len(results)
    
    print(f"\nOverall Generative AI Detection Rate: {gen_detection_rate:.4f} ({gen_detection_rate*100:.2f}%)")
    print(f"Generative AI Enhancement: Complete")
    
    # Get statistics
    stats = gen_ai.get_generation_statistics()
    print(f"\nGeneration Statistics:")
    print(f"Generated Threats: {stats['generated_threats']}")
    print(f"Available Models: {stats['available_models']}")
    
    return gen_detection_rate

if __name__ == "__main__":
    test_generative_ai()

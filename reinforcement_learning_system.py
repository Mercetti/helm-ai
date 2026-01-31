#!/usr/bin/env python3
"""
Stellar Logic AI - Reinforcement Learning System
==============================================

Adaptive optimization from environment feedback
Q-learning and policy gradient methods for threat detection
"""

import json
import time
import random
import statistics
import math
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from collections import defaultdict, deque

class ReinforcementLearningSystem:
    """
    Reinforcement learning system for adaptive threat detection
    Q-learning and policy gradient methods with environment feedback
    """
    
    def __init__(self):
        # Q-learning parameters
        self.q_table = defaultdict(lambda: defaultdict(float))
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.1  # Exploration rate
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        
        # State and action spaces
        self.state_space_size = 100
        self.action_space = [0, 1]  # 0: safe, 1: threat
        
        # Experience replay buffer
        self.experience_buffer = deque(maxlen=10000)
        self.batch_size = 32
        
        # Policy network parameters
        self.policy_weights = [[random.uniform(-0.1, 0.1) for _ in range(20)] for _ in range(2)]
        self.policy_learning_rate = 0.01
        
        # Training history
        self.training_history = []
        self.reward_history = []
        self.episode_rewards = []
        
        # Performance tracking
        self.performance_metrics = {
            'total_episodes': 0,
            'total_rewards': 0,
            'average_reward': 0,
            'success_rate': 0,
            'exploration_rate': self.epsilon
        }
        
        print("🤖 Reinforcement Learning System Initialized")
        print("🎯 Methods: Q-Learning, Policy Gradient, Experience Replay")
        print("📊 Adaptive: Environment feedback optimization")
        
    def discretize_state(self, features: Dict[str, Any]) -> int:
        """Discretize continuous features into discrete state"""
        # Extract key features
        behavior_score = features.get('behavior_score', 0)
        anomaly_score = features.get('anomaly_score', 0)
        risk_factors = features.get('risk_factors', 0)
        suspicious_activities = features.get('suspicious_activities', 0)
        ai_indicators = features.get('ai_indicators', 0)
        
        # Discretize each feature
        behavior_bin = int(behavior_score * 10)
        anomaly_bin = int(anomaly_score * 10)
        risk_bin = min(int(risk_factors / 2), 5)
        suspicious_bin = min(int(suspicious_activities / 2), 5)
        ai_bin = min(int(ai_indicators / 2), 5)
        
        # Combine into single state ID
        state_id = (behavior_bin * 10000 + anomaly_bin * 1000 + 
                   risk_bin * 100 + suspicious_bin * 10 + ai_bin)
        
        return state_id % self.state_space_size
    
    def q_learning_action(self, state: int) -> int:
        """Q-learning action selection with epsilon-greedy"""
        if random.random() < self.epsilon:
            # Explore: random action
            return random.choice(self.action_space)
        else:
            # Exploit: best action from Q-table
            q_values = [self.q_table[state][action] for action in self.action_space]
            max_q = max(q_values)
            best_actions = [action for action, q in zip(self.action_space, q_values) if q == max_q]
            return random.choice(best_actions)
    
    def update_q_table(self, state: int, action: int, reward: float, next_state: int):
        """Update Q-table using Q-learning update rule"""
        # Get current Q-value
        current_q = self.q_table[state][action]
        
        # Get maximum Q-value for next state
        next_max_q = max([self.q_table[next_state][a] for a in self.action_space])
        
        # Q-learning update rule
        new_q = current_q + self.learning_rate * (reward + self.discount_factor * next_max_q - current_q)
        
        # Update Q-table
        self.q_table[state][action] = new_q
    
    def policy_gradient_action(self, features: List[float]) -> int:
        """Policy gradient action selection"""
        # Calculate policy probabilities
        policy_scores = []
        for action in self.action_space:
            score = 0
            for i, feature in enumerate(features):
                if i < len(self.policy_weights[action]):
                    score += feature * self.policy_weights[action][i]
            policy_scores.append(score)
        
        # Apply softmax to get probabilities (with overflow protection)
        max_score = max(policy_scores)
        exp_scores = [math.exp(score - max_score) for score in policy_scores]
        sum_exp = sum(exp_scores)
        policy_probs = [exp_score / sum_exp for exp_score in exp_scores]
        
        # Sample action according to policy
        return random.choices(self.action_space, weights=policy_probs)[0]
    
    def update_policy(self, features: List[float], action: int, reward: float):
        """Update policy using policy gradient"""
        # Calculate gradient
        for i, feature in enumerate(features):
            if i < len(self.policy_weights[action]):
                # Simple policy gradient update
                gradient = feature * reward
                self.policy_weights[action][i] += self.policy_learning_rate * gradient
    
    def calculate_reward(self, prediction: int, actual: int, confidence: float) -> float:
        """Calculate reward based on prediction accuracy and confidence"""
        if prediction == actual:
            # Correct prediction
            base_reward = 1.0
            if confidence > 0.8:
                base_reward += 0.5  # Bonus for high confidence
        else:
            # Incorrect prediction
            base_reward = -1.0
            if confidence > 0.8:
                base_reward -= 0.5  # Penalty for high confidence wrong prediction
        
        return base_reward
    
    def store_experience(self, state: int, action: int, reward: float, next_state: int, done: bool):
        """Store experience in replay buffer"""
        experience = {
            'state': state,
            'action': action,
            'reward': reward,
            'next_state': next_state,
            'done': done
        }
        self.experience_buffer.append(experience)
    
    def experience_replay_training(self):
        """Train using experience replay"""
        if len(self.experience_buffer) < self.batch_size:
            return
        
        # Sample random batch from experience buffer
        batch = random.sample(list(self.experience_buffer), self.batch_size)
        
        for experience in batch:
            state = experience['state']
            action = experience['action']
            reward = experience['reward']
            next_state = experience['next_state']
            done = experience['done']
            
            if done:
                target = reward
            else:
                next_max_q = max([self.q_table[next_state][a] for a in self.action_space])
                target = reward + self.discount_factor * next_max_q
            
            # Update Q-table
            current_q = self.q_table[state][action]
            self.q_table[state][action] += self.learning_rate * (target - current_q)
    
    def detect_threat_reinforcement_learning(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """Reinforcement learning threat detection"""
        start_time = time.time()
        
        # Discretize state
        state = self.discretize_state(features)
        
        # Extract features for policy gradient
        neural_features = self._extract_rl_features(features)
        
        # Get actions from both methods
        q_action = self.q_learning_action(state)
        policy_action = self.policy_gradient_action(neural_features)
        
        # Ensemble decision
        ensemble_action = q_action if self.q_table[state][q_action] > self.q_table[state][1-q_action] else policy_action
        
        # Calculate confidence
        q_confidence = max(self.q_table[state][0], self.q_table[state][1])
        policy_confidence = self._calculate_policy_confidence(neural_features, policy_action)
        ensemble_confidence = (q_confidence + policy_confidence) / 2
        
        # Apply RL optimization
        final_prediction = float(ensemble_action)
        final_confidence = ensemble_confidence
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create comprehensive result
        result = {
            'prediction': final_prediction,
            'confidence': final_confidence,
            'q_action': q_action,
            'policy_action': policy_action,
            'ensemble_action': ensemble_action,
            'q_confidence': q_confidence,
            'policy_confidence': policy_confidence,
            'state': state,
            'processing_time': processing_time,
            'detection_result': 'THREAT_DETECTED' if final_prediction > 0.5 else 'SAFE',
            'risk_level': self._calculate_risk_level(final_prediction, final_confidence),
            'recommendation': self._generate_recommendation(final_prediction, final_confidence),
            'rl_strength': self._calculate_rl_strength(q_confidence, policy_confidence),
            'exploration_rate': self.epsilon,
            'learning_progress': self._calculate_learning_progress()
        }
        
        return result
    
    def _extract_rl_features(self, features: Dict[str, Any]) -> List[float]:
        """Extract features for reinforcement learning"""
        rl_features = []
        
        # Key features for RL
        rl_features.append(features.get('behavior_score', 0))
        rl_features.append(features.get('anomaly_score', 0))
        rl_features.append(features.get('risk_factors', 0) / 10)
        rl_features.append(features.get('suspicious_activities', 0) / 8)
        rl_features.append(features.get('ai_indicators', 0) / 7)
        
        # Additional features
        if 'movement_data' in features:
            movement = features['movement_data']
            if isinstance(movement, list) and len(movement) > 0:
                rl_features.append(statistics.mean(movement))
                rl_features.append(statistics.stdev(movement) if len(movement) > 1 else 0)
        
        if 'action_timing' in features:
            timing = features['action_timing']
            if isinstance(timing, list) and len(timing) > 0:
                rl_features.append(statistics.mean(timing))
                rl_features.append(statistics.stdev(timing) if len(timing) > 1 else 0)
        
        # Pad to fixed size
        while len(rl_features) < 20:
            rl_features.append(0.0)
        
        return rl_features[:20]
    
    def _calculate_policy_confidence(self, features: List[float], action: int) -> float:
        """Calculate policy confidence"""
        policy_scores = []
        for a in self.action_space:
            score = 0
            for i, feature in enumerate(features):
                if i < len(self.policy_weights[a]):
                    score += feature * self.policy_weights[a][i]
            policy_scores.append(score)
        
        # Apply softmax (with overflow protection)
        max_score = max(policy_scores)
        exp_scores = [math.exp(score - max_score) for score in policy_scores]
        sum_exp = sum(exp_scores)
        policy_probs = [exp_score / sum_exp for exp_score in exp_scores]
        
        return policy_probs[action]
    
    def _calculate_rl_strength(self, q_confidence: float, policy_confidence: float) -> float:
        """Calculate reinforcement learning strength"""
        return (q_confidence + policy_confidence) / 2
    
    def _calculate_learning_progress(self) -> float:
        """Calculate learning progress"""
        if len(self.episode_rewards) < 10:
            return 0.5
        
        recent_rewards = self.episode_rewards[-10:]
        return sum(recent_rewards) / len(recent_rewards)
    
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
            return "RL_IMMEDIATE_ACTION_REQUIRED"
        elif prediction > 0.5 and confidence > 0.7:
            return "RL_ENHANCED_MONITORING"
        elif prediction > 0.3 and confidence > 0.6:
            return "RL_ANALYSIS_RECOMMENDED"
        else:
            return "CONTINUE_RL_MONITORING"
    
    def train_episode(self, training_data: List[Dict[str, Any]], max_steps: int = 100):
        """Train one episode"""
        total_reward = 0
        steps = 0
        
        for data_point in training_data[:max_steps]:
            features = data_point['features']
            actual_label = data_point['label']
            
            # Get state
            state = self.discretize_state(features)
            neural_features = self._extract_rl_features(features)
            
            # Choose action
            action = self.q_learning_action(state)
            
            # Calculate reward
            reward = self.calculate_reward(action, actual_label, 0.8)  # Assuming 0.8 confidence
            total_reward += reward
            
            # Get next state (simplified - use same state for now)
            next_state = self.discretize_state(features)
            
            # Update Q-table
            self.update_q_table(state, action, reward, next_state)
            
            # Update policy
            self.update_policy(neural_features, action, reward)
            
            # Store experience
            self.store_experience(state, action, reward, next_state, steps == max_steps - 1)
            
            steps += 1
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        # Update metrics
        self.performance_metrics['total_episodes'] += 1
        self.performance_metrics['total_rewards'] += total_reward
        self.performance_metrics['average_reward'] = self.performance_metrics['total_rewards'] / self.performance_metrics['total_episodes']
        self.performance_metrics['exploration_rate'] = self.epsilon
        
        # Store episode reward
        self.episode_rewards.append(total_reward)
        
        # Experience replay training
        self.experience_replay_training()
        
        return total_reward
    
    def train_multiple_episodes(self, training_data: List[Dict[str, Any]], num_episodes: int = 100):
        """Train multiple episodes"""
        print(f"🤖 Training Reinforcement Learning for {num_episodes} episodes...")
        
        for episode in range(num_episodes):
            reward = self.train_episode(training_data)
            
            if episode % 10 == 0:
                avg_reward = sum(self.episode_rewards[-10:]) / min(10, len(self.episode_rewards))
                print(f"Episode {episode}: Reward = {reward:.3f}, Avg Reward (last 10) = {avg_reward:.3f}, Epsilon = {self.epsilon:.3f}")
        
        print("🤖 Reinforcement Learning Training Complete!")
    
    def evaluate_performance(self, test_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate RL performance"""
        correct_predictions = 0
        total_predictions = len(test_data)
        
        for data_point in test_data:
            features = data_point['features']
            actual_label = data_point['label']
            
            result = self.detect_threat_reinforcement_learning(features)
            prediction = 1 if result['prediction'] > 0.5 else 0
            
            if prediction == actual_label:
                correct_predictions += 1
        
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        
        return {
            'accuracy': accuracy,
            'total_predictions': total_predictions,
            'correct_predictions': correct_predictions,
            'performance_metrics': self.performance_metrics,
            'q_table_size': len(self.q_table),
            'experience_buffer_size': len(self.experience_buffer)
        }

# Test the reinforcement learning system
def test_reinforcement_learning():
    """Test the reinforcement learning system"""
    print("Testing Reinforcement Learning System")
    print("=" * 50)
    
    # Initialize RL system
    rl_system = ReinforcementLearningSystem()
    
    # Generate training data
    training_data = []
    for i in range(100):
        is_threat = random.choice([True, False])
        features = {
            'signatures': [f'test_signature_{i}'],
            'behavior_score': random.uniform(0.8, 1.0) if is_threat else random.uniform(0.0, 0.3),
            'anomaly_score': random.uniform(0.7, 1.0) if is_threat else random.uniform(0.0, 0.2),
            'risk_factors': random.randint(5, 10) if is_threat else random.randint(0, 2),
            'suspicious_activities': random.randint(3, 8) if is_threat else random.randint(0, 2),
            'ai_indicators': random.randint(2, 6) if is_threat else random.randint(0, 1),
            'movement_data': [random.uniform(50, 150) for _ in range(5)],
            'action_timing': [random.uniform(0.001, 0.01) for _ in range(5)]
        }
        training_data.append({
            'features': features,
            'label': 1 if is_threat else 0
        })
    
    # Train the RL system
    rl_system.train_multiple_episodes(training_data, num_episodes=50)
    
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
                'action_timing': [0.2, 0.3, 0.25, 0.18, 0.22]
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
                'movement_data': [60, 65, 58, 62, 61],
                'action_timing': [0.15, 0.12, 0.18, 0.14, 0.16]
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
                'action_timing': [0.01, 0.008, 0.012, 0.009, 0.011]
            }
        }
    ]
    
    # Run tests
    results = []
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        result = rl_system.detect_threat_reinforcement_learning(test_case['features'])
        
        print(f"Detection: {result['detection_result']}")
        print(f"Prediction: {result['prediction']:.4f}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"RL Strength: {result['rl_strength']:.4f}")
        print(f"Exploration Rate: {result['exploration_rate']:.4f}")
        print(f"Learning Progress: {result['learning_progress']:.4f}")
        
        results.append(result['prediction'])
    
    # Calculate overall RL detection rate
    rl_detection_rate = sum(results) / len(results)
    
    print(f"\nOverall RL Detection Rate: {rl_detection_rate:.4f} ({rl_detection_rate*100:.2f}%)")
    print(f"Reinforcement Learning Enhancement: Complete")
    
    return rl_detection_rate

if __name__ == "__main__":
    test_reinforcement_learning()

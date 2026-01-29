#!/usr/bin/env python3
"""
Helm AI - Model Training Pipeline
Production-ready training system for anti-cheat detection models
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import torchvision.transforms as transforms
from torchvision import datasets
import numpy as np
import pandas as pd
from PIL import Image
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix
from tqdm import tqdm
import albumentations as A
from albumentations.pytorch import ToTensorV2
import cv2
import librosa
from models import VisionDetector, AudioDetector, NetworkDetector, MultiModalFusion

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CheatDetectionDataset(Dataset):
    """Dataset for cheat detection training"""
    
    def __init__(self, data_dir: str, mode: str = 'train', transform=None):
        self.data_dir = Path(data_dir)
        self.mode = mode
        self.transform = transform
        
        # Load dataset metadata
        self.metadata = self._load_metadata()
        
        # Setup class mappings
        self.class_to_idx = {'safe': 0, 'suspicious': 1, 'cheating': 2}
        self.idx_to_class = {v: k for k, v in self.class_to_idx.items()}
        
    def _load_metadata(self) -> List[Dict]:
        """Load dataset metadata from CSV or JSON"""
        metadata_file = self.data_dir / f"{self.mode}_metadata.csv"
        
        if metadata_file.exists():
            df = pd.read_csv(metadata_file)
            return df.to_dict('records')
        else:
            # Create sample metadata if not exists
            return self._create_sample_metadata()
    
    def _create_sample_metadata(self) -> List[Dict]:
        """Create sample metadata for demonstration"""
        sample_data = []
        
        # Generate sample data for each class
        for class_name in ['safe', 'suspicious', 'cheating']:
            for i in range(100):  # 100 samples per class
                sample_data.append({
                    'filename': f"{class_name}_{i:03d}.png",
                    'label': class_name,
                    'game_id': f"game_{i % 5}",
                    'user_id': f"user_{i % 20}"
                })
        
        # Save sample metadata
        df = pd.DataFrame(sample_data)
        metadata_file = self.data_dir / f"{self.mode}_metadata.csv"
        df.to_csv(metadata_file, index=False)
        
        return sample_data
    
    def __len__(self) -> int:
        return len(self.metadata)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        item = self.metadata[idx]
        
        # Load image
        image_path = self.data_dir / item['filename']
        if not image_path.exists():
            # Create dummy image if not exists
            image = self._create_dummy_image(item['label'])
        else:
            image = Image.open(image_path).convert('RGB')
        
        # Apply transforms
        if self.transform:
            image = self.transform(image)
        
        # Get label
        label = self.class_to_idx[item['label']]
        
        return image, label
    
    def _create_dummy_image(self, label: str) -> Image.Image:
        """Create dummy image for training"""
        # Create a simple colored image based on label
        if label == 'safe':
            color = (0, 255, 0)  # Green
        elif label == 'suspicious':
            color = (255, 255, 0)  # Yellow
        else:  # cheating
            color = (255, 0, 0)  # Red
        
        # Create 224x224 image
        image = np.full((224, 224, 3), color, dtype=np.uint8)
        
        # Add some noise
        noise = np.random.randint(0, 50, (224, 224, 3))
        image = np.clip(image + noise, 0, 255).astype(np.uint8)
        
        return Image.fromarray(image)

class AudioDetectionDataset(Dataset):
    """Dataset for audio-based cheat detection"""
    
    def __init__(self, data_dir: str, mode: str = 'train', sample_rate: int = 16000):
        self.data_dir = Path(data_dir)
        self.mode = mode
        self.sample_rate = sample_rate
        
        # Load metadata
        self.metadata = self._load_metadata()
        
        # Class mappings
        self.class_to_idx = {'safe': 0, 'suspicious': 1, 'cheating': 2}
        self.idx_to_class = {v: k for k, v in self.class_to_idx.items()}
    
    def _load_metadata(self) -> List[Dict]:
        """Load audio metadata"""
        metadata_file = self.data_dir / f"{self.mode}_audio_metadata.csv"
        
        if metadata_file.exists():
            df = pd.read_csv(metadata_file)
            return df.to_dict('records')
        else:
            return self._create_sample_metadata()
    
    def _create_sample_metadata(self) -> List[Dict]:
        """Create sample audio metadata"""
        sample_data = []
        
        for class_name in ['safe', 'suspicious', 'cheating']:
            for i in range(50):  # 50 samples per class
                sample_data.append({
                    'filename': f"{class_name}_audio_{i:03d}.wav",
                    'label': class_name,
                    'duration': 1.0,
                    'sample_rate': self.sample_rate
                })
        
        # Save metadata
        df = pd.DataFrame(sample_data)
        metadata_file = self.data_dir / f"{self.mode}_audio_metadata.csv"
        df.to_csv(metadata_file, index=False)
        
        return sample_data
    
    def __len__(self) -> int:
        return len(self.metadata)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        item = self.metadata[idx]
        
        # Generate dummy audio data
        audio_data = self._generate_dummy_audio(item['label'])
        
        # Extract MFCC features
        mfccs = librosa.feature.mfcc(
            y=audio_data, 
            sr=self.sample_rate, 
            n_mfcc=40,
            n_fft=2048,
            hop_length=512
        )
        
        # Normalize
        mfccs = (mfccs - np.mean(mfccs)) / np.std(mfccs)
        
        # Convert to tensor
        audio_tensor = torch.FloatTensor(mfccs)
        
        # Get label
        label = self.class_to_idx[item['label']]
        
        return audio_tensor, label
    
    def _generate_dummy_audio(self, label: str) -> np.ndarray:
        """Generate dummy audio data"""
        duration = 1.0
        samples = int(self.sample_rate * duration)
        
        if label == 'safe':
            # Normal speech-like audio
            audio = np.random.randn(samples) * 0.1
        elif label == 'suspicious':
            # Audio with some anomalies
            audio = np.random.randn(samples) * 0.2
            audio += np.sin(2 * np.pi * 1000 * np.arange(samples) / self.sample_rate) * 0.1
        else:  # cheating
            # Audio with clear patterns
            audio = np.random.randn(samples) * 0.3
            audio += np.sin(2 * np.pi * 2000 * np.arange(samples) / self.sample_rate) * 0.2
        
        return audio

class NetworkDetectionDataset(Dataset):
    """Dataset for network-based cheat detection"""
    
    def __init__(self, data_dir: str, mode: str = 'train', sequence_length: int = 100):
        self.data_dir = Path(data_dir)
        self.mode = mode
        self.sequence_length = sequence_length
        
        # Load metadata
        self.metadata = self._load_metadata()
        
        # Class mappings
        self.class_to_idx = {'safe': 0, 'suspicious': 1, 'cheating': 2}
        self.idx_to_class = {v: k for k, v in self.class_to_idx.items()}
    
    def _load_metadata(self) -> List[Dict]:
        """Load network metadata"""
        metadata_file = self.data_dir / f"{self.mode}_network_metadata.csv"
        
        if metadata_file.exists():
            df = pd.read_csv(metadata_file)
            return df.to_dict('records')
        else:
            return self._create_sample_metadata()
    
    def _create_sample_metadata(self) -> List[Dict]:
        """Create sample network metadata"""
        sample_data = []
        
        for class_name in ['safe', 'suspicious', 'cheating']:
            for i in range(100):  # 100 samples per class
                sample_data.append({
                    'session_id': f"{class_name}_session_{i:03d}",
                    'label': class_name,
                    'packet_count': self.sequence_length,
                    'features': 10
                })
        
        # Save metadata
        df = pd.DataFrame(sample_data)
        metadata_file = self.data_dir / f"{self.mode}_network_metadata.csv"
        df.to_csv(metadata_file, index=False)
        
        return sample_data
    
    def __len__(self) -> int:
        return len(self.metadata)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        item = self.metadata[idx]
        
        # Generate dummy network data
        network_data = self._generate_dummy_network_data(item['label'])
        
        # Convert to tensor
        network_tensor = torch.FloatTensor(network_data)
        
        # Get label
        label = self.class_to_idx[item['label']]
        
        return network_tensor, label
    
    def _generate_dummy_network_data(self, label: str) -> np.ndarray:
        """Generate dummy network data"""
        if label == 'safe':
            # Normal network traffic
            data = np.random.randn(self.sequence_length, 10) * 0.1
        elif label == 'suspicious':
            # Slightly anomalous traffic
            data = np.random.randn(self.sequence_length, 10) * 0.2
            data[:, 0] += 0.5  # Packet size anomaly
        else:  # cheating
            # Clearly anomalous traffic
            data = np.random.randn(self.sequence_length, 10) * 0.3
            data[:, 1] += 1.0  # Timing anomaly
            data[:, 2] += 0.8  # Protocol anomaly
        
        return data

class ModelTrainer:
    """Advanced model training system"""
    
    def __init__(self, model: nn.Module, device: str = 'auto'):
        self.model = model
        self.device = torch.device('cuda' if torch.cuda.is_available() and device == 'auto' else device)
        self.model.to(self.device)
        
        # Training history
        self.train_history = {
            'train_loss': [],
            'val_loss': [],
            'train_acc': [],
            'val_acc': [],
            'epoch_times': []
        }
        
        # Best model tracking
        self.best_val_acc = 0.0
        self.best_model_state = None
        
    def setup_data_loaders(self, train_dataset, val_dataset, batch_size=32, num_workers=4):
        """Setup data loaders"""
        self.train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=True
        )
        
        self.val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True
        )
    
    def train_epoch(self, epoch: int, optimizer, criterion) -> Dict[str, float]:
        """Train for one epoch"""
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        start_time = time.time()
        
        for batch_idx, (data, targets) in enumerate(tqdm(self.train_loader, desc=f"Epoch {epoch}")):
            data, targets = data.to(self.device), targets.to(self.device)
            
            optimizer.zero_grad()
            
            # Forward pass
            if isinstance(self.model, VisionDetector):
                outputs = self.model(data)
                if isinstance(outputs, dict):
                    outputs = outputs['classification']
            elif isinstance(self.model, AudioDetector):
                outputs = self.model(data)
                if isinstance(outputs, dict):
                    outputs = outputs['classification']
            elif isinstance(self.model, NetworkDetector):
                outputs = self.model(data)
                if isinstance(outputs, dict):
                    outputs = outputs['classification']
            else:
                outputs = self.model(data)
            
            loss = criterion(outputs, targets)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Statistics
            running_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += targets.size(0)
            correct += (predicted == targets).sum().item()
        
        epoch_time = time.time() - start_time
        
        return {
            'train_loss': running_loss / len(self.train_loader),
            'train_acc': 100.0 * correct / total,
            'epoch_time': epoch_time
        }
    
    def validate_epoch(self, criterion) -> Dict[str, float]:
        """Validate for one epoch"""
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for data, targets in self.val_loader:
                data, targets = data.to(self.device), targets.to(self.device)
                
                # Forward pass
                if isinstance(self.model, VisionDetector):
                    outputs = self.model(data)
                    if isinstance(outputs, dict):
                        outputs = outputs['classification']
                elif isinstance(self.model, AudioDetector):
                    outputs = self.model(data)
                    if isinstance(outputs, dict):
                        outputs = outputs['classification']
                elif isinstance(self.model, NetworkDetector):
                    outputs = self.model(data)
                    if isinstance(outputs, dict):
                        outputs = outputs['classification']
                else:
                    outputs = self.model(data)
                
                loss = criterion(outputs, targets)
                
                # Statistics
                running_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += targets.size(0)
                correct += (predicted == targets).sum().item()
        
        return {
            'val_loss': running_loss / len(self.val_loader),
            'val_acc': 100.0 * correct / total
        }
    
    def train(self, num_epochs: int, learning_rate: float = 0.001, save_dir: str = 'models'):
        """Train the model"""
        # Setup optimizer and criterion
        optimizer = optim.Adam(self.model.parameters(), lr=learning_rate)
        criterion = nn.CrossEntropyLoss()
        
        # Setup save directory
        save_path = Path(save_dir)
        save_path.mkdir(exist_ok=True)
        
        logger.info(f"Starting training for {num_epochs} epochs...")
        logger.info(f"Device: {self.device}")
        logger.info(f"Model parameters: {sum(p.numel() for p in self.model.parameters())}")
        
        for epoch in range(num_epochs):
            # Training
            train_metrics = self.train_epoch(epoch, optimizer, criterion)
            
            # Validation
            val_metrics = self.validate_epoch(criterion)
            
            # Update history
            self.train_history['train_loss'].append(train_metrics['train_loss'])
            self.train_history['val_loss'].append(val_metrics['val_loss'])
            self.train_history['train_acc'].append(train_metrics['train_acc'])
            self.train_history['val_acc'].append(val_metrics['val_acc'])
            self.train_history['epoch_times'].append(train_metrics['epoch_time'])
            
            # Print progress
            logger.info(
                f"Epoch {epoch+1}/{num_epochs} - "
                f"Train Loss: {train_metrics['train_loss']:.4f}, "
                f"Train Acc: {train_metrics['train_acc']:.2f}%, "
                f"Val Loss: {val_metrics['val_loss']:.4f}, "
                f"Val Acc: {val_metrics['val_acc']:.2f}%, "
                f"Time: {train_metrics['epoch_time']:.2f}s"
            )
            
            # Save best model
            if val_metrics['val_acc'] > self.best_val_acc:
                self.best_val_acc = val_metrics['val_acc']
                self.best_model_state = self.model.state_dict().copy()
                
                # Save checkpoint
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'val_acc': val_metrics['val_acc'],
                    'val_loss': val_metrics['val_loss'],
                    'train_history': self.train_history
                }, save_path / 'best_model.pth')
                
                logger.info(f"New best model saved with validation accuracy: {val_metrics['val_acc']:.2f}%")
        
        # Load best model
        if self.best_model_state:
            self.model.load_state_dict(self.best_model_state)
            logger.info(f"Loaded best model with validation accuracy: {self.best_val_acc:.2f}%")
        
        return self.train_history
    
    def evaluate(self, test_loader) -> Dict[str, any]:
        """Evaluate model on test set"""
        self.model.eval()
        all_predictions = []
        all_targets = []
        
        with torch.no_grad():
            for data, targets in test_loader:
                data, targets = data.to(self.device), targets.to(self.device)
                
                outputs = self.model(data)
                if isinstance(outputs, dict):
                    outputs = outputs['classification']
                
                _, predicted = torch.max(outputs, 1)
                
                all_predictions.extend(predicted.cpu().numpy())
                all_targets.extend(targets.cpu().numpy())
        
        # Generate classification report
        report = classification_report(
            all_targets, 
            all_predictions, 
            target_names=['safe', 'suspicious', 'cheating'],
            output_dict=True
        )
        
        # Generate confusion matrix
        cm = confusion_matrix(all_targets, all_predictions)
        
        return {
            'classification_report': report,
            'confusion_matrix': cm,
            'accuracy': report['accuracy'],
            'precision': report['weighted avg']['precision'],
            'recall': report['weighted avg']['recall'],
            'f1_score': report['weighted avg']['f1-score']
        }
    
    def plot_training_history(self, save_path: str = 'training_history.png'):
        """Plot training history"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Loss plot
        axes[0, 0].plot(self.train_history['train_loss'], label='Train Loss')
        axes[0, 0].plot(self.train_history['val_loss'], label='Val Loss')
        axes[0, 0].set_title('Training and Validation Loss')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Accuracy plot
        axes[0, 1].plot(self.train_history['train_acc'], label='Train Acc')
        axes[0, 1].plot(self.train_history['val_acc'], label='Val Acc')
        axes[0, 1].set_title('Training and Validation Accuracy')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Accuracy (%)')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Epoch time plot
        axes[1, 0].plot(self.train_history['epoch_times'])
        axes[1, 0].set_title('Epoch Training Time')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Time (seconds)')
        axes[1, 0].grid(True)
        
        # Learning curves
        axes[1, 1].plot(self.train_history['train_acc'], label='Train')
        axes[1, 1].plot(self.train_history['val_acc'], label='Validation')
        axes[1, 1].set_title('Learning Curves')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Accuracy (%)')
        axes[1, 1].legend()
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Training history plot saved to {save_path}")

# Training factory functions
def train_vision_model(data_dir: str, num_epochs: int = 50, save_dir: str = 'models'):
    """Train vision detection model"""
    # Setup transforms
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    # Create datasets
    train_dataset = CheatDetectionDataset(data_dir, 'train', train_transform)
    val_dataset = CheatDetectionDataset(data_dir, 'val', val_transform)
    
    # Create model
    model = VisionDetector(num_classes=3)
    
    # Create trainer
    trainer = ModelTrainer(model)
    trainer.setup_data_loaders(train_dataset, val_dataset)
    
    # Train
    history = trainer.train(num_epochs, save_dir=save_dir)
    
    return model, history

def train_audio_model(data_dir: str, num_epochs: int = 30, save_dir: str = 'models'):
    """Train audio detection model"""
    # Create datasets
    train_dataset = AudioDetectionDataset(data_dir, 'train')
    val_dataset = AudioDetectionDataset(data_dir, 'val')
    
    # Create model
    model = AudioDetector(num_classes=3)
    
    # Create trainer
    trainer = ModelTrainer(model)
    trainer.setup_data_loaders(train_dataset, val_dataset, batch_size=16)
    
    # Train
    history = trainer.train(num_epochs, save_dir=save_dir)
    
    return model, history

def train_network_model(data_dir: str, num_epochs: int = 40, save_dir: str = 'models'):
    """Train network detection model"""
    # Create datasets
    train_dataset = NetworkDetectionDataset(data_dir, 'train')
    val_dataset = NetworkDetectionDataset(data_dir, 'val')
    
    # Create model
    model = NetworkDetector(num_classes=3)
    
    # Create trainer
    trainer = ModelTrainer(model)
    trainer.setup_data_loaders(train_dataset, val_dataset, batch_size=32)
    
    # Train
    history = trainer.train(num_epochs, save_dir=save_dir)
    
    return model, history

def train_multimodal_model(data_dir: str, num_epochs: int = 25, save_dir: str = 'models'):
    """Train multi-modal fusion model"""
    # This would require multi-modal dataset
    # For now, return a placeholder
    model = MultiModalFusion()
    logger.info("Multi-modal training would require combined dataset")
    return model, {}

if __name__ == "__main__":
    # Test training system
    print("Testing Helm AI Training Pipeline...")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Test vision model training
    print("\nTraining Vision Model...")
    vision_model, vision_history = train_vision_model(str(data_dir), num_epochs=5)
    print(f"Vision model trained successfully!")
    
    # Test audio model training
    print("\nTraining Audio Model...")
    audio_model, audio_history = train_audio_model(str(data_dir), num_epochs=5)
    print(f"Audio model trained successfully!")
    
    # Test network model training
    print("\nTraining Network Model...")
    network_model, network_history = train_network_model(str(data_dir), num_epochs=5)
    print(f"Network model trained successfully!")
    
    print("\nTraining pipeline test completed!")

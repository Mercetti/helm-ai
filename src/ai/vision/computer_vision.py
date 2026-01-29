"""
Helm AI Computer Vision Detection Module
This module provides computer vision capabilities for cheat detection
"""

import os
import cv2
import numpy as np
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from dataclasses import dataclass
import json
import base64
from pathlib import Path
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from PIL import Image, ImageEnhance
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class DetectionResult:
    """Detection result data class"""
    is_cheating: bool
    confidence: float
    cheat_types: List[str]
    regions: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    timestamp: datetime
    processing_time: float

@dataclass
class CheatRegion:
    """Cheat detection region"""
    x: int
    y: int
    width: int
    height: int
    cheat_type: str
    confidence: float

class CheatType:
    """Cheat type constants"""
    AIM_BOT = "aimbot"
    WALL_HACK = "wallhack"
    ESP_OVERLAY = "esp_overlay"
    AUTO_AIM = "auto_aim"
    TRIGGER_BOT = "trigger_bot"
    RECOIL_CONTROL = "recoil_control"
    SPEED_HACK = "speed_hack"
    RADAR_HACK = "radar_hack"

class ComputerVisionDetector:
    """Computer vision-based cheat detection system"""
    
    def __init__(self, model_path: Optional[str] = None, device: str = "auto"):
        """
        Initialize computer vision detector
        
        Args:
            model_path: Path to trained model file
            device: Device to run inference on (cpu, cuda, auto)
        """
        self.model_path = model_path or os.getenv('CV_MODEL_PATH', 'models/cheat_detection.pth')
        self.device = self._setup_device(device)
        
        # Detection models
        self.aim_detector = None
        self.esp_detector = None
        self.wallhack_detector = None
        
        # Processing settings
        self.confidence_threshold = float(os.getenv('CV_CONFIDENCE_THRESHOLD', '0.7'))
        self.nms_threshold = float(os.getenv('CV_NMS_THRESHOLD', '0.4'))
        self.max_detections = int(os.getenv('CV_MAX_DETECTIONS', '100'))
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((640, 640)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Thread pool for async processing
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize models
        self._load_models()
    
    def _setup_device(self, device: str) -> str:
        """Setup computation device"""
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return device
    
    def _load_models(self):
        """Load detection models"""
        try:
            # Load aim bot detection model
            self.aim_detector = self._load_model("aimbot")
            
            # Load ESP detection model
            self.esp_detector = self._load_model("esp")
            
            # Load wallhack detection model
            self.wallhack_detector = self._load_model("wallhack")
            
            logger.info("Computer vision models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            # Create dummy models for testing
            self._create_dummy_models()
    
    def _load_model(self, model_type: str) -> Optional[nn.Module]:
        """Load specific model type"""
        try:
            model_path = Path(self.model_path)
            if model_path.exists():
                # Load actual model
                model = torch.load(model_path, map_location=self.device)
                model.eval()
                return model.to(self.device)
            else:
                logger.warning(f"Model file not found: {model_path}")
                return None
        except Exception as e:
            logger.error(f"Failed to load {model_type} model: {e}")
            return None
    
    def _create_dummy_models(self):
        """Create dummy models for testing"""
        class DummyModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1 = nn.Conv2d(3, 16, 3, padding=1)
                self.pool = nn.AdaptiveAvgPool2d((1, 1))
                self.fc = nn.Linear(16, 2)
            
            def forward(self, x):
                x = self.pool(torch.relu(self.conv1(x)))
                x = x.view(x.size(0), -1)
                return torch.softmax(self.fc(x), dim=1)
        
        self.aim_detector = DummyModel().to(self.device)
        self.esp_detector = DummyModel().to(self.device)
        self.wallhack_detector = DummyModel().to(self.device)
    
    async def analyze_image(self, image_data: Union[str, bytes, np.ndarray]) -> DetectionResult:
        """
        Analyze image for cheat detection
        
        Args:
            image_data: Image data (file path, base64 string, bytes, or numpy array)
            
        Returns:
            DetectionResult with analysis results
        """
        start_time = datetime.now()
        
        try:
            # Preprocess image
            image = self._preprocess_image(image_data)
            if image is None:
                return DetectionResult(
                    is_cheating=False,
                    confidence=0.0,
                    cheat_types=[],
                    regions=[],
                    metadata={"error": "Invalid image data"},
                    timestamp=start_time,
                    processing_time=0.0
                )
            
            # Run detection in thread pool
            detections = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._detect_cheats, image
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Process detection results
            cheat_regions = []
            cheat_types = []
            max_confidence = 0.0
            
            for detection in detections:
                cheat_regions.append(CheatRegion(
                    x=detection['x'],
                    y=detection['y'],
                    width=detection['width'],
                    height=detection['height'],
                    cheat_type=detection['type'],
                    confidence=detection['confidence']
                ))
                
                if detection['type'] not in cheat_types:
                    cheat_types.append(detection['type'])
                
                max_confidence = max(max_confidence, detection['confidence'])
            
            is_cheating = len(cheat_regions) > 0 and max_confidence >= self.confidence_threshold
            
            return DetectionResult(
                is_cheating=is_cheating,
                confidence=max_confidence,
                cheat_types=cheat_types,
                regions=[{
                    'x': r.x, 'y': r.y, 'width': r.width, 'height': r.height,
                    'type': r.cheat_type, 'confidence': r.confidence
                } for r in cheat_regions],
                metadata={
                    'image_shape': image.shape,
                    'detection_count': len(cheat_regions),
                    'threshold': self.confidence_threshold
                },
                timestamp=start_time,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return DetectionResult(
                is_cheating=False,
                confidence=0.0,
                cheat_types=[],
                regions=[],
                metadata={"error": str(e)},
                timestamp=start_time,
                processing_time=processing_time
            )
    
    def _preprocess_image(self, image_data: Union[str, bytes, np.ndarray]) -> Optional[np.ndarray]:
        """Preprocess image for detection"""
        try:
            if isinstance(image_data, str):
                if image_data.startswith('data:image'):
                    # Base64 encoded image
                    header, encoded = image_data.split(',', 1)
                    image_bytes = base64.b64decode(encoded)
                    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
                    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                else:
                    # File path
                    image = cv2.imread(image_data)
                    if image is None:
                        raise ValueError(f"Could not read image from path: {image_data}")
            
            elif isinstance(image_data, bytes):
                # Raw bytes
                image_array = np.frombuffer(image_data, dtype=np.uint8)
                image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            
            elif isinstance(image_data, np.ndarray):
                # Numpy array
                image = image_data.copy()
            
            else:
                raise ValueError(f"Unsupported image data type: {type(image_data)}")
            
            if image is None:
                raise ValueError("Failed to decode image")
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Enhance image for better detection
            image = self._enhance_image(image)
            
            return image
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return None
    
    def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Enhance image for better detection"""
        try:
            # Convert to PIL for enhancement
            pil_image = Image.fromarray(image)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(pil_image)
            pil_image = enhancer.enhance(1.2)
            
            # Enhance sharpness
            enhancer = ImageEnhance.Sharpness(pil_image)
            pil_image = enhancer.enhance(1.1)
            
            # Convert back to numpy
            enhanced_image = np.array(pil_image)
            
            return enhanced_image
            
        except Exception as e:
            logger.warning(f"Image enhancement failed: {e}")
            return image
    
    def _detect_cheats(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect cheats in image"""
        detections = []
        
        try:
            # Prepare image tensor
            image_tensor = self._prepare_image_tensor(image)
            
            # Run each detector
            if self.aim_detector is not None:
                aim_detections = self._run_detector(self.aim_detector, image_tensor, CheatType.AIM_BOT)
                detections.extend(aim_detections)
            
            if self.esp_detector is not None:
                esp_detections = self._run_detector(self.esp_detector, image_tensor, CheatType.ESP_OVERLAY)
                detections.extend(esp_detections)
            
            if self.wallhack_detector is not None:
                wallhack_detections = self._run_detector(self.wallhack_detector, image_tensor, CheatType.WALL_HACK)
                detections.extend(wallhack_detections)
            
            # Apply Non-Maximum Suppression
            filtered_detections = self._apply_nms(detections)
            
            # Filter by confidence threshold
            final_detections = [
                d for d in filtered_detections 
                if d['confidence'] >= self.confidence_threshold
            ]
            
            # Limit number of detections
            if len(final_detections) > self.max_detections:
                final_detections = sorted(final_detections, key=lambda x: x['confidence'], reverse=True)[:self.max_detections]
            
            return final_detections
            
        except Exception as e:
            logger.error(f"Cheat detection failed: {e}")
            return []
    
    def _prepare_image_tensor(self, image: np.ndarray) -> torch.Tensor:
        """Prepare image tensor for inference"""
        # Convert PIL to tensor
        pil_image = Image.fromarray(image)
        tensor = self.transform(pil_image)
        
        # Add batch dimension
        tensor = tensor.unsqueeze(0)
        
        # Move to device
        tensor = tensor.to(self.device)
        
        return tensor
    
    def _run_detector(self, model: nn.Module, image_tensor: torch.Tensor, cheat_type: str) -> List[Dict[str, Any]]:
        """Run specific detector model"""
        detections = []
        
        try:
            with torch.no_grad():
                # Run inference
                outputs = model(image_tensor)
                
                # Process outputs based on model type
                if isinstance(outputs, (list, tuple)):
                    # YOLO-style output
                    detections = self._process_yolo_output(outputs, cheat_type)
                else:
                    # Classification output
                    detections = self._process_classification_output(outputs, cheat_type)
            
        except Exception as e:
            logger.error(f"Detector {cheat_type} failed: {e}")
        
        return detections
    
    def _process_yolo_output(self, outputs: List[torch.Tensor], cheat_type: str) -> List[Dict[str, Any]]:
        """Process YOLO-style model output"""
        detections = []
        
        try:
            # Simplified YOLO output processing
            for output in outputs:
                if output.dim() == 3:
                    output = output.squeeze(0)
                
                # Get detections above threshold
                scores = output[:, 4]  # Confidence scores
                mask = scores > self.confidence_threshold
                
                if mask.any():
                    filtered_output = output[mask]
                    
                    for detection in filtered_output:
                        x1, y1, x2, y2, conf = detection[:5]
                        
                        detections.append({
                            'x': int(x1.item()),
                            'y': int(y1.item()),
                            'width': int((x2 - x1).item()),
                            'height': int((y2 - y1).item()),
                            'confidence': conf.item(),
                            'type': cheat_type
                        })
        
        except Exception as e:
            logger.error(f"YOLO output processing failed: {e}")
        
        return detections
    
    def _process_classification_output(self, outputs: torch.Tensor, cheat_type: str) -> List[Dict[str, Any]]:
        """Process classification model output"""
        detections = []
        
        try:
            # Get probabilities
            probabilities = torch.softmax(outputs, dim=1)
            
            # Get cheat probability (assuming class 1 is cheat)
            cheat_prob = probabilities[0, 1].item()
            
            if cheat_prob >= self.confidence_threshold:
                # Create full image detection
                detections.append({
                    'x': 0,
                    'y': 0,
                    'width': 640,  # Default image size
                    'height': 640,
                    'confidence': cheat_prob,
                    'type': cheat_type
                })
        
        except Exception as e:
            logger.error(f"Classification output processing failed: {e}")
        
        return detections
    
    def _apply_nms(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply Non-Maximum Suppression to reduce overlapping detections"""
        if len(detections) == 0:
            return detections
        
        try:
            # Convert to numpy arrays
            boxes = np.array([[d['x'], d['y'], d['x'] + d['width'], d['y'] + d['height']] for d in detections])
            scores = np.array([d['confidence'] for d in detections])
            
            # Apply NMS
            indices = cv2.dnn.NMSBoxes(
                boxes.tolist(), scores.tolist(), self.confidence_threshold, self.nms_threshold
            )
            
            if len(indices) > 0:
                indices = indices.flatten()
                return [detections[i] for i in indices]
            else:
                return []
        
        except Exception as e:
            logger.error(f"NMS failed: {e}")
            return detections
    
    def analyze_video_frame(self, frame_data: Union[str, bytes, np.ndarray]) -> DetectionResult:
        """Analyze single video frame for cheats"""
        # Synchronous version for video processing
        return asyncio.run(self.analyze_image(frame_data))
    
    def get_detection_stats(self) -> Dict[str, Any]:
        """Get detection statistics"""
        return {
            "model_path": self.model_path,
            "device": self.device,
            "confidence_threshold": self.confidence_threshold,
            "nms_threshold": self.nms_threshold,
            "max_detections": self.max_detections,
            "models_loaded": {
                "aimbot": self.aim_detector is not None,
                "esp": self.esp_detector is not None,
                "wallhack": self.wallhack_detector is not None
            }
        }
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update detection settings"""
        if 'confidence_threshold' in settings:
            self.confidence_threshold = float(settings['confidence_threshold'])
        
        if 'nms_threshold' in settings:
            self.nms_threshold = float(settings['nms_threshold'])
        
        if 'max_detections' in settings:
            self.max_detections = int(settings['max_detections'])
        
        logger.info(f"Detection settings updated: {settings}")

# Global instance
computer_vision_detector = ComputerVisionDetector()

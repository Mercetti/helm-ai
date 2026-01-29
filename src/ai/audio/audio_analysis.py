"""
Helm AI Audio Analysis Module
This module provides audio analysis capabilities for cheat detection
"""

import os
import logging
import numpy as np
import librosa
import soundfile as sf
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime
from dataclasses import dataclass
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import base64
from pathlib import Path
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import signal
from scipy.stats import entropy
import warnings

logger = logging.getLogger(__name__)

# Suppress librosa warnings
warnings.filterwarnings('ignore')

@dataclass
class AudioAnalysisResult:
    """Audio analysis result data class"""
    is_suspicious: bool
    confidence: float
    suspicious_activities: List[str]
    audio_features: Dict[str, Any]
    metadata: Dict[str, Any]
    timestamp: datetime
    processing_time: float

@dataclass
class AudioSegment:
    """Audio segment analysis"""
    start_time: float
    end_time: float
    activity_type: str
    confidence: float
    features: Dict[str, Any]

class SuspiciousActivity:
    """Suspicious activity types"""
    VOICE_STRESS = "voice_stress"
    COORDINATED_CHEATING = "coordinated_cheating"
    UNUSUAL_PATTERN = "unusual_pattern"
    BACKGROUND_NOISE = "background_noise"
    MULTIPLE_VOICES = "multiple_voices"
    AUTOMATED_RESPONSES = "automated_responses"
    SILENCE_ANOMALIES = "silence_anomalies"

class AudioAnalyzer:
    """Audio analysis system for cheat detection"""
    
    def __init__(self, model_path: Optional[str] = None, device: str = "auto"):
        """
        Initialize audio analyzer
        
        Args:
            model_path: Path to trained model file
            device: Device to run inference on (cpu, cuda, auto)
        """
        self.model_path = model_path or os.getenv('AUDIO_MODEL_PATH', 'models/audio_analysis.pth')
        self.device = self._setup_device(device)
        
        # Analysis models
        self.stress_detector = None
        self.pattern_analyzer = None
        self.voice_classifier = None
        
        # Analysis settings
        self.sample_rate = int(os.getenv('AUDIO_SAMPLE_RATE', '16000'))
        self.hop_length = int(os.getenv('AUDIO_HOP_LENGTH', '512'))
        self.n_fft = int(os.getenv('AUDIO_N_FFT', '2048'))
        self.confidence_threshold = float(os.getenv('AUDIO_CONFIDENCE_THRESHOLD', '0.7'))
        
        # Audio processing parameters
        self.segment_duration = float(os.getenv('AUDIO_SEGMENT_DURATION', '5.0'))  # seconds
        self.overlap_ratio = float(os.getenv('AUDIO_OVERLAP_RATIO', '0.5'))
        
        # Feature extraction settings
        self.mel_bands = int(os.getenv('AUDIO_MEL_BANDS', '128'))
        self.mfcc_count = int(os.getenv('AUDIO_MFCC_COUNT', '13'))
        
        # Thread pool for async processing
        self.executor = ThreadPoolExecutor(max_workers=2)
        
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
        """Load analysis models"""
        try:
            # Load stress detection model
            self.stress_detector = self._load_model("stress")
            
            # Load pattern analysis model
            self.pattern_analyzer = self._load_model("pattern")
            
            # Load voice classification model
            self.voice_classifier = self._load_model("voice")
            
            logger.info("Audio analysis models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load audio models: {e}")
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
                logger.warning(f"Audio model file not found: {model_path}")
                return None
        except Exception as e:
            logger.error(f"Failed to load {model_type} audio model: {e}")
            return None
    
    def _create_dummy_models(self):
        """Create dummy models for testing"""
        class DummyAudioModel(nn.Module):
            def __init__(self, input_size=128, hidden_size=64, output_size=2):
                super().__init__()
                self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
                self.fc = nn.Linear(hidden_size, output_size)
            
            def forward(self, x):
                lstm_out, _ = self.lstm(x)
                # Take the last time step
                output = self.fc(lstm_out[:, -1, :])
                return torch.softmax(output, dim=1)
        
        self.stress_detector = DummyAudioModel().to(self.device)
        self.pattern_analyzer = DummyAudioModel().to(self.device)
        self.voice_classifier = DummyAudioModel().to(self.device)
    
    async def analyze_audio(self, audio_data: Union[str, bytes, np.ndarray, Tuple]) -> AudioAnalysisResult:
        """
        Analyze audio for suspicious activities
        
        Args:
            audio_data: Audio data (file path, base64 string, bytes, numpy array, or tuple)
            
        Returns:
            AudioAnalysisResult with analysis results
        """
        start_time = datetime.now()
        
        try:
            # Load and preprocess audio
            audio, sr = self._load_audio(audio_data)
            if audio is None:
                return AudioAnalysisResult(
                    is_suspicious=False,
                    confidence=0.0,
                    suspicious_activities=[],
                    audio_features={},
                    metadata={"error": "Invalid audio data"},
                    timestamp=start_time,
                    processing_time=0.0
                )
            
            # Resample if necessary
            if sr != self.sample_rate:
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sample_rate)
            
            # Run analysis in thread pool
            analysis_results = await asyncio.get_event_loop().run_in_executor(
                self.executor, self._analyze_audio_features, audio
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Process analysis results
            suspicious_activities = []
            max_confidence = 0.0
            
            for result in analysis_results['segments']:
                if result['confidence'] >= self.confidence_threshold:
                    suspicious_activities.append(result['activity_type'])
                    max_confidence = max(max_confidence, result['confidence'])
            
            is_suspicious = len(suspicious_activities) > 0
            
            return AudioAnalysisResult(
                is_suspicious=is_suspicious,
                confidence=max_confidence,
                suspicious_activities=suspicious_activities,
                audio_features=analysis_results['features'],
                metadata={
                    'duration': len(audio) / self.sample_rate,
                    'sample_rate': self.sample_rate,
                    'segments_analyzed': len(analysis_results['segments']),
                    'threshold': self.confidence_threshold
                },
                timestamp=start_time,
                processing_time=processing_time
            )
            
        except Exception as e:
            logger.error(f"Audio analysis failed: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AudioAnalysisResult(
                is_suspicious=False,
                confidence=0.0,
                suspicious_activities=[],
                audio_features={},
                metadata={"error": str(e)},
                timestamp=start_time,
                processing_time=processing_time
            )
    
    def _load_audio(self, audio_data: Union[str, bytes, np.ndarray, Tuple]) -> Tuple[Optional[np.ndarray], int]:
        """Load audio data"""
        try:
            if isinstance(audio_data, str):
                if audio_data.startswith('data:audio'):
                    # Base64 encoded audio
                    header, encoded = audio_data.split(',', 1)
                    audio_bytes = base64.b64decode(encoded)
                    audio, sr = sf.read(io.BytesIO(audio_bytes))
                else:
                    # File path
                    audio, sr = librosa.load(audio_data, sr=None)
            
            elif isinstance(audio_data, bytes):
                # Raw bytes
                import io
                audio, sr = sf.read(io.BytesIO(audio_data))
            
            elif isinstance(audio_data, np.ndarray):
                # Numpy array
                if len(audio_data.shape) == 2:
                    # Stereo to mono
                    audio = np.mean(audio_data, axis=1)
                else:
                    audio = audio_data
                sr = self.sample_rate
            
            elif isinstance(audio_data, tuple) and len(audio_data) == 2:
                # Tuple of (audio_array, sample_rate)
                audio, sr = audio_data
                if len(audio.shape) == 2:
                    audio = np.mean(audio, axis=1)
            
            else:
                raise ValueError(f"Unsupported audio data type: {type(audio_data)}")
            
            if audio is None or len(audio) == 0:
                raise ValueError("Failed to load audio or empty audio data")
            
            return audio, sr
            
        except Exception as e:
            logger.error(f"Audio loading failed: {e}")
            return None, self.sample_rate
    
    def _analyze_audio_features(self, audio: np.ndarray) -> Dict[str, Any]:
        """Analyze audio features for suspicious activities"""
        results = {
            'segments': [],
            'features': {}
        }
        
        try:
            # Extract global features
            global_features = self._extract_global_features(audio)
            results['features'] = global_features
            
            # Segment audio for analysis
            segments = self._segment_audio(audio)
            
            # Analyze each segment
            for i, (segment, start_time, end_time) in enumerate(segments):
                segment_features = self._extract_segment_features(segment)
                
                # Run detection models
                segment_results = self._detect_suspicious_activities(segment_features)
                
                # Add segment results
                for activity_type, confidence in segment_results.items():
                    if confidence >= self.confidence_threshold:
                        results['segments'].append({
                            'start_time': start_time,
                            'end_time': end_time,
                            'activity_type': activity_type,
                            'confidence': confidence,
                            'features': segment_features
                        })
            
        except Exception as e:
            logger.error(f"Audio feature analysis failed: {e}")
        
        return results
    
    def _segment_audio(self, audio: np.ndarray) -> List[Tuple[np.ndarray, float, float]]:
        """Segment audio into overlapping windows"""
        segments = []
        segment_samples = int(self.segment_duration * self.sample_rate)
        hop_samples = int(segment_samples * (1 - self.overlap_ratio))
        
        for start in range(0, len(audio) - segment_samples + 1, hop_samples):
            end = start + segment_samples
            segment = audio[start:end]
            
            start_time = start / self.sample_rate
            end_time = end / self.sample_rate
            
            segments.append((segment, start_time, end_time))
        
        return segments
    
    def _extract_global_features(self, audio: np.ndarray) -> Dict[str, Any]:
        """Extract global audio features"""
        features = {}
        
        try:
            # Basic features
            features['duration'] = len(audio) / self.sample_rate
            features['rms_energy'] = np.sqrt(np.mean(audio**2))
            features['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(audio)[0])
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate)[0]
            features['spectral_centroid_mean'] = np.mean(spectral_centroids)
            features['spectral_centroid_std'] = np.std(spectral_centroids)
            
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio, sr=self.sample_rate)[0]
            features['spectral_rolloff_mean'] = np.mean(spectral_rolloff)
            
            # MFCC features
            mfccs = librosa.feature.mfcc(y=audio, sr=self.sample_rate, n_mfcc=self.mfcc_count)
            for i in range(self.mfcc_count):
                features[f'mfcc_{i}_mean'] = np.mean(mfccs[i])
                features[f'mfcc_{i}_std'] = np.std(mfccs[i])
            
            # Mel spectrogram features
            mel_spec = librosa.feature.melspectrogram(y=audio, sr=self.sample_rate, n_mels=self.mel_bands)
            features['mel_spec_mean'] = np.mean(mel_spec)
            features['mel_spec_std'] = np.std(mel_spec)
            
            # Chroma features
            chroma = librosa.feature.chroma_stft(y=audio, sr=self.sample_rate)
            features['chroma_mean'] = np.mean(chroma)
            features['chroma_std'] = np.std(chroma)
            
            # Tempo and beat features
            tempo, beats = librosa.beat.beat_track(y=audio, sr=self.sample_rate)
            features['tempo'] = tempo
            features['beat_count'] = len(beats)
            
            # Silence ratio
            silence_threshold = 0.01 * np.max(np.abs(audio))
            silence_samples = np.sum(np.abs(audio) < silence_threshold)
            features['silence_ratio'] = silence_samples / len(audio)
            
        except Exception as e:
            logger.error(f"Global feature extraction failed: {e}")
        
        return features
    
    def _extract_segment_features(self, segment: np.ndarray) -> Dict[str, Any]:
        """Extract features from audio segment"""
        features = {}
        
        try:
            # Basic segment features
            features['rms_energy'] = np.sqrt(np.mean(segment**2))
            features['zero_crossing_rate'] = np.mean(librosa.feature.zero_crossing_rate(segment)[0])
            
            # Spectral features
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=segment, sr=self.sample_rate)[0])
            features['spectral_centroid'] = spectral_centroid
            
            spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=segment, sr=self.sample_rate)[0])
            features['spectral_rolloff'] = spectral_rolloff
            
            # MFCC features (reduced for segments)
            mfccs = librosa.feature.mfcc(y=segment, sr=self.sample_rate, n_mfcc=13)
            features['mfcc_mean'] = np.mean(mfccs, axis=1)
            features['mfcc_std'] = np.std(mfccs, axis=1)
            
            # Pitch features
            pitches, magnitudes = librosa.piptrack(y=segment, sr=self.sample_rate)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if pitch_values:
                features['pitch_mean'] = np.mean(pitch_values)
                features['pitch_std'] = np.std(pitch_values)
            else:
                features['pitch_mean'] = 0
                features['pitch_std'] = 0
            
        except Exception as e:
            logger.error(f"Segment feature extraction failed: {e}")
        
        return features
    
    def _detect_suspicious_activities(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Detect suspicious activities using models"""
        results = {}
        
        try:
            # Prepare feature vector
            feature_vector = self._prepare_feature_vector(features)
            
            if feature_vector is not None:
                # Run stress detection
                if self.stress_detector is not None:
                    stress_confidence = self._run_model(self.stress_detector, feature_vector)
                    results[SuspiciousActivity.VOICE_STRESS] = stress_confidence
                
                # Run pattern analysis
                if self.pattern_analyzer is not None:
                    pattern_confidence = self._run_model(self.pattern_analyzer, feature_vector)
                    if pattern_confidence > self.confidence_threshold:
                        results[SuspiciousActivity.COORDINATED_CHEATING] = pattern_confidence
                    else:
                        results[SuspiciousActivity.UNUSUAL_PATTERN] = pattern_confidence
                
                # Run voice classification
                if self.voice_classifier is not None:
                    voice_confidence = self._run_model(self.voice_classifier, feature_vector)
                    results[SuspiciousActivity.MULTIPLE_VOICES] = voice_confidence
            
            # Rule-based detection
            rule_based_results = self._rule_based_detection(features)
            results.update(rule_based_results)
            
        except Exception as e:
            logger.error(f"Suspicious activity detection failed: {e}")
        
        return results
    
    def _prepare_feature_vector(self, features: Dict[str, Any]) -> Optional[torch.Tensor]:
        """Prepare feature vector for model input"""
        try:
            # Collect numeric features
            numeric_features = []
            
            # Basic features
            if 'rms_energy' in features:
                numeric_features.append(features['rms_energy'])
            if 'zero_crossing_rate' in features:
                numeric_features.append(features['zero_crossing_rate'])
            
            # Spectral features
            if 'spectral_centroid' in features:
                numeric_features.append(features['spectral_centroid'])
            if 'spectral_rolloff' in features:
                numeric_features.append(features['spectral_rolloff'])
            
            # MFCC features
            if 'mfcc_mean' in features:
                numeric_features.extend(features['mfcc_mean'])
            if 'mfcc_std' in features:
                numeric_features.extend(features['mfcc_std'])
            
            # Pitch features
            if 'pitch_mean' in features:
                numeric_features.append(features['pitch_mean'])
            if 'pitch_std' in features:
                numeric_features.append(features['pitch_std'])
            
            if len(numeric_features) == 0:
                return None
            
            # Convert to tensor
            feature_vector = torch.tensor(numeric_features, dtype=torch.float32)
            
            # Add batch and sequence dimensions
            feature_vector = feature_vector.unsqueeze(0).unsqueeze(0)
            
            # Move to device
            feature_vector = feature_vector.to(self.device)
            
            return feature_vector
            
        except Exception as e:
            logger.error(f"Feature vector preparation failed: {e}")
            return None
    
    def _run_model(self, model: nn.Module, feature_vector: torch.Tensor) -> float:
        """Run model and return confidence"""
        try:
            with torch.no_grad():
                outputs = model(feature_vector)
                confidence = outputs[0, 1].item()  # Probability of suspicious class
                return confidence
        except Exception as e:
            logger.error(f"Model inference failed: {e}")
            return 0.0
    
    def _rule_based_detection(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Rule-based suspicious activity detection"""
        results = {}
        
        try:
            # High energy detection (possible shouting/agitation)
            if 'rms_energy' in features:
                energy_threshold = 0.1  # Adjust based on calibration
                if features['rms_energy'] > energy_threshold:
                    results[SuspiciousActivity.VOICE_STRESS] = min(0.9, features['rms_energy'] * 5)
            
            # Unusual zero crossing rate (possible automated speech)
            if 'zero_crossing_rate' in features:
                zcr_threshold = 0.1
                if features['zero_crossing_rate'] > zcr_threshold:
                    results[SuspiciousActivity.AUTOMATED_RESPONSES] = min(0.8, features['zero_crossing_rate'] * 3)
            
            # Silence anomalies (possible coordination gaps)
            if 'silence_ratio' in features:
                silence_threshold = 0.3
                if features['silence_ratio'] > silence_threshold:
                    results[SuspiciousActivity.SILENCE_ANOMALIES] = min(0.7, features['silence_ratio'] * 2)
            
            # Spectral anomalies (possible background noise)
            if 'spectral_centroid' in features and 'spectral_rolloff' in features:
                centroid = features['spectral_centroid']
                rolloff = features['spectral_rolloff']
                
                # Unusual spectral characteristics
                if centroid < 1000 or rolloff < 2000:
                    results[SuspiciousActivity.BACKGROUND_NOISE] = 0.6
            
        except Exception as e:
            logger.error(f"Rule-based detection failed: {e}")
        
        return results
    
    def analyze_audio_stream(self, audio_chunk: np.ndarray) -> AudioAnalysisResult:
        """Analyze audio chunk for real-time processing"""
        # Synchronous version for streaming
        return asyncio.run(self.analyze_audio(audio_chunk))
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """Get analysis statistics"""
        return {
            "model_path": self.model_path,
            "device": self.device,
            "sample_rate": self.sample_rate,
            "confidence_threshold": self.confidence_threshold,
            "segment_duration": self.segment_duration,
            "models_loaded": {
                "stress_detector": self.stress_detector is not None,
                "pattern_analyzer": self.pattern_analyzer is not None,
                "voice_classifier": self.voice_classifier is not None
            }
        }
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update analysis settings"""
        if 'confidence_threshold' in settings:
            self.confidence_threshold = float(settings['confidence_threshold'])
        
        if 'segment_duration' in settings:
            self.segment_duration = float(settings['segment_duration'])
        
        if 'sample_rate' in settings:
            self.sample_rate = int(settings['sample_rate'])
        
        logger.info(f"Audio analysis settings updated: {settings}")

# Global instance
audio_analyzer = AudioAnalyzer()

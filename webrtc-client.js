// WebRTC Client Implementation for Voice and Video Calls
// Complete real-time communication with compliance recording

class WebRTCClient {
    constructor() {
        this.localStream = null;
        this.remoteStreams = new Map();
        this.peerConnections = new Map();
        this.currentCall = null;
        this.isRecording = false;
        this.mediaRecorder = null;
        this.recordedChunks = [];
        
        // Server configuration
        this.signalingServer = 'http://localhost:5003';
        this.videoSignalingServer = 'http://localhost:5004';
        
        // STUN/TURN servers
        this.configuration = {
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ]
        };
    }
    
    async initializeVoiceCall(callId, userId) {
        try {
            console.log('🎤 Initializing voice call...');
            
            // Get microphone access
            this.localStream = await navigator.mediaDevices.getUserMedia({
                audio: true,
                video: false
            });
            
            // Create peer connection
            const peerConnection = new RTCPeerConnection(this.configuration);
            
            // Add local stream
            this.localStream.getTracks().forEach(track => {
                peerConnection.addTrack(track, this.localStream);
            });
            
            // Handle ICE candidates
            peerConnection.onicecandidate = (event) => {
                if (event.candidate) {
                    this.sendSignal(callId, {
                        type: 'ice-candidate',
                        candidate: event.candidate
                    });
                }
            };
            
            // Handle remote streams
            peerConnection.ontrack = (event) => {
                console.log('🎤 Received remote audio stream');
                this.handleRemoteStream(event.streams[0], 'audio');
            };
            
            // Store connection
            this.peerConnections.set(callId, peerConnection);
            
            // Create offer
            const offer = await peerConnection.createOffer();
            await peerConnection.setLocalDescription(offer);
            
            // Send offer to signaling server
            this.sendSignal(callId, {
                type: 'offer',
                offer: offer
            });
            
            // Start recording for compliance
            this.startRecording('voice');
            
            // Join voice call room
            this.joinVoiceCall(callId, userId);
            
            return { success: true, callId };
            
        } catch (error) {
            console.error('❌ Voice call initialization failed:', error);
            return { success: false, error: error.message };
        }
    }
    
    async initializeVideoCall(callId, userId, quality = 'medium') {
        try {
            console.log('📹 Initializing video call...');
            
            // Get camera and microphone access
            this.localStream = await navigator.mediaDevices.getUserMedia({
                audio: true,
                video: {
                    width: quality === 'high' ? 1920 : quality === 'medium' ? 1280 : 640,
                    height: quality === 'high' ? 1080 : quality === 'medium' ? 720 : 480
                }
            });
            
            // Create peer connection
            const peerConnection = new RTCPeerConnection(this.configuration);
            
            // Add local stream
            this.localStream.getTracks().forEach(track => {
                peerConnection.addTrack(track, this.localStream);
            });
            
            // Handle ICE candidates
            peerConnection.onicecandidate = (event) => {
                if (event.candidate) {
                    this.sendVideoSignal(callId, {
                        type: 'ice-candidate',
                        candidate: event.candidate
                    });
                }
            };
            
            // Handle remote streams
            peerConnection.ontrack = (event) => {
                console.log('📹 Received remote video stream');
                this.handleRemoteStream(event.streams[0], 'video');
            };
            
            // Store connection
            this.peerConnections.set(callId, peerConnection);
            
            // Create offer
            const offer = await peerConnection.createOffer();
            await peerConnection.setLocalDescription(offer);
            
            // Send offer to video signaling server
            this.sendVideoSignal(callId, {
                type: 'offer',
                offer: offer
            });
            
            // Start recording for compliance
            this.startRecording('video');
            
            // Join video call room
            this.joinVideoCall(callId, userId);
            
            return { success: true, callId };
            
        } catch (error) {
            console.error('❌ Video call initialization failed:', error);
            return { success: false, error: error.message };
        }
    }
    
    async handleSignal(data) {
        const { callId, signal } = data;
        const peerConnection = this.peerConnections.get(callId);
        
        if (!peerConnection) return;
        
        try {
            if (signal.type === 'offer') {
                await peerConnection.setRemoteDescription(new RTCSessionDescription(signal.offer));
                const answer = await peerConnection.createAnswer();
                await peerConnection.setLocalDescription(answer);
                
                this.sendSignal(callId, {
                    type: 'answer',
                    answer: answer
                });
                
            } else if (signal.type === 'answer') {
                await peerConnection.setRemoteDescription(new RTCSessionDescription(signal.answer));
                
            } else if (signal.type === 'ice-candidate') {
                await peerConnection.addIceCandidate(new RTCIceCandidate(signal.candidate));
            }
        } catch (error) {
            console.error('❌ Signal handling failed:', error);
        }
    }
    
    async startScreenShare(callId) {
        try {
            console.log('🖥️ Starting screen share...');
            
            const screenStream = await navigator.mediaDevices.getDisplayMedia({
                video: true,
                audio: true
            });
            
            const peerConnection = this.peerConnections.get(callId);
            if (peerConnection) {
                // Replace video track with screen share
                const videoTrack = screenStream.getVideoTracks()[0];
                const sender = peerConnection.getSenders().find(s => 
                    s.track && s.track.kind === 'video'
                );
                
                if (sender) {
                    await sender.replaceTrack(videoTrack);
                }
                
                // Handle screen share end
                videoTrack.onended = () => {
                    console.log('🖥️ Screen share ended');
                    // Switch back to camera
                    this.switchToCamera(callId);
                };
            }
            
            return { success: true };
            
        } catch (error) {
            console.error('❌ Screen share failed:', error);
            return { success: false, error: error.message };
        }
    }
    
    async switchToCamera(callId) {
        try {
            const cameraStream = await navigator.mediaDevices.getUserMedia({
                video: true,
                audio: true
            });
            
            const peerConnection = this.peerConnections.get(callId);
            if (peerConnection) {
                const videoTrack = cameraStream.getVideoTracks()[0];
                const sender = peerConnection.getSenders().find(s => 
                    s.track && s.track.kind === 'video'
                );
                
                if (sender) {
                    await sender.replaceTrack(videoTrack);
                }
            }
            
        } catch (error) {
            console.error('❌ Camera switch failed:', error);
        }
    }
    
    startRecording(callType) {
        if (!this.localStream) return;
        
        this.recordedChunks = [];
        this.mediaRecorder = new MediaRecorder(this.localStream, {
            mimeType: callType === 'video' ? 'video/webm' : 'audio/webm'
        });
        
        this.mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                this.recordedChunks.push(event.data);
            }
        };
        
        this.mediaRecorder.onstop = () => {
            const blob = new Blob(this.recordedChunks, {
                type: callType === 'video' ? 'video/webm' : 'audio/webm'
            });
            this.saveRecording(blob, callType);
        };
        
        this.mediaRecorder.start();
        this.isRecording = true;
        
        console.log(`🔴 Started ${callType} recording for compliance`);
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            console.log('⏹️ Stopped recording');
        }
    }
    
    saveRecording(blob, callType) {
        // In a real implementation, this would upload to server
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${callType}-recording-${Date.now()}.webm`;
        a.click();
        
        console.log(`💾 Saved ${callType} recording for compliance`);
    }
    
    handleRemoteStream(stream, type) {
        const remoteVideo = document.createElement(type === 'video' ? 'video' : 'audio');
        remoteVideo.srcObject = stream;
        remoteVideo.autoplay = true;
        remoteVideo.playsinline = true;
        
        if (type === 'video') {
            remoteVideo.muted = false;
            remoteVideo.controls = true;
        }
        
        // Add to UI
        const remoteContainer = document.getElementById('remote-media');
        if (remoteContainer) {
            remoteContainer.innerHTML = '';
            remoteContainer.appendChild(remoteVideo);
        }
        
        this.remoteStreams.set(stream.id, stream);
    }
    
    async endCall(callId) {
        console.log('📞 Ending call...');
        
        // Stop recording
        this.stopRecording();
        
        // Stop local stream
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
        }
        
        // Close peer connections
        const peerConnection = this.peerConnections.get(callId);
        if (peerConnection) {
            peerConnection.close();
            this.peerConnections.delete(callId);
        }
        
        // Clear remote streams
        this.remoteStreams.clear();
        
        // Clear UI
        const remoteContainer = document.getElementById('remote-media');
        if (remoteContainer) {
            remoteContainer.innerHTML = '';
        }
        
        this.currentCall = null;
        
        console.log('✅ Call ended');
    }
    
    // Signaling methods
    async sendSignal(callId, signal) {
        try {
            const response = await fetch(`${this.signalingServer}/voice_signal`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    call_id: callId,
                    signal: signal,
                    from_user: 'current_user'
                })
            });
        } catch (error) {
            console.error('❌ Signal send failed:', error);
        }
    }
    
    async sendVideoSignal(callId, signal) {
        try {
            const response = await fetch(`${this.videoSignalingServer}/video_signal`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    call_id: callId,
                    signal: signal,
                    from_user: 'current_user'
                })
            });
        } catch (error) {
            console.error('❌ Video signal send failed:', error);
        }
    }
    
    async joinVoiceCall(callId, userId) {
        try {
            const response = await fetch(`${this.signalingServer}/join_voice_call`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    call_id: callId,
                    user_id: userId
                })
            });
        } catch (error) {
            console.error('❌ Join voice call failed:', error);
        }
    }
    
    async joinVideoCall(callId, userId) {
        try {
            const response = await fetch(`${this.videoSignalingServer}/join_video_call`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    call_id: callId,
                    user_id: userId
                })
            });
        } catch (error) {
            console.error('❌ Join video call failed:', error);
        }
    }
}

// Initialize WebRTC client
window.webrtcClient = new WebRTCClient();

// Socket.io for real-time signaling
const script = document.createElement('script');
script.src = 'https://cdn.socket.io/4.7.2/socket.io.min.js';
document.head.appendChild(script);

script.onload = () => {
    const voiceSocket = io('http://localhost:5003');
    const videoSocket = io('http://localhost:5004');
    
    // Handle voice signals
    voiceSocket.on('voice_signal', (data) => {
        window.webrtcClient.handleSignal(data);
    });
    
    // Handle video signals
    videoSocket.on('video_signal', (data) => {
        window.webrtcClient.handleSignal(data);
    });
};

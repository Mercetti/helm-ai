#!/usr/bin/env python3
"""
Stellar Logic AI - Ollama LLM Integration Server
Connects dashboard AI assistant to local Ollama instance and custom Stellar Logic AI model
"""

import requests
import json
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app, origins=['http://localhost:5000', 'http://localhost:8000', 'http://127.0.0.1:5000', 'http://127.0.0.1:8000'])

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
STELLAR_MODEL = "stellar-logic-ai:latest"  # Your custom model name with tag

class StellarLLM:
    def __init__(self):
        self.base_url = OLLAMA_BASE_URL
        self.model = STELLAR_MODEL
        self.conversation_history = {}
        
    def check_ollama_connection(self):
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def get_available_models(self):
        """Get list of available models from Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return [model['name'] for model in models]
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching models: {e}")
            return []
    
    def generate_response(self, prompt, context="", user_id="default"):
        """Generate response using Stellar Logic AI model"""
        try:
            # Build conversation context
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # Add context to prompt
            full_prompt = f"""
Business Context: Stellar Logic AI - 99.2% accuracy anti-cheat technology for gaming industry
Target: $5M funding from VC investors
Current Stage: Pre-seed with 27 investor prospects
User: Jamie Brown, Founder & CEO

Recent Context: {context}

User Message: {prompt}

Provide a helpful, strategic response focused on business growth, investor outreach, and market expansion.
"""
            
            # Call Ollama API
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result.get('response', '')
                
                # Store in conversation history
                self.conversation_history[user_id].append({
                    'user': prompt,
                    'ai': ai_response,
                    'timestamp': time.time()
                })
                
                # Keep only last 10 conversations
                if len(self.conversation_history[user_id]) > 10:
                    self.conversation_history[user_id] = self.conversation_history[user_id][-10:]
                
                return ai_response
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return "I'm having trouble connecting to my AI brain. Please check if Ollama is running."
                
        except requests.exceptions.Timeout:
            return "The AI is taking too long to respond. Please try again."
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return "I'm having trouble connecting to the AI service."
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return "Something went wrong. Please try again."

# Initialize LLM
stellar_llm = StellarLLM()

@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if the service is running and Ollama is accessible"""
    ollama_running = stellar_llm.check_ollama_connection()
    models = stellar_llm.get_available_models()
    
    return jsonify({
        'status': 'healthy',
        'ollama_running': ollama_running,
        'available_models': models,
        'stellar_model_available': STELLAR_MODEL in models
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint for AI assistant"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        message = data['message']
        context = data.get('context', '')
        user_id = data.get('user_id', 'default')
        
        # Generate AI response
        ai_response = stellar_llm.generate_response(message, context, user_id)
        
        return jsonify({
            'response': ai_response,
            'timestamp': time.time(),
            'model': STELLAR_MODEL
        })
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/models', methods=['GET'])
def list_models():
    """Get available models"""
    models = stellar_llm.get_available_models()
    return jsonify({
        'models': models,
        'current_model': STELLAR_MODEL
    })

@app.route('/api/email/generate', methods=['POST'])
def generate_email():
    """Generate personalized email using LLM"""
    try:
        data = request.get_json()
        
        investor_name = data.get('investor_name', '')
        investor_firm = data.get('investor_firm', '')
        custom_context = data.get('context', '')
        
        prompt = f"""
Generate a personalized email to {investor_name} at {investor_firm}.

Context: {custom_context}

Requirements:
1. Professional business email format
2. Clear subject line
3. Proper paragraph structure (3-4 paragraphs max)
4. Include specific details about Stellar Logic AI:
   - 99.2% accuracy anti-cheat technology
   - $15B annual gaming losses from cheating
   - 32 production modules
   - $5M funding goal
5. Clear call to action (15-minute meeting)
6. Jamie Brown's signature as Founder & CEO

Format the email with proper line breaks between paragraphs. Make it scannable and professional.
"""
        
        ai_response = stellar_llm.generate_response(prompt, custom_context)
        
        return jsonify({
            'email': ai_response,
            'investor': investor_name,
            'firm': investor_firm
        })
        
    except Exception as e:
        logger.error(f"Email generation error: {e}")
        return jsonify({'error': 'Failed to generate email'}), 500

@app.route('/api/research', methods=['POST'])
def research():
    """Conduct research using LLM"""
    try:
        data = request.get_json()
        research_query = data.get('query', '')
        research_type = data.get('type', 'market')
        
        context = f"Research request: {research_type} analysis for {research_query}"
        
        prompt = f"""
Conduct comprehensive {research_type} research on: {research_query}

Provide insights on:
- Current market trends
- Key players and competitors
- Opportunities and challenges
- Strategic recommendations for Stellar Logic AI

Focus on actionable intelligence for business growth and investor relations.
"""
        
        ai_response = stellar_llm.generate_response(prompt, context)
        
        return jsonify({
            'research': ai_response,
            'query': research_query,
            'type': research_type
        })
        
    except Exception as e:
        logger.error(f"Research error: {e}")
        return jsonify({'error': 'Failed to conduct research'}), 500

if __name__ == '__main__':
    print("🚀 Starting Stellar Logic AI LLM Integration Server...")
    print(f"🌐 Connecting to Ollama at: {OLLAMA_BASE_URL}")
    print(f"⭐ Using model: {STELLAR_MODEL}")
    
    # Check Ollama connection
    if stellar_llm.check_ollama_connection():
        print("✅ Ollama connection successful!")
        models = stellar_llm.get_available_models()
        print(f"📋 Available models: {', '.join(models)}")
        
        # Check if Stellar Logic AI model exists
        if STELLAR_MODEL in models:
            print(f"✅ Stellar Logic AI model found: {STELLAR_MODEL}")
        else:
            print(f"⚠️  Stellar Logic AI model not found. Available models:")
            for model in models:
                print(f"  • {model}")
            print(f"💡 Your {STELLAR_MODEL} model is already created!")
        
        # Start Flask server
        app.run(host='0.0.0.0', port=5001, debug=True)

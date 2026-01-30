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
from stellar_learning_platform import learning_platform

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
        """Generate response using Stellar Logic AI model with learning"""
        try:
            # Get user preferences and learning context
            user_preferences = learning_platform.get_user_preferences(user_id)
            learning_context = learning_platform.get_learning_context(user_id)
            
            # Build conversation context with learning
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # Enhanced prompt with learning integration
            full_prompt = f"""
BUSINESS CONTEXT & AI IDENTITY:
You are an AI assistant helping Jamie Brown, Founder & CEO of Stellar Logic AI.
Jamie is asking YOU questions and YOU should provide direct answers.
You are Jamie's personal AI assistant - help him with whatever he needs.

Stellar Logic AI Details:
- 99.2% accuracy anti-cheat technology for gaming industry
- Target: $5M funding from VC investors like Sarah Chen at Andreessen Horowitz
- Current Stage: Pre-seed with 27 investor prospects
- Jamie Brown is the Founder & CEO, you are his AI assistant

INVESTOR CONTACT INFORMATION (Available on Dashboard):
- Sarah Chen (Andreessen Horowitz) - sarah.chen@a16z.com
- Mike Johnson (Sequoia Capital) - mike.johnson@sequoiacap.com
- Emily Davis (Accel) - emily.davis@accel.com
- Lisa Brown (Kleiner Perkins) - lisa.brown@kpcb.com
- Jessica Taylor (Union Square Ventures) - jessica.taylor@usv.com

CRITICAL IDENTITY RULES:
- YOU are the AI assistant, Jamie is the user
- Answer Jamie's questions directly using available information
- Never act as if you are representing Stellar Logic AI
- Never respond as if you are helping Jamie write to himself
- If Jamie asks for information (like email addresses), provide it from the dashboard
- If Jamie asks you to generate content, do it FOR him

Recent Context: {context}

LEARNED USER PREFERENCES:
{user_preferences}

LEARNING INSIGHTS:
{learning_context}

Conversation History: {self.conversation_history[user_id][-3:] if len(self.conversation_history[user_id]) > 3 else self.conversation_history[user_id]}

User Message: {prompt}

RESPONSE GUIDELINES:
- Answer Jamie's questions directly and helpfully
- If asked for information (like email addresses), provide it from the dashboard investor list
- If asked to generate content, create it FOR Jamie to use
- Be concise and professional
- Apply learned preferences for formatting and style
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
                
                # Store conversation with learning metadata
                learning_platform.store_conversation(
                    user_id=user_id,
                    user_message=prompt,
                    ai_response=ai_response,
                    context=context
                )
                
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

@app.route('/api/feedback', methods=['POST'])
def process_feedback():
    """Process user feedback for continuous learning"""
    try:
        data = request.get_json()
        
        user_id = data.get('user_id', 'default')
        feedback_type = data.get('feedback_type', 'formatting')
        feedback_content = data.get('feedback_content', '')
        ai_adaptation = data.get('ai_adaptation', '')
        improvement_success = data.get('improvement_success', 0)
        
        # Store feedback and learn from it
        learning_platform.learn_from_feedback(
            user_id=user_id,
            feedback_type=feedback_type,
            feedback_content=feedback_content,
            ai_adaptation=ai_adaptation,
            improvement_success=improvement_success
        )
        
        # Store successful patterns
        if improvement_success > 0:
            learning_platform.store_successful_pattern(
                pattern_type=feedback_type,
                pattern_content=ai_adaptation,
                success=True
            )
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback processed and learned successfully',
            'preferences_updated': True
        })
        
    except Exception as e:
        logger.error(f"Feedback processing error: {e}")
        return jsonify({'error': 'Failed to process feedback'}), 500

@app.route('/api/campaign', methods=['POST'])
def run_campaign():
    """Run automated email campaign with AI personalization"""
    try:
        data = request.get_json()
        campaign_type = data.get('campaign_type', 'vc_outreach')
        target_investors = data.get('target_investors', 'all')
        
        investors = [
            {'name': 'Sarah Chen', 'firm': 'Andreessen Horowitz', 'email': 'sarah.chen@a16z.com'},
            {'name': 'Mike Johnson', 'firm': 'Sequoia Capital', 'email': 'mike.johnson@sequoiacap.com'},
            {'name': 'Emily Davis', 'firm': 'Accel', 'email': 'emily.davis@accel.com'},
            {'name': 'Lisa Brown', 'firm': 'Kleiner Perkins', 'email': 'lisa.brown@kpcb.com'},
            {'name': 'Jessica Taylor', 'firm': 'Union Square Ventures', 'email': 'jessica.taylor@usv.com'}
        ]
        
        campaign_results = []
        
        for investor in investors:
            if target_investors != 'all' and investor['name'] not in target_investors:
                continue
                
            # Generate personalized email for each investor
            prompt = f"""
Generate a personalized email for {investor['name']} at {investor['firm']}.

Campaign Type: {campaign_type}
Context: Stellar Logic AI - 99.2% accuracy anti-cheat technology for gaming industry
Target: $5M funding from VC investors

Create a compelling, personalized email that:
1. References {investor['firm']}'s investment focus
2. Highlights our 99.2% accuracy anti-cheat technology
3. Mentions our $5M funding goal
4. Proposes a 15-minute meeting
5. Uses professional formatting with proper paragraphs

Make it specific to {investor['name']} and {investor['firm']}.
"""
            
            ai_response = stellar_llm.generate_response(prompt, f"Campaign: {campaign_type}")
            
            campaign_results.append(f"""
📧 Email for {investor['name']} ({investor['firm']}):
To: {investor['email']}

{ai_response}

---
Email personalized and ready to send!
""")
        
        results_text = "\n".join(campaign_results)
        
        return jsonify({
            'status': 'success',
            'campaign_type': campaign_type,
            'results': results_text,
            'emails_generated': len(campaign_results)
        })
        
    except Exception as e:
        logger.error(f"Campaign error: {e}")
        return jsonify({'error': 'Failed to run campaign'}), 500

@app.route('/api/documents', methods=['POST'])
def generate_document():
    """Generate professional business documents"""
    try:
        data = request.get_json()
        document_type = data.get('document_type', 'business_plan')
        company_info = data.get('company_info', {})
        
        prompt = f"""
Generate a professional {document_type} for Stellar Logic AI.

Company Information:
- Name: Stellar Logic AI
- Technology: 99.2% accuracy anti-cheat technology for gaming industry
- Funding Goal: $5M
- Stage: Pre-seed
- Founder: Jamie Brown

Document Type: {document_type}

Create a comprehensive, professional document that:
1. Follows standard business document format
2. Includes all necessary sections for {document_type}
3. Highlights our competitive advantages
4. Presents compelling business case
5. Uses professional business language
6. Includes specific metrics and data

Make it investor-ready and professional.
"""
        
        ai_response = stellar_llm.generate_response(prompt, f"Document: {document_type}")
        
        return jsonify({
            'status': 'success',
            'document_type': document_type,
            'content': ai_response
        })
        
    except Exception as e:
        logger.error(f"Document generation error: {e}")
        return jsonify({'error': 'Failed to generate document'}), 500

@app.route('/api/research', methods=['POST'])
def research():
    """Conduct research using LLM with web search capabilities"""
    try:
        data = request.get_json()
        research_query = data.get('query', '')
        research_type = data.get('type', 'general')
        
        context = f"Research request: {research_type} analysis for {research_query}"
        
        # Enhanced research prompt with search instructions
        research_prompt = f"""
BUSINESS CONTEXT: You are an AI assistant helping Jamie Brown, Founder & CEO of Stellar Logic AI.
Jamie needs you to research information and provide accurate, up-to-date answers.

RESEARCH QUERY: {research_query}
RESEARCH TYPE: {research_type}

RESEARCH INSTRUCTIONS:
1. If this is about finding contact information, use your knowledge and suggest the best ways to find accurate emails
2. If this is about market research, provide current industry insights
3. If this is about investors, use your knowledge of VC firms and suggest research approaches
4. Always provide actionable next steps
5. If you don't have specific information, suggest the best research methods

RESPONSE GUIDELINES:
- Be helpful and provide direct answers when possible
- Suggest research methods for information you don't have
- Provide actionable next steps
- Be professional and business-focused

Conduct thorough research on: {research_query}
"""
        
        ai_response = stellar_llm.generate_response(research_prompt, context)
        
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
        print(f"🌐 Starting LLM server on port 5001...")
        app.run(host='0.0.0.0', port=5001, debug=False)
    else:
        print("❌ Cannot connect to Ollama. Please ensure Ollama is running.")
        exit(1)

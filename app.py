from http.server import BaseHTTPRequestHandler
import json
import base64
import requests
import tempfile
import os

class Handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        try:
            # Get request data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            if 'audio' not in data:
                return self.send_error_response("Missing 'audio' field", 400)
            
            # Extract base64 audio
            audio_b64 = data['audio']
            if ',' in audio_b64:
                audio_b64 = audio_b64.split(',')[1]
            
            # Decode base64
            try:
                audio_data = base64.b64decode(audio_b64)
            except:
                return self.send_error_response("Invalid base64 audio data", 400)
            
            # Use external speech-to-text service
            text = self.transcribe_with_external_api(audio_data)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "success": True,
                "text": text,
                "service": "external_api"
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            return self.send_error_response(f"Server error: {str(e)}", 500)
    
    def transcribe_with_external_api(self, audio_data):
        """Use free external speech-to-text APIs"""
        try:
            # Option 1: Hugging Face Inference API (Free)
            return self.try_hugging_face(audio_data)
        except:
            try:
                # Option 2: AssemblyAI (Free tier)
                return self.try_assembly_ai(audio_data)
            except:
                return "Speech-to-text service temporarily unavailable"
    
    def try_hugging_face(self, audio_data):
        """Try Hugging Face Whisper API"""
        API_URL = "https://api-inference.huggingface.co/models/openai/whisper-large-v3"
        headers = {"Authorization": "Bearer hf_your_token_here"}
        
        # Save audio to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
            f.write(audio_data)
            temp_path = f.name
        
        try:
            with open(temp_path, "rb") as f:
                response = requests.post(API_URL, headers=headers, data=f)
            
            result = response.json()
            return result.get('text', 'No transcription available')
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def try_assembly_ai(self, audio_data):
        """Try AssemblyAI (replace with your API key)"""
        # This is just a template - you'll need to sign up for free API key
        return "Sign up for free at assemblyai.com for speech-to-text API"
    
    def send_error_response(self, error_msg, status_code=500):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {
            "success": False,
            "error": error_msg
        }
        self.wfile.write(json.dumps(response).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        """Health check"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {
            "status": "active",
            "service": "Speech-to-Text API",
            "version": "1.0",
            "message": "API is running. Use POST /api/transcribe with audio data."
        }
        self.wfile.write(json.dumps(response).encode())

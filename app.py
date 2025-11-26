from http.server import BaseHTTPRequestHandler
import json
import requests
import base64
import tempfile
import os

class Handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        try:
            # Get audio data from request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            if 'audio' not in data:
                return self.send_error_response("Missing 'audio' field")
            
            # Extract base64 audio
            audio_b64 = data['audio']
            if ',' in audio_b64:
                audio_b64 = audio_b64.split(',')[1]
            
            # Decode base64
            try:
                audio_data = base64.b64decode(audio_b64)
            except:
                return self.send_error_response("Invalid base64 audio data")
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as f:
                f.write(audio_data)
                temp_path = f.name
            
            try:
                # Use Web Speech API (free)
                text = self.transcribe_with_speech_recognition(temp_path)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    "success": True,
                    "text": text,
                    "service": "web_speech_api"
                }
                
                self.wfile.write(json.dumps(response).encode())
                
            except Exception as e:
                return self.send_error_response(f"Transcription failed: {str(e)}")
            
            finally:
                # Cleanup
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            return self.send_error_response(f"Server error: {str(e)}")
    
    def transcribe_with_speech_recognition(self, audio_path):
        """Simple transcription using external service"""
        # You can replace this with any free speech-to-text API
        # For now, returning a placeholder
        return "Speech-to-text functionality would be implemented here"
    
    def send_error_response(self, error_msg):
        self.send_response(500)
        self.send_header('Content-type', 'application/json')
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
            "version": "1.0"
        }
        self.wfile.write(json.dumps(response).encode())

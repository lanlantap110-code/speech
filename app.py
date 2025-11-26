from flask import Flask, request, jsonify
from flask_cors import CORS
from vosk import Model, KaldiRecognizer
import json
import wave
import tempfile
import os
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global model variable
model = None

def load_model():
    """Vosk model load karein"""
    global model
    try:
        # Model paths try karein
        model_paths = [
            "model",
            "vosk-model-small-en-us-0.15",
            "/tmp/model"
        ]
        
        for path in model_paths:
            if os.path.exists(path):
                print(f"Loading model from: {path}")
                model = Model(path)
                print("Model loaded successfully!")
                return
        
        # Agar model nahi mila toh error
        raise Exception("Vosk model not found. Please download model.")
        
    except Exception as e:
        print(f"Model loading error: {str(e)}")
        raise e

@app.before_first_request
def initialize_model():
    """First request se pehle model load karein"""
    load_model()

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        "status": "active",
        "service": "Vosk Speech-to-Text API",
        "version": "1.0",
        "model_loaded": model is not None
    })

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    """Audio transcription endpoint"""
    try:
        # Check if model is loaded
        if model is None:
            load_model()
            if model is None:
                return jsonify({
                    "success": False,
                    "error": "Speech model not available"
                }), 500

        # Get JSON data
        data = request.get_json()
        if not data or 'audio' not in data:
            return jsonify({
                "success": False,
                "error": "Missing 'audio' field in request"
            }), 400

        # Extract base64 audio
        audio_b64 = data['audio']
        if ',' in audio_b64:
            audio_b64 = audio_b64.split(',')[1]

        # Decode base64
        try:
            audio_data = base64.b64decode(audio_b64)
        except:
            return jsonify({
                "success": False,
                "error": "Invalid base64 audio data"
            }), 400

        # Create temporary WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name

        try:
            # Open audio file
            wf = wave.open(temp_path, 'rb')
            
            # Check audio format
            if wf.getnchannels() != 1:
                return jsonify({
                    "success": False,
                    "error": "Audio must be mono (1 channel)"
                }), 400
            
            if wf.getsampwidth() != 2:
                return jsonify({
                    "success": False, 
                    "error": "Audio must be 16-bit PCM format"
                }), 400

            # Initialize recognizer
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)

            # Process audio in chunks
            results = []
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    results.append(result)

            # Get final result
            final_result = json.loads(rec.FinalResult())
            results.append(final_result)

            # Extract text from all results
            full_text = " ".join([
                result.get('text', '') 
                for result in results 
                if result.get('text')
            ]).strip()

            wf.close()

            return jsonify({
                "success": True,
                "text": full_text,
                "language": "auto",
                "model": "vosk"
            })

        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Audio processing failed: {str(e)}"
            }), 500

        finally:
            # Cleanup temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500

@app.route('/languages', methods=['GET'])
def available_languages():
    """Available languages batayein"""
    return jsonify({
        "languages": ["en", "hi", "es", "fr", "de", "cn"],
        "default": "en",
        "note": "Download specific model for each language"
    })

@app.route('/model/status', methods=['GET'])
def model_status():
    """Model status check karein"""
    return jsonify({
        "model_loaded": model is not None,
        "model_type": "vosk",
        "status": "ready" if model else "not_loaded"
    })

if __name__ == '__main__':
    # Pre-load model on startup
    print("Loading Vosk model...")
    try:
        load_model()
        print("Model loaded successfully!")
    except Exception as e:
        print(f"Model loading failed: {e}")
    
    # Start Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )

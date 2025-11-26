import os
import requests
import zipfile

def download_model():
    """Vosk model download karein"""
    model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
    model_dir = "model"
    
    if not os.path.exists(model_dir):
        print("Downloading Vosk model...")
        
        # Download zip file
        response = requests.get(model_url, stream=True)
        zip_path = "model.zip"
        
        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Extract model
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(".")
        
        # Rename to 'model'
        extracted_dir = "vosk-model-small-en-us-0.15"
        if os.path.exists(extracted_dir):
            os.rename(extracted_dir, model_dir)
        
        # Cleanup
        os.remove(zip_path)
        print("Model downloaded successfully!")
    else:
        print("Model already exists!")

if __name__ == "__main__":
    download_model()

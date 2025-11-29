import os
import requests
from typing import Dict, Any, Optional
from .base import BasePublisher

class WhatsAppPublisher(BasePublisher):
    def __init__(self):
        super().__init__()
        self.whapi_token = os.getenv("WHAPI_TOKEN")

    def publish(self, text: str, media_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Publishes content to WhatsApp using Whapi.cloud API.
        Sends image with caption using stories/send/media endpoint.
        """
        if not self.whapi_token:
            return {"error": "CONFIG_ERROR", "message": "Whapi.cloud token (WHAPI_TOKEN) not configured."}

        if not media_url:
            return {"error": "NO_MEDIA", "message": "WhatsApp stories require an image. No media provided."}

        # Whapi.cloud endpoint
        url = "https://gate.whapi.cloud/stories/send/media"
        
        headers = {
            "Authorization": f"Bearer {self.whapi_token}"
        }
        
        try:
            # Check if URL is local (starts with http://127.0.0.1 or http://localhost)
            # In that case, read the file directly from disk
            if media_url.startswith(("http://127.0.0.1", "http://localhost")):
                # Extract local file path from URL
                # URL format: http://127.0.0.1:8080/static/media/filename.png
                # We need: /app/static/media/filename.png
                import re
                match = re.search(r'/static/media/(.+)$', media_url)
                if match:
                    filename = match.group(1)
                    local_path = f"/app/static/media/{filename}"
                    print(f"📂 Reading local file: {local_path}")
                    
                    try:
                        with open(local_path, 'rb') as f:
                            image_content = f.read()
                    except FileNotFoundError:
                        return {"error": "FILE_NOT_FOUND", "message": f"Local file not found: {local_path}"}
                else:
                    return {"error": "INVALID_URL", "message": "Could not extract filename from local URL"}
            else:
                print(f"Descargando imagen de: {media_url}")
                image_response = requests.get(media_url, timeout=10)
                
                if image_response.status_code != 200:
                    return {"error": "DOWNLOAD_ERROR", "message": f"Failed to download image: {image_response.status_code}"}
                
                image_content = image_response.content
            
            # Prepare multipart/form-data
            files = {
                'media': ('image.png', image_content, 'image/png')
            }
            
            data = {
                'mime_type': 'image/png',
                'caption': text
            }
            
            print(f"Subiendo a Whapi.cloud con caption: {text[:50]}...")
            response = requests.post(url, headers=headers, files=files, data=data, timeout=30)
            
            if response.status_code in [200, 201]:
                print(f"Historia de WhatsApp publicada exitosamente")
                return {"success": True, "details": {"status": response.status_code, "response": response.json()}}
            else:
                error_msg = f"Error enviando media: {response.text}"
                print(f"{error_msg}")
                return {"error": "API_ERROR", "message": error_msg}

        except requests.exceptions.Timeout:
            return {"error": "TIMEOUT", "message": "Request timed out while uploading to Whapi.cloud"}
        except requests.exceptions.RequestException as e:
            return {"error": "REQUEST_ERROR", "message": f"Network error: {str(e)}"}
        except Exception as e:
            return {"error": "EXCEPTION", "message": str(e)}

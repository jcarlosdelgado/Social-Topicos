import os
import requests
from typing import Dict, Any, Optional
from .base import BasePublisher

class InstagramPublisher(BasePublisher):
    def __init__(self):
        super().__init__()
        self.instagram_account_id = os.getenv("IG_BUSINESS_ACCOUNT_ID")
        self.facebook_access_token = os.getenv("FB_PAGE_ACCESS_TOKEN")
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def publish(self, text: str, media_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Publishes a photo to Instagram Business Account.
        Requires two steps: 1. Create Media Container, 2. Publish Container.
        IMPORTANT: Instagram API REQUIRES a public URL. Localhost will fail.
        """
        if not self.instagram_account_id or not self.facebook_access_token:
             return {"error": "CONFIG_ERROR", "message": "Instagram credentials not configured."}

        if not media_url:
            return {"error": "VALIDATION_ERROR", "message": "Image URL is required for Instagram."}
            
        if "127.0.0.1" in media_url or "localhost" in media_url:
            return {
                "error": "LOCALHOST_ERROR", 
                "message": "Instagram requiere una URL pública (https). No puede acceder a tu localhost. Para probar esto localmente, necesitas usar una herramienta como 'ngrok' para exponer tu servidor."
            }

        # Validate that the URL actually returns an image (and not a warning page from ngrok/localtunnel)
        try:
            head_response = requests.head(media_url, timeout=5)
            content_type = head_response.headers.get("Content-Type", "")
            if "image" not in content_type:
                return {
                    "error": "INVALID_MEDIA_TYPE",
                    "message": f"La URL pública no devuelve una imagen, sino '{content_type}'. Esto suele pasar con ngrok/localtunnel gratuitos que muestran una página de advertencia. Prueba usar 'serveo.net' o un túnel sin página de espera."
                }
        except Exception as e:
            print(f"Warning: Could not validate image URL: {e}")

        try:
            # Step 1: Create Media Container
            container_url = f"{self.base_url}/{self.instagram_account_id}/media"
            container_payload = {
                "image_url": media_url,
                "caption": text,
                "access_token": self.facebook_access_token
            }
            
            response = requests.post(container_url, params=container_payload)
            container_data = response.json()

            if "error" in container_data:
                return {"error": "API_ERROR_STEP_1", "message": container_data["error"]["message"]}

            creation_id = container_data.get("id")

            # Step 2: Publish Media Container
            publish_url = f"{self.base_url}/{self.instagram_account_id}/media_publish"
            publish_payload = {
                "creation_id": creation_id,
                "access_token": self.facebook_access_token
            }

            response = requests.post(publish_url, params=publish_payload)
            publish_data = response.json()

            if "error" in publish_data:
                return {"error": "API_ERROR_STEP_2", "message": publish_data["error"]["message"]}

            return {"success": True, "id": publish_data.get("id")}

        except Exception as e:
            return {"error": "EXCEPTION", "message": str(e)}

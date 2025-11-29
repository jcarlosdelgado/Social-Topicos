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
            "Authorization": f"Bearer {self.wa_token}",
            "Content-Type": "application/json"
        }
        
        results = []
        
        try:
            # 1. Send Image (if available)
            if media_url:
                payload_image = {
                    "messaging_product": "whatsapp",
                    "to": self.wa_recipient,
                    "type": "image",
                    "image": {
                        "link": media_url
                    }
                }
                resp_img = requests.post(url, headers=headers, json=payload_image)
                results.append({"type": "image", "status": resp_img.status_code, "response": resp_img.json()})
                
                if resp_img.status_code not in [200, 201]:
                     return {"error": "API_ERROR_IMAGE", "message": resp_img.json().get("error", {}).get("message", "Unknown error sending image")}

            # 2. Send Text
            payload_text = {
                "messaging_product": "whatsapp",
                "to": self.wa_recipient,
                "type": "text",
                "text": {
                    "body": text
                }
            }
            resp_text = requests.post(url, headers=headers, json=payload_text)
            results.append({"type": "text", "status": resp_text.status_code, "response": resp_text.json()})

            if resp_text.status_code not in [200, 201]:
                 return {"error": "API_ERROR_TEXT", "message": resp_text.json().get("error", {}).get("message", "Unknown error sending text")}

            return {"success": True, "details": results}

        except Exception as e:
            return {"error": "EXCEPTION", "message": str(e)}

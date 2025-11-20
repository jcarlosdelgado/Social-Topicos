import os
import requests
from typing import Dict, Any, Optional
from .base import BasePublisher

class WhatsAppPublisher(BasePublisher):
    def __init__(self):
        super().__init__()
        self.wa_token = os.getenv("WHATSAPP_API_TOKEN")
        self.wa_phone_id = os.getenv("WHATSAPP_PHONE_ID")
        self.wa_recipient = os.getenv("WHATSAPP_RECIPIENT_PHONE")

    def publish(self, text: str, media_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Publishes content to WhatsApp Cloud API.
        Sends image first (if available), then text.
        """
        if not self.wa_token or not self.wa_phone_id or not self.wa_recipient:
            return {"error": "CONFIG_ERROR", "message": "WhatsApp credentials (TOKEN, PHONE_ID, RECIPIENT) not configured."}

        url = f"https://graph.facebook.com/v22.0/{self.wa_phone_id}/messages"
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

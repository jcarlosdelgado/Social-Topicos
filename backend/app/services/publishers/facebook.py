import os
import requests
from typing import Dict, Any, Optional
from .base import BasePublisher

class FacebookPublisher(BasePublisher):
    def __init__(self):
        super().__init__()
        self.facebook_page_id = os.getenv("FB_PAGE_ID")
        self.facebook_access_token = os.getenv("FB_PAGE_ACCESS_TOKEN")
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def publish(self, text: str, media_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Publishes a post to the Facebook Page.
        If media_url is provided, publishes a photo. 
        If the URL is local, uploads the file binary. Otherwise, uses the URL.
        """
        if not self.facebook_page_id or not self.facebook_access_token:
            return {"error": "CONFIG_ERROR", "message": "Facebook credentials not configured."}

        try:
            if media_url:
                url = f"{self.base_url}/{self.facebook_page_id}/photos"
                local_path = self._get_local_path_from_url(media_url)
                
                if local_path:
                    # Upload local file binary
                    payload = {
                        "message": text,
                        "access_token": self.facebook_access_token
                    }
                    files = {
                        'source': open(local_path, 'rb')
                    }
                    response = requests.post(url, data=payload, files=files)
                else:
                    # Use public URL
                    payload = {
                        "url": media_url,
                        "message": text,
                        "access_token": self.facebook_access_token
                    }
                    response = requests.post(url, params=payload)
            else:
                url = f"{self.base_url}/{self.facebook_page_id}/feed"
                payload = {
                    "message": text,
                    "access_token": self.facebook_access_token
                }
                response = requests.post(url, params=payload)

            data = response.json()

            if "error" in data:
                return {"error": "API_ERROR", "message": data["error"]["message"]}
            
            return {"success": True, "id": data.get("id"), "post_id": data.get("post_id")}

        except Exception as e:
            return {"error": "EXCEPTION", "message": str(e)}

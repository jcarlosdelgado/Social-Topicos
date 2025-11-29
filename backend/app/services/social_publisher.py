from typing import Dict, Any, Optional
from .publishers import FacebookPublisher, InstagramPublisher, LinkedInPublisher, WhatsAppPublisher, TikTokPublisher

class SocialPublisher:
    def __init__(self):
        self.facebook = FacebookPublisher()
        self.instagram = InstagramPublisher()
        self.linkedin = LinkedInPublisher()
        self.whatsapp = WhatsAppPublisher()
        self.tiktok = TikTokPublisher()

    def publish_facebook(self, message: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        return self.facebook.publish(message, image_url)

    def publish_instagram(self, caption: str, image_url: str) -> Dict[str, Any]:
        return self.instagram.publish(caption, image_url)

    def publish_whatsapp(self, text: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        return self.whatsapp.publish(text, image_url)

    def publish_linkedin(self, text: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        return self.linkedin.publish(text, image_url)

    def publish_tiktok(self, text: str, video_path: Optional[str] = None) -> Dict[str, Any]:
        return self.tiktok.publish(text, video_path)

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.social_publisher import SocialPublisher


class TestSocialPublisher:
    
    def setup_method(self):
        self.publisher = SocialPublisher()
    
    @patch('app.services.social_publisher.FacebookPublisher')
    def test_publish_facebook_success(self, mock_fb_publisher):
        mock_instance = MagicMock()
        mock_instance.publish.return_value = {
            "success": True,
            "post_id": "123456789",
            "message": "Published successfully"
        }
        mock_fb_publisher.return_value = mock_instance
        
        publisher = SocialPublisher()
        result = publisher.publish_facebook(
            message="Test post",
            image_url="https://example.com/image.png"
        )
        
        assert result["success"] is True
        assert "post_id" in result
    
    @patch('app.services.social_publisher.InstagramPublisher')
    def test_publish_instagram_success(self, mock_ig_publisher):
        mock_instance = MagicMock()
        mock_instance.publish.return_value = {
            "success": True,
            "media_id": "IG123456",
            "message": "Published to Instagram"
        }
        mock_ig_publisher.return_value = mock_instance
        
        publisher = SocialPublisher()
        result = publisher.publish_instagram(
            caption="Test caption #test",
            image_url="https://example.com/photo.jpg"
        )
        
        assert result["success"] is True
        assert "media_id" in result
    
    @patch('app.services.social_publisher.LinkedInPublisher')
    def test_publish_linkedin_success(self, mock_li_publisher):
        mock_instance = MagicMock()
        mock_instance.publish.return_value = {
            "success": True,
            "share_id": "LI987654",
            "message": "Posted to LinkedIn"
        }
        mock_li_publisher.return_value = mock_instance
        
        publisher = SocialPublisher()
        result = publisher.publish_linkedin(
            text="Professional update",
            image_url="https://example.com/business.jpg"
        )
        
        assert result["success"] is True
        assert "share_id" in result
    
    @patch('app.services.social_publisher.TikTokPublisher')
    def test_publish_tiktok_with_video(self, mock_tiktok_publisher):
        mock_instance = MagicMock()
        mock_instance.publish.return_value = {
            "success": True,
            "publish_id": "TT456789",
            "message": "Video uploaded to TikTok"
        }
        mock_tiktok_publisher.return_value = mock_instance
        
        publisher = SocialPublisher()
        result = publisher.publish_tiktok(
            text="Viral video #fyp",
            video_path="/tmp/test_video.mp4"
        )
        
        assert result["success"] is True
        assert "publish_id" in result
    
    @patch('app.services.social_publisher.WhatsAppPublisher')
    def test_publish_whatsapp_success(self, mock_wa_publisher):
        mock_instance = MagicMock()
        mock_instance.publish.return_value = {
            "success": True,
            "message_id": "WA789012",
            "message": "Story posted to WhatsApp"
        }
        mock_wa_publisher.return_value = mock_instance
        
        publisher = SocialPublisher()
        result = publisher.publish_whatsapp(
            text="Check this out!",
            image_url="https://example.com/story.jpg"
        )
        
        assert result["success"] is True
        assert "message_id" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

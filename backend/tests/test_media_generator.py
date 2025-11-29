import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import os
from pathlib import Path
from app.services.media_generator import MediaGenerator


class TestMediaGenerator:
    
    def setup_method(self):
        self.generator = MediaGenerator()
    
    @patch('app.services.media_generator.OpenAI')
    @patch('app.services.media_generator.requests.get')
    def test_generate_image_success(self, mock_requests, mock_openai):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [MagicMock()]
        mock_response.data[0].url = "https://example.com/image.png"
        mock_client.images.generate.return_value = mock_response
        
        mock_http_response = MagicMock()
        mock_http_response.content = b"fake_image_data"
        mock_http_response.raise_for_status = MagicMock()
        mock_requests.return_value = mock_http_response
        
        generator = MediaGenerator()
        generator.client = mock_client
        
        with patch('tempfile.mkstemp') as mock_mkstemp:
            mock_fd = 123
            mock_path = "/tmp/test_image.png"
            mock_mkstemp.return_value = (mock_fd, mock_path)
            
            with patch('os.fdopen', mock_open()) as mock_file:
                path, url = generator.generate_image("Test prompt")
                
                assert path == mock_path
                assert url == "https://example.com/image.png"
                mock_client.images.generate.assert_called_once()
    
    def test_get_public_url_image(self):
        test_path = str(self.generator.media_dir / "test123.png")
        url = self.generator.get_public_url(test_path)
        
        assert "static/media/test123.png" in url
        assert "http" in url
    
    def test_get_public_url_video(self):
        test_path = str(self.generator.video_dir / "test456.mp4")
        url = self.generator.get_public_url(test_path)
        
        assert "static/videos/test456.mp4" in url
        assert "http" in url
    
    def test_get_localhost_url(self):
        test_path = str(self.generator.media_dir / "local_test.png")
        url = self.generator.get_localhost_url(test_path)
        
        assert url.startswith("http://127.0.0.1")
        assert "static/media/local_test.png" in url
    
    def test_generate_image_no_client(self):
        generator = MediaGenerator()
        generator.client = None
        
        with pytest.raises(RuntimeError, match="OpenAI API Key not configured"):
            generator.generate_image("Test prompt")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

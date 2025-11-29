import os
import tempfile
import base64
import requests
from pathlib import Path
from openai import OpenAI
try:
    from moviepy import ImageClip
except ImportError:
    ImageClip = None
    print("WARNING: MoviePy not available - video generation will be disabled")

class MediaGenerator:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        
        # Setup media directories
        self.base_dir = Path(__file__).resolve().parents[2] # backend/
        self.media_dir = self.base_dir / "static" / "media"
        self.video_dir = self.base_dir / "static" / "videos"
        os.makedirs(self.media_dir, exist_ok=True)
        os.makedirs(self.video_dir, exist_ok=True)

    def generate_image(self, prompt: str, size: str = "512x512") -> tuple[str, str]:
        """
        Generates an image using DALL-E.
        Returns a tuple: (absolute_local_path, openai_public_url)
        """
        if not self.client:
            raise RuntimeError("OpenAI API Key not configured")

        try:
            response = self.client.images.generate(
                model="dall-e-2",
                prompt=prompt,
                n=1,
                size=size,
                response_format="url"
            )
            
            image_url = response.data[0].url
            
            # Download image to save locally (for frontend display and cache)
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            
            # Save to file
            fd, path = tempfile.mkstemp(suffix=".png", dir=str(self.media_dir))
            with os.fdopen(fd, "wb") as f:
                f.write(img_response.content)
            
            return path, image_url

        except Exception as e:
            print(f"Error generating image: {e}")
            return None, None

    def create_video_from_image(self, image_path: str, duration: int = 6) -> str:
        """
        Creates a simple video from a static image using MoviePy.
        Returns the absolute path to the saved video.
        """
        if not ImageClip:
            print("ERROR: MoviePy not installed or failed to import.")
            return None

        try:
            print(f"Creating video from image: {image_path} with duration: {duration}s")
            # Create a clip from the image
            clip = ImageClip(image_path, duration=duration)
            
            fd, out_path = tempfile.mkstemp(suffix=".mp4", dir=str(self.video_dir))
            os.close(fd) # Close the file descriptor so moviepy can write to it
            
            print(f"Writing video to: {out_path}")
            # Use 30fps and yuv420p pixel format for better compatibility
            # Note: MoviePy 2.x removed 'verbose' and 'logger' parameters
            clip.write_videofile(
                out_path, 
                fps=30, 
                codec="libx264", 
                audio=False,
                preset='medium',
                ffmpeg_params=['-pix_fmt', 'yuv420p']
            )
            clip.close()  # Clean up
            print(f"Video created successfully: {out_path}")
            return out_path
            
        except Exception as e:
            print(f"ERROR creating video: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_public_url(self, file_path: str) -> str:
        """Converts a local file path to a public URL (assuming served via static)"""
        if not file_path:
            return None
        filename = Path(file_path).name
        
        # Determine if it's a video or image based on directory
        folder = "videos" if str(self.video_dir) in file_path else "media"
        
        # Check for PUBLIC_URL env var (e.g. for ngrok)
        public_url = os.getenv("PUBLIC_URL")
        if public_url:
            # Ensure no trailing slash
            public_url = public_url.rstrip("/")
            return f"{public_url}/static/{folder}/{filename}"
            
        # Default to localhost
        return f"http://127.0.0.1:8080/static/{folder}/{filename}"

    def get_localhost_url(self, file_path: str) -> str:
        """Returns a guaranteed localhost URL for frontend display"""
        if not file_path:
            return None
        filename = Path(file_path).name
        
        # Determine if it's a video or image based on directory
        folder = "videos" if str(self.video_dir) in file_path else "media"
        
        return f"http://127.0.0.1:8080/static/{folder}/{filename}"

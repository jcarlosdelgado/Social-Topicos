import os
import requests
from typing import Dict, Any, Optional
from pathlib import Path
from .base import BasePublisher

class TikTokPublisher(BasePublisher):
    def __init__(self):
        super().__init__()
        self.access_token = os.getenv("TIKTOK_ACCESS_TOKEN")
        
    def publish(self, text: str, video_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Publishes a video to TikTok using the two-step upload process.
        1. Initialize upload to get upload_url
        2. Upload video file via PUT request
        """
        if not self.access_token:
            return {"error": "CONFIG_ERROR", "message": "TikTok access token not configured."}
        
        if not video_path:
            return {"error": "VALIDATION_ERROR", "message": "TikTok requires a video file path."}
        
        # Check if video file exists
        if not os.path.exists(video_path):
            return {"error": "FILE_ERROR", "message": f"Video file not found: {video_path}"}
        
        try:
            # Get video file size
            video_size = os.path.getsize(video_path)
            
            # Step 1: Initialize upload
            init_url = "https://open.tiktokapis.com/v2/post/publish/video/init/"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            init_payload = {
                "post_info": {
                    "title": text[:150],  # TikTok title limit
                    "privacy_level": "SELF_ONLY",
                    "disable_duet": False,
                    "disable_comment": False,
                    "disable_stitch": False,
                    "video_cover_timestamp_ms": 1000
                },
                "source_info": {
                    "source": "FILE_UPLOAD",
                    "video_size": video_size,
                    "chunk_size": video_size,
                    "total_chunk_count": 1
                }
            }
            
            init_response = requests.post(init_url, headers=headers, json=init_payload)
            
            print(f"TikTok Init Response: {init_response.status_code} - {init_response.text}")
            
            if init_response.status_code not in [200, 201]:
                return {
                    "error": "INIT_ERROR",
                    "message": f"Failed to initialize upload: {init_response.text}",
                    "status_code": init_response.status_code
                }
            
            init_data = init_response.json()
            
            # Check if initialization was successful
            if init_data.get("error", {}).get("code") != "ok":
                return {
                    "error": "INIT_ERROR",
                    "message": init_data.get("error", {}).get("message", "Unknown error"),
                    "log_id": init_data.get("error", {}).get("log_id")
                }
            
            upload_url = init_data.get("data", {}).get("upload_url")
            publish_id = init_data.get("data", {}).get("publish_id")
            
            print(f"TikTok Upload URL: {upload_url}")
            print(f"TikTok Publish ID: {publish_id}")
            
            if not upload_url:
                return {"error": "INIT_ERROR", "message": "No upload_url received from TikTok"}
            
            # Step 2: Upload video file
            with open(video_path, 'rb') as video_file:
                video_data = video_file.read()
            
            upload_headers = {
                "Content-Type": "video/mp4",
                "Content-Range": f"bytes 0-{video_size-1}/{video_size}"
            }
            
            print(f"Uploading video to TikTok... Size: {video_size} bytes. Range: {upload_headers['Content-Range']}")
            print(f"Upload Headers: {upload_headers}")
            
            # Send as raw binary data, exactly like Postman "binary" body
            upload_response = requests.put(upload_url, headers=upload_headers, data=video_data)
            
            print(f"TikTok Upload Response: {upload_response.status_code} - {upload_response.text}")
            
            if upload_response.status_code not in [200, 201]:
                return {
                    "error": "UPLOAD_ERROR",
                    "message": f"Failed to upload video: {upload_response.text}",
                    "status_code": upload_response.status_code
                }
            
            return {
                "success": True,
                "publish_id": publish_id,
                "message": "Video uploaded successfully to TikTok",
                "details": {
                    "video_size": video_size,
                    "upload_status": upload_response.status_code,
                    "init_response": init_data
                }
            }
            
        except Exception as e:
            return {"error": "EXCEPTION", "message": str(e)}


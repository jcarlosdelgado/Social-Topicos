from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from app.services.content_generator import ContentGenerator
from app.services.media_generator import MediaGenerator

router = APIRouter()
content_gen = ContentGenerator()
media_gen = MediaGenerator()

class GenerateRequest(BaseModel):
    title: str
    body: str
    platforms: Optional[List[str]] = ["facebook", "instagram", "tiktok", "linkedin", "whatsapp"]

@router.post("/generate")
async def generate_content(request: GenerateRequest):
    """
    Generates social media content and media assets for the requested platforms.
    """
    # 1. Generate Textual Content
    results = content_gen.generate_social_content(request.title, request.body, request.platforms)
    
    # 2. Generate Media Assets (Images/Videos)
    # Find the first available image prompt to use as the "master" image
    master_image_path = None
    master_image_url = None
    
    # First pass: Generate the master image
    for platform, content in results.items():
        if "error" in content:
            continue
        
        if "image_prompt" in content and not master_image_path:
            print(f"Generating master image using prompt from {platform}...")
            # Now returns a tuple (path, url)
            master_image_path, master_openai_url = media_gen.generate_image(content["image_prompt"])
            if master_image_path:
                # We prefer the OpenAI URL for publishing, but we have the local path for display
                master_image_url = master_openai_url
            break # Stop after generating one image
            
    # Second pass: Assign image to all platforms and generate video if needed
    for platform, content in results.items():
        if "error" in content:
            continue
            
        # Assign the master image to all platforms
        if master_image_url:
            content["media_url"] = master_image_url
            content["display_url"] = media_gen.get_localhost_url(master_image_path)
            
            # Generate Video for TikTok if applicable (using the master image)
            if platform == "tiktok" and "script" in content and master_image_path:
                # OPTIMIZATION: Skip video generation for now to speed up response
                # video_path = media_gen.create_video_from_image(master_image_path, duration=5)
                # if video_path:
                #         content["video_url"] = media_gen.get_public_url(video_path)
                #         content["display_video_url"] = media_gen.get_localhost_url(video_path)
                pass
    
    import json
    print(f"Returning results: {json.dumps(results, indent=2)}")
    return results

# --- Publishing Endpoints ---

from app.services.social_publisher import SocialPublisher
social_pub = SocialPublisher()

class PublishRequest(BaseModel):
    platform: str
    text: str
    media_url: Optional[str] = None

@router.post("/publish")
async def publish_content(request: PublishRequest):
    """
    Publishes content to the specified platform.
    """
    if request.platform == "facebook":
        return social_pub.publish_facebook(request.text, request.media_url)
    elif request.platform == "instagram":
        return social_pub.publish_instagram(request.text, request.media_url)
    elif request.platform == "whatsapp":
        return social_pub.publish_whatsapp(request.text, request.media_url)
    elif request.platform == "linkedin":
        return social_pub.publish_linkedin(request.text, request.media_url)
    else:
        raise HTTPException(status_code=400, detail="Platform not supported for auto-publishing yet.")

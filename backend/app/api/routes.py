from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.services.content_generator import ContentGenerator
from app.services.media_generator import MediaGenerator

router = APIRouter()
content_gen = ContentGenerator()
media_gen = MediaGenerator()

class GenerateRequest(BaseModel):
    title: str
    body: str
    platforms: Optional[List[str]] = ["facebook", "instagram", "tiktok", "linkedin", "whatsapp"]

from sqlalchemy.orm import Session
from app.api import deps
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
import json

@router.post("/generate")
async def generate_content(
    request: GenerateRequest,
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_current_user_optional)
):
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
            # Use 1024x1024 for TikTok to ensure video acceptance (256x256 is too small)
            image_size = "1024x1024" if "tiktok" in request.platforms else "512x512"
            print(f"Using image size: {image_size}")
            # Now returns a tuple (path, url)
            master_image_path, master_openai_url = media_gen.generate_image(content["image_prompt"], size=image_size)
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
                print(f"Generating 6-second video for TikTok...")
                video_path = media_gen.create_video_from_image(master_image_path, duration=6)
                if video_path:
                    content["video_path"] = video_path  # Local file path for upload
                    content["display_video_url"] = media_gen.get_localhost_url(video_path)
    
    # Save History if User is Logged In
    if current_user:
        try:
            # Create Chat Session
            chat = ChatSession(user_id=current_user.id, title=request.title)
            db.add(chat)
            db.commit()
            db.refresh(chat)
            
            # User Message
            user_msg = ChatMessage(
                session_id=chat.id, 
                role="user", 
                content=json.dumps({"title": request.title, "body": request.body}) # Store as JSON for easier parsing
            )
            db.add(user_msg)
            
<<<<<<< HEAD
            
=======
            # AI Message
>>>>>>> edab826f1c006fb5c88c99504b503d04cf67df9a
            ai_msg = ChatMessage(
                session_id=chat.id, 
                role="assistant", 
                content=json.dumps(results)
            )
            db.add(ai_msg)
            db.commit()
        except Exception as e:
            print(f"Error saving history: {e}")

    print(f"Returning results: {json.dumps(results, indent=2)}")
    return results

# --- Publishing Endpoints ---

from app.models.publication import Publication

class PublishRequest(BaseModel):
    platform: str
    text: str
    media_url: Optional[str] = None
    video_path: Optional[str] = None  # For TikTok local video file path
<<<<<<< HEAD

from app.services.social_publisher import SocialPublisher
social_publisher = SocialPublisher()
=======
>>>>>>> edab826f1c006fb5c88c99504b503d04cf67df9a

@router.post("/publish")
async def publish_content(
    request: PublishRequest,
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_current_user_optional)
):
    """
<<<<<<< HEAD
    Publishes content directly to the specified platform.
    """
    try:
        # Publish directly to the platform
        if request.platform == "tiktok":
            result = social_publisher.publish_tiktok(request.text, request.video_path)
        elif request.platform == "facebook":
            result = social_publisher.publish_facebook(request.text, request.media_url)
        elif request.platform == "instagram":
            result = social_publisher.publish_instagram(request.text, request.media_url)
        elif request.platform == "linkedin":
            result = social_publisher.publish_linkedin(request.text, request.media_url)
        elif request.platform == "whatsapp":
            result = social_publisher.publish_whatsapp(request.text, request.media_url)
        else:
            return {
                "success": False,
                "message": f"Unsupported platform: {request.platform}"
            }
        
        # Save publication record
        publication = Publication(
            user_id=current_user.id if current_user else None,
            platform=request.platform,
            text=request.text,
            media_url=request.media_url,
            video_path=request.video_path,
            status="published" if result.get("success") else "failed",
            error_message=result.get("message") if not result.get("success") else None
        )
        db.add(publication)
        db.commit()
        db.refresh(publication)
        
        return {
            "success": result.get("success", False),
            "message": result.get("message", "Unknown error"),
            "publication_id": publication.id,
            "status": publication.status
        }
    except Exception as e:
        # Save failed publication record
        publication = Publication(
            user_id=current_user.id if current_user else None,
            platform=request.platform,
            text=request.text,
            media_url=request.media_url,
            video_path=request.video_path,
            status="failed",
            error_message=str(e)
        )
        db.add(publication)
        db.commit()
        
        return {
            "success": False,
            "message": str(e),
            "publication_id": publication.id,
            "status": "failed"
        }

# --- Publications History Endpoints ---

class PublicationResponse(BaseModel):
    id: int
    user_id: Optional[int]
    platform: str
    text: str
    media_url: Optional[str]
    video_path: Optional[str]
    status: str
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/publications", response_model=List[PublicationResponse])
async def get_all_publications(
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_current_user_optional),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all publications. If user is logged in, returns their publications first.
    """
    query = db.query(Publication)
    
    if current_user:
        # Show user's publications first, then others
        query = query.filter(Publication.user_id == current_user.id)
    
    publications = query.order_by(Publication.created_at.desc()).offset(skip).limit(limit).all()
    return publications

@router.get("/publications/me", response_model=List[PublicationResponse])
async def get_my_publications(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Get current user's publications only (requires authentication).
    """
    publications = db.query(Publication).filter(
        Publication.user_id == current_user.id
    ).order_by(Publication.created_at.desc()).offset(skip).limit(limit).all()
    return publications

@router.get("/publications/{publication_id}", response_model=PublicationResponse)
async def get_publication(
    publication_id: int,
    db: Session = Depends(deps.get_db),
    current_user: Optional[User] = Depends(deps.get_current_user_optional)
):
    """
    Get a specific publication by ID.
    """
    publication = db.query(Publication).filter(Publication.id == publication_id).first()
    
    if not publication:
        raise HTTPException(status_code=404, detail="Publication not found")
    
    return publication
=======
    Saves publication to database with status 'pending'.
    The queue processor will handle actual publishing.
    """
    publication = Publication(
        user_id=current_user.id if current_user else None,
        platform=request.platform,
        text=request.text,
        media_url=request.media_url,
        video_path=request.video_path,  # Save video_path for TikTok
        status="pending"
    )
    db.add(publication)
    db.commit()
    db.refresh(publication)
    
    return {
        "success": True,
        "message": "Publication added to queue",
        "publication_id": publication.id,
        "status": publication.status
    }
>>>>>>> edab826f1c006fb5c88c99504b503d04cf67df9a

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Publication(Base):
    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    platform = Column(String)  # facebook, instagram, whatsapp, linkedin, tiktok
    text = Column(Text)
    media_url = Column(String, nullable=True)
    video_path = Column(String, nullable=True)  # Local file path for TikTok videos
    status = Column(String, default="published") # published, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="publications")


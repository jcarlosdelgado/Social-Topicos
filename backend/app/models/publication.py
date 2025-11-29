from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, JSON
<<<<<<< HEAD
from sqlalchemy.orm import relationship
=======
>>>>>>> edab826f1c006fb5c88c99504b503d04cf67df9a
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
<<<<<<< HEAD
    status = Column(String, default="published") # published, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    user = relationship("User", back_populates="publications")

=======
    status = Column(String, default="pending") # pending, processing, published, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
>>>>>>> edab826f1c006fb5c88c99504b503d04cf67df9a

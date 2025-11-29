from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.api import deps
from app.models.chat import ChatSession, ChatMessage
from app.models.user import User
from app.services.content_generator import ContentGenerator

router = APIRouter()
content_gen = ContentGenerator()

class ChatSessionCreate(BaseModel):
    title: str = "New Chat"

class ChatMessageCreate(BaseModel):
    content: str

class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content: str
    
    class Config:
        from_attributes = True

class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: Any
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[ChatSessionResponse])
def get_chats(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    return db.query(ChatSession).filter(ChatSession.user_id == current_user.id).order_by(ChatSession.created_at.desc()).all()

@router.post("/", response_model=ChatSessionResponse)
def create_chat(
    chat_in: ChatSessionCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    chat = ChatSession(user_id=current_user.id, title=chat_in.title)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat

@router.get("/{chat_id}/messages", response_model=List[ChatMessageResponse])
def get_messages(
    chat_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    chat = db.query(ChatSession).filter(ChatSession.id == chat_id, ChatSession.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat.messages

@router.post("/{chat_id}/messages", response_model=ChatMessageResponse)
def send_message(
    chat_id: int,
    msg_in: ChatMessageCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user)
):
    chat = db.query(ChatSession).filter(ChatSession.id == chat_id, ChatSession.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Save User Message
    user_msg = ChatMessage(session_id=chat.id, role="user", content=msg_in.content)
    db.add(user_msg)
    db.commit()
    
    
    # We use the content generator client directly for a simple chat
    # In a real app, we might want a dedicated ChatService
    try:
        if content_gen.client:
            response = content_gen.client.chat.completions.create(
                model=content_gen.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for a university social media manager."},
                    {"role": "user", "content": msg_in.content}
                ]
            )
            ai_content = response.choices[0].message.content
        else:
            ai_content = "AI is not configured (API Key missing)."
    except Exception as e:
        ai_content = f"Error generating response: {str(e)}"

    
    ai_msg = ChatMessage(session_id=chat.id, role="assistant", content=ai_content)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)
    
    return ai_msg

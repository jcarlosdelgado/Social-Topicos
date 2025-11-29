from fastapi import APIRouter
from app.api.endpoints import auth, chat
from app.api import routes as content_routes

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(chat.router, prefix="/chats", tags=["chats"])
api_router.include_router(content_routes.router, tags=["content"]) # Keep existing routes at root or specific path


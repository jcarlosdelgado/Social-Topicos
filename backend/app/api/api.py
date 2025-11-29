from fastapi import APIRouter
<<<<<<< HEAD
from app.api.endpoints import auth, chat
=======
from app.api.endpoints import auth, chat, queue
>>>>>>> edab826f1c006fb5c88c99504b503d04cf67df9a
from app.api import routes as content_routes

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(chat.router, prefix="/chats", tags=["chats"])
<<<<<<< HEAD
api_router.include_router(content_routes.router, tags=["content"]) # Keep existing routes at root or specific path

=======
api_router.include_router(queue.router, prefix="/queue", tags=["queue"])
api_router.include_router(content_routes.router, tags=["content"]) # Keep existing routes at root or specific path
>>>>>>> edab826f1c006fb5c88c99504b503d04cf67df9a

import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.api import api_router
from app.db.base import Base
from app.db.session import engine
<<<<<<< HEAD

# Create Tables
Base.metadata.create_all(bind=engine)
=======
import asyncio
from contextlib import asynccontextmanager
>>>>>>> edab826f1c006fb5c88c99504b503d04cf67df9a

# Create Tables
Base.metadata.create_all(bind=engine)

# Background task for queue processing
async def process_queue_worker():
    """Background worker that processes queue every 10 seconds"""
    from app.services.queue_service import queue_service
    
    print("🚀 Queue worker started!")
    
    while True:
        try:
            # Check if queue is ON
            status = queue_service.get_status()
            pending_count = queue_service.get_queue_length()
            
            print(f"⏰ Worker check - Status: {status}, Pending: {pending_count}")
            
            if status == "ON":
                # Check if there are pending publications
                if pending_count > 0:
                    print(f"📝 Processing {pending_count} pending publications...")
                    result = queue_service.process_pending_publications()
                    print(f"✅ Processed: {result}")
                else:
                    print("✓ Queue is ON but no pending items")
            else:
                print("⏸ Queue is OFF - skipping processing")
        except Exception as e:
            print(f"❌ Error in queue worker: {e}")
        
        # Wait 10 seconds before next check
        await asyncio.sleep(10)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize queue and create background task
    from app.services.queue_service import queue_service
    
    # Force queue status to ON on startup
    queue_service.set_status("ON")
    print("✅ Queue status initialized to ON")
    
    task = asyncio.create_task(process_queue_worker())
    yield
    # Shutdown: Cancel background task
    task.cancel()

app = FastAPI(title="University Social Media Generator", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(os.path.dirname(BASE_DIR), "static")
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include Routes
app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to the University Social Media Generator API"}

@app.get("/health")
def health_check():
    """Health check endpoint for Docker and load balancers"""
    return {"status": "healthy", "service": "backend"}
<<<<<<< HEAD

=======
>>>>>>> edab826f1c006fb5c88c99504b503d04cf67df9a

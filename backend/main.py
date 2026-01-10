from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .routers import cameras, events, streams
from .database import engine, Base, SessionLocal
from .models import Camera
from .stream_manager import stream_manager
from contextlib import asynccontextmanager

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load cameras from DB and start streams
    db = SessionLocal()
    cameras_db = db.query(Camera).filter(Camera.is_active == True).all()
    print(f"Loading {len(cameras_db)} cameras...")
    for cam in cameras_db:
        stream_manager.add_stream(cam.id, cam.rtsp_url, cam.zone_config)
    db.close()
    
    yield
    
    # Shutdown: Stop all streams
    stream_manager.streams.clear() # Or iterate and stop explicitly

app = FastAPI(title="SentinelSight API", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(cameras.router, prefix="/api/cameras", tags=["cameras"])
app.include_router(events.router, prefix="/api/events", tags=["events"])
app.include_router(streams.router, prefix="/api/streams", tags=["streams"])

# Static files for snapshots
# Ensure backend/data directory is served
import os
os.makedirs("backend/data", exist_ok=True)
app.mount("/snapshots", StaticFiles(directory="backend/data"), name="snapshots")

@app.get("/health")
def health_check():
    return {"status": "ok"}

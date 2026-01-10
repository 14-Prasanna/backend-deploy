from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Camera
from pydantic import BaseModel
from typing import Optional
from ..stream_manager import stream_manager
import json

router = APIRouter()

class CameraCreate(BaseModel):
    name: String
    rtsp_url: String
    location: Optional[String] = None
    zone_config: Optional[String] = None

class CameraUpdate(BaseModel):
    name: Optional[String] = None
    rtsp_url: Optional[String] = None
    location: Optional[String] = None
    is_active: Optional[bool] = None
    zone_config: Optional[String] = None

# Correcting pydantic types since String is SQLAlchemy
class CameraCreate(BaseModel):
    name: str
    rtsp_url: str
    location: Optional[str] = None
    zone_config: Optional[str] = None

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    rtsp_url: Optional[str] = None
    location: Optional[str] = None
    is_active: Optional[bool] = None
    zone_config: Optional[str] = None

@router.get("/")
def get_cameras(db: Session = Depends(get_db)):
    return db.query(Camera).all()

@router.post("/")
def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    db_camera = Camera(
        name=camera.name,
        rtsp_url=camera.rtsp_url,
        location=camera.location,
        zone_config=camera.zone_config
    )
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    
    # Start stream if active (default is true)
    stream_manager.add_stream(db_camera.id, db_camera.rtsp_url, db_camera.zone_config)
    
    return db_camera

@router.put("/{camera_id}")
def update_camera(camera_id: int, camera: CameraUpdate, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    
    if camera.name is not None:
        db_camera.name = camera.name
    if camera.rtsp_url is not None:
        db_camera.rtsp_url = camera.rtsp_url
    if camera.location is not None:
        db_camera.location = camera.location
    if camera.is_active is not None:
        db_camera.is_active = camera.is_active
    if camera.zone_config is not None:
        db_camera.zone_config = camera.zone_config
        
    db.commit()
    db.refresh(db_camera)
    
    # Update stream
    if db_camera.is_active:
        stream_manager.add_stream(db_camera.id, db_camera.rtsp_url, db_camera.zone_config)
    else:
        stream_manager.stop_stream(db_camera.id)
        
    return db_camera

@router.delete("/{camera_id}")
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if not db_camera:
        raise HTTPException(status_code=404, detail="Camera not found")
        
    stream_manager.stop_stream(camera_id)
    db.delete(db_camera)
    db.commit()
    return {"message": "Camera deleted"}

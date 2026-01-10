from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, Text
from sqlalchemy.sql import func
from .database import Base

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    rtsp_url = Column(String)
    location = Column(String, nullable=True)
    site = Column(String, nullable=True)  # New: Site/Facility name
    is_active = Column(Boolean, default=True)
    status = Column(String, default="offline") # New: online/offline
    zone_config = Column(Text, nullable=True)  # JSON string for zone coordinates
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    rule_name = Column(String) # "Intrusion", "Loitering"
    object_type = Column(String) # "person", "car"
    confidence = Column(Float)
    snapshot_path = Column(String, nullable=True)

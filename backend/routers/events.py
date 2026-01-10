from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Event
from typing import Optional, List
from datetime import datetime

router = APIRouter()

@router.get("/")
def get_events(
    camera_id: Optional[int] = None,
    rule: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Event)
    if camera_id:
        query = query.filter(Event.camera_id == camera_id)
    if rule:
        query = query.filter(Event.rule_name == rule)
        
    # Order by timestamp desc
    return query.order_by(Event.timestamp.desc()).limit(limit).all()

@router.get("/{event_id}")
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

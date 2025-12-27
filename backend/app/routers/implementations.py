from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Implementation, User, Vibe, Notification, NotificationType
from app.schemas import schemas
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/vibes/{vibe_id}/implementations", response_model=List[schemas.Implementation])
def get_vibe_implementations(vibe_id: int, db: Session = Depends(get_db)):
    return db.query(Implementation).filter(Implementation.vibe_id == vibe_id).all()

@router.post("/vibes/{vibe_id}/implementations", response_model=schemas.Implementation)
def create_implementation(
    vibe_id: int,
    impl_in: schemas.ImplementationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vibe = db.query(Vibe).filter(Vibe.id == vibe_id).first()
    if not vibe:
        raise HTTPException(status_code=404, detail="Vibe not found")
    
    db_impl = Implementation(
        vibe_id=vibe_id,
        user_id=current_user.id,
        **impl_in.model_dump()
    )
    db.add(db_impl)
    
    # Notify creator
    if vibe.creator_id != current_user.id:
        notification = Notification(
            user_id=vibe.creator_id,
            type=NotificationType.IMPLEMENTATION,
            content=f"{current_user.username} submitted an implementation for your vibe",
            link=f"/vibes/{vibe_id}"
        )
        db.add(notification)
        
    db.commit()
    db.refresh(db_impl)
    return db_impl

@router.patch("/implementations/{impl_id}/official", response_model=schemas.Implementation)
def mark_official(
    impl_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    impl = db.query(Implementation).filter(Implementation.id == impl_id).first()
    if not impl:
        raise HTTPException(status_code=404, detail="Implementation not found")
    
    vibe = db.query(Vibe).filter(Vibe.id == impl.vibe_id).first()
    if vibe.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only vibe creator can mark implementation as official")
    
    # Unmark others as official for this vibe
    db.query(Implementation).filter(
        Implementation.vibe_id == vibe.id, 
        Implementation.is_official == True
    ).update({"is_official": False})
    
    impl.is_official = True
    db.add(impl)
    db.commit()
    db.refresh(impl)
    return impl

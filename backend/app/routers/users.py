from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, UserLink
from app.schemas import schemas
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int, 
    user_in: schemas.UserUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    
    update_data = user_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/{user_id}/links", response_model=schemas.UserLink)
def create_user_link(
    user_id: int,
    link_in: schemas.UserLinkBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_link = UserLink(**link_in.model_dump(), user_id=user_id)
    db.add(db_link)
    db.commit()
    db.refresh(db_link)
    return db_link

@router.delete("/{user_id}/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_link(
    user_id: int,
    link_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_link = db.query(UserLink).filter(UserLink.id == link_id, UserLink.user_id == user_id).first()
    if not db_link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    db.delete(db_link)
    db.commit()
    return None

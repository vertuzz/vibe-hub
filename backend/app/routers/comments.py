from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Comment, User, Vibe, Notification, NotificationType
from app.schemas import schemas
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/vibes/{vibe_id}/comments", response_model=List[schemas.Comment])
def get_vibe_comments(vibe_id: int, db: Session = Depends(get_db)):
    return db.query(Comment).filter(Comment.vibe_id == vibe_id).all()

@router.post("/vibes/{vibe_id}/comments", response_model=schemas.Comment)
def create_comment(
    vibe_id: int,
    comment_in: schemas.CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vibe = db.query(Vibe).filter(Vibe.id == vibe_id).first()
    if not vibe:
        raise HTTPException(status_code=404, detail="Vibe not found")
    
    db_comment = Comment(
        vibe_id=vibe_id,
        user_id=current_user.id,
        content=comment_in.content
    )
    db.add(db_comment)
    
    # Notify creator
    if vibe.creator_id != current_user.id:
        notification = Notification(
            user_id=vibe.creator_id,
            type=NotificationType.COMMENT,
            content=f"{current_user.username} commented on your vibe",
            link=f"/vibes/{vibe_id}"
        )
        db.add(notification)
        
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.patch("/comments/{comment_id}", response_model=schemas.Comment)
def update_comment(
    comment_id: int,
    comment_in: schemas.CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db_comment.content = comment_in.content
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if db_comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(db_comment)
    db.commit()
    return None

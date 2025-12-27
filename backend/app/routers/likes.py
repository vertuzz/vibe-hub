from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import Like, CommentLike, User, Vibe, Comment, Notification, NotificationType
from app.routers.auth import get_current_user

router = APIRouter()

@router.post("/vibes/{vibe_id}/like")
def like_vibe(
    vibe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    vibe = db.query(Vibe).filter(Vibe.id == vibe_id).first()
    if not vibe:
        raise HTTPException(status_code=404, detail="Vibe not found")
    
    db_like = Like(vibe_id=vibe_id, user_id=current_user.id)
    db.add(db_like)
    
    try:
        db.commit()
        # Notify
        if vibe.creator_id != current_user.id:
            notification = Notification(
                user_id=vibe.creator_id,
                type=NotificationType.LIKE,
                content=f"{current_user.username} liked your vibe",
                link=f"/vibes/{vibe_id}"
            )
            db.add(notification)
            db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Already liked")
    
    return {"message": "Liked"}

@router.delete("/vibes/{vibe_id}/like")
def unlike_vibe(
    vibe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_like = db.query(Like).filter(Like.vibe_id == vibe_id, Like.user_id == current_user.id).first()
    if not db_like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    db.delete(db_like)
    db.commit()
    return {"message": "Unliked"}

@router.post("/comments/{comment_id}/like")
def like_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    db_like = CommentLike(comment_id=comment_id, user_id=current_user.id)
    db.add(db_like)
    
    # Update counter cache
    comment.likes_count += 1
    db.add(comment)
    
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Already liked")
        
    return {"message": "Liked"}

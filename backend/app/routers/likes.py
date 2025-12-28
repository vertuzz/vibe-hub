from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import Like, CommentLike, User, Vibe, Comment, Notification, NotificationType
from app.routers.auth import get_current_user

router = APIRouter()

@router.post("/vibes/{vibe_id}/like")
async def like_vibe(
    vibe_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Vibe).filter(Vibe.id == vibe_id))
    vibe = result.scalars().first()
    if not vibe:
        raise HTTPException(status_code=404, detail="Vibe not found")
    
    db_like = Like(vibe_id=vibe_id, user_id=current_user.id)
    db.add(db_like)
    
    try:
        await db.commit()
        # Notify
        if vibe.creator_id != current_user.id:
            notification = Notification(
                user_id=vibe.creator_id,
                type=NotificationType.LIKE,
                content=f"{current_user.username} liked your vibe",
                link=f"/vibes/{vibe_id}"
            )
            db.add(notification)
            await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Already liked")
    
    return {"message": "Liked"}

@router.delete("/vibes/{vibe_id}/like")
async def unlike_vibe(
    vibe_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Like).filter(Like.vibe_id == vibe_id, Like.user_id == current_user.id))
    db_like = result.scalars().first()
    if not db_like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    await db.delete(db_like)
    await db.commit()
    return {"message": "Unliked"}

@router.post("/comments/{comment_id}/like")
async def like_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalars().first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    db_like = CommentLike(comment_id=comment_id, user_id=current_user.id)
    db.add(db_like)
    
    # Update counter cache
    comment.likes_count += 1
    db.add(comment)
    
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Already liked")
        
    return {"message": "Liked"}

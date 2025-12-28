from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import Like, CommentLike, User, Dream, Comment, Notification, NotificationType
from app.routers.auth import get_current_user

router = APIRouter()

@router.post("/dreams/{dream_id}/like")
async def like_dream(
    dream_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Dream).filter(Dream.id == dream_id))
    dream = result.scalars().first()
    if not dream:
        raise HTTPException(status_code=404, detail="Dream not found")
    
    db_like = Like(dream_id=dream_id, user_id=current_user.id)
    db.add(db_like)
    
    try:
        await db.commit()
        # Notify
        if dream.creator_id != current_user.id:
            notification = Notification(
                user_id=dream.creator_id,
                type=NotificationType.LIKE,
                content=f"{current_user.username} liked your dream",
                link=f"/dreams/{dream_id}"
            )
            db.add(notification)
            await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Already liked")
    
    return {"message": "Liked"}

@router.delete("/dreams/{dream_id}/like")
async def unlike_dream(
    dream_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Like).filter(Like.dream_id == dream_id, Like.user_id == current_user.id))
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

@router.delete("/comments/{comment_id}/like")
async def unlike_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CommentLike).filter(
            CommentLike.comment_id == comment_id, 
            CommentLike.user_id == current_user.id
        )
    )
    db_like = result.scalars().first()
    if not db_like:
        raise HTTPException(status_code=404, detail="Like not found")
    
    # Update counter cache
    result = await db.execute(select(Comment).filter(Comment.id == comment_id))
    comment = result.scalars().first()
    if comment:
        comment.likes_count = max(0, comment.likes_count - 1)
        db.add(comment)
    
    await db.delete(db_like)
    await db.commit()
    
    return {"message": "Unliked"}

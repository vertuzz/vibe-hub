from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database import get_db
from app.models import User, Follow
from app.routers.auth import get_current_user

router = APIRouter()

@router.post("/{user_id}/follow")
async def follow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
        
    result = await db.execute(select(User).filter(User.id == user_id))
    target = result.scalars().first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
        
    db_follow = Follow(follower_id=current_user.id, followed_id=user_id)
    db.add(db_follow)
    
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Already following")
        
    return {"message": f"Following {target.username}"}

@router.delete("/{user_id}/follow")
async def unfollow_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Follow).filter(
            Follow.follower_id == current_user.id,
            Follow.followed_id == user_id
        )
    )
    db_follow = result.scalars().first()
    if not db_follow:
        raise HTTPException(status_code=404, detail="Not following this user")
        
    await db.delete(db_follow)
    await db.commit()
    return {"message": "Unfollowed"}

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Implementation, User, App, Notification, NotificationType
from app.schemas import schemas
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/apps/{app_id}/implementations", response_model=List[schemas.Implementation])
async def get_implementations(app_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Implementation).filter(Implementation.app_id == app_id))
    return result.scalars().all()

@router.post("/apps/{app_id}/implementations", response_model=schemas.Implementation)
async def create_implementation(
    app_id: int,
    impl_in: schemas.ImplementationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(App).filter(App.id == app_id))
    app = result.scalars().first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    db_impl = Implementation(
        app_id=app_id,
        user_id=current_user.id,
        **impl_in.model_dump()
    )
    db.add(db_impl)
    
    # Notify creator
    if app.creator_id != current_user.id:
        notification = Notification(
            user_id=app.creator_id,
            type=NotificationType.IMPLEMENTATION,
            content=f"{current_user.username} submitted an implementation for your app",
            link=f"/apps/{app_id}"
        )
        db.add(notification)
        
    await db.commit()
    await db.refresh(db_impl)
    return db_impl

@router.patch("/implementations/{impl_id}/official", response_model=schemas.Implementation)
async def mark_official(
    impl_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Implementation).filter(Implementation.id == impl_id))
    impl = result.scalars().first()
    if not impl:
        raise HTTPException(status_code=404, detail="Implementation not found")
    
    result = await db.execute(select(App).filter(App.id == impl.app_id))
    app = result.scalars().first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    if app.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Only app creator can mark implementation as official")
    
    # Unmark others as official for this app
    result = await db.execute(
        select(Implementation).filter(
            Implementation.app_id == app.id, 
            Implementation.is_official == True
        )
    )
    for other_impl in result.scalars().all():
        other_impl.is_official = False
        db.add(other_impl)
    
    impl.is_official = True
    db.add(impl)
    await db.commit()
    await db.refresh(impl)
    return impl

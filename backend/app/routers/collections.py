from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.database import get_db
from app.models import Collection, User, App, collection_apps
from app.schemas import schemas
from app.routers.auth import get_current_user, get_current_user_optional

router = APIRouter()

@router.post("/", response_model=schemas.Collection)
async def create_collection(
    col_in: schemas.CollectionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    db_col = Collection(
        name=col_in.name,
        description=col_in.description,
        is_public=col_in.is_public,
        owner_id=current_user.id
    )
    if col_in.app_ids:
        result = await db.execute(select(App).filter(App.id.in_(col_in.app_ids)))
        apps = result.scalars().all()
        db_col.apps = apps
        
    db.add(db_col)
    await db.commit()
    # Reload with eager loading for nested relationships
    result = await db.execute(
        select(Collection)
        .options(
            selectinload(Collection.apps).selectinload(App.tools),
            selectinload(Collection.apps).selectinload(App.tags),
            selectinload(Collection.apps).selectinload(App.media)
        )
        .filter(Collection.id == db_col.id)
    )
    return result.scalars().first()

@router.get("/{col_id}", response_model=schemas.Collection)
async def get_collection(
    col_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    result = await db.execute(
        select(Collection)
        .options(
            selectinload(Collection.apps).selectinload(App.tools),
            selectinload(Collection.apps).selectinload(App.tags),
            selectinload(Collection.apps).selectinload(App.media)
        )
        .filter(Collection.id == col_id)
    )
    col = result.scalars().first()
    if not col:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    if not col.is_public:
        if not current_user or col.owner_id != current_user.id:
            raise HTTPException(status_code=403, detail="This collection is private")
            
    return col

@router.post("/{col_id}/apps/{app_id}")
async def add_to_collection(
    col_id: int,
    app_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Collection)
        .options(selectinload(Collection.apps))
        .filter(Collection.id == col_id, Collection.owner_id == current_user.id)
    )
    col = result.scalars().first()
    if not col:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    result = await db.execute(select(App).filter(App.id == app_id))
    app = result.scalars().first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    
    if app not in col.apps:
        col.apps.append(app)
        db.add(col)
        await db.commit()
        
    return {"message": "Added"}

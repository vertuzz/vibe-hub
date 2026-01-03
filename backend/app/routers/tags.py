from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database import get_db
from app.models import Tag, User, dream_tags
from app.schemas import schemas
from app.routers.auth import require_admin

router = APIRouter()

@router.get("/", response_model=List[schemas.Tag])
async def get_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag))
    return result.scalars().all()

@router.get("/with-counts", response_model=List[schemas.TagWithCount])
async def get_tags_with_counts(db: AsyncSession = Depends(get_db)):
    """Get all tags with their dream usage counts (for admin)."""
    result = await db.execute(
        select(
            Tag,
            func.count(dream_tags.c.dream_id).label("dream_count")
        )
        .outerjoin(dream_tags, Tag.id == dream_tags.c.tag_id)
        .group_by(Tag.id)
        .order_by(Tag.name)
    )
    tags_with_counts = []
    for row in result.all():
        tag = row[0]
        count = row[1]
        tags_with_counts.append(schemas.TagWithCount(
            id=tag.id,
            name=tag.name,
            dream_count=count
        ))
    return tags_with_counts

@router.post("/", response_model=schemas.Tag)
async def create_tag(
    tag_in: schemas.TagBase, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    # Check for duplicate name
    existing = await db.execute(select(Tag).where(Tag.name == tag_in.name))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag '{tag_in.name}' already exists"
        )
    db_tag = Tag(name=tag_in.name)
    db.add(db_tag)
    await db.commit()
    await db.refresh(db_tag)
    return db_tag

@router.put("/{tag_id}", response_model=schemas.Tag)
async def update_tag(
    tag_id: int,
    tag_in: schemas.TagUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a tag (admin only)."""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Check for duplicate name (excluding current tag)
    existing = await db.execute(
        select(Tag).where(Tag.name == tag_in.name, Tag.id != tag_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag '{tag_in.name}' already exists"
        )
    
    tag.name = tag_in.name
    await db.commit()
    await db.refresh(tag)
    return tag

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a tag (admin only). Removes associations with dreams."""
    result = await db.execute(select(Tag).where(Tag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    await db.delete(tag)
    await db.commit()
    return None

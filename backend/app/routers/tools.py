from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from typing import List

from app.database import get_db
from app.models import Tool, User, dream_tools
from app.schemas import schemas
from app.routers.auth import require_admin

router = APIRouter()

@router.get("/", response_model=List[schemas.Tool])
async def get_tools(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tool))
    return result.scalars().all()

@router.get("/with-counts", response_model=List[schemas.ToolWithCount])
async def get_tools_with_counts(db: AsyncSession = Depends(get_db)):
    """Get all tools with their dream usage counts (for admin)."""
    result = await db.execute(
        select(
            Tool,
            func.count(dream_tools.c.dream_id).label("dream_count")
        )
        .outerjoin(dream_tools, Tool.id == dream_tools.c.tool_id)
        .group_by(Tool.id)
        .order_by(Tool.name)
    )
    tools_with_counts = []
    for row in result.all():
        tool = row[0]
        count = row[1]
        tools_with_counts.append(schemas.ToolWithCount(
            id=tool.id,
            name=tool.name,
            dream_count=count
        ))
    return tools_with_counts

@router.post("/", response_model=schemas.Tool)
async def create_tool(
    tool_in: schemas.ToolBase, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    # Check for duplicate name
    existing = await db.execute(select(Tool).where(Tool.name == tool_in.name))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tool '{tool_in.name}' already exists"
        )
    db_tool = Tool(name=tool_in.name)
    db.add(db_tool)
    await db.commit()
    await db.refresh(db_tool)
    return db_tool

@router.put("/{tool_id}", response_model=schemas.Tool)
async def update_tool(
    tool_id: int,
    tool_in: schemas.ToolUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Update a tool (admin only)."""
    result = await db.execute(select(Tool).where(Tool.id == tool_id))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    # Check for duplicate name (excluding current tool)
    existing = await db.execute(
        select(Tool).where(Tool.name == tool_in.name, Tool.id != tool_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tool '{tool_in.name}' already exists"
        )
    
    tool.name = tool_in.name
    await db.commit()
    await db.refresh(tool)
    return tool

@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(
    tool_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete a tool (admin only). Removes associations with dreams."""
    result = await db.execute(select(Tool).where(Tool.id == tool_id))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tool not found"
        )
    
    await db.delete(tool)
    await db.commit()
    return None

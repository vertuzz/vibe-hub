from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models import Tool
from app.schemas import schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.Tool])
async def get_tools(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tool))
    return result.scalars().all()

@router.post("/", response_model=schemas.Tool)
async def create_tool(tool_in: schemas.ToolBase, db: AsyncSession = Depends(get_db)):
    # Simple admin restriction or public? For now anyone for dev
    db_tool = Tool(name=tool_in.name)
    db.add(db_tool)
    await db.commit()
    await db.refresh(db_tool)
    return db_tool

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Tool
from app.schemas import schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.Tool])
def get_tools(db: Session = Depends(get_db)):
    return db.query(Tool).all()

@router.post("/", response_model=schemas.Tool)
def create_tool(tool_in: schemas.ToolBase, db: Session = Depends(get_db)):
    # Simple admin restriction or public? For now anyone for dev
    db_tool = Tool(name=tool_in.name)
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    return db_tool

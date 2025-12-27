from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Tag
from app.schemas import schemas

router = APIRouter()

@router.get("/", response_model=List[schemas.Tag])
def get_tags(db: Session = Depends(get_db)):
    return db.query(Tag).all()

@router.post("/", response_model=schemas.Tag)
def create_tag(tag_in: schemas.TagBase, db: Session = Depends(get_db)):
    db_tag = Tag(name=tag_in.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

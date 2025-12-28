from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List

from app.database import get_db
from app.models import Review, User, Dream
from app.schemas import schemas
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/dreams/{dream_id}/reviews", response_model=List[schemas.Review])
async def get_dream_reviews(dream_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Review).filter(Review.dream_id == dream_id))
    return result.scalars().all()

@router.post("/dreams/{dream_id}/reviews", response_model=schemas.Review)
async def create_review(
    dream_id: int,
    review_in: schemas.ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if user already reviewed
    result = await db.execute(select(Review).filter(Review.dream_id == dream_id, Review.user_id == current_user.id))
    existing = result.scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="You already reviewed this dream")
    
    db_review = Review(
        dream_id=dream_id,
        user_id=current_user.id,
        score=review_in.score,
        comment=review_in.comment
    )
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    return db_review

@router.get("/dreams/{dream_id}/avg-score")
async def get_avg_score(dream_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(func.avg(Review.score)).filter(Review.dream_id == dream_id))
    avg = result.scalar()
    return {"dream_id": dream_id, "average_score": avg or 0.0}

@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Review).filter(Review.id == review_id))
    db_review = result.scalars().first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    if db_review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.delete(db_review)
    await db.commit()
    return None

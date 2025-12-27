from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.database import get_db
from app.models import Review, User, Vibe
from app.schemas import schemas
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/vibes/{vibe_id}/reviews", response_model=List[schemas.Review])
def get_vibe_reviews(vibe_id: int, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.vibe_id == vibe_id).all()

@router.post("/vibes/{vibe_id}/reviews", response_model=schemas.Review)
def create_review(
    vibe_id: int,
    review_in: schemas.ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if user already reviewed
    existing = db.query(Review).filter(Review.vibe_id == vibe_id, Review.user_id == current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already reviewed this vibe")
    
    db_review = Review(
        vibe_id=vibe_id,
        user_id=current_user.id,
        score=review_in.score,
        comment=review_in.comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

@router.get("/vibes/{vibe_id}/avg-score")
def get_avg_score(vibe_id: int, db: Session = Depends(get_db)):
    avg = db.query(func.avg(Review.score)).filter(Review.vibe_id == vibe_id).scalar()
    return {"vibe_id": vibe_id, "average_score": avg or 0.0}

@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_review = db.query(Review).filter(Review.id == review_id).first()
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    if db_review.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db.delete(db_review)
    db.commit()
    return None

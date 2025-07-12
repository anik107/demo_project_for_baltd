from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from schemas import User as UserSchema
from user_service import UserService

router = APIRouter(
    prefix="/doctors",
    tags=["doctors"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[UserSchema])
async def get_doctors(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all doctors"""
    doctors = UserService.get_doctors(db, skip=skip, limit=limit)
    return doctors

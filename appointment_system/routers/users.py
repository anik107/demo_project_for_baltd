from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import SessionLocal
from schemas import User as UserSchema
from user_service import UserService
from pathlib import Path

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/{user_id}", response_model=UserSchema)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/{user_id}/profile-image")
async def get_user_profile_image(user_id: int, db: Session = Depends(get_db)):
    """Get user profile image"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not user.profile_image_filename:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile image not found"
        )

    # Construct path to profile image
    current_dir = Path(__file__).parent.parent
    image_path = current_dir / "static" / "profiles" / user.profile_image_filename

    if not image_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile image file not found"
        )

    return FileResponse(
        path=str(image_path),
        media_type=user.profile_image_content_type,
        filename=user.profile_image_filename
    )

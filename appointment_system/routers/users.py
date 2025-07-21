from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import models
from auth_utils import get_current_user_from_token
from schemas import User as UserSchema
from user_service import UserService
from pathlib import Path
from database import get_db

router = APIRouter(
    prefix="/users",
    tags=["users"]
)
templates = Jinja2Templates(directory="templates")

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
@router.get("/user/{user_id}/edit")
async def edit_user_information(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_admin_cookie)
):
    """Edit user information"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return templates.TemplateResponse("edit_profile.html", {
        "request": request,
        "user": current_user,
    })
from fastapi import APIRouter, Depends, HTTPException, Request, status, Form, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
import models
from auth_utils import get_current_user_from_token, verify_password, hash_password
from schemas import User as UserSchema
from user_service import UserService
from pathlib import Path
from database import get_db
import uuid
from typing import Optional

router = APIRouter(
    prefix="/users",
    tags=["users"]
)
templates = Jinja2Templates(directory="templates")

def get_user_from_cookie(request: Request, db: Session = Depends(get_db)):
    """Get user from cookie token"""
    token = request.cookies.get("access_token")

    if not token:
        return None

    try:
        user = get_current_user_from_token(token, db)
        return user
    except:
        return None

def require_user_cookie(request: Request, db: Session = Depends(get_db)):
    """Require user authentication via cookie"""
    user = get_user_from_cookie(request, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    return user

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

@router.get("/{user_id}/edit", response_class=HTMLResponse)
async def edit_user_information(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    """Edit user information"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
        # Get location data
    divisions = db.query(models.Division).all()
    districts = db.query(models.District).all()
    thanas = db.query(models.Thana).all()
    return templates.TemplateResponse("edit_profile.html", {
        "request": request,
        "current_user": user,
        "user": user,
        "divisions": divisions,
        "districts": districts,
        "thanas": thanas
    })

@router.post("/{user_id}/edit")
async def update_user_profile(
    user_id: int,
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    mobile_number: str = Form(...),
    division_id: int = Form(...),
    district_id: int = Form(...),
    thana_id: int = Form(...),
    current_password: Optional[str] = Form(None),
    new_password: Optional[str] = Form(None),
    confirm_password: Optional[str] = Form(None),
    profile_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_user_cookie)
):
    """Update user profile information"""
    user = UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if current_user.id != user_id and current_user.user_type != models.UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own profile"
        )

    try:
        existing_user = db.query(models.User).filter(
            or_(models.User.email == email, models.User.mobile_number == mobile_number),
            models.User.id != user_id
        ).first()

        if existing_user:
            error_msg = "Email already exists" if existing_user.email == email else "Mobile number already exists"
            return RedirectResponse(url=f"/users/{user_id}/edit?error={error_msg}", status_code=303)

        # Handle password change if provided
        if current_password or new_password or confirm_password:
            if not current_password:
                return RedirectResponse(url=f"/users/{user_id}/edit?error=Current password is required", status_code=303)

            if not verify_password(current_password, user.hashed_password):
                return RedirectResponse(url=f"/users/{user_id}/edit?error=Current password is incorrect", status_code=303)

            if not new_password:
                return RedirectResponse(url=f"/users/{user_id}/edit?error=New password is required", status_code=303)

            if new_password != confirm_password:
                return RedirectResponse(url=f"/users/{user_id}/edit?error=Passwords do not match", status_code=303)

            # Update password
            user.hashed_password = hash_password(new_password)

        # Handle profile image upload
        if profile_image and profile_image.filename:
            # Validate file type
            allowed_types = ["image/jpeg", "image/jpg", "image/png"]
            if profile_image.content_type not in allowed_types:
                return RedirectResponse(url=f"/users/{user_id}/edit?error=Only JPG and PNG files are allowed", status_code=303)

            # Validate file size (5MB limit)
            content = await profile_image.read()
            if len(content) > 5 * 1024 * 1024:
                return RedirectResponse(url=f"/users/{user_id}/edit?error=File size must be less than 5MB", status_code=303)

            # Generate unique filename
            file_extension = profile_image.filename.split('.')[-1].lower()
            unique_filename = f"{uuid.uuid4()}.{file_extension}"

            # Save file
            current_dir = Path(__file__).parent.parent
            upload_dir = current_dir / "static" / "profiles"
            upload_dir.mkdir(exist_ok=True)

            file_path = upload_dir / unique_filename
            with open(file_path, "wb") as buffer:
                buffer.write(content)

            # Delete old profile image if exists
            if user.profile_image_filename:
                old_file_path = upload_dir / user.profile_image_filename
                if old_file_path.exists():
                    old_file_path.unlink()

            # Update user profile image info
            user.profile_image_filename = unique_filename
            user.profile_image_content_type = profile_image.content_type

        # Update user information
        user.full_name = full_name
        user.email = email
        user.mobile_number = mobile_number
        user.division_id = division_id
        user.district_id = district_id
        user.thana_id = thana_id

        db.commit()

        # Redirect to dashboard with success message
        return RedirectResponse(url="/dashboard?success=Profile updated successfully", status_code=303)

    except Exception as e:
        db.rollback()
        return RedirectResponse(url=f"/users/{user_id}/edit?error=An error occurred while updating profile", status_code=303)